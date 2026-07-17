"""program_search_artifacts unified tool.

Replaces 2 separate program tools (program_get_capabilities,
program_get_milestones) with 1 config-driven search tool.
"""

from typing import Annotated, Any

from pydantic import WithJsonSchema

from mcp_server_spira.features.artifact_configs import ARTIFACT_CONFIG
from mcp_server_spira.features.search.tools._shared import (
    apply_contains_filter,
    finalize_search_results,
)
from mcp_server_spira.utils.common import SpiraApiError, get_spira_client
from mcp_server_spira.utils.common.responses import (
    format_error_response,
    format_search_response,
)
from mcp_server_spira.utils.common.validation import ParameterValidator

# Derived from ArtifactConfig — program-scoped types only.
PROGRAM_ARTIFACT_TYPES: tuple[str, ...] = tuple(
    name for name, cfg in ARTIFACT_CONFIG.items() if cfg.workspace_type == "program"
)

# Type hint for the tool signature — advertises valid values in the JSON
# schema but accepts any string at Pydantic validation time.  Actual
# validation happens in _impl via ParameterValidator.
ProgramArtifactType = Annotated[
    str,
    WithJsonSchema(
        {
            "type": "string",
            "enum": list(PROGRAM_ARTIFACT_TYPES),
        }
    ),
]


def _has_cp_filters(
    filters: list,
    all_fields: list[str],
) -> bool:
    """Check if any filter entries are likely custom property filters.

    A filter entry is considered a potential CP filter if its field is NOT
    in all_fields. Program scope has no product context to resolve CP
    definitions, so we use this heuristic: any field not in the standard
    field list is likely a custom property name.

    Spec:
        - ALWAYS returns bool — never raises
        - Returns True if at least one filter entry has a field not in
          all_fields
        - Returns False if all filter fields are standard or on error
        - Does not require product context (program scope has none)
        - Non-dict entries in filters are skipped gracefully
    """
    all_fields_set = set(all_fields)
    for entry in filters:
        if not isinstance(entry, dict):
            continue
        field = entry.get("field")
        if field is None:
            continue
        if field not in all_fields_set:
            return True
    return False


