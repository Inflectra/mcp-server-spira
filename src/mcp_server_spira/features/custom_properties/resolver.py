"""CustomPropertyResolver — resolves wire-format custom properties.

Async class that caches custom property definitions per
(template_id, api_artifact_type) and provides methods to resolve
wire-format arrays to friendly {name: value} dicts.

Requires a TemplateContext for shared template_id caching across
resolvers within the same tool invocation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mcp_server_spira.features.search.template_context import TemplateContext
    from mcp_server_spira.models import ArtifactConfig
    from mcp_server_spira.utils.spira_client import SpiraClient

logger = logging.getLogger(__name__)

# Custom property type IDs
CP_TEXT = 1
CP_INTEGER = 2
CP_DECIMAL = 3
CP_BOOLEAN = 4
CP_DATE = 5
CP_LIST = 6
CP_MULTI_LIST = 7
CP_USER = 8
CP_PASSWORD = 9
CP_RELEASE = 10
CP_DATETIME = 11
CP_AUTOMATION_HOST = 12

# Wire-format value field per type ID
_VALUE_FIELD_MAP: dict[int, str] = {
    CP_TEXT: "StringValue",
    CP_INTEGER: "IntegerValue",
    CP_DECIMAL: "DecimalValue",
    CP_BOOLEAN: "BooleanValue",
    CP_DATE: "DateTimeValue",
    CP_LIST: "IntegerValue",
    CP_MULTI_LIST: "IntegerListValue",
    CP_USER: "IntegerValue",
    CP_PASSWORD: "StringValue",
    CP_RELEASE: "IntegerValue",
    CP_DATETIME: "DateTimeValue",
    CP_AUTOMATION_HOST: "IntegerValue",
}


@dataclass(frozen=True)
class CustomPropertyResult:
    """Output of the custom property pre-projection pipeline.

    Returned by ``resolve_for_search_results`` — carries all information
    needed for post-projection injection without the caller needing to
    manage extraction, resolution, or counting logic.

    Spec:
        - Frozen dataclass — immutable after construction
        - effective_fields: fields list with "custom_properties" stripped
          (or original fields if not requested / unsupported)
        - resolved_map: artifact_id → friendly dict; empty dict when not
          requested or resolution failed for all
        - requested: True only when "custom_properties" was in fields AND
          the artifact type supports it (has id_field)
        - warnings: accumulated warnings from resolution (always a list)
    """

    effective_fields: list[str] | None
    resolved_map: dict[int, dict[str, Any]] = field(default_factory=dict)
    requested: bool = False
    warnings: list[str] = field(default_factory=list)
    _id_field_injected: bool = field(default=False, repr=False)

    def inject_into_search_results(
        self,
        result_dict: dict[str, Any],
        config: Any,
    ) -> None:
        """Inject resolved custom properties into a finalized search result dict.

        Mutates *result_dict* in place — updates ``data`` (injects CP dicts),
        ``fields_returned``, ``fields_available``, and optionally adds
        ``custom_properties_resolved``.

        This absorbs the duplicated "step 5a" logic previously inlined in
        both ``_single_product_search`` and ``_single_artifact_search``.

        Spec:
            - Mutates result_dict in place — no return value
            - When not requested: appends "custom_properties" to
              fields_available (advertise availability)
            - When requested and resolved_map is non-empty: injects
              friendly dicts into each artifact in data, appends
              "custom_properties" to fields_returned, sets
              custom_properties_resolved=True
            - When requested but resolved_map is empty: no-op (warning
              already in self.warnings, added by resolve_for_search_results)
            - Uses config.id_field to match artifacts to resolved_map keys
            - When _id_field_injected is True: strips the id_field from
              each projected artifact and from fields_returned after
              injection (user didn't request it, it was only needed for
              matching)
            - Never raises — gracefully skips artifacts without id_field value

        Args:
            result_dict: Output of ``finalize_search_results`` — must have
                keys: data, fields_returned, fields_available.
            config: ArtifactConfig (or any object with id_field attribute).
        """
        if not self.requested:
            # Add to fields_available when not requested
            result_dict["fields_available"] = [
                *result_dict["fields_available"],
                "custom_properties",
            ]
            return

        if self.resolved_map:
            # Inject resolved CPs into projected artifacts
            id_field_name = config.id_field
            for artifact in result_dict["data"]:
                artifact_id = artifact.get(id_field_name) if id_field_name else None
                if artifact_id in self.resolved_map:
                    artifact["custom_properties"] = self.resolved_map[artifact_id]
            # Strip id_field from projected artifacts if it was only added
            # to enable matching (user didn't originally request it).
            if self._id_field_injected and id_field_name:
                for artifact in result_dict["data"]:
                    artifact.pop(id_field_name, None)
                result_dict["fields_returned"] = [
                    f for f in result_dict["fields_returned"] if f != id_field_name
                ]
            result_dict["fields_returned"] = [
                *result_dict["fields_returned"],
                "custom_properties",
            ]
            result_dict["custom_properties_resolved"] = True


class CustomPropertyResolver:
    """Resolves custom property wire format to/from friendly format.

    Caches definitions per (template_id, api_artifact_type). Instance
    lifetime matches a single tool invocation.

    Requires a TemplateContext for shared template_id caching across
    resolvers within the same tool invocation.
    """

    def __init__(
        self,
        spira_client: SpiraClient,
        template_context: TemplateContext,
    ) -> None:
        self._client = spira_client
        self._template_context = template_context
        # Cache: (template_id, api_artifact_type) → list[definition_dict]
        self._definitions_cache: dict[tuple[int, str], list[dict]] = {}

    async def get_template_id(self, product_id: int) -> int | None:
        """Resolve product_id to template_id with caching.

        Delegates to TemplateContext (shared cache across resolvers).

        Spec:
            - Returns int on success, None on failure — never raises
            - Caches per product_id — second call makes zero API calls
            - Delegates entirely to TemplateContext (shared cache)
            - Non-dict response → None (graceful degradation)
            - Missing ProjectTemplateId key → None
            - Non-int ProjectTemplateId value → None
            - API exception → None (logged, not propagated)
        """
        return await self._template_context.get_template_id(product_id)

    async def get_definitions(self, product_id: int, artifact_type: str) -> list[dict]:
        """Fetch custom property definitions for a product/artifact_type pair.

        Spec:
            - ALWAYS returns a list (never raises) — empty list on failure
            - Caches per (template_id, api_artifact_type) tuple
            - If artifact_type has no mapping, returns empty list
            - Uses TemplateContext for artifact type name mapping
            - If template_id resolution fails, returns empty list without
              caching a definitions entry
            - If API call fails or returns non-list, caches empty list
        """
        # Check artifact type mapping via TemplateContext
        api_artifact_type = self._template_context.get_custom_property_api_name(artifact_type)
        if api_artifact_type is None:
            return []

        # Resolve template_id
        template_id = await self.get_template_id(product_id)
        if template_id is None:
            return []

        # Check definitions cache
        cache_key = (template_id, api_artifact_type)
        if cache_key in self._definitions_cache:
            return self._definitions_cache[cache_key]

        # Fetch definitions from API
        try:
            data = await self._client.make_spira_api_get_request(
                f"project-templates/{template_id}/custom-properties/{api_artifact_type}"
            )
            if isinstance(data, list):
                self._definitions_cache[cache_key] = data
                return data
            # Non-list response — cache empty list
            logger.warning(
                "Non-list response for custom property definitions (template=%d, type=%s)",
                template_id,
                api_artifact_type,
            )
            self._definitions_cache[cache_key] = []
            return []
        except Exception:
            logger.exception(
                "Failed to fetch custom property definitions (template=%d, type=%s)",
                template_id,
                api_artifact_type,
            )
            self._definitions_cache[cache_key] = []
            return []

    async def resolve(
        self,
        raw_custom_properties: list[dict],
        product_id: int,
        artifact_type: str,
    ) -> tuple[dict[str, Any], list[str]]:
        """Transform wire-format array to friendly-format dict.

        Args:
            raw_custom_properties: The raw CustomProperties array from API
            product_id: Product ID for template resolution
            artifact_type: Tool-facing artifact type string

        Returns:
            (friendly_dict, warnings) — friendly_dict uses definition Name
            as keys; warnings lists any resolution issues.

        Spec:
            - ALWAYS returns (dict, list[str]) — never raises
            - Null/absent values omitted from output dict
            - Password (type 9) properties always omitted
            - List/MultiList values resolved to display names
            - User/Release/AutomationHost returned as raw integers
            - Unmatched PropertyNumbers produce warning and are skipped
            - Unresolvable list values produce warning, raw int included
        """
        friendly_dict: dict[str, Any] = {}
        warnings: list[str] = []

        try:
            definitions = await self.get_definitions(product_id, artifact_type)
            if not definitions:
                return friendly_dict, warnings

            # Build lookup: CustomPropertyFieldName → definition
            definitions_by_field_name: dict[str, dict] = {
                d["CustomPropertyFieldName"]: d
                for d in definitions
                if "CustomPropertyFieldName" in d
            }

            for entry in raw_custom_properties:
                key, value, warning = self._resolve_single_property(
                    entry, definitions_by_field_name
                )
                if warning:
                    warnings.append(warning)
                if key is not None and value is not None:
                    friendly_dict[key] = value
        except Exception:
            logger.exception(
                "Unexpected error resolving custom properties (product=%d, type=%s)",
                product_id,
                artifact_type,
            )

        return friendly_dict, warnings

    def _resolve_single_property(
        self,
        entry: dict,
        definitions_by_field_name: dict[str, dict],
    ) -> tuple[str | None, Any, str | None]:
        """Resolve a single wire-format entry to (key, value, warning).

        Returns (None, None, warning) if the entry should be skipped.
        Pure function — no I/O.

        Spec:
            - PropertyNumber N → lookup Custom_{N:02d} in definitions
            - Unmatched PropertyNumber → (None, None, warning)
            - Password (type 9) → (None, None, None) — silently omit
            - Unknown type ID → (None, None, warning)
            - Null/absent value → (None, None, None) — silently omit
            - List (6) → resolve integer to display name
            - MultiList (7) → resolve each integer to display name list
            - User (8), Release (10), AutomationHost (12) → raw integer
            - Unresolvable list value → include raw int + warning
        """
        prop_number = entry.get("PropertyNumber")
        if prop_number is None:
            return None, None, None

        # Map PropertyNumber to CustomPropertyFieldName
        field_name = f"Custom_{prop_number:02d}"
        definition = definitions_by_field_name.get(field_name)
        if definition is None:
            return (
                None,
                None,
                f"Unmatched PropertyNumber {prop_number} (no definition for {field_name})",
            )

        type_id = definition.get("CustomPropertyTypeId")
        prop_name = definition.get("Name", field_name)

        # Password — always omit
        if type_id == CP_PASSWORD:
            return None, None, None

        # Unknown type ID
        value_field = _VALUE_FIELD_MAP.get(type_id)  # type: ignore[arg-type]
        if value_field is None:
            return (
                None,
                None,
                f"Unknown type ID {type_id} for property '{prop_name}'",
            )

        # Extract raw value
        raw_value = entry.get(value_field)
        if raw_value is None:
            return None, None, None

        # List (6) — resolve single integer to display name
        if type_id == CP_LIST:
            return self._resolve_list_value(raw_value, definition, prop_name)

        # MultiList (7) — resolve each integer to display name
        if type_id == CP_MULTI_LIST:
            return self._resolve_multi_list_value(raw_value, definition, prop_name)

        # User (8), Release (10), AutomationHost (12) — raw integer
        if type_id in (CP_USER, CP_RELEASE, CP_AUTOMATION_HOST):
            return prop_name, raw_value, None

        # All other scalar types — pass through
        return prop_name, raw_value, None

    def _resolve_list_value(
        self,
        raw_value: Any,
        definition: dict,
        prop_name: str,
    ) -> tuple[str | None, Any, str | None]:
        """Resolve a single List integer to its display name.

        Returns (key, value, warning). If unresolvable, returns raw int
        with a warning.

        Spec:
            - Pure function — no I/O
            - Looks up raw_value in CustomList.Values by CustomPropertyValueId
            - Match found → (prop_name, display_name, None)
            - No match → (prop_name, raw_value, warning) — raw int preserved
            - Missing/empty CustomList → same as no match
        """
        custom_list = definition.get("CustomList") or {}
        values = custom_list.get("Values") or []
        for item in values:
            if item.get("CustomPropertyValueId") == raw_value:
                return prop_name, item.get("Name", raw_value), None
        # Unresolvable — include raw integer with warning
        return (
            prop_name,
            raw_value,
            f"Unresolvable list value {raw_value} for property '{prop_name}'",
        )

    def _resolve_multi_list_value(
        self,
        raw_value: Any,
        definition: dict,
        prop_name: str,
    ) -> tuple[str | None, Any, str | None]:
        """Resolve MultiList integers to display names.

        Returns (key, list_of_names, warning). Unresolvable values are
        included as raw integers with a warning.

        Spec:
            - Pure function — no I/O
            - raw_value may be a list of ints or a single int (coerced to [int])
            - Each int resolved independently via CustomList.Values lookup
            - Unresolvable ints included as raw integers in output list
            - Returns (prop_name, resolved_list, warning_or_None)
            - Warning aggregates all unresolved value IDs
            - Missing/empty CustomList → all values unresolved
        """
        custom_list = definition.get("CustomList") or {}
        values = custom_list.get("Values") or []
        # Build lookup: value_id → name
        id_to_name: dict[int, str] = {
            item["CustomPropertyValueId"]: item.get("Name", "")
            for item in values
            if "CustomPropertyValueId" in item
        }

        # raw_value may be a list or a single int
        int_list = raw_value if isinstance(raw_value, list) else [raw_value]

        resolved_names: list[str | int] = []
        warning: str | None = None
        unresolved: list[int] = []

        for val in int_list:
            name = id_to_name.get(val)
            if name is not None:
                resolved_names.append(name)
            else:
                resolved_names.append(val)
                unresolved.append(val)

        if unresolved:
            warning = f"Unresolvable list value(s) {unresolved} for property '{prop_name}'"

        return prop_name, resolved_names, warning

    # ------------------------------------------------------------------
    # Pipeline method — replaces duplicated steps 4a/5a in callers
    # ------------------------------------------------------------------

    async def resolve_for_search_results(
        self,
        data: list[dict],
        fields: list[str] | None,
        config: ArtifactConfig,
        *,
        product_id: int | None = None,
    ) -> CustomPropertyResult:
        """Full virtual-field pipeline: detect, extract, resolve, report.

        Call BEFORE field projection. Returns a CustomPropertyResult with
        all information needed for post-projection injection.

        Encapsulates the repeated 4-step pattern:
        1. Detect "custom_properties" in fields, strip it
        2. Guard: artifact types without id_field cannot support CP resolution
        3. Extract raw CustomProperties (and ProjectId for mywork) from data
        4. Resolve each artifact's raw CP array to friendly dict

        Args:
            data: Raw API response dicts (read-only for extraction — does
                not mutate the input list).
            fields: Requested field list (may contain "custom_properties").
            config: ArtifactConfig for id_field and artifact_type lookup.
            product_id: Fixed product ID (product search path). When None,
                each artifact's ProjectId is used (mywork cross-product path).

        Returns:
            CustomPropertyResult with effective_fields, resolved_map,
            requested flag, and accumulated warnings.

        Spec:
            - ALWAYS returns CustomPropertyResult — never raises
            - When "custom_properties" not in fields: returns early with
              requested=False, effective_fields=fields unchanged
            - When config.id_field is None: returns requested=False with
              warning, effective_fields=fields unchanged
            - effective_fields always includes config.id_field when
              custom_properties is requested (ensures projection preserves
              the key needed for post-injection matching)
            - _id_field_injected is True when id_field was not in the
              original user-requested fields and was added to effective_fields
            - resolved_map keys are artifact IDs (from config.id_field)
            - resolved_map values are friendly dicts (from self.resolve())
            - Artifacts without raw CustomProperties data are counted as
              failed — warning produced when mixed with successes
            - When product_id is None (mywork path), uses each artifact's
              ProjectId for template resolution
            - Warnings include per-artifact resolution warnings AND
              summary warnings about skipped/failed counts
        """
        # Early return: custom_properties not requested
        if not fields or "custom_properties" not in fields:
            return CustomPropertyResult(effective_fields=fields)

        # Guard: artifact types without id_field cannot support CP resolution
        id_field_name = config.id_field
        if not id_field_name:
            return CustomPropertyResult(
                effective_fields=fields,  # Restore original fields
                warnings=[
                    f"custom_properties is not supported for '{config.artifact_type}' "
                    "(no artifact ID field configured). Ignoring."
                ],
            )

        # Strip "custom_properties" from fields, ensure id_field survives
        # projection so inject_into_search_results can match artifacts.
        effective_fields = [f for f in fields if f != "custom_properties"]
        id_field_injected = False
        if id_field_name not in effective_fields:
            effective_fields.append(id_field_name)
            id_field_injected = True

        # Extract raw CustomProperties (and ProjectId for mywork) BEFORE projection
        raw_cp_map: dict[int, list[dict]] = {}
        raw_project_ids: dict[int, int] = {}
        for artifact in data:
            artifact_id = artifact.get(id_field_name)
            if artifact_id is None:
                continue
            raw_cp = artifact.get("CustomProperties")
            if raw_cp is not None:
                raw_cp_map[artifact_id] = raw_cp
            if product_id is None:
                # Mywork path: need per-artifact ProjectId
                proj_id = artifact.get("ProjectId")
                if proj_id is not None:
                    raw_project_ids[artifact_id] = proj_id

        # Resolve custom properties for each artifact
        warnings: list[str] = []
        resolved_map: dict[int, dict[str, Any]] = {}
        resolved_count = 0
        failed_count = 0

        for artifact in data:
            artifact_id = artifact.get(id_field_name)
            if artifact_id is None:
                failed_count += 1
                continue

            raw_cp = raw_cp_map.get(artifact_id)
            # Determine the product_id for this artifact
            resolve_product_id = product_id
            if resolve_product_id is None:
                resolve_product_id = raw_project_ids.get(artifact_id)

            if raw_cp is not None and resolve_product_id is not None:
                friendly, cp_warnings = await self.resolve(
                    raw_cp, resolve_product_id, config.artifact_type
                )
                warnings.extend(cp_warnings)
                resolved_map[artifact_id] = friendly
                resolved_count += 1
            else:
                failed_count += 1

        # Summary warnings
        if failed_count > 0 and resolved_count > 0:
            detail = "missing CustomProperties data"
            if product_id is None:
                detail += " or ProjectId"
            warnings.append(f"Custom properties skipped for {failed_count} artifact(s) ({detail}).")
        elif failed_count > 0 and resolved_count == 0:
            detail = "no CustomProperties data available"
            if product_id is None:
                detail += " or ProjectId"
            warnings.append(
                "Custom property resolution failed for all artifacts "
                f"({config.artifact_type}): {detail}."
            )

        return CustomPropertyResult(
            effective_fields=effective_fields,
            resolved_map=resolved_map,
            requested=True,
            warnings=warnings,
            _id_field_injected=id_field_injected,
        )
