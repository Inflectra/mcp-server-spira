"""workspace_search unified tool.

Replaces system_get_products, system_get_program_products,
system_get_programs, and system_get_product_templates with a single
config-driven tool using a ``workspace_type`` discriminator.
"""

import json
from typing import Annotated, Any

from pydantic import WithJsonSchema

from mcp_server_spira.features.workspace_configs import WORKSPACE_CONFIG, WORKSPACE_TYPES
from mcp_server_spira.utils.common import get_spira_client
from mcp_server_spira.utils.common.field_projection import apply_field_projection
from mcp_server_spira.utils.common.responses import (
    ErrorCodes,
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
    except Exception as e:
        return format_error_response(
            error=f"Failed to retrieve {workspace_type} data: {e}",
            error_code=ErrorCodes.API_ERROR,
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
    lines = ["Lists workspaces in Spira with optional field projection.\n"]
    lines.append(
        f"workspace_type (str, required): One of {', '.join(repr(t) for t in WORKSPACE_TYPES)}."
    )
    for wtype in WORKSPACE_TYPES:
        cfg = WORKSPACE_CONFIG[wtype]
        lines.append(f'  - "{wtype}": {cfg.description}')
    lines.append(
        "program_id (int, optional): "
        "Filter products by program membership (ProjectGroupId). "
        "Only applies to workspace_type='product'; ignored for other types."
    )
    lines.append("fields (list[str], optional): Field projection. None returns summary fields.")
    return "\n".join(lines)


def register_tools(mcp) -> None:
    """Register the workspace_search unified tool."""
    docstring = _build_docstring()

    @mcp.tool(
        name="workspace_search",
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
        spira_client = get_spira_client()
        return await _search_workspaces_impl(spira_client, workspace_type, program_id, fields)

    workspace_search.__doc__ = docstring