async def _program_search_impl(
    spira_client,
    artifact_type: Any,
    program_id: int,
    fields: list[str] | None,
    status: str | None,
    priority: str | None,
    starting_row: int,
    number_of_rows: int,
    filters: list[dict] | None = None,
) -> str:
    """Core implementation for program_search_artifacts.

    Takes *spira_client* as first arg so callers (and tests) can inject a
    mock without touching MCP registration.

    Returns a JSON string — either a search response envelope or an error.

    Spec:
        Return type:
            - ALWAYS returns a JSON string (never raises, never returns None)
            - On success: search envelope via format_search_response with keys:
              data, artifact_type, fields_returned, fields_available, pagination,
              warnings
            - On validation failure: error envelope with error_code

        Validation order (short-circuits on first failure, no API call made):
            1. artifact_type must be in PROGRAM_ARTIFACT_TYPES
            2. program_id must be a positive integer (>= 1)
            3. starting_row must be a positive integer (>= 1)
            4. number_of_rows must be a positive integer (>= 1)

        Pipeline (post-validation):
            - Endpoint URL built from config.search_endpoint with {program_id}
              substitution and config.search_query_params for pagination + sort
            - POST body is always an empty list [] (no server-side filters)
            - API returning None treated as empty list (not an error)
            - Client-side status filter via apply_contains_filter — skipped
              with warning when config.status_field is None
            - Client-side priority filter via apply_contains_filter — skipped
              with warning when config.priority_field is None
            - Field projection via apply_field_projection after filtering
            - If filters contains CP filter entries, a warning is produced
              and those entries are skipped (program scope does not support
              custom property filtering)

        Response envelope invariants:
            - warnings is always a list (never None), even when empty
            - pagination.total_returned always equals len(data)
            - fields_available is the delta of all_fields minus fields_returned
            - artifact_type in response matches the input artifact_type

        Error handling:
            - API exceptions caught and converted to error envelope with
              error_code=API_ERROR — never raises to the MCP layer
            - Validation errors return error envelope with appropriate
              error_code — no API call made

        Consistency with siblings:
            - Follows same pipeline pattern as _product_search_impl (single-
              product path) and _mywork_search_impl (single-type path)
            - No multi-program fan-out (unlike product's multi-product path)
            - No env-default fallback for program_id (unlike product_ids)
    """
    # 1. Validate artifact_type
    type_error = ParameterValidator.validate_type_param(
        artifact_type, PROGRAM_ARTIFACT_TYPES, "artifact_type"
    )
    if type_error is not None:
        return format_error_response(**type_error)

    # 2. Validate program_id (mandatory, positive integer, no env default)
    pid_error = ParameterValidator.validate_positive_integer(program_id, "program_id")
    if pid_error is not None:
        return format_error_response(**pid_error)

    # 3. Validate pagination params
    sr_error = ParameterValidator.validate_positive_integer(starting_row, "starting_row")
    if sr_error is not None:
        return format_error_response(**sr_error)

    nr_error = ParameterValidator.validate_positive_integer(number_of_rows, "number_of_rows")
    if nr_error is not None:
        return format_error_response(**nr_error)

    config = ARTIFACT_CONFIG[artifact_type]
    warnings: list[str] = []

    # 3b. Handle custom_properties in fields — not supported for program scope
    if fields and "custom_properties" in fields:
        warnings.append(
            "custom_properties is not supported for program-scoped artifact types. "
            "Ignoring custom_properties field."
        )
        fields = [f for f in fields if f != "custom_properties"]
        if not fields:
            fields = None

    # 3c. Detect and warn about custom property filters
    if filters:
        cp_filter_detected = _has_cp_filters(filters, config.all_fields)
        if cp_filter_detected:
            warnings.append(
                "Custom property filters not supported for program-scoped searches. Filter skipped."
            )
        # Standard Tier 2 filters are also not supported (POST body is always empty)
        all_fields_set = set(config.all_fields)
        standard_fields_in_filters: list[str] = [
            field
            for e in filters
            if isinstance(e, dict)
            for field in [e.get("field")]
            if isinstance(field, str) and field in all_fields_set
        ]
        if standard_fields_in_filters:
            warnings.append(
                "Tier 2 filters are not supported for program-scoped searches "
                "(server does not accept filter body). "
                f"Ignored filter field(s): {', '.join(standard_fields_in_filters)}."
            )

    # 4. Build endpoint URL with config-driven query parameter names
    url = config.build_search_url(
        starting_row=starting_row,
        number_of_rows=number_of_rows,
        program_id=program_id,
    )

    # 5. POST with empty body (no server-side filters)
    try:
        raw = await spira_client.make_spira_api_post_request(url, [])
    except SpiraApiError as e:
        return format_error_response(
            error=f"Failed to retrieve {artifact_type} data: {e}",
            error_code=e.error_code,
            suggestion="Check your Spira connection and try again.",
        )

    data: list[dict] = raw if raw else []

    # 6. Filter status
    data, status_warnings = apply_contains_filter(
        data,
        config.status_field,
        status,
        config.all_fields,
        "status",
    )
    warnings.extend(status_warnings)

    # 7. Filter priority
    data, priority_warnings = apply_contains_filter(
        data,
        config.priority_field,
        priority,
        config.all_fields,
        "priority",
    )
    warnings.extend(priority_warnings)

    # 8. Project fields and assemble result
    result = finalize_search_results(
        data,
        fields,
        config,
        pagination={
            "starting_row": starting_row,
            "number_of_rows": number_of_rows,
            "total_returned": len(data),
        },
        warnings=warnings,
    )

    # 9. Format response envelope
    return format_search_response(
        data=result["data"],
        artifact_type=artifact_type,
        fields_returned=result["fields_returned"],
        pagination=result["pagination"],
        fields_available=result["fields_available"],
        warnings=result["warnings"],
    )


def _build_search_docstring() -> str:
    """Build the dynamic docstring for program_search_artifacts."""
    type_names = ", ".join(PROGRAM_ARTIFACT_TYPES)
    return (
        "Search artifacts in a Spira program.\n"
        "\n"
        f"artifact_type: [{type_names}]\n"
        "program_id: required, no default"
    )


def register_tools(mcp) -> None:
    """Register program_search_artifacts."""
    docstring = _build_search_docstring()

    @mcp.tool(
        name="program_search_artifacts",
        description=docstring,
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )
    async def program_search_artifacts(
        artifact_type: ProgramArtifactType,
        program_id: int,
        fields: list[str] | None = None,
        status: str | None = None,
        priority: str | None = None,
        starting_row: int = 1,
        number_of_rows: int = 100,
        filters: list[dict] | None = None,
    ) -> str:
        """Search artifacts in a Spira program."""
        spira_client = get_spira_client()
        return await _program_search_impl(
            spira_client,
            artifact_type,
            program_id,
            fields,
            status,
            priority,
            starting_row,
            number_of_rows,
            filters=filters,
        )
