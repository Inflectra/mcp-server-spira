"""Shared utility functions for unified search tools.

Contains field derivation, client-side filtering, and field projection
logic used by both ``mywork`` and ``product`` search tools.

Extracted from ``mywork.py`` to keep the codebase DRY.
"""


def derive_display_name_field(id_field: str) -> str:
    """Derive the human-readable display name field from a normalised ID field.

    Replaces trailing ``"Id"`` with ``"Name"``.  If the input does not end in
    ``"Id"``, appends ``"Name"`` instead.

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


# Re-export from canonical location — kept here for backward compatibility.
from mcp_server_spira.utils.common.field_projection import apply_field_projection  # noqa: E402

__all__ = [
    "apply_contains_filter",
    "apply_field_projection",
    "derive_display_name_field",
]
