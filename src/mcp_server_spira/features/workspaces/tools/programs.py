"""
Provides operations for working with the Spira program workspace

This module provides MCP tools for retrieving and updating programs
(also known as projects).
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)


def _get_programs_impl(spira_client) -> str:
    """
    Implementation of retrieving the list of Spira programs
    the current user has access to

    Args:
        spira_client: The Inflectra Spira API client instance

    Returns:
        JSON string containing the list of available programs
    """
    try:
        # Get the list of available programs for the current user
        programs_url = "programs"
        programs = spira_client.make_spira_api_get_request(programs_url)

        if not programs:
            # Return empty data array if no programs
            return format_success_response(data=[])

        # Return all programs as JSON (no truncation)
        return format_success_response(data=programs)
    except Exception as e:
        return format_error_response(
            error="Failed to retrieve programs",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e)},
            suggestion="Check API connectivity and authentication",
        )


def register_tools(mcp) -> None:
    """
    Register my work tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_programs() -> str:
        """
        Retrieves a list of the programs (projects) that the current
        user has access to

        Maps to Spira API: GET /programs

        Use this to discover available programs and their organizational
        structure.

        Returns:
            JSON string with structure: {"data": [program objects]}
            See Key Fields section below for important program fields.
            Full response structure documented in API.

        Key Fields:
            - ProgramId: Unique identifier (use in other tool calls)
            - Name: Display name of the program
            - isActive: Whether the program is currently active
            - PortfolioId: Portfolio this program belongs to
            - LastUpdatedDate: Last modification timestamp

            Additional fields available: Description, Website, isDefault,
            ProjectTemplateId, PortfolioId, CustomProperties, Guid

        Related Tools:
            - get_products: Get all products user has access to
            - get_milestones: Get milestones for a specific program

        Error Responses:
            Returns structured JSON with error, error_code, details, and
            suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            programs_json = get_programs()
            programs = json.loads(programs_json)
            active_programs = [
                p for p in programs["data"] if p["isActive"]
            ]
        """
        try:
            spira_client = get_spira_client()
            return _get_programs_impl(spira_client)
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve programs",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
