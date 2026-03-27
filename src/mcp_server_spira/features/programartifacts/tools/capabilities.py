"""
Provides operations for working with the Spira program capabilities

This module provides MCP tools for retrieving program capabilities
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


async def _get_capabilities_impl(spira_client, program_id: int) -> str:
    """
    Implementation of retrieving the list of capabilities in the specified program

    Args:
        spira_client: The Inflectra Spira API client instance
        program_id: The numeric ID of the program. If the ID is PG:45, just use 45.

    Returns:
        JSON string containing the list of capabilities
    """
    try:
        # Validate program_id
        validation_error = ParameterValidator.validate_positive_integer(
            program_id, "program_id", min_value=1
        )
        if validation_error:
            return format_error_response(**validation_error)

        # Get the list of capabilities in the program
        capabilities_url = f"programs/{program_id}/capabilities/search?current_page=1&page_size=500"
        capabilities = await spira_client.make_spira_api_get_request(capabilities_url)

        # Return JSON response
        return format_success_response(data=capabilities if capabilities else [])

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve capabilities",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e)},
            suggestion="Check API connectivity and program_id validity",
        )


def register_tools(mcp) -> None:
    """
    Register program capabilities tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool(
        name="program_get_capabilities",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    )
    async def get_capabilities(program_id: int) -> str:
        """
        Retrieves a list of the capabilities in the specified program

        Maps to Spira API: GET /programs/{program_id}/capabilities/search

        Capabilities are high-level features or epics that span multiple products/projects within a program.

        Args:
            program_id: The numeric ID of the program. If the ID is PG:45, just use 45.

        Returns:
            JSON string with structure: {"data": [capability objects]}
            Full response structure documented in API.

        Call system_get_artifact_schema(artifact_type='capability') to see available fields.

        Related Tools:
            - get_milestones: Get program milestones
            - get_programs: Get list of programs

        Error Responses:
            Returns structured JSON with error, error_code, details, and suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            capabilities_json = get_capabilities(program_id=10)
            capabilities = json.loads(capabilities_json)
        """
        try:
            spira_client = get_spira_client()
            return await _get_capabilities_impl(spira_client, program_id)
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve capabilities",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
