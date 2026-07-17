"""workspace_search unified tool.

Replaces system_get_products, system_get_program_products,
system_get_programs, and system_get_product_templates with a single
config-driven tool using a ``workspace_type`` discriminator.
"""

import json
from typing import Annotated, Any

from pydantic import WithJsonSchema

from mcp_server_spira.features.workspace_configs import WORKSPACE_CONFIG, WORKSPACE_TYPES
from mcp_server_spira.utils.common import SpiraApiError, get_spira_client
from mcp_server_spira.utils.common.field_projection import apply_field_projection
from mcp_server_spira.utils.common.responses import (
    format_error_response,
)
from mcp_server_spira.utils.common.validation import ParameterValidator

WorkspaceType = Annotated[
    str,
    WithJsonSchema(
        {
            "type": "string",
            "enum": list(WORKSPACE_TYPES),
        }
    ),
]


async def _search_workspaces_impl(
    spira_client,
    workspace_type: Any,
    program_id: int | None,
    fields: list[str] | None,
) -> str:
    """Core implementation for workspace_search.

    Takes *spira_client* as first arg so callers (and tests) can inject
    a mock without touching MCP registration.

    Returns a JSON string — workspace search response envelope.

    Spec:
        - ALWAYS returns a JSON string (never raises to the MCP layer)
        - Response envelope always has: data (list), workspace_type (str),
          fields_returned (list), fields_available (list), warnings (list)
        - warnings is always a list, never None — even on success with no
          issues
        - No pagination key in the response — workspace lists are not
          paginated (all items returned in one call)
        - Validation failures (invalid workspace_type, invalid program_id)
          short-circuit before any API call
        - fields=None or fields=[] → summary_fields from WorkspaceConfig;
          fields_available shows the delta of remaining fields
        - Unknown field names in fields → silently dropped with warning;
          if ALL fields unknown, falls back to summary_fields with warning
        - program_id is only applicable to workspace_type="product" — for
          other types it is ignored with a warning (search still runs)
        - API returning None is treated as empty list (not error)
        - API exceptions → error response with API_ERROR code (not crash)
    """
    # 1. Validate workspace_type
    type_error = ParameterValidator.validate_type_param(
        workspace_type, WORKSPACE_TYPES, "workspace_type"
    )
    if type_error is not None:
        return format_error_response(**type_error)

    config = WORKSPACE_CONFIG[workspace_type]
    warnings: list[str] = []

    # 2. Handle program_id
    if program_id is not None:
        if workspace_type != "product":
            warnings.append("program_id is only applicable to workspace_type='product'. Ignoring.")
            program_id = None  # ignore for non-product types
        else:
            pid_error = ParameterValidator.validate_positive_integer(program_id, "program_id")
            if pid_error is not None:
                return format_error_response(**pid_error)

    # 3. Fetch data from list endpoint
    try:
        raw = await spira_client.make_spira_api_get_request(config.list_endpoint)
    except SpiraApiError as e:
        return format_error_response(
            error=f"Failed to retrieve {workspace_type} data: {e}",
            error_code=e.error_code,
            details={"workspace_type": workspace_type},
            suggestion="Check your Spira connection and try again.",
        )

    data: list[dict] = raw if raw else []

    # 4. Client-side program_id filter for products
    if program_id is not None:
        data = [item for item in data if item.get("ProjectGroupId") == program_id]
        if not data:
            warnings.append(f"No products matched program_id={program_id}.")

    # 5. Field projection
    schema_hint = f"Valid fields for {workspace_type}: {', '.join(config.all_fields)}"
    projected, fields_returned, fields_available, proj_warnings = apply_field_projection(
        data,
        fields,
        config.summary_fields,
        config.all_fields,
        schema_hint=schema_hint,
    )
    warnings.extend(proj_warnings)

    # 6. Build response envelope
    response: dict[str, Any] = {
        "data": projected,
        "workspace_type": workspace_type,
        "fields_returned": fields_returned,
        "fields_available": fields_available,
        "warnings": warnings,
    }

    return json.dumps(response, indent=2, default=str)


def _build_docstring() -> str:
    """Build the dynamic docstring for workspace_search at registration time."""
    type_names = ", ".join(repr(t) for t in WORKSPACE_TYPES)
    return f"Lists workspaces in Spira.\n\nworkspace_type: {type_names}"


def register_tools(mcp) -> None:
    """Register the workspace_search unified tool."""
    docstring = _build_docstring()

    @mcp.tool(
        name="workspace_search",
        description=docstring,
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )
    async def workspace_search(
        workspace_type: WorkspaceType,
        program_id: int | None = None,
        fields: list[str] | None = None,
    ) -> str:
        """Lists workspaces in Spira."""
        spira_client = get_spira_client()
        return await _search_workspaces_impl(spira_client, workspace_type, program_id, fields)
