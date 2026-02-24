"""
Provides operations for working with the Spira program milestones

This module provides MCP tools for retrieving and updating program milestones
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _get_milestones_impl(spira_client, program_id: int) -> str:
    """
    Implementation of retrieving the list of milestones in the specified program

    Args:
        spira_client: The Inflectra Spira API client instance
        program_id: The numeric ID of the program. If the ID is PG:45, just use 45.

    Returns:
        JSON string containing the list of milestones
    """
    try:
        # Validate program_id
        validation_error = ParameterValidator.validate_positive_integer(
            program_id, "program_id", min_value=1
        )
        if validation_error:
            return format_error_response(**validation_error)

        # Get the list of milestones in the program
        milestones_url = f"programs/{program_id}/milestones"
        milestones = spira_client.make_spira_api_get_request(milestones_url)

        # Return JSON response
        return format_success_response(data=milestones if milestones else [])

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve milestones",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e)},
            suggestion="Check API connectivity and program_id validity",
        )


def register_tools(mcp) -> None:
    """
    Register program milestone tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_milestones(program_id: int) -> str:
        """
        Retrieves a list of the milestones in the specified program

        Maps to Spira API: GET /programs/{program_id}/milestones

        Milestones are major delivery points or phases that span across multiple products/projects within a program.

        Args:
            program_id: The numeric ID of the program. If the ID is PG:45, just use 45.

        Returns:
            JSON string with structure: {"data": [milestone objects]}
            See Key Fields section below for important milestone fields.
            Full response structure documented in API.

        Key Fields:
            - MilestoneId: Unique identifier for the milestone
            - Name: The name of the milestone
            - MilestoneStatusId/MilestoneStatusName: Current status
            - StartDate/EndDate: Planned timeline
            - PercentComplete: Completion percentage (0-100)
            - ProgramId/ProgramName: Parent program

            Additional fields available: Description, MilestoneTypeId/MilestoneTypeName, CreationDate, LastUpdateDate, CustomProperties

        Related Tools:
            - get_capabilities: Get program capabilities
            - get_programs: Get list of programs

        Error Responses:
            Returns structured JSON with error, error_code, details, and suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            milestones_json = get_milestones(program_id=10)
            milestones = json.loads(milestones_json)
        """
        try:
            spira_client = get_spira_client()
            return _get_milestones_impl(spira_client, program_id)
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve milestones",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
