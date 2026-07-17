"""Custom property serialization — friendly format to wire format.

Stateless functions that convert friendly-format {name: value} dicts
to wire-format arrays for POST requests to the Spira API.
"""

from __future__ import annotations

import logging
from typing import Any

from mcp_server_spira.features.custom_properties.resolver import (
    _VALUE_FIELD_MAP,
    CP_AUTOMATION_HOST,
    CP_LIST,
    CP_MULTI_LIST,
    CP_RELEASE,
    CP_USER,
)

logger = logging.getLogger(__name__)

# Types that require integer-only values (non-int → warning + skip)
_INT_ONLY_TYPES = frozenset({CP_USER, CP_RELEASE, CP_AUTOMATION_HOST})

# All supported type IDs for serialization
_SUPPORTED_TYPES = frozenset(_VALUE_FIELD_MAP.keys()) - frozenset({9})  # Exclude Password (type 9)


def serialize_custom_properties(
    friendly_dict: dict[str, Any],
    definitions: list[dict],
    *,
    warnings: list[str] | None = None,
) -> tuple[list[dict], list[str]]:
    """Transform friendly-format dict to wire-format array.

    Pure function — no I/O, no async. Definitions must be pre-fetched
    by the caller via resolver.get_definitions().

    Args:
        friendly_dict: {property_name: value} dict from user
        definitions: Custom property definitions for this artifact type
        warnings: Optional pre-existing warnings list to extend

    Returns:
        (wire_format_array, warnings)

    Spec:
        - ALWAYS returns (list, list[str]) — never raises
        - Property name matching is case-insensitive
        - List values: string → resolved to CustomPropertyValueId int;
          int → passed through
        - MultiList values: each element resolved independently
        - User/AutomationHost/Release: must be int, non-int →
          warning + skip
        - Unknown property names produce warning + skip
        - Unresolvable list display names produce warning + skip
        - Null/empty values (None, "", []) produce a wire entry with
          typed value field set to None (clears the property in Spira).
          No warning is produced for cleared properties.
        - Each wire entry has: PropertyNumber,
          Definition.CustomPropertyId, and the correct typed value field
    """
    warn_list: list[str] = warnings if warnings is not None else []
    wire_array: list[dict] = []

    try:
        # Build case-insensitive lookup: lower(Name) → definition
        defs_by_name: dict[str, dict[str, Any]] = {}
        for d in definitions:
            name = d.get("Name")
            if name is not None:
                defs_by_name[name.lower()] = d

        for prop_name, value in friendly_dict.items():
            # Case-insensitive lookup — unknown names warned+skipped
            # regardless of whether value is null/empty
            defn = defs_by_name.get(prop_name.lower())
            if defn is None:
                warn_list.append(f"Unknown property name '{prop_name}' — skipped")
                continue

            type_id = defn.get("CustomPropertyTypeId")

            # Unsupported type — warn+skip even for null values
            if type_id not in _SUPPORTED_TYPES:
                warn_list.append(
                    f"Unsupported type ID {type_id} for property '{prop_name}' — skipped"
                )
                continue

            # Determine if this is a "clear" request (null/empty value)
            is_clear = (
                value is None
                or (isinstance(value, str) and value == "")
                or (isinstance(value, list) and len(value) == 0)
            )

            if is_clear:
                # Build a wire entry with null value — clears the property
                entry = _build_null_wire_entry(defn)
                if entry is not None:
                    wire_array.append(entry)
                continue

            # Parse property number from field name
            field_name = defn.get("CustomPropertyFieldName", "")
            prop_number = _parse_property_number(field_name)
            if prop_number is None:
                warn_list.append(
                    f"Malformed CustomPropertyFieldName "
                    f"'{field_name}' for property "
                    f"'{prop_name}' — skipped"
                )
                continue

            # Integer-only types: User, Release, AutomationHost
            if type_id in _INT_ONLY_TYPES and not isinstance(value, int):
                warn_list.append(
                    f"Property '{prop_name}' (type "
                    f"{type_id}) requires int, got "
                    f"{type(value).__name__} — skipped"
                )
                continue

            # Resolve List values
            if type_id == CP_LIST:
                resolved = _resolve_list_for_wire(value, defn, prop_name, warn_list)
                if resolved is None:
                    continue
                value = resolved

            # Resolve MultiList values
            elif type_id == CP_MULTI_LIST:
                resolved_list = _resolve_multi_list_for_wire(value, defn, prop_name, warn_list)
                if resolved_list is None:
                    continue
                value = resolved_list

            # Build wire entry
            entry = _build_wire_entry(defn, value, type_id)
            if entry is not None:
                wire_array.append(entry)

    except Exception:
        logger.exception("Unexpected error in serialize_custom_properties")

    return wire_array, warn_list


def _build_wire_entry(
    definition: dict,
    value: Any,
    type_id: int,
) -> dict | None:
    """Build a single wire-format entry from a definition and value.

    Returns None if the value cannot be serialized (caller adds
    warning). Pure function — no I/O.

    Spec:
        - Extracts PropertyNumber from CustomPropertyFieldName
        - Sets Definition.CustomPropertyId from definition
        - Places value in the correct typed field per
          _VALUE_FIELD_MAP[type_id]
        - Returns None only if PropertyNumber cannot be parsed
    """
    field_name = definition.get("CustomPropertyFieldName", "")
    prop_number = _parse_property_number(field_name)
    if prop_number is None:
        return None

    cp_id = definition.get("CustomPropertyId")
    value_field = _VALUE_FIELD_MAP.get(type_id)
    if value_field is None:
        return None

    return {
        "PropertyNumber": prop_number,
        "Definition": {"CustomPropertyId": cp_id},
        value_field: value,
    }


