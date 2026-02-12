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

        Use this tool when you need to:
        - View the list of programs that a user has access to
        - Get information about multiple programs at once
        - Access the full description and selected fields of programs

        Returns:
            JSON string with structure:
            {
                "data": [
                    {
                        "ProgramId": 10,
                        "Name": "Engineering Programs",
                        "Description": "All engineering-related programs",
                        "Website": "https://engineering.example.com",
                        "PortfolioId": 5,
                        "ProjectTemplateId": 1,
                        "isActive": true,
                        "isDefault": false,
                        "WorkspaceTypeId": 2,
                        "Guid": "abc-123-def-456",
                        "LastUpdatedDate": "2024-01-15T10:00:00Z",
                        "ArtifactTypeId": 7,
                        "ConcurrencyGuid": "xyz-789",
                        "CustomProperties": []
                    }
                ]
            }

        Key Fields:
            - ProgramId: Unique identifier for the program (use this in
                other tool calls)
            - Name: Display name of the program
            - Description: Detailed description of the program
            - Website: URL associated with the program
            - PortfolioId: ID of the portfolio this program belongs to
                (null if none)
            - ProjectTemplateId: ID of the template used for this
                program (null if none)
            - isActive: Whether the program is currently active
                (boolean)
            - isDefault: Whether this is the default program (boolean)
            - WorkspaceTypeId: Type of workspace (integer)
            - Guid: Unique global identifier (string)
            - LastUpdatedDate: Last modification timestamp
                (ISO 8601 datetime, nullable)
            - ArtifactTypeId: Type of artifact (integer, typically 7
                for programs)
            - ConcurrencyGuid: Used for optimistic concurrency control
                (string)
            - CustomProperties: Array of custom fields for this program

        When to Use:
            - Discovering available programs for the current user
            - Listing programs for user selection
            - Validating program IDs before other operations
            - Getting program metadata for reporting
            - Finding programs by portfolio

        Related Tools:
            - get_program_products: Get products that belong to a
                specific program
            - get_products: Get all products user has access to
            - get_milestones: Get milestones for a specific program

        Error Responses:
            {
                "error": "Failed to retrieve programs",
                "error_code": "API_ERROR",
                "details": {
                    "message": "Connection timeout"
                },
                "suggestion": "Check API connectivity and authentication"
            }

        Example Usage:
            # Get all programs
            programs_json = get_programs()
            programs = json.loads(programs_json)

            # Filter active programs
            active_programs = [p for p in programs["data"]
                               if p["isActive"]]

            # Find program by name
            eng_program = next((p for p in programs["data"]
                                if "Engineering" in p["Name"]), None)

            # Get programs in a specific portfolio
            portfolio_programs = [p for p in programs["data"]
                                  if p["PortfolioId"] == 5]
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
