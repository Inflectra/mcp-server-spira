"""
Provides operations for working with the Spira product test runs

This module provides MCP tools for retrieving and updating product test runs
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _get_test_runs_impl(
    spira_client,
    product_id: int,
    starting_row: int = 1,
    number_of_rows: int = 100,
    sort_field: str = "",
    sort_direction: str = "DESC",
) -> str:
    """
    Implementation of retrieving the list of test runs in the specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product.
            If the ID is PR:45, just use 45.
        starting_row: The starting row number for pagination (1-based index)
        number_of_rows: The number of rows to return
        sort_field: The field to sort by (optional)
        sort_direction: The sort direction - "ASC" or "DESC"

    Returns:
        JSON string containing the list of test runs with data structure
    """
    try:
        # Build the search endpoint URL with query parameters
        test_runs_url = (
            f"projects/{product_id}/test-runs/search?"
            f"starting_row={starting_row}&number_of_rows={number_of_rows}"
        )

        # Add optional sort parameters if provided
        if sort_field:
            test_runs_url += f"&sort_field={sort_field}&sort_direction={sort_direction}"

        # Make POST request with empty filter array (no filtering for now)
        test_runs = spira_client.make_spira_api_post_request(test_runs_url, [])

        # Return JSON response with data structure
        return format_success_response(data=test_runs)

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve test runs",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e), "product_id": product_id},
            suggestion=("Check API connectivity, authentication, and that the product_id is valid"),
        )


def register_tools(mcp) -> None:
    """
    Register product test runs tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_test_runs(
        product_id: int,
        starting_row: int = 1,
        number_of_rows: int = 100,
        sort_field: str = "",
        sort_direction: str = "DESC",
    ) -> str:
        """
        Retrieves a list of the test runs in the specified product

        Maps to Spira API: POST /projects/{product_id}/test-runs/search

        This tool returns test runs from the specified product using
        server-side pagination. Use this for retrieving product-level
        test run lists with filtering and sorting capabilities.

        **API Endpoint**: POST /projects/{product_id}/test-runs/search
        **Query Parameters**: starting_row, number_of_rows, sort_field,
            sort_direction
        **Request Body**: [] (empty RemoteFilter array - no filtering
            for now)

        **Note**: This endpoint uses server-side pagination. The API
        returns only the requested page of results. A dedicated filter
        tool will be added in a future milestone. Test runs do not
        include test run steps in this response.

        Args:
            product_id: The numeric ID of the product.
                If the ID is PR:45, just use 45.
            starting_row: The starting row number for pagination
                (default: 1, 1-based index)
            number_of_rows: The number of rows to return (default: 100)
            sort_field: The field to sort by (optional, e.g., "TestRunId",
                "Name", "ExecutionStatusId", "EndDate")
            sort_direction: The sort direction - "ASC" or "DESC"
                (default: "DESC")

        Returns:
            JSON string with structure:
            {
                "data": [
                    {
                        "TestRunId": 123,
                        "Name": "Login Test - Chrome",
                        "TestCaseId": 45,
                        "TestCaseGuid": "abc-123-def-456",
                        "TestRunTypeId": 2,
                        "TesterId": 5,
                        "TesterGuid": "def-456-ghi-789",
                        "ExecutionStatusId": 2,
                        "ReleaseId": 10,
                        "ReleaseGuid": "ghi-789-jkl-012",
                        "TestSetId": 15,
                        "TestSetGuid": "jkl-012-mno-345",
                        "TestSetTestCaseId": 20,
                        "StartDate": "2024-01-15T09:00:00Z",
                        "EndDate": "2024-01-15T09:15:00Z",
                        "BuildId": 8,
                        "EstimatedDuration": 15,
                        "ActualDuration": 12,
                        "TestConfigurationId": 3,
                        "ReleaseVersionNumber": "1.5.0",
                        "ProjectId": 55,
                        "ProjectGuid": "mno-345-pqr-678",
                        "ArtifactTypeId": 5,
                        "ConcurrencyDate": "2024-01-15T09:15:00Z",
                        "CustomProperties": [],
                        "IsAttachments": false,
                        "Tags": "smoke,regression",
                        "Guid": "pqr-678-stu-901"
                    }
                ]
            }

        Key Fields:
            - TestRunId: Unique identifier for the test run
            - Name: The name of the test run (usually same as test case)
            - TestCaseId/TestCaseGuid: The test case this run is an
                instance of
            - TestRunTypeId: Type of test run (1 = Manual, 2 = Automated)
            - TesterId/TesterGuid: User who executed the test
            - ExecutionStatusId: Overall execution status
                (1 = Failed, 2 = Passed, 3 = Not Run, 4 = N/A,
                5 = Blocked, 6 = Caution)
            - ReleaseId/ReleaseVersionNumber/ReleaseGuid: Release the
                test run is reported against
            - TestSetId/TestSetGuid: Test set the test run belongs to
                (null if standalone)
            - TestSetTestCaseId: Unique test case entry in the test set
            - StartDate: When test execution started
            - EndDate: When test execution completed (null if not finished)
            - BuildId: Build the test was executed against
            - EstimatedDuration: Estimated duration in minutes (read-only)
            - ActualDuration: Actual duration in minutes (read-only)
            - TestConfigurationId: Specific test configuration used
            - ProjectId/ProjectGuid: Project the test run belongs to
            - ArtifactTypeId: Type of artifact (5 for test runs)
            - ConcurrencyDate: Timestamp for optimistic concurrency control
            - CustomProperties: List of custom fields for this test run
            - Tags: Meta-tags associated with the test run
            - IsAttachments: Whether the test run has attachments
            - Guid: Unique global identifier for the test run

        When to Use:
            - Getting test run list for a specific product
            - Retrieving test runs with server-side pagination
            - Sorting test runs by specific fields (e.g., EndDate)
            - Analyzing product-level test execution data
            - Reviewing recent test results

        Related Tools:
            - format_artifacts_as_markdown: Format filtered/processed
                results for display
            - get_test_cases: Get test cases in a product
            - get_test_sets: Get test sets in a product

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
            # Get first 100 test runs from product 55
            test_runs_json = get_test_runs(product_id=55)
            test_runs = json.loads(test_runs_json)

            # Get next page of test runs
            test_runs_json = get_test_runs(
                product_id=55, starting_row=101, number_of_rows=100
            )

            # Get test runs sorted by end date (most recent first)
            test_runs_json = get_test_runs(
                product_id=55,
                sort_field="EndDate",
                sort_direction="DESC"
            )

            # Process and filter results
            test_runs = json.loads(test_runs_json)
            failed_runs = [
                tr for tr in test_runs["data"]
                if tr["ExecutionStatusId"] == 1
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

            # Get Spira client and retrieve test runs
            spira_client = get_spira_client()
            return _get_test_runs_impl(
                spira_client,
                product_id,
                starting_row,
                number_of_rows,
                sort_field,
                sort_direction,
            )
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve test runs",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
