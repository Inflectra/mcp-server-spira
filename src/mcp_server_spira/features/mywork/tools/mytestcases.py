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

        This tool returns test cases where the current user is the Owner
        (assigned to). Use this for personal test case lists, test execution
        planning, or test coverage analysis.

        **Pagination:** This endpoint uses CLIENT-SIDE pagination. The API
        returns all test cases, and we slice the results in Python. This is
        acceptable for "my work" queries which typically return < 500 items.
        For large result sets, consider using project-level queries with
        server-side pagination (available in Milestone 2+).

        **For Display:** Modern LLMs can format JSON naturally for simple
        display. For complex workflows where you've filtered or processed
        the data, use format_artifacts_as_markdown() to ensure consistent
        formatting.

        Args:
            limit: Maximum number of test cases to return (1-500, default: 25)
                Controls result set size for pagination.
            offset: Number of test cases to skip (>= 0, default: 0)
                Used for retrieving subsequent pages of results.

        Returns:
            JSON string with structure:
            {
                "data": [
                    {
                        "TestCaseId": 123,
                        "Name": "Login with valid credentials",
                        "Description": "Verify user can log in with valid
                            username and password",
                        "TestCaseStatusId": 2,
                        "TestCaseStatusName": "Ready for Review",
                        "TestCaseTypeId": 1,
                        "TestCaseTypeName": "Functional",
                        "TestCasePriorityId": 1,
                        "TestCasePriorityName": "1 - Critical",
                        "ExecutionStatusId": 2,
                        "ExecutionStatusName": "Passed",
                        "OwnerId": 5,
                        "OwnerName": "John Doe",
                        "OwnerGuid": "abc-123",
                        "AuthorId": 4,
                        "AuthorName": "Jane Smith",
                        "AuthorGuid": "def-456",
                        "EstimatedDuration": 15,
                        "ActualDuration": 12,
                        "CreationDate": "2024-01-10T08:00:00Z",
                        "LastUpdateDate": "2024-01-15T14:30:00Z",
                        "ExecutionDate": "2024-01-16T10:00:00Z",
                        "ProjectId": 55,
                        "ProjectName": "Web Application",
                        "ProjectGuid": "mno-345",
                        "TestCaseFolderId": 10,
                        "ComponentIds": [3, 7],
                        "AutomationEngineId": null,
                        "AutomationAttachmentId": null,
                        "IsSuspect": false,
                        "IsTestSteps": true,
                        "TestSteps": [],
                        "ArtifactTypeId": 2,
                        "ConcurrencyDate": "2024-01-15T14:30:00Z",
                        "CustomProperties": [],
                        "Tags": "smoke,login,authentication",
                        "IsAttachments": false,
                        "Guid": "pqr-678"
                    }
                ],
                "pagination": {
                    "limit": 25,
                    "offset": 0,
                    "returned_count": 25,
                    "total_count": 87,
                    "has_more": true,
                    "pagination_type": "client-side"
                }
            }

        Key Fields:
            - TestCaseId: Unique identifier for the test case
            - Name: The name of the test case
            - Description: The detailed description of the test case
            - TestCaseStatusId/TestCaseStatusName: Current status of the
                test case (Draft, Ready for Review, Approved, etc.)
            - TestCaseTypeId/TestCaseTypeName: Type of test case
                (Functional, Performance, Security, etc.)
            - TestCasePriorityId/TestCasePriorityName: Priority level
                (1-Critical to 4-Low)
            - ExecutionStatusId/ExecutionStatusName: Result of most recent
                execution (Passed, Failed, Blocked, Not Run, etc.)
            - OwnerId/OwnerName/OwnerGuid: User the test case is assigned to
            - AuthorId/AuthorName/AuthorGuid: User who created the test case
            - EstimatedDuration: Estimated time to execute in minutes
            - ActualDuration: Actual time from most recent execution in
                minutes
            - CreationDate: When the test case was originally created
            - LastUpdateDate: When the test case was last modified
            - ExecutionDate: When the test case was last executed
            - ProjectId/ProjectName/ProjectGuid: Project the test case
                belongs to
            - TestCaseFolderId: Folder the test case is stored in (null for
                root)
            - ComponentIds: List of component IDs this test case belongs to
            - AutomationEngineId: ID of automation engine if automated (null
                if manual)
            - AutomationAttachmentId: ID of test script attachment (null if
                manual)
            - IsSuspect: Whether associated requirements have changed
            - IsTestSteps: Whether the test case has test steps
            - TestSteps: List of test steps (may be empty in list view)
            - ArtifactTypeId: Type of artifact (2 for test cases)
            - ConcurrencyDate: Timestamp for optimistic concurrency control
            - CustomProperties: List of custom fields for this test case
            - Tags: Meta-tags associated with the test case
            - IsAttachments: Whether the test case has attachments
            - Guid: Unique global identifier for the test case

        When to Use:
            - Getting personal test case list for current user
            - Planning test execution activities
            - Analyzing test coverage and status
            - Finding test cases by status, priority, or execution result
                (filter the JSON)

        Related Tools:
            - format_artifacts_as_markdown: Format filtered/processed
                results for display
            - get_test_case_by_id: Get single test case with full details
                (future)
            - search_test_cases: Advanced filtering across all test cases
                (future)

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
            testcases_json = get_my_testcases()
            # LLM can format this JSON for display without additional tools

            # Pagination - Get next page
            testcases_json = get_my_testcases(limit=25, offset=25)

            # Complex workflow - Use formatting tool for filtered results
            testcases_json = get_my_testcases(limit=100)
            testcases = json.loads(testcases_json)
            failed = [tc for tc in testcases["data"]
                      if tc["ExecutionStatusName"] == "Failed"]
            failed_json = json.dumps({"data": failed})
            readable = format_artifacts_as_markdown(failed_json, "test_case")
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
