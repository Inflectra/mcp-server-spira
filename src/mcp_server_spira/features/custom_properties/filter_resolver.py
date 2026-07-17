"""Custom property filter resolution — friendly names to RemoteFilter format.

Separates Tier 2 filter entries into standard filters (field in all_fields)
and custom property filters (field matches a CP definition name). CP filters
are resolved to wire-format field names and integer values, returned as
already-built RemoteFilter dicts ready to append to the filter array.
"""

from __future__ import annotations

import logging
from typing import Any

from mcp_server_spira.features.custom_properties.resolver import (
    CP_AUTOMATION_HOST,
    CP_BOOLEAN,
    CP_DATE,
    CP_DATETIME,
    CP_DECIMAL,
    CP_INTEGER,
    CP_LIST,
    CP_MULTI_LIST,
    CP_PASSWORD,
    CP_RELEASE,
    CP_TEXT,
    CP_USER,
    CustomPropertyResolver,
)
from mcp_server_spira.features.search.filter_builder import build_date_range_filter_fov

logger = logging.getLogger(__name__)

# Types that produce IntValue RemoteFilters (single integer)
_INT_VALUE_TYPES = frozenset({CP_INTEGER, CP_DECIMAL, CP_USER, CP_RELEASE, CP_AUTOMATION_HOST})

# Types that produce StringValue RemoteFilters
_STRING_VALUE_TYPES = frozenset({CP_TEXT, CP_PASSWORD})

# Operator aliases for equality
_EQUALITY_OPS: set[str] = {"eq", "=", "==", "is", "equals"}

# Operator aliases for "in"
_IN_OPS: set[str] = {"in"}

# Operator aliases for string matching
_STRING_MATCH_OPS: set[str] = {"contains", "like", "startswith", "starts_with", "icontains"}

# Comparison operators (numeric)
_COMPARISON_OPS: set[str] = {">=", "gte", ">", "gt", "<=", "lte", "<", "lt"}

# All date operators
_DATE_OPS: set[str] = {">=", "gte", ">", "gt", "after", "<=", "lte", "<", "lt", "before", "between"}


async def resolve_custom_property_filters(
    tier2_filters: list[dict] | None,
    all_fields: list[str],
    custom_property_resolver: CustomPropertyResolver,
    product_id: int,
    artifact_type: str,
) -> tuple[list[dict], list[dict], list[str]]:
    """Separate and resolve custom property filters from Tier 2 filters.

    Splits tier2_filters into:
    - standard_filters: entries whose field IS in all_fields (pass through unchanged)
    - cp_filters_resolved: entries whose field matched a CP definition, resolved
      to wire-format field names and integer values

    The caller merges cp_filters_resolved into the RemoteFilter array directly
    (they are already in RemoteFilter format, not field/operator/value format).

    Args:
        tier2_filters: Raw Tier 2 filter dicts from the LLM
        all_fields: The artifact config's all_fields for standard field validation
        custom_property_resolver: Resolver instance (already instantiated)
        product_id: Product ID for definition lookup
        artifact_type: Tool-facing artifact type string

    Returns:
        (standard_filters, cp_remote_filters, warnings)
        - standard_filters: Tier 2 entries that are NOT custom properties
          (passed to build_remote_filters as before)
        - cp_remote_filters: Already-built RemoteFilter dicts for CP filters
        - warnings: Any resolution issues

    Spec:
        - ALWAYS returns (list, list, list[str]) — never raises
        - A filter entry is a CP filter IFF: field not in all_fields AND
          field matches a definition Name (case-insensitive)
        - If field is in all_fields, it's always a standard filter (even if
          it happens to match a CP name — standard fields take precedence)
        - List/MultiList string values resolved to integer IDs
        - List/MultiList integer values passed through
        - Boolean values converted to "Y"/"N" StringValue
        - Date/DateTime values delegated to existing date filter logic
        - Unresolvable list values → warning + skip
        - Password type filters → StringValue (same as Text)
        - Definitions fetched once via resolver (cached)
    """
    standard_filters: list[dict] = []
    cp_remote_filters: list[dict] = []
    warnings: list[str] = []

    if not tier2_filters:
        return standard_filters, cp_remote_filters, warnings

    try:
        # Fetch definitions once (cached by resolver)
        definitions = await custom_property_resolver.get_definitions(product_id, artifact_type)

        # Build case-insensitive lookup: lower(Name) → definition
        defs_by_name: dict[str, dict] = {}
        for d in definitions:
            name = d.get("Name")
            if name is not None:
                defs_by_name[name.lower()] = d

        # Build set for exact match (standard fields use exact match)
        all_fields_set: set[str] = set(all_fields)

        for entry in tier2_filters:
            field = entry.get("field")
            if field is None:
                # Missing field — pass through to standard (build_remote_filters will warn)
                standard_filters.append(entry)
                continue

            # Standard fields take precedence
            if field in all_fields_set:
                standard_filters.append(entry)
                continue

            # Attempt case-insensitive match against CP definition names
            defn = defs_by_name.get(field.lower())
            if defn is None:
                # Not a CP either — pass through to standard (build_remote_filters will warn)
                standard_filters.append(entry)
                continue

            # This is a CP filter — resolve it
            remote_filter, warning = _build_cp_remote_filter(entry, defn)
            if warning:
                warnings.append(warning)
            if remote_filter is not None:
                cp_remote_filters.append(remote_filter)

    except Exception:
        logger.exception(
            "Unexpected error resolving custom property filters (product=%d, type=%s)",
            product_id,
            artifact_type,
        )
        # On failure, pass all filters through as standard so they aren't
        # silently dropped — build_remote_filters will handle/warn as needed.
        return list(tier2_filters), [], warnings

    return standard_filters, cp_remote_filters, warnings


