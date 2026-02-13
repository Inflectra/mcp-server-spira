"""
Provides operations for working with the Spira product test sets

This module provides MCP tools for retrieving and updating product test sets
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _get_test_sets_impl(
    spira_client,
    product_id: int,
    starting_row: int = 1,
    number_of_rows: int = 100,
    sort_field: str = "",
    sort_direction: str = "ASC",
) -> str:
    """
    Implementation of retrieving the list of test sets in the specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product.
            If the ID is PR:45, just use 45.
        starting_row: The starting row number for pagination (1-based index)
        number_of_rows: The number of rows to return
        sort_field: The field to sort by (optional)
        sort_direction: The sort direction - "ASC" or "DESC"

    Returns:
        JSON string containing the list of test sets with data structure
    """
    try:
        # Build the search endpoint URL with query parameters
        test_sets_url = (
            f"projects/{product_id}/test-sets/search?"
            f"starting_row={starting_row}&number_of_rows={number_of_rows}"
        )

        # Add optional sort parameters if provided
        if sort_field:
            test_sets_url += f"&sort_field={sort_field}&sort_direction={sort_direction}"

        # Make POST request with empty filter array (no filtering for now)
        test_sets = spira_client.make_spira_api_post_request(test_sets_url, [])

        # Return JSON response with data structure
        return format_success_response(data=test_sets)

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve test sets",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e), "product_id": product_id},
            suggestion=("Check API connectivity, authentication, and that the product_id is valid"),
        )


def register_tools(mcp) -> None:
    """
    Register product test sets tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_test_sets(
        product_id: int,
        starting_row: int = 1,
        number_of_rows: int = 100,
        sort_field: str = "",
        sort_direction: str = "ASC",
    ) -> str:
        """
        Retrieves a list of the test sets in the specified product

        Maps to Spira API: POST /projects/{product_id}/test-sets/search

        This tool returns test sets from the specified product using
        server-side pagination. Use this for retrieving product-level
        test set lists with filtering and sorting capabilities.

        **API Endpoint**: POST /projects/{product_id}/test-sets/search
        **Query Parameters**: starting_row, number_of_rows, sort_field,
            sort_direction
        **Request Body**: [] (empty RemoteFilter array - no filtering
            for now)

        **Note**: This endpoint uses server-side pagination. The API
        returns only the requested page of results. A dedicated filter
        tool will be added in a future milestone.

        Args:
            product_id: The numeric ID of the product.
                If the ID is PR:45, just use 45.
            starting_row: The starting row number for pagination
                (default: 1, 1-based index)
            number_of_rows: The number of rows to return (default: 100)
            sort_field: The field to sort by (optional, e.g., "TestSetId",
                "Name", "TestSetStatusName")
            sort_direction: The sort direction - "ASC" or "DESC"
                (default: "ASC")

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
                ]
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
            - Getting test set list for a specific product
            - Retrieving test sets with server-side pagination
            - Sorting test sets by specific fields
            - Analyzing product-level test suite data

        Related Tools:
            - get_my_testsets: Get test sets assigned to current user
                (with client-side pagination)
            - format_artifacts_as_markdown: Format filtered/processed
                results for display

        Error Responses:
            {
                "error": "Invalid product_id parameter",
                "error_code": "INVALID_VALUE",
                "details": {
                    "parameter": "product_id",
                    "value": -1,
                    "expected": ">= 1"
                },
                "suggestion": "product_id must be >= 1"
            }

        Example Usage:
            # Get first 100 test sets from product 55
            test_sets_json = get_test_sets(product_id=55)
            test_sets = json.loads(test_sets_json)

            # Get next page of test sets
            test_sets_json = get_test_sets(
                product_id=55, starting_row=101, number_of_rows=100
            )

            # Get test sets sorted by status
            test_sets_json = get_test_sets(
                product_id=55,
                sort_field="TestSetStatusName",
                sort_direction="ASC"
            )

            # Process and filter results
            test_sets = json.loads(test_sets_json)
            failed_sets = [
                ts for ts in test_sets["data"]
                if ts["CountFailed"] > 0
            ]
        """
        try:
            # Validate product_id
            validation_error = ParameterValidator.validate_positive_integer(
                product_id, "product_id", min_value=1
            )
            if validation_error:
                return format_error_response(**validation_error)

            # Validate starting_row
            validation_error = ParameterValidator.validate_positive_integer(
                starting_row, "starting_row", min_value=1
            )
            if validation_error:
                return format_error_response(**validation_error)

            # Validate number_of_rows
            validation_error = ParameterValidator.validate_positive_integer(
                number_of_rows, "number_of_rows", min_value=1
            )
            if validation_error:
                return format_error_response(**validation_error)

            # Get Spira client and retrieve test sets
            spira_client = get_spira_client()
            return _get_test_sets_impl(
                spira_client,
                product_id,
                starting_row,
                number_of_rows,
                sort_field,
                sort_direction,
            )
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve test sets",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
