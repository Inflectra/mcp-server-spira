"""
Provides operations for working with the Spira test sets I have been assigned

This module provides MCP tools for retrieving and updating my assigned test
sets.
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.pagination import paginate_client_side
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _get_my_testsets_impl(spira_client, limit: int, offset: int) -> str:
    """
    Implementation of retrieving my assigned Spira test sets.

    Args:
        spira_client: The Inflectra Spira API client instance
        limit: Maximum number of test sets to return
        offset: Number of test sets to skip

    Returns:
        JSON string with paginated test set data
    """
    try:
        # Get the list of open testsets for the current user
        testsets_url = "test-sets"
        all_testsets = spira_client.make_spira_api_get_request(testsets_url)

        # Handle empty results
        if not all_testsets:
            all_testsets = []

        # Apply client-side pagination
        result = paginate_client_side(all_testsets, limit, offset)

        # Return formatted JSON response
        return format_success_response(data=result["data"], pagination=dict(result["pagination"]))

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve test sets",
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
    def get_my_testsets(limit: int = 25, offset: int = 0) -> str:
        """
        Retrieves test sets assigned to the current user.

        Maps to Spira API: GET /test-sets

        This tool returns test sets where the current user is the Owner
        (assigned to). Use this for personal test set lists, test execution
        planning, or test suite management.

        **Pagination:** This endpoint uses CLIENT-SIDE pagination. The API
        returns all test sets, and we slice the results in Python. This is
        acceptable for "my work" queries which typically return < 500 items.
        For large result sets, consider using project-level queries with
        server-side pagination (available in Milestone 2+).

        **For Display:** Modern LLMs can format JSON naturally for simple
        display. For complex workflows where you've filtered or processed
        the data, use format_artifacts_as_markdown() to ensure consistent
        formatting.

        Args:
            limit: Maximum number of test sets to return (1-500, default: 25)
                Controls result set size for pagination.
            offset: Number of test sets to skip (>= 0, default: 0)
                Used for retrieving subsequent pages of results.

        Returns:
            JSON string with structure:
            {
                "data": [
                    {
                        "TestSetId": 123,
                        "Name": "Smoke Test Suite",
                        "Description": "Critical smoke tests for release
                            validation",
                        "TestSetStatusId": 2,
                        "TestSetStatusName": "In Progress",
                        "TestRunTypeId": 1,
                        "CreatorId": 4,
                        "CreatorName": "Jane Smith",
                        "CreatorGuid": "def-456",
                        "OwnerId": 5,
                        "OwnerName": "John Doe",
                        "OwnerGuid": "abc-123",
                        "ReleaseId": 10,
                        "ReleaseVersionNumber": "1.5.0",
                        "ReleaseGuid": "ghi-789",
                        "AutomationHostId": null,
                        "RecurrenceId": null,
                        "RecurrenceName": null,
                        "CreationDate": "2024-01-10T08:00:00Z",
                        "LastUpdateDate": "2024-01-15T14:30:00Z",
                        "PlannedDate": "2024-01-20T09:00:00Z",
                        "ExecutionDate": "2024-01-16T10:00:00Z",
                        "CountPassed": 15,
                        "CountFailed": 3,
                        "CountCaution": 1,
                        "CountBlocked": 2,
                        "CountNotRun": 5,
                        "CountNotApplicable": 0,
                        "ProjectId": 55,
                        "ProjectName": "Web Application",
                        "ProjectGuid": "mno-345",
                        "TestSetFolderId": 10,
                        "EstimatedDuration": 180,
                        "ActualDuration": 165,
                        "IsAutoScheduled": false,
                        "IsDynamic": false,
                        "DynamicQuery": null,
                        "TestConfigurationSetId": null,
                        "BuildExecuteTimeInterval": null,
                        "ArtifactTypeId": 8,
                        "ConcurrencyDate": "2024-01-15T14:30:00Z",
                        "CustomProperties": [],
                        "Tags": "smoke,critical,release",
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
            - TestSetId: Unique identifier for the test set
            - Name: The name of the test set
            - Description: The detailed description of the test set
            - TestSetStatusId/TestSetStatusName: Current status of the test
                set (Not Started, In Progress, Completed, etc.)
            - TestRunTypeId: Type of test set (1 = Manual, 2 = Automated)
            - CreatorId/CreatorName/CreatorGuid: User who created the test
                set
            - OwnerId/OwnerName/OwnerGuid: User the test set is assigned to
            - ReleaseId/ReleaseVersionNumber/ReleaseGuid: Release/sprint the
                test set is scheduled for
            - AutomationHostId: ID of automation host if automated (null if
                manual)
            - RecurrenceId/RecurrenceName: Recurrence pattern if scheduled
                (null if one-time)
            - CreationDate: When the test set was originally created
            - LastUpdateDate: When the test set was last modified
            - PlannedDate: When the test set is planned to be executed
            - ExecutionDate: When the test set was last executed
            - CountPassed: Number of passed test cases in the set
            - CountFailed: Number of failed test cases in the set
            - CountCaution: Number of cautioned test cases in the set
            - CountBlocked: Number of blocked test cases in the set
            - CountNotRun: Number of test cases not yet run
            - CountNotApplicable: Number of test cases marked N/A
            - ProjectId/ProjectName/ProjectGuid: Project the test set
                belongs to
            - TestSetFolderId: Folder the test set is stored in (null for
                root)
            - EstimatedDuration: Total estimated duration for all test cases
                in minutes
            - ActualDuration: Total actual duration for all test cases in
                minutes
            - IsAutoScheduled: Whether test set auto-executes when a build
                runs
            - IsDynamic: Whether this is a dynamic test set (query-based)
            - DynamicQuery: The underlying query if dynamic test set
            - TestConfigurationSetId: ID of test configuration set if used
            - BuildExecuteTimeInterval: Interval between build finish and
                test execution (if auto-scheduled)
            - ArtifactTypeId: Type of artifact (8 for test sets)
            - ConcurrencyDate: Timestamp for optimistic concurrency control
            - CustomProperties: List of custom fields for this test set
            - Tags: Meta-tags associated with the test set
            - IsAttachments: Whether the test set has attachments
            - Guid: Unique global identifier for the test set

        When to Use:
            - Getting personal test set list for current user
            - Planning test execution activities
            - Analyzing test suite status and progress
            - Finding test sets by status, release, or execution results
                (filter the JSON)

        Related Tools:
            - format_artifacts_as_markdown: Format filtered/processed
                results for display
            - get_test_set_by_id: Get single test set with full details
                (future)
            - search_test_sets: Advanced filtering across all test sets
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
            testsets_json = get_my_testsets()
            # LLM can format this JSON for display without additional tools

            # Pagination - Get next page
            testsets_json = get_my_testsets(limit=25, offset=25)

            # Complex workflow - Use formatting tool for filtered results
            testsets_json = get_my_testsets(limit=100)
            testsets = json.loads(testsets_json)
            failed = [ts for ts in testsets["data"]
                      if ts["CountFailed"] > 0]
            failed_json = json.dumps({"data": failed})
            readable = format_artifacts_as_markdown(failed_json, "test_set")
        """
        try:
            # Validate pagination parameters
            validation_error = ParameterValidator.validate_pagination_params(limit, offset)
            if validation_error:
                return format_error_response(**validation_error)

            # Get Spira client
            spira_client = get_spira_client()

            # Retrieve and paginate test sets
            return _get_my_testsets_impl(spira_client, limit, offset)

        except Exception as e:
            return format_error_response(
                error="Failed to retrieve test sets",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