def _build_cp_remote_filter(
    entry: dict,
    definition: dict,
) -> tuple[dict | None, str | None]:
    """Build a RemoteFilter dict from a CP filter entry and its definition.

    Resolves the friendly field name to CustomPropertyFieldName and builds
    the appropriate RemoteFilter based on the CP type.

    Spec:
        - Never raises — all invalid inputs produce (None, warning_string)
        - Returns (RemoteFilter_dict, None) on success
        - Returns (None, warning) on failure (unresolvable value, wrong type)
        - RemoteFilter uses CustomPropertyFieldName as PropertyName
        - List/MultiList string values resolved to integer IDs
        - Boolean → "Y"/"N" StringValue
        - Date/DateTime → delegated to build_date_range_filter_fov
    """
    field_name = definition.get("CustomPropertyFieldName", "")
    type_id = definition.get("CustomPropertyTypeId")
    prop_name = definition.get("Name", field_name)

    if not field_name:
        return None, f"CP filter '{prop_name}': missing CustomPropertyFieldName — skipped"

    operator_raw = entry.get("operator")
    value = entry.get("value")
    op = _normalize_operator(operator_raw, value)

    # --- Date/DateTime types → delegate to existing date filter logic ---
    if type_id in (CP_DATE, CP_DATETIME):
        if op in _DATE_OPS:
            return build_date_range_filter_fov(field_name, op, value)
        # eq operator on date → treat as >= (start of day)
        if op in _EQUALITY_OPS:
            return build_date_range_filter_fov(field_name, ">=", value)
        return None, (
            f"CP filter '{prop_name}': unsupported operator '{op}' for Date/DateTime type — skipped"
        )

    # --- Boolean type → "Y"/"N" StringValue ---
    if type_id == CP_BOOLEAN:
        if op not in _EQUALITY_OPS:
            return None, (
                f"CP filter '{prop_name}': only 'eq' operator supported for "
                f"Boolean type, got '{op}' — skipped"
            )
        if isinstance(value, bool):
            return {
                "PropertyName": field_name,
                "StringValue": "Y" if value else "N",
            }, None
        # Try string coercion for common representations
        if isinstance(value, str) and value.lower() in ("true", "yes", "y", "1"):
            return {"PropertyName": field_name, "StringValue": "Y"}, None
        if isinstance(value, str) and value.lower() in ("false", "no", "n", "0"):
            return {"PropertyName": field_name, "StringValue": "N"}, None
        return None, (
            f"CP filter '{prop_name}': Boolean type requires true/false value, "
            f"got {type(value).__name__} '{value}' — skipped"
        )

    # --- Text / Password types → StringValue ---
    if type_id in _STRING_VALUE_TYPES:
        if op in (_EQUALITY_OPS | _STRING_MATCH_OPS):
            if isinstance(value, str):
                return {"PropertyName": field_name, "StringValue": value}, None
            return None, (
                f"CP filter '{prop_name}': Text/Password type requires string value, "
                f"got {type(value).__name__} — skipped"
            )
        return None, (
            f"CP filter '{prop_name}': unsupported operator '{op}' for Text type — skipped"
        )

    # --- List type ---
    if type_id == CP_LIST:
        return _build_list_filter(entry, definition, field_name, prop_name, op, value)

    # --- MultiList type ---
    if type_id == CP_MULTI_LIST:
        return _build_multi_list_filter(definition, field_name, prop_name, op, value)

    # --- Integer / Decimal / User / Release / AutomationHost → IntValue ---
    if type_id in _INT_VALUE_TYPES:
        return _build_int_filter(field_name, prop_name, type_id, op, value)

    # Unknown type
    return None, f"CP filter '{prop_name}': unsupported type ID {type_id} — skipped"


