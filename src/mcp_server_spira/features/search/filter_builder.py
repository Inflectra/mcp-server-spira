"""RemoteFilter builder — constructs Spira POST filter arrays.

Pure-function module with no async, no API calls, no side effects.
Converts resolved Tier 1 parameters and raw Tier 2 dicts into the
``RemoteFilter`` wire format expected by Spira search endpoints.

Tier 1 filters are resolved (field_name, int | list[int]) tuples
produced by the Name_Resolver.  Tier 2 filters are raw LLM dicts
using the field/operator/value format.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

# ---------------------------------------------------------------------------
# Operator alias sets
# ---------------------------------------------------------------------------

_EQUALITY_OPS: set[str] = {"eq", "=", "==", "is", "equals"}
_STRING_MATCH_OPS: set[str] = {"contains", "like", "startswith", "starts_with", "icontains"}
_IN_OPS: set[str] = {"in"}
_NULL_OPS: set[str] = {"isnull", "is_null", "null"}
_NOT_NULL_OPS: set[str] = {"notnull", "is_not_null", "not_null"}
_DATE_GTE_OPS: set[str] = {">=", "gte"}
_DATE_GT_OPS: set[str] = {">", "gt", "after"}
_DATE_LTE_OPS: set[str] = {"<=", "lte"}
_DATE_LT_OPS: set[str] = {"<", "lt", "before"}
_DATE_BETWEEN_OPS: set[str] = {"between"}
_UNSUPPORTED_OPS: set[str] = {"ne", "!=", "neq", "not_equal", "not_in"}

_ALL_DATE_OPS: set[str] = (
    _DATE_GTE_OPS | _DATE_GT_OPS | _DATE_LTE_OPS | _DATE_LT_OPS | _DATE_BETWEEN_OPS
)


def build_remote_filters(
    tier1_filters: list[tuple[str, int | list[int]]] | None,
    tier2_filters: list[dict[str, Any]] | None,
    all_fields: list[str],
) -> tuple[list[dict], list[str]]:
    """Build a RemoteFilter JSON array from resolved Tier 1 and raw Tier 2 entries.

    Spec:
        - Output filters list never contains two entries with the same
          PropertyName when both have DateRangeValue (they must be merged)
        - Output warnings is always a list, never None
        - Every dict in output filters has a "PropertyName" key
        - Invalid tier2 entries (missing field, unknown field) produce a
          warning and are skipped, not an exception
        - Unrecognized operators produce a warning listing supported operators
        - Multiple date filters on the same field with conflicting ranges
          (start > end after merge) produce a warning and skip all date
          filters for that field

    Args:
        tier1_filters: List of (PropertyName, value) tuples where value is
            an int (→ IntValue) or list[int] (→ MultiValue).
            None or empty → no Tier 1 filters.
        tier2_filters: Raw Tier 2 dicts from the LLM using field/operator/value
            format, e.g. [{"field": "Name", "operator": "contains", "value": "login"}].
            None or empty → no Tier 2 filters.
        all_fields: The artifact config's all_fields for Tier 2 validation.

    Returns:
        (remote_filters, warnings) — the JSON-serialisable list and any
        warning strings collected during construction.
    """
    filters: list[dict] = []
    warnings: list[str] = []

    # --- Tier 1: resolved (field_name, value) tuples ---
    for field_name, value in tier1_filters or []:
        filters.append(_build_tier1_filter(field_name, value))

    # --- Tier 2: field/operator/value dicts ---
    for entry in tier2_filters or []:
        rf, warning = _build_tier2_filter_fov(entry, all_fields)
        if warning:
            warnings.append(warning)
        if rf is not None:
            filters.append(rf)

    # --- Merge multiple DateRangeValue filters on the same field ---
    filters, merge_warnings = merge_date_range_filters(filters)
    warnings.extend(merge_warnings)

    return filters, warnings


def _build_tier1_filter(field_name: str, value: int | list[int]) -> dict:
    """Convert a single resolved Tier 1 entry to a RemoteFilter dict.

    Spec:
        - int value → dict with "PropertyName" and "IntValue" keys only
        - list[int] value → dict with "PropertyName" and "MultiValue" keys only
        - Output dict ALWAYS has a "PropertyName" key equal to field_name
        - Never raises — inputs are pre-validated by callers (NameResolver)
    """
    if isinstance(value, list):
        return {
            "PropertyName": field_name,
            "MultiValue": {"Values": value, "IsNone": False},
        }
    return {"PropertyName": field_name, "IntValue": value}


def merge_date_range_filters(
    filters: list[dict],
) -> tuple[list[dict], list[str]]:
    """Merge multiple DateRangeValue filters on the same field into one.

    The Spira API expects a single DateRangeValue per field. When the LLM
    provides separate "after" and "before" filters on the same date field,
    this function merges them into a single DateRangeValue with both
    StartDate and EndDate set.

    Spec:
        - Output never contains two dicts with the same PropertyName that
          both have a "DateRangeValue" key — they are always merged
        - Non-date filters (no "DateRangeValue" key) pass through unchanged
        - Single date filter on a field passes through unchanged (no merge)
        - Conflicting range (merged start > end) → all date filters for that
          field are dropped and a warning is emitted
        - warnings is always a list (never None)
        - Output filter order: non-date filters first, then merged date filters

    Args:
        filters: List of RemoteFilter dicts, some of which may have
            DateRangeValue entries for the same PropertyName.

    Returns:
        (merged_filters, warnings) — filters with date ranges merged,
        and any warnings about conflicts or invalid ranges.
    """
    warnings: list[str] = []
    non_date_filters: list[dict] = []
    date_filters_by_field: dict[str, list[dict]] = {}

    # Separate date filters from non-date filters
    for f in filters:
        if "DateRangeValue" in f:
            field = f["PropertyName"]
            date_filters_by_field.setdefault(field, []).append(f)
        else:
            non_date_filters.append(f)

    # Merge date filters per field
    merged_date_filters: list[dict] = []
    for field, date_list in date_filters_by_field.items():
        if len(date_list) == 1:
            # Single date filter — no merge needed
            merged_date_filters.append(date_list[0])
            continue

        # Multiple date filters on same field — merge them
        merged, merge_warning = _merge_single_field_date_ranges(field, date_list)
        if merge_warning:
            warnings.append(merge_warning)
        if merged is not None:
            merged_date_filters.append(merged)

    return non_date_filters + merged_date_filters, warnings


def _merge_single_field_date_ranges(
    field: str,
    date_filters: list[dict],
) -> tuple[dict | None, str | None]:
    """Merge multiple DateRangeValue filters for a single field.

    Collects all StartDate and EndDate values, picks the most restrictive
    (latest StartDate, earliest EndDate), and validates the resulting range.

    Spec:
        - Picks the LATEST StartDate and EARLIEST EndDate (most restrictive)
        - If merged start > end → returns (None, warning) — caller drops
          all date filters for this field
        - If merged range is valid → returns a single dict with merged
          DateRangeValue containing both StartDate and EndDate
        - ConsiderTimes is always False in the output
        - Never raises

    Args:
        field: The PropertyName being filtered.
        date_filters: List of RemoteFilter dicts with DateRangeValue.

    Returns:
        (merged_filter_or_None, warning_or_None)
    """
    start_dates: list[str] = []
    end_dates: list[str] = []

    for f in date_filters:
        drv = f.get("DateRangeValue", {})
        if drv.get("StartDate"):
            start_dates.append(drv["StartDate"])
        if drv.get("EndDate"):
            end_dates.append(drv["EndDate"])

    # Pick most restrictive bounds: latest start, earliest end
    final_start: str | None = max(start_dates) if start_dates else None
    final_end: str | None = min(end_dates) if end_dates else None

    # Validate: start must not be after end
    if final_start and final_end and final_start > final_end:
        return None, (
            f"Tier 2 date filters for field '{field}' produce an invalid "
            f"range: StartDate ({final_start}) is after EndDate ({final_end}). "
            f"Skipping all date filters for this field."
        )

    return {
        "PropertyName": field,
        "DateRangeValue": {
            "StartDate": final_start,
            "EndDate": final_end,
            "ConsiderTimes": False,
        },
    }, None


# ---------------------------------------------------------------------------
# Tier 2 — field/operator/value dispatch
# ---------------------------------------------------------------------------


def _resolve_operator(operator: str | None, value: Any) -> str:
    """Normalise an operator alias or infer from value type when absent.

    Returns the canonical lower-cased operator string.  When *operator* is
    ``None``, the type of *value* determines the default:

    * ``bool``  → ``"eq"``  (checked before ``int``)
    * ``int``   → ``"eq"``
    * ``str``   → ``"contains"``
    * ``list``  → ``"in"``
    * ``dict``  → ``"date_range_infer"``  (legacy dict-as-value inference)
    * other     → ``"_unknown"``

    Spec:
        - ALWAYS returns a non-empty string — never None, never raises
        - When operator is provided, returns it stripped and lowercased
        - When operator is None, bool is checked BEFORE int (bool is
          subclass of int in Python) — this prevents True/False being
          treated as 1/0
        - Inference is deterministic: same (operator, value) always
          produces the same result
    """
    if operator is not None:
        return str(operator).strip().lower()

    # Infer from value type — bool before int (bool is subclass of int)
    if isinstance(value, bool):
        return "eq"
    if isinstance(value, int):
        return "eq"
    if isinstance(value, str):
        return "contains"
    if isinstance(value, list):
        return "in"
    if isinstance(value, dict):
        return "date_range_infer"
    return "_unknown"


def _build_tier2_filter_fov(
    entry: Any,
    all_fields: list[str],
) -> tuple[dict | None, str | None]:
    """Build a RemoteFilter from a single field/operator/value dict.

    Expected shape::

        {"field": "FieldName", "operator": "op", "value": val}

    The ``operator`` key is optional (inferred from value type).
    The ``value`` key is optional for null/not-null operators.

    Spec:
        - Never raises — all invalid inputs produce (None, warning_string)
        - Non-dict entry → (None, warning)
        - Missing "field" key → (None, warning)
        - field not in all_fields → (None, warning) — search still runs
        - Unsupported operator (ne, !=, etc.) → (None, warning listing
          supported operators)
        - Id/Ids field with non-numeric string → (None, warning suggesting
          integer ID or Tier 1 named parameter)
        - float value → (None, warning) regardless of operator
        - None value with non-null operator → (None, warning)
        - Valid entry → (RemoteFilter dict with "PropertyName", warning=None)
        - Output dict always has "PropertyName" key when non-None

    Returns:
        (remote_filter_dict_or_None, warning_or_None)
    """
    # --- Shape validation ---
    if not isinstance(entry, dict):
        return None, (
            f"Tier 2 filter entry is not a dict (got {type(entry).__name__}). "
            f"Expected {{'field': ..., 'operator': ..., 'value': ...}}."
        )

    field_name = entry.get("field")
    if field_name is None:
        return None, (
            f"Tier 2 filter entry is missing the 'field' key: {entry}. "
            f"Expected {{'field': ..., 'operator': ..., 'value': ...}}."
        )

    # --- Field validation ---
    if field_name not in all_fields:
        return None, (
            f"Tier 2 filter field '{field_name}' is not a valid field. "
            f"Use get_artifact_schema to discover valid field names."
        )

    operator_raw = entry.get("operator")
    value = entry.get("value")
    op = _resolve_operator(operator_raw, value)

    # --- Unsupported operators ---
    if op in _UNSUPPORTED_OPS:
        return None, (
            f"Operator '{op}' is not supported by the Spira RemoteFilter API "
            f"for field '{field_name}'. Skipped filter: {entry}. "
            f"Supported operators: eq, contains, in, isnull, notnull, "
            f">=, >, <=, <, between."
        )

    # --- Null / not-null (no value needed) ---
    if op in _NULL_OPS:
        return {
            "PropertyName": field_name,
            "MultiValue": {"Values": [], "IsNone": True},
        }, None

    if op in _NOT_NULL_OPS:
        return {
            "PropertyName": field_name,
            "MultiValue": {"Values": [], "IsNone": False},
        }, None

    # --- Value-type validation (early exit before operator dispatch) ---
    # float values are never supported by any operator
    if isinstance(value, float):
        return None, (
            f"Tier 2 filter field '{field_name}' has unsupported value type "
            f"'float'. Supported types: int, str, bool, list."
        )

    # None value with a non-null operator → skip + warning
    if value is None and op not in (_NULL_OPS | _NOT_NULL_OPS):
        return None, (
            f"Tier 2 filter field '{field_name}' has value None with "
            f"operator '{operator_raw}'. Use 'isnull' or 'notnull' operators "
            f"for null checks."
        )

    # Id/Ids field with string value not parseable as integer → skip + warning
    if (field_name.endswith("Id") or field_name.endswith("Ids")) and isinstance(value, str):
        try:
            int(value)
        except (ValueError, TypeError):
            return None, (
                f"Tier 2 filter field '{field_name}' is a lookup field and "
                f"requires an integer value, not a string ('{value}'). "
                f"Use an integer ID or use a Tier 1 named parameter for "
                f"name-based resolution."
            )

    # --- Date operators → delegate to date builder ---
    if op in _ALL_DATE_OPS:
        return build_date_range_filter_fov(field_name, op, value)

    # --- Equality operators ---
    if op in _EQUALITY_OPS:
        # bool → StringValue "Y"/"N" (checked before int)
        if isinstance(value, bool):
            return {
                "PropertyName": field_name,
                "StringValue": "Y" if value else "N",
            }, None
        if isinstance(value, int):
            return {"PropertyName": field_name, "IntValue": value}, None
        if isinstance(value, str):
            return {"PropertyName": field_name, "StringValue": value}, None
        # Unsupported value type for equality
        return None, (
            f"Tier 2 filter field '{field_name}' with operator '{op}' has "
            f"unsupported value type '{type(value).__name__}'. "
            f"Supported value types for equality: int, str, bool."
        )

    # --- String-match operators ---
    if op in _STRING_MATCH_OPS:
        if isinstance(value, str):
            return {"PropertyName": field_name, "StringValue": value}, None
        return None, (
            f"Tier 2 filter field '{field_name}' with operator '{op}' "
            f"requires a string value, got '{type(value).__name__}'."
        )

    # --- In operator ---
    if op in _IN_OPS:
        if isinstance(value, list):
            return {
                "PropertyName": field_name,
                "MultiValue": {"Values": value, "IsNone": False},
            }, None
        return None, (
            f"Tier 2 filter field '{field_name}' with operator 'in' "
            f"requires a list value, got '{type(value).__name__}'."
        )

    # --- Inferred date range from dict value (legacy inference path) ---
    if op == "date_range_infer":
        # Dict value with no explicit operator — not supported in new format.
        # The new format requires an explicit date operator.
        return None, (
            f"Tier 2 filter field '{field_name}' has a dict value but no "
            f"explicit date operator. Use an explicit operator: "
            f">=, >, <=, <, between."
        )

    # --- Unknown / unrecognised operator ---
    return None, (
        f"Unrecognised operator '{op}' for field '{field_name}'. "
        f"Skipped filter: {entry}. "
        f"Supported operators: eq, =, ==, is, equals, contains, like, "
        f"startswith, starts_with, icontains, in, isnull, is_null, null, "
        f"notnull, is_not_null, not_null, >=, gte, >, gt, after, "
        f"<=, lte, <, lt, before, between."
    )


# ---------------------------------------------------------------------------
# Date range builder
# ---------------------------------------------------------------------------


def build_date_range_filter_fov(
    field_name: str,
    operator: str,
    value: Any,
) -> tuple[dict | None, str | None]:
    """Build a DateRangeValue RemoteFilter from a date operator and value.

    Handles all date range operators with day-shift logic:
    - >=, gte → StartDate, no shift
    - >, gt, after → StartDate + 1 day
    - <=, lte → EndDate, no shift
    - <, lt, before → EndDate − 1 day
    - between → StartDate + EndDate, no shift

    Spec:
        - Never raises — unparseable dates produce (None, warning)
        - "between" requires a 2-element list; anything else → (None, warning)
        - "between" with start > end → (None, warning) — nonsensical range
        - All output dates are UTC wire format: "YYYY-MM-DDTHH:MM:SS.000Z"
        - ConsiderTimes is always False in the output DateRangeValue
        - Day-shift operators (>, gt, after, <, lt, before) shift by exactly
          1 calendar day — this is the design contract for "exclusive" bounds
        - Non-shift operators (>=, gte, <=, lte) use the parsed date as-is
    """
    # --- between operator: value must be a 2-element list ---
    if operator in _DATE_BETWEEN_OPS:
        if not isinstance(value, list) or len(value) != 2:
            return None, (
                f"Tier 2 filter field '{field_name}' with operator "
                f"'between' requires a 2-element list value, got: "
                f"{value!r}."
            )
        start_dt = _parse_date(value[0])
        if start_dt is None:
            return None, (
                f"Tier 2 filter field '{field_name}': cannot parse start date '{value[0]}'."
            )
        end_dt = _parse_date(value[1])
        if end_dt is None:
            return None, (
                f"Tier 2 filter field '{field_name}': cannot parse end date '{value[1]}'."
            )
        # Validate start <= end
        if start_dt > end_dt:
            return None, (
                f"Tier 2 filter field '{field_name}' with operator "
                f"'between': start date '{value[0]}' is later than "
                f"end date '{value[1]}'. Skipping nonsensical range."
            )
        return {
            "PropertyName": field_name,
            "DateRangeValue": {
                "StartDate": _format_wire(start_dt),
                "EndDate": _format_wire(end_dt),
                "ConsiderTimes": False,
            },
        }, None

    # --- Single-value date operators ---
    dt = _parse_date(value)
    if dt is None:
        return None, (f"Tier 2 filter field '{field_name}': cannot parse date value '{value}'.")

    if operator in _DATE_GTE_OPS:
        return {
            "PropertyName": field_name,
            "DateRangeValue": {
                "StartDate": _format_wire(dt),
                "EndDate": None,
                "ConsiderTimes": False,
            },
        }, None

    if operator in _DATE_GT_OPS:
        shifted = dt + timedelta(days=1)
        return {
            "PropertyName": field_name,
            "DateRangeValue": {
                "StartDate": _format_wire(shifted),
                "EndDate": None,
                "ConsiderTimes": False,
            },
        }, None

    if operator in _DATE_LTE_OPS:
        return {
            "PropertyName": field_name,
            "DateRangeValue": {
                "StartDate": None,
                "EndDate": _format_wire(dt),
                "ConsiderTimes": False,
            },
        }, None

    if operator in _DATE_LT_OPS:
        shifted = dt - timedelta(days=1)
        return {
            "PropertyName": field_name,
            "DateRangeValue": {
                "StartDate": None,
                "EndDate": _format_wire(shifted),
                "ConsiderTimes": False,
            },
        }, None

    # Should not reach here given _ALL_DATE_OPS check upstream
    return None, (f"Tier 2 filter field '{field_name}': unrecognised date operator '{operator}'.")


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------


def _parse_date(value: Any) -> datetime | None:
    """Parse an ISO 8601 date string to a UTC datetime.

    Uses ``datetime.fromisoformat()`` (Python 3.12+) which handles:
    - Bare dates: ``2024-01-01``
    - Z suffix: ``2024-01-01T14:30:00Z``
    - Timezone offsets: ``2024-01-01T14:30:00+05:30``
    - No timezone: ``2024-01-01T14:30:00`` (treated as UTC)

    Spec:
        - Non-string input → None (never raises TypeError)
        - Unparseable string → None (never raises ValueError)
        - Naive datetime (no tzinfo) treated as UTC
        - Timezone-aware datetime converted to UTC
        - Return value is always UTC-aware or None
    """
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None
    # If no timezone info, treat as UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    # Convert to UTC
    return dt.astimezone(UTC)


def _format_wire(dt: datetime) -> str:
    """Format a datetime to Spira's UTC wire format.

    Output: ``YYYY-MM-DDTHH:MM:SS.000Z``

    Spec:
        - Output always matches pattern r"\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.000Z"
        - Milliseconds are always ".000" (Spira ignores sub-second precision)
        - Caller is responsible for ensuring dt is UTC — this function does
          not re-convert
    """
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + ".000Z"
