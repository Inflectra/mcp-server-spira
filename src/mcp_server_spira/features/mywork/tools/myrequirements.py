"""
Provides operations for working with the Spira requirements I have been
assigned

This module provides MCP tools for retrieving and updating my assigned
requirements.
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.pagination import paginate_client_side
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _get_my_requirements_impl(spira_client, limit: int, offset: int) -> str:
    """
    Implementation of retrieving my assigned Spira requirements.

    Args:
        spira_client: The Inflectra Spira API client instance
        limit: Maximum number of requirements to return
        offset: Number of requirements to skip

    Returns:
        JSON string with paginated requirement data
    """
    try:
        # Validate pagination parameters
        validation_error = ParameterValidator.validate_pagination_params(limit, offset)
        if validation_error:
            return format_error_response(**validation_error)

        # Get the list of open requirements for the current user
        requirements_url = "requirements"
        all_requirements = spira_client.make_spira_api_get_request(requirements_url)

        # Handle empty results
        if not all_requirements:
            all_requirements = []

        # Apply client-side pagination
        result = paginate_client_side(all_requirements, limit, offset)

        # Return formatted JSON response
        return format_success_response(data=result["data"], pagination=dict(result["pagination"]))

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve requirements",
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
    def get_my_requirements(limit: int = 25, offset: int = 0) -> str:
        """
        Retrieves requirements assigned to the current user.

        Maps to Spira API: GET /requirements

        This tool returns requirements where the current user is the
        Owner (assigned to). Use this for personal requirement lists,
        sprint planning, or workload analysis.

        **Pagination:** This endpoint uses CLIENT-SIDE pagination. The
        API returns all requirements, and we slice the results in Python.
        This is acceptable for "my work" queries which typically return
        < 500 items. For large result sets, consider using project-level
        queries with server-side pagination (available in Milestone 2+).

        **For Display:** Modern LLMs can format JSON naturally for simple
        display. For complex workflows where you've filtered or processed
        the data, use format_artifacts_as_markdown() to ensure consistent
        formatting.

        Args:
            limit: Maximum number of requirements to return (1-500,
                default: 25)
                Controls result set size for pagination.
            offset: Number of requirements to skip (>= 0, default: 0)
                Used for retrieving subsequent pages of results.

        Returns:
            JSON string with structure:
            {
                "data": [
                    {
                        "RequirementId": 123,
                        "Name": "User Authentication",
                        "Description": "Implement secure user login system",
                        "StatusId": 2,
                        "StatusName": "In Progress",
                        "RequirementTypeId": 1,
                        "RequirementTypeName": "Feature",
                        "ImportanceId": 1,
                        "ImportanceName": "Critical",
                        "OwnerId": 5,
                        "OwnerName": "John Doe",
                        "AuthorId": 4,
                        "AuthorName": "Jane Smith",
                        "EstimatePoints": 8.0,
                        "EstimatedEffort": 480,
                        "TaskEstimatedEffort": 450,
                        "TaskActualEffort": 240,
                        "TaskCount": 5,
                        "PercentComplete": 50,
                        "CoverageCountTotal": 10,
                        "CoverageCountPassed": 6,
                        "CoverageCountFailed": 2,
                        "CoverageCountCaution": 1,
                        "CoverageCountBlocked": 1,
                        "StartDate": "2024-01-15T09:00:00Z",
                        "EndDate": "2024-01-30T17:00:00Z",
                        "CreationDate": "2024-01-10T08:00:00Z",
                        "LastUpdateDate": "2024-01-20T14:30:00Z",
                        "ReleaseId": 10,
                        "ReleaseVersionNumber": "1.5.0",
                        "ProjectId": 55,
                        "ProjectName": "Web Application",
                        "ComponentId": 3,
                        "Summary": false,
                        "IsSuspect": false,
                        "CustomProperties": [],
                        "Tags": "security,authentication",
                        "IsAttachments": true
                    }
                ],
                "pagination": {
                    "limit": 25,
                    "offset": 0,
                    "returned_count": 25,
                    "total_count": 150,
                    "has_more": true,
                    "pagination_type": "client-side"
                }
            }

        Key Fields:
            - RequirementId: Unique identifier for the requirement
            - Name: The name of the requirement
            - Description: The detailed description of the requirement
            - StatusId/StatusName: Current status of the requirement
            - RequirementTypeId/RequirementTypeName: Type of requirement
                (Feature, Use Case, etc.)
            - ImportanceId/ImportanceName: Priority/importance level
            - OwnerId/OwnerName: User the requirement is assigned to
            - AuthorId/AuthorName: User who created the requirement
            - EstimatePoints: Story points estimate (decimal)
            - EstimatedEffort: Top-down effort estimate in minutes
                (calculated from points)
            - TaskEstimatedEffort: Bottom-up estimated effort from all
                associated tasks (minutes)
            - TaskActualEffort: Bottom-up actual effort from all
                associated tasks (minutes)
            - TaskCount: Number of tasks associated with this requirement
            - PercentComplete: Percentage complete of the requirement
            - CoverageCountTotal: Total number of test cases covering
                this requirement
            - CoverageCountPassed/Failed/Caution/Blocked: Test case
                coverage breakdown by status
            - StartDate: Scheduled start date for planning
            - EndDate: Scheduled end date for planning
            - CreationDate: When the requirement was originally created
            - LastUpdateDate: When the requirement was last modified
            - ReleaseId/ReleaseVersionNumber: Sprint/iteration assignment
            - ProjectId/ProjectName: Project the requirement belongs to
            - ComponentId: Component the requirement belongs to (null if none)
            - Summary: Whether this is a summary requirement (parent)
            - IsSuspect: Whether requirement is marked as suspect due to
                dependent item changes
            - CustomProperties: List of custom fields for this requirement
            - Tags: Meta-tags associated with the requirement
            - IsAttachments: Whether the requirement has attachments

        When to Use:
            - Getting personal requirement list for current user
            - Sprint planning and backlog grooming
            - Analyzing personal workload
            - Finding requirements by status or importance (filter the JSON)
            - Tracking test coverage for assigned requirements

        Related Tools:
            - format_artifacts_as_markdown: Format filtered/processed
                results for display
            - get_requirement_by_id: Get single requirement with full
                details (future)
            - search_requirements: Advanced filtering across all
                requirements (future)

        Error Responses:
            {
                "error": "Invalid pagination parameters",
                "error_code": "INVALID_PARAMETER",
                "details": {
                    "parameter": "limit",
                    "value": 1000,
                    "expected": "1-500"
                },
                "suggestion": "Use limit between 1 and 500"
            }

        Example Usage:
            # Simple display - LLM formats naturally
            requirements_json = get_my_requirements()
            # LLM can format this JSON for display without additional tools

            # Pagination - Get next page
            requirements_json = get_my_requirements(limit=25, offset=25)

            # Complex workflow - Use formatting tool for filtered results
            requirements_json = get_my_requirements(limit=100)
            requirements = json.loads(requirements_json)
            critical = [r for r in requirements["data"]
                        if r["ImportanceName"] == "Critical"]
            critical_json = json.dumps({"data": critical})
            readable = format_artifacts_as_markdown(critical_json,
                                                     "requirement")
        """
        try:
            # Validate pagination parameters
            validation_error = ParameterValidator.validate_pagination_params(limit, offset)
            if validation_error:
                return format_error_response(**validation_error)

            # Get Spira client
            spira_client = get_spira_client()

            # Retrieve and paginate requirements
            return _get_my_requirements_impl(spira_client, limit, offset)

        except Exception as e:
            return format_error_response(
                error="Failed to retrieve requirements",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