def _build_list_filter(
    entry: dict,
    definition: dict,
    field_name: str,
    prop_name: str,
    op: str,
    value: Any,
) -> tuple[dict | None, str | None]:
    """Build RemoteFilter for a List (6) type CP filter.

    Spec:
        - eq operator + string value → resolve to IntValue
        - eq operator + int value → IntValue passthrough
        - in operator + list of strings → resolve each to MultiValue
        - in operator + list of ints → MultiValue passthrough
        - Unresolvable display name → (None, warning)
    """
    if op in _EQUALITY_OPS:
        if isinstance(value, int):
            return {"PropertyName": field_name, "IntValue": value}, None
        if isinstance(value, str):
            resolved_id, warning = _resolve_list_display_name(value, definition, prop_name)
            if resolved_id is None:
                return None, warning or (
                    f"CP filter '{prop_name}': unresolvable list value '{value}' — skipped"
                )
            return {"PropertyName": field_name, "IntValue": resolved_id}, None
        return None, (
            f"CP filter '{prop_name}': List type with 'eq' requires string or int, "
            f"got {type(value).__name__} — skipped"
        )

    if op in _IN_OPS:
        if not isinstance(value, list):
            return None, (
                f"CP filter '{prop_name}': 'in' operator requires a list value, "
                f"got {type(value).__name__} — skipped"
            )
        resolved_ids, warning = _resolve_list_values(value, definition, prop_name)
        if resolved_ids is None:
            return None, warning or (
                f"CP filter '{prop_name}': unresolvable list value(s) in {value!r} — skipped"
            )
        return {
            "PropertyName": field_name,
            "MultiValue": {"Values": resolved_ids, "IsNone": False},
        }, None

    return None, (f"CP filter '{prop_name}': unsupported operator '{op}' for List type — skipped")


def _build_multi_list_filter(
    definition: dict,
    field_name: str,
    prop_name: str,
    op: str,
    value: Any,
) -> tuple[dict | None, str | None]:
    """Build RemoteFilter for a MultiList (7) type CP filter.

    Spec:
        - in operator + list of strings → resolve each to MultiValue
        - in operator + list of ints → MultiValue passthrough
        - Unresolvable display name → (None, warning)
    """
    if op not in _IN_OPS:
        return None, (
            f"CP filter '{prop_name}': only 'in' operator supported for "
            f"MultiList type, got '{op}' — skipped"
        )

    if not isinstance(value, list):
        return None, (
            f"CP filter '{prop_name}': MultiList 'in' requires a list value, "
            f"got {type(value).__name__} — skipped"
        )

    resolved_ids, warning = _resolve_list_values(value, definition, prop_name)
    if resolved_ids is None:
        return None, warning or (
            f"CP filter '{prop_name}': unresolvable list value(s) in {value!r} — skipped"
        )

    return {
        "PropertyName": field_name,
        "MultiValue": {"Values": resolved_ids, "IsNone": False},
    }, None


