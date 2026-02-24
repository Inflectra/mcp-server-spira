"""
Provides operations for working with the Spira test cases I have been assigned

This module provides MCP tools for retrieving and updating my assigned test
cases.
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.pagination import paginate_client_side
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _get_my_testcases_impl(spira_client, limit: int, offset: int) -> str:
    """
    Implementation of retrieving my assigned Spira test cases.

    Args:
        spira_client: The Inflectra Spira API client instance
        limit: Maximum number of test cases to return
        offset: Number of test cases to skip

    Returns:
        JSON string with paginated test case data
    """
    try:
        # Validate pagination parameters
        validation_error = ParameterValidator.validate_pagination_params(limit, offset)
        if validation_error:
            return format_error_response(**validation_error)

        # Get the list of open testcases for the current user
        testcases_url = "test-cases"
        all_testcases = spira_client.make_spira_api_get_request(testcases_url)

        # Handle empty results
        if not all_testcases:
            all_testcases = []

        # Apply client-side pagination
        result = paginate_client_side(all_testcases, limit, offset)

        # Return formatted JSON response
        return format_success_response(data=result["data"], pagination=dict(result["pagination"]))

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve test cases",
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
    def get_my_testcases(limit: int = 25, offset: int = 0) -> str:
        """
        Retrieves test cases assigned to the current user.

        Maps to Spira API: GET /test-cases

        Use this for personal test case lists, test execution planning, or test coverage analysis.
        **Pagination:** Client-side (API returns all, sliced in Python).

        Args:
            limit: Maximum number of test cases to return (1-500, default: 25)
            offset: Number of test cases to skip (>= 0, default: 0)

        Returns:
            JSON string with structure: {"data": [test case objects], "pagination": {...}}
            See Key Fields section below for important test case fields.
            Full response structure documented in API.

        Key Fields:
            - TestCaseId: Unique identifier for the test case
            - Name: The name of the test case
            - TestCaseStatusId/TestCaseStatusName: Current status
            - TestCasePriorityId/TestCasePriorityName: Priority level
            - ExecutionStatusId/ExecutionStatusName: Most recent execution result
            - OwnerId/OwnerName: User the test case is assigned to
            - EstimatedDuration: Estimated time to execute in minutes
            - ExecutionDate: When last executed
            - AutomationEngineId: Automation engine ID (null if manual)
            - ProjectId/ProjectName: Project the test case belongs to

            Additional fields available: Description, TestCaseTypeId/TestCaseTypeName, AuthorId/AuthorName, ActualDuration, CreationDate, LastUpdateDate, TestCaseFolderId, ComponentIds, AutomationAttachmentId, IsSuspect, IsTestSteps, TestSteps, CustomProperties, Tags, IsAttachments, Guid

        Related Tools:
            - format_artifacts_as_markdown: Format filtered/processed results for display

        Error Responses:
            Returns structured JSON with error, error_code, details, and suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            # Simple display - LLM formats naturally
            testcases_json = get_my_testcases()

            # Pagination - Get next page
            testcases_json = get_my_testcases(limit=25, offset=25)
        """
        try:
            # Validate pagination parameters
            validation_error = ParameterValidator.validate_pagination_params(limit, offset)
            if validation_error:
                return format_error_response(**validation_error)

            # Get Spira client
            spira_client = get_spira_client()

            # Retrieve and paginate test cases
            return _get_my_testcases_impl(spira_client, limit, offset)

        except Exception as e:
            return format_error_response(
                error="Failed to retrieve test cases",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
