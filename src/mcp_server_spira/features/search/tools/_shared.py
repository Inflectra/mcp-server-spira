"""Shared utility functions for unified search tools.

Contains field derivation, client-side filtering, and field projection
logic used by both ``mywork`` and ``product`` search tools.

Extracted from ``mywork.py`` to keep the codebase DRY.
"""

from collections.abc import Mapping
from typing import Any

from mcp_server_spira.utils.common.field_projection import apply_field_projection


def derive_display_name_field(id_field: str) -> str:
    """Derive the human-readable display name field from a normalised ID field.

    Replaces trailing ``"Id"`` with ``"Name"``.  If the input does not end in
    ``"Id"``, appends ``"Name"`` instead.

    Spec:
        - Input ending in "Id" → trailing "Id" replaced with "Name"
        - Input NOT ending in "Id" → "Name" appended
        - Pure function — no side effects, deterministic
        - Never raises for any string input

    Examples:
        >>> derive_display_name_field("IncidentStatusId")
        'IncidentStatusName'
        >>> derive_display_name_field("ImportanceId")
        'ImportanceName'
        >>> derive_display_name_field("Foo")
        'FooName'
    """
    if id_field.endswith("Id"):
        return id_field[:-2] + "Name"
    return id_field + "Name"


def apply_contains_filter(
    data: list[dict],
    field_name: str | None,
    filter_value: str | None,
    all_fields: list[str],
    filter_label: str,
) -> tuple[list[dict], list[str]]:
    """Apply case-insensitive substring filtering on a display name field.

    The *field_name* is the raw normalised ID field from config (e.g.
    ``"IncidentStatusId"``).  The function derives the display name field
    (``"IncidentStatusName"``) via :func:`derive_display_name_field` and
    matches *filter_value* as a case-insensitive substring against each
    object's value for that field.

    Spec:
        - filter_value is None → no-op, returns (data, []) — original list
          object unchanged
        - field_name is None → returns (data, [warning]) — filter skipped,
          warning mentions "does not support {filter_label} filtering"
        - Derived display field not in all_fields → returns (data, [warning])
          — filter skipped, warning mentions "not available"
        - At least one match → returns (filtered_subset, []) — only matching
          objects, no warnings
        - Zero matches → returns (data, [warning]) — ALL data returned
          unfiltered with warning mentioning the filter_value and filter_label
        - Matching is case-insensitive substring (not exact, not fuzzy)
        - warnings is always a list (never None)
        - Never raises

    Returns ``(filtered_data, warnings)``.

    Fallback behaviour:
    - *filter_value* is ``None`` → no-op, return original data.
    - *field_name* is ``None`` → skip filter with warning.
    - Derived display field not in *all_fields* → skip filter with warning.
    - No objects match → return all data unfiltered with warning.
    """
    if filter_value is None:
        return data, []

    if field_name is None:
        return data, [f"This artifact type does not support {filter_label} filtering."]

    display_field = derive_display_name_field(field_name)

    if display_field not in all_fields:
        return data, [
            f"Cannot filter by {filter_label}: field '{display_field}' "
            f"is not available for this artifact type."
        ]

    filtered = [
        obj for obj in data if filter_value.lower() in str(obj.get(display_field, "")).lower()
    ]

    if not filtered:
        return data, [
            f"No items matched {filter_label} filter '{filter_value}'. "
            f"Returning all data unfiltered."
        ]

    return filtered, []


__all__ = [
    "apply_contains_filter",
    "derive_display_name_field",
    "finalize_search_results",
]


def finalize_search_results(
    data: list[dict],
    fields: list[str] | None,
    config: Any,
    *,
    pagination: Mapping[str, Any],
    warnings: list[str],
    artifact_type: str | None = None,
) -> dict[str, Any]:
    """Apply field projection and assemble a search result dict.

    Shared tail of the search pipeline used by mywork, product, and program
    tools. Handles the "project fields → build result dict" step that was
    previously duplicated in each tool.

    Spec:
        - Pure function — no I/O, no async, no side effects
        - ALWAYS returns a dict with keys: data, fields_returned,
          fields_available, pagination, warnings — callers destructure
          without key-existence checks
        - artifact_type key is present only when artifact_type arg is not None
        - warnings list is extended in place with projection warnings, then
          the same list reference is included in the result dict
        - pagination dict is passed through as-is (caller builds it)
        - Field projection uses config.summary_fields and config.all_fields
        - Never raises for valid inputs

    Args:
        data: Raw artifact dicts to project.
        fields: Requested field projection (None → summary defaults).
        config: ArtifactConfig (or any object with summary_fields/all_fields).
        pagination: Pre-built pagination metadata dict.
        warnings: Mutable warnings list — projection warnings are appended.
        artifact_type: Optional artifact type string to include in result.

    Returns:
        Result dict ready for format_search_response or direct return.
    """
    projected, fields_returned, fields_available, proj_warnings = apply_field_projection(
        data,
        fields,
        config.summary_fields,
        config.all_fields,
    )
    warnings.extend(proj_warnings)

    result: dict[str, Any] = {
        "data": projected,
        "fields_returned": fields_returned,
        "fields_available": fields_available,
        "pagination": pagination,
        "warnings": warnings,
    }
    if artifact_type is not None:
        result["artifact_type"] = artifact_type

    return result