def _build_int_filter(
    field_name: str,
    prop_name: str,
    type_id: int,
    op: str,
    value: Any,
) -> tuple[dict | None, str | None]:
    """Build RemoteFilter for Integer/Decimal/User/Release/AutomationHost types.

    Spec:
        - eq operator + int value → IntValue
        - in operator + list of ints → MultiValue
        - Comparison operators (>=, >, <=, <) + int → IntValue with warning
          (Spira API treats IntValue as equality regardless of operator)
        - Non-int value → (None, warning)
    """
    if op in _EQUALITY_OPS:
        if isinstance(value, int) and not isinstance(value, bool):
            return {"PropertyName": field_name, "IntValue": value}, None
        return None, (
            f"CP filter '{prop_name}': Integer type with 'eq' requires int value, "
            f"got {type(value).__name__} — skipped"
        )

    if op in _IN_OPS:
        if not isinstance(value, list):
            return None, (
                f"CP filter '{prop_name}': 'in' operator requires a list value, "
                f"got {type(value).__name__} — skipped"
            )
        # Validate all elements are int
        if not all(isinstance(v, int) and not isinstance(v, bool) for v in value):
            return None, (
                f"CP filter '{prop_name}': 'in' operator requires all integer values — skipped"
            )
        return {
            "PropertyName": field_name,
            "MultiValue": {"Values": value, "IsNone": False},
        }, None

    if op in _COMPARISON_OPS:
        if isinstance(value, int) and not isinstance(value, bool):
            return {"PropertyName": field_name, "IntValue": value}, (
                f"CP filter '{prop_name}': comparison operator '{op}' on integer custom "
                "properties is treated as equality by the Spira API."
            )
        return None, (
            f"CP filter '{prop_name}': comparison operator requires int value, "
            f"got {type(value).__name__} — skipped"
        )

    return None, (
        f"CP filter '{prop_name}': unsupported operator '{op}' for Integer type — skipped"
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _normalize_operator(operator: str | None, value: Any) -> str:
    """Normalize operator string or infer from value type.

    Spec:
        - If operator provided, return stripped lowercase
        - If None: bool → "eq", int → "eq", str → "eq", list → "in"
        - Default → "eq"
    """
    if operator is not None:
        return str(operator).strip().lower()

    # Infer from value type
    if isinstance(value, bool):
        return "eq"
    if isinstance(value, int):
        return "eq"
    if isinstance(value, str):
        return "eq"
    if isinstance(value, list):
        return "in"
    return "eq"


def _resolve_list_display_name(
    display_name: str,
    definition: dict,
    prop_name: str,
) -> tuple[int | None, str | None]:
    """Resolve a single list display name to its CustomPropertyValueId.

    Two-stage resolution matching standard field behaviour:
    1. Case-insensitive exact match on Name
    2. Substring fallback — if exactly one item's Name contains the search
       string (case-insensitively), resolve to that item. Multiple matches
       produce an ambiguity warning.

    Returns (resolved_id, warning).

    Spec:
        - Case-insensitive exact match tried first — "Production" == "production"
        - Substring fallback: "Easy" matches "1 - Easy" when unambiguous
        - Ambiguous substring (multiple matches) → (None, warning)
        - Returns (int, None) on match
        - Returns (None, warning) on no match or ambiguity
        - Returns (None, warning) if CustomPropertyValueId is not an int
        - Returns (None, None) if CustomList or Values is missing/empty
    """
    custom_list = definition.get("CustomList") or {}
    list_values = custom_list.get("Values") or []
    display_name_lower = display_name.lower()

    # Stage 1: case-insensitive exact match
    for item in list_values:
        item_name = item.get("Name")
        if item_name is not None and item_name.lower() == display_name_lower:
            val_id = item.get("CustomPropertyValueId")
            if isinstance(val_id, int):
                return val_id, None
            return None, (
                f"CP filter '{prop_name}': matched '{item_name}' but "
                f"CustomPropertyValueId is not an int — skipped"
            )

    # Stage 2: substring fallback — match when display_name contains an
    # item's Name, or an item's Name contains display_name
    # (mirrors NameResolver._resolve_name behaviour, extended to handle
    # prefixed user input like "1 - Easy" matching stored "Easy")
    substring_matches: list[tuple[str, int]] = []
    for item in list_values:
        item_name = item.get("Name")
        if item_name is not None:
            item_lower = item_name.lower()
            if display_name_lower in item_lower or item_lower in display_name_lower:
                val_id = item.get("CustomPropertyValueId")
                if isinstance(val_id, int):
                    substring_matches.append((item_name, val_id))

    if len(substring_matches) == 1:
        return substring_matches[0][1], None

    if len(substring_matches) > 1:
        valid_names = ", ".join(name for name, _ in substring_matches)
        return None, (
            f"CP filter '{prop_name}': '{display_name}' is ambiguous — "
            f"matches: {valid_names}. Use a more specific name or integer ID."
        )

    # No match (neither exact nor substring)
    valid_names = ", ".join(item.get("Name", "") for item in list_values if item.get("Name"))
    return None, (
        f"CP filter '{prop_name}': unresolvable list value '{display_name}' — "
        f"valid values: {valid_names}"
    )


def _resolve_list_values(
    values: list,
    definition: dict,
    prop_name: str,
) -> tuple[list[int] | None, str | None]:
    """Resolve a list of display names/ints to integer IDs.

    Each element: int → passthrough, str → resolve via CustomList with
    substring fallback (same two-stage logic as _resolve_list_display_name).
    Returns (None, warning) if any string element is unresolvable.

    Spec:
        - int elements pass through unchanged
        - str elements resolved case-insensitively via CustomList.Values
        - Substring fallback for str elements (unambiguous single match)
        - Ambiguous substring → (None, warning)
        - Any unresolvable str → (None, warning) (entire filter skipped)
        - Non-str/non-int element → (None, warning)
    """
    custom_list = definition.get("CustomList") or {}
    list_values = custom_list.get("Values") or []
    name_to_id: dict[str, int] = {
        item["Name"].lower(): item["CustomPropertyValueId"]
        for item in list_values
        if "Name" in item and "CustomPropertyValueId" in item
    }

    resolved: list[int] = []
    for element in values:
        if isinstance(element, int) and not isinstance(element, bool):
            resolved.append(element)
        elif isinstance(element, str):
            # Stage 1: exact case-insensitive match
            val_id = name_to_id.get(element.lower())
            if val_id is not None:
                resolved.append(val_id)
                continue

            # Stage 2: substring fallback
            element_lower = element.lower()
            substring_matches: list[tuple[str, int]] = []
            for item in list_values:
                item_name = item.get("Name")
                if item_name is not None and isinstance(item.get("CustomPropertyValueId"), int):
                    item_lower = item_name.lower()
                    if element_lower in item_lower or item_lower in element_lower:
                        substring_matches.append((item_name, item["CustomPropertyValueId"]))

            if len(substring_matches) == 1:
                resolved.append(substring_matches[0][1])
            elif len(substring_matches) > 1:
                ambiguous = ", ".join(name for name, _ in substring_matches)
                return None, (
                    f"CP filter '{prop_name}': '{element}' is ambiguous — "
                    f"matches: {ambiguous}. Use a more specific name or integer ID."
                )
            else:
                valid_names = ", ".join(
                    item.get("Name", "") for item in list_values if item.get("Name")
                )
                return None, (
                    f"CP filter '{prop_name}': unresolvable list value '{element}' — "
                    f"valid values: {valid_names}"
                )
        else:
            return None, (
                f"CP filter '{prop_name}': expected int or str in list, "
                f"got {type(element).__name__} — skipped"
            )

    return resolved, None
