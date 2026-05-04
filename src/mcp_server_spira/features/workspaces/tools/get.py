"""workspace_get unified tool.

Replaces system_get_product_by_id and system_get_product_template
with a single config-driven tool using a ``workspace_type`` discriminator.
"""

from typing import Annotated, Any

from pydantic import WithJsonSchema

from mcp_server_spira.features.workspace_configs import WORKSPACE_CONFIG, WORKSPACE_TYPES
from mcp_server_spira.utils.common import get_spira_client
from mcp_server_spira.utils.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
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


async def _get_workspace_impl(
    spira_client,
    workspace_type: Any,
    workspace_id: int,
) -> str:
    """Core implementation for workspace_get.

    Takes *spira_client* as first arg so callers (and tests) can inject
    a mock without touching MCP registration.

    Returns a JSON string — success envelope or error response.
    """
    # 1. Validate workspace_type
    type_error = ParameterValidator.validate_type_param(
        workspace_type, WORKSPACE_TYPES, "workspace_type"
    )
    if type_error is not None:
        return format_error_response(**type_error)

    # 2. Validate workspace_id
    id_error = ParameterValidator.validate_positive_integer(workspace_id, "workspace_id")
    if id_error is not None:
        return format_error_response(**id_error)

    config = WORKSPACE_CONFIG[workspace_type]

    # 3. Fetch data
    try:
        if config.single_endpoint is not None:
            # Direct GET by ID (product, product_template)
            endpoint = config.single_endpoint.format(workspace_id=workspace_id)
            raw = await spira_client.make_spira_api_get_request(endpoint)

            if not raw:
                return format_error_response(
                    error=f"{workspace_type} with ID {workspace_id} not found.",
                    error_code=ErrorCodes.NOT_FOUND,
                    details={"workspace_type": workspace_type, "workspace_id": workspace_id},
                    suggestion="Verify the workspace_id is correct.",
                )

            return format_success_response(raw)

        else:
            # No single endpoint (program) — fetch all and filter client-side
            raw = await spira_client.make_spira_api_get_request(config.list_endpoint)
            items: list[dict] = raw if raw else []

            # Determine the ID field name from the workspace_type
            id_field = _id_field_for(workspace_type)
            match = next((item for item in items if item.get(id_field) == workspace_id), None)

            if match is None:
                return format_error_response(
                    error=f"{workspace_type} with ID {workspace_id} not found.",
                    error_code=ErrorCodes.NOT_FOUND,
                    details={"workspace_type": workspace_type, "workspace_id": workspace_id},
                    suggestion=(
                        f'Use workspace_search(workspace_type="{workspace_type}") '
                        f"to list available {workspace_type}s."
                    ),
                )

            return format_success_response(match)

    except Exception as e:
        return format_error_response(
            error=f"Failed to retrieve {workspace_type} data: {e}",
            error_code=ErrorCodes.API_ERROR,
            details={"workspace_type": workspace_type, "workspace_id": workspace_id},
            suggestion="Check your Spira connection and try again.",
        )


def _id_field_for(workspace_type: str) -> str:
    """Return the primary-key field name for a workspace type."""
    return {
        "product": "ProjectId",
        "program": "ProgramId",
        "product_template": "ProjectTemplateId",
    }[workspace_type]


def _build_docstring() -> str:
    """Build the dynamic docstring for workspace_get at registration time."""
    lines = ["Retrieves a single workspace entity by its numeric ID.\n"]
    lines.append(
        f"workspace_type (str, required): One of {', '.join(repr(t) for t in WORKSPACE_TYPES)}."
    )
    for wtype in WORKSPACE_TYPES:
        cfg = WORKSPACE_CONFIG[wtype]
        lines.append(f'  - "{wtype}": {cfg.description}')
    lines.append(
        "workspace_id (int, required): The numeric ID of the workspace entity (without prefix)."
    )
    return "\n".join(lines)


def register_tools(mcp) -> None:
    """Register the workspace_get unified tool."""
    docstring = _build_docstring()

    @mcp.tool(
        name="workspace_get",
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )
    async def workspace_get(
        workspace_type: WorkspaceType,
        workspace_id: int,
    ) -> str:
        spira_client = get_spira_client()
        return await _get_workspace_impl(spira_client, workspace_type, workspace_id)

    workspace_get.__doc__ = docstring
