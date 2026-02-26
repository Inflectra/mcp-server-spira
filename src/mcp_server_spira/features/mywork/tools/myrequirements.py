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

    @mcp.tool(
        name="my_get_requirements",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    )
    def get_my_requirements(limit: int = 25, offset: int = 0) -> str:
        """
        Retrieves requirements assigned to the current user.

        Maps to Spira API: GET /requirements

        Use this for personal requirement lists, sprint planning, or workload analysis.
        **Pagination:** Client-side (API returns all, sliced in Python).

        Args:
            limit: Maximum number of requirements to return (1-500, default: 25)
            offset: Number of requirements to skip (>= 0, default: 0)

        Returns:
            JSON string with structure: {"data": [requirement objects], "pagination": {...}}
            See Key Fields section below for important requirement fields.
            Full response structure documented in API.

        Key Fields:
            - RequirementId: Unique identifier for the requirement
            - Name: The name of the requirement
            - StatusId/StatusName: Current status
            - ImportanceId/ImportanceName: Priority/importance level
            - OwnerId/OwnerName: User the requirement is assigned to
            - EstimatePoints: Story points estimate
            - TaskCount: Number of associated tasks
            - CoverageCountTotal: Total test cases covering this requirement
            - PercentComplete: Percentage complete
            - ReleaseId/ReleaseVersionNumber: Sprint/iteration assignment

            Additional fields available: Description, RequirementTypeId/RequirementTypeName, AuthorId/AuthorName, EstimatedEffort, TaskEstimatedEffort, TaskActualEffort, CoverageCountPassed/Failed/Caution/Blocked, StartDate, EndDate, CreationDate, LastUpdateDate, ComponentId, Summary, IsSuspect, CustomProperties, Tags, IsAttachments

        Related Tools:
            - format_artifacts_as_markdown: Format filtered/processed results for display

        Error Responses:
            Returns structured JSON with error, error_code, details, and suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            # Simple display - LLM formats naturally
            requirements_json = get_my_requirements()

            # Pagination - Get next page
            requirements_json = get_my_requirements(limit=25, offset=25)
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
