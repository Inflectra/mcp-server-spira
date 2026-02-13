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

        This tool returns all milestones in a program. Milestones are major
        delivery points or phases that span across multiple products/projects
        within a program.

        Args:
            program_id: The numeric ID of the program. If the ID is PG:45, just use 45.

        Returns:
            JSON string with structure:
            {
                "data": [
                    {
                        "MilestoneId": 456,
                        "Name": "Q1 Release",
                        "Description": "First quarter major release",
                        "MilestoneStatusId": 2,
                        "MilestoneStatusName": "In Progress",
                        "MilestoneTypeId": 1,
                        "MilestoneTypeName": "Major Release",
                        "CreationDate": "2024-01-01T08:00:00Z",
                        "LastUpdateDate": "2024-01-20T14:30:00Z",
                        "StartDate": "2024-01-01T00:00:00Z",
                        "EndDate": "2024-03-31T23:59:59Z",
                        "ProgramId": 10,
                        "ProgramName": "Engineering Programs",
                        "PercentComplete": 45
                    }
                ]
            }

        Key Fields:
            - MilestoneId: Unique identifier for the milestone
            - Name: The name of the milestone
            - Description: Detailed description of the milestone
            - MilestoneStatusId/MilestoneStatusName: Current status
            - MilestoneTypeId/MilestoneTypeName: Type of milestone
            - StartDate/EndDate: Planned timeline
            - ProgramId/ProgramName: Parent program
            - PercentComplete: Completion percentage (0-100)

        When to Use:
            - Getting list of milestones in a program
            - Understanding program timeline and phases
            - Tracking program-level delivery points
            - Finding milestones by status or date (filter the JSON)

        Related Tools:
            - get_capabilities: Get program capabilities
            - get_programs: Get list of programs

        Error Responses:
            {
                "error": "Invalid program_id parameter",
                "error_code": "INVALID_PARAMETER",
                "details": {
                    "parameter": "program_id",
                    "value": -1,
                    "expected": ">= 1"
                },
                "suggestion": "program_id must be >= 1"
            }

        Example Usage:
            # Get all milestones in a program
            milestones_json = get_milestones(program_id=10)
            milestones = json.loads(milestones_json)

            # Filter by status
            in_progress = [m for m in milestones["data"]
                          if m["MilestoneStatusName"] == "In Progress"]

            # Find upcoming milestones
            from datetime import datetime
            now = datetime.now().isoformat()
            upcoming = [m for m in milestones["data"]
                       if m["StartDate"] > now]
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