def _build_null_wire_entry(definition: dict) -> dict | None:
    """Build a wire-format entry that clears a custom property.

    Sets the typed value field to None (JSON null). Spira interprets
    this as "clear the property value".

    Returns None if PropertyNumber cannot be parsed (malformed definition).

    Spec:
        - Extracts PropertyNumber via _parse_property_number
        - Looks up value_field from _VALUE_FIELD_MAP using type ID
        - Returns dict with PropertyNumber, Definition.CustomPropertyId,
          and value_field set to None
        - Returns None if PropertyNumber parse fails or type unsupported
    """
    field_name = definition.get("CustomPropertyFieldName", "")
    prop_number = _parse_property_number(field_name)
    if prop_number is None:
        return None

    type_id = definition.get("CustomPropertyTypeId")
    value_field = _VALUE_FIELD_MAP.get(type_id)  # type: ignore[arg-type]
    if value_field is None:
        return None

    cp_id = definition.get("CustomPropertyId")
    return {
        "PropertyNumber": prop_number,
        "Definition": {"CustomPropertyId": cp_id},
        value_field: None,
    }


def _parse_property_number(field_name: str) -> int | None:
    """Extract integer from CustomPropertyFieldName.

    Examples: 'Custom_04' → 4, 'Custom_12' → 12.

    Returns None if field_name doesn't match expected pattern.

    Spec:
        - Split on '_', parse second part as int
        - Returns None for empty string, missing underscore,
          non-integer suffix, or unexpected prefix
    """
    if not field_name or "_" not in field_name:
        return None
    parts = field_name.split("_", 1)
    if len(parts) != 2:
        return None
    try:
        return int(parts[1])
    except (ValueError, TypeError):
        return None


def _resolve_list_for_wire(
    value: Any,
    definition: dict,
    prop_name: str,
    warnings: list[str],
) -> int | None:
    """Resolve a List value to its integer ID for wire format.

    If value is already int, pass through. If string, look up in
    CustomList.Values by Name. Returns None if unresolvable (adds
    warning).

    Spec:
        - int value → passthrough (no lookup needed)
        - str value → case-insensitive lookup in CustomList.Values by Name
        - Match found → return CustomPropertyValueId int
        - No match → append warning, return None (caller skips)
        - Non-str/non-int → append warning, return None
        - Missing/empty CustomList → same as no match for str values
    """
    if isinstance(value, int):
        return value

    if not isinstance(value, str):
        warnings.append(
            f"Property '{prop_name}' (List) expects string or "
            f"int, got {type(value).__name__} — skipped"
        )
        return None

    custom_list = definition.get("CustomList") or {}
    list_values = custom_list.get("Values") or []
    # Case-insensitive lookup for list display names
    value_lower = value.lower()
    for item in list_values:
        item_name = item.get("Name")
        if item_name is not None and item_name.lower() == value_lower:
            val_id: int | None = item.get("CustomPropertyValueId")
            return val_id

    warnings.append(f"Unresolvable list value '{value}' for property '{prop_name}' — skipped")
    return None


def _resolve_multi_list_for_wire(
    value: Any,
    definition: dict,
    prop_name: str,
    warnings: list[str],
) -> list[int] | None:
    """Resolve MultiList values to integer IDs for wire format.

    Each element resolved independently: string → ID, int →
    passthrough. Returns None if any element is unresolvable (adds
    warning).

    Spec:
        - value must be a list — non-list → warning + return None
        - Each element: int → passthrough, str → case-insensitive lookup by Name
        - Any unresolvable string → warning + return None (entire property skipped)
        - Non-str/non-int element → warning + return None
        - All resolved → return list[int]
        - Missing/empty CustomList → all string elements unresolvable
    """
    if not isinstance(value, list):
        warnings.append(
            f"Property '{prop_name}' (MultiList) expects a "
            f"list, got {type(value).__name__} — skipped"
        )
        return None

    custom_list = definition.get("CustomList") or {}
    list_values = custom_list.get("Values") or []
    # Build case-insensitive lookup: lower(name) → id
    name_to_id: dict[str, int] = {
        item["Name"].lower(): item["CustomPropertyValueId"]
        for item in list_values
        if "Name" in item and "CustomPropertyValueId" in item
    }

    resolved_ids: list[int] = []
    for element in value:
        if isinstance(element, int):
            resolved_ids.append(element)
        elif isinstance(element, str):
            val_id = name_to_id.get(element.lower())
            if val_id is not None:
                resolved_ids.append(val_id)
            else:
                warnings.append(
                    f"Unresolvable list value '{element}' for property '{prop_name}' — skipped"
                )
                return None
        else:
            warnings.append(
                f"Property '{prop_name}' (MultiList) element "
                f"must be string or int, got "
                f"{type(element).__name__} — skipped"
            )
            return None

    return resolved_ids
