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


def _get_capabilities_impl(spira_client, program_id: int) -> str:
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
        capabilities = spira_client.make_spira_api_get_request(capabilities_url)

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

    @mcp.tool()
    def get_capabilities(program_id: int) -> str:
        """
        Retrieves a list of the capabilities in the specified program

        Maps to Spira API: GET /programs/{program_id}/capabilities/search

        This tool returns all capabilities in a program. Capabilities are high-level
        features or epics that span multiple products/projects within a program.

        Args:
            program_id: The numeric ID of the program. If the ID is PG:45, just use 45.

        Returns:
            JSON string with structure:
            {
                "data": [
                    {
                        "CapabilityId": 123,
                        "Name": "User Authentication",
                        "Description": "Implement secure user login system",
                        "CapabilityStatusId": 2,
                        "CapabilityStatusName": "In Progress",
                        "CapabilityTypeId": 1,
                        "CapabilityTypeName": "Feature",
                        "CapabilityPriorityId": 1,
                        "CapabilityPriorityName": "Critical",
                        "OwnerId": 5,
                        "OwnerName": "John Doe",
                        "CreationDate": "2024-01-10T08:00:00Z",
                        "LastUpdateDate": "2024-01-20T14:30:00Z",
                        "StartDate": "2024-01-15T09:00:00Z",
                        "EndDate": "2024-03-30T17:00:00Z",
                        "ProgramId": 10,
                        "ProgramName": "Engineering Programs"
                    }
                ]
            }

        Key Fields:
            - CapabilityId: Unique identifier for the capability
            - Name: The name of the capability
            - Description: Detailed description of the capability
            - CapabilityStatusId/CapabilityStatusName: Current status
            - CapabilityTypeId/CapabilityTypeName: Type of capability
            - CapabilityPriorityId/CapabilityPriorityName: Priority level
            - OwnerId/OwnerName: User responsible for the capability
            - StartDate/EndDate: Planned timeline
            - ProgramId/ProgramName: Parent program

        When to Use:
            - Getting list of capabilities in a program
            - Understanding program-level features and epics
            - Analyzing program scope and priorities
            - Finding capabilities by status or priority (filter the JSON)

        Related Tools:
            - get_milestones: Get program milestones
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
            # Get all capabilities in a program
            capabilities_json = get_capabilities(program_id=10)
            capabilities = json.loads(capabilities_json)

            # Filter by status
            in_progress = [c for c in capabilities["data"]
                          if c["CapabilityStatusName"] == "In Progress"]
        """
        try:
            spira_client = get_spira_client()
            return _get_capabilities_impl(spira_client, program_id)
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve capabilities",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
