"""program_search_artifacts unified tool.

Replaces 2 separate program tools (program_get_capabilities,
program_get_milestones) with 1 config-driven search tool.
"""

from typing import Annotated, Any

from pydantic import WithJsonSchema

from mcp_server_spira.features.artifact_configs import ARTIFACT_CONFIG
from mcp_server_spira.features.search.tools._shared import (
    apply_contains_filter,
    apply_field_projection,
)
from mcp_server_spira.utils.common import get_spira_client
from mcp_server_spira.utils.common.responses import (
    ErrorCodes,
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


async def _program_search_impl(
    spira_client,
    artifact_type: Any,
    program_id: int,
    fields: list[str] | None,
    status: str | None,
    priority: str | None,
    starting_row: int,
    number_of_rows: int,
) -> str:
    """Core implementation for program_search_artifacts.

    Takes *spira_client* as first arg so callers (and tests) can inject a
    mock without touching MCP registration.

    Returns a JSON string — either a search response envelope or an error.
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

    # 4. Build endpoint URL with config-driven query parameter names
    endpoint = config.search_endpoint.format(program_id=program_id)
    qp = config.search_query_params
    query_parts = []
    for role, api_name in qp.items():
        if role == "row_start":
            query_parts.append(f"{api_name}={starting_row}")
        elif role == "row_count":
            query_parts.append(f"{api_name}={number_of_rows}")
        elif role in ("sort_field", "sort_by"):
            default = config.default_sort_field or ""
            query_parts.append(f"{api_name}={default}")
        elif role == "sort_direction":
            query_parts.append(f"{api_name}={config.default_sort_direction}")
    url = f"{endpoint}?{'&'.join(query_parts)}"

    # 5. POST with empty body (no server-side filters)
    try:
        raw = await spira_client.make_spira_api_post_request(url, [])
    except Exception as e:
        return format_error_response(
            error=f"Failed to retrieve {artifact_type} data: {e}",
            error_code=ErrorCodes.API_ERROR,
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

    # 8. Project fields
    projected, fields_returned, fields_available, proj_warnings = apply_field_projection(
        data,
        fields,
        config.summary_fields,
        config.all_fields,
    )
    warnings.extend(proj_warnings)

    # 9. Format response envelope
    return format_search_response(
        data=projected,
        artifact_type=artifact_type,
        fields_returned=fields_returned,
        pagination={
            "starting_row": starting_row,
            "number_of_rows": number_of_rows,
            "total_returned": len(projected),
        },
        fields_available=fields_available,
        warnings=warnings,
    )


def _build_search_docstring() -> str:
    """Build the dynamic docstring for program_search_artifacts.

    Injects valid ProgramArtifactType values from ARTIFACT_CONFIG at
    registration time so the docstring always reflects the current config.
    """
    type_names = ", ".join(PROGRAM_ARTIFACT_TYPES)
    return (
        "Searches for artifacts in a Spira program.\n"
        "\n"
        f"Valid artifact types: {type_names}\n"
        "\n"
        "Args:\n"
        f"  artifact_type: One of [{type_names}].\n"
        "  program_id: Program ID to search (required, no default).\n"
        "  fields: Fields to return per object. "
        "Defaults to summary fields. "
        "Use get_artifact_schema to "
        "discover valid field names.\n"
        "  status: Substring filter on status "
        "(case-insensitive).\n"
        "  priority: Substring filter on priority "
        "(case-insensitive).\n"
        "  starting_row: Pagination start "
        "(1-based, default 1).\n"
        "  number_of_rows: Page size (default 100).\n"
        "\n"
        "Call get_artifact_schema for full "
        "field discovery per artifact type."
    )


def register_tools(mcp) -> None:
    """Register program_search_artifacts."""
    docstring = _build_search_docstring()

    @mcp.tool(
        name="program_search_artifacts",
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
    ) -> str:
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
        )

    program_search_artifacts.__doc__ = docstring
