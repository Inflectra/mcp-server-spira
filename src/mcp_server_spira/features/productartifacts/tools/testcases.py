"""
Provides operations for working with the Spira product test cases

This module provides MCP tools for retrieving and updating product test cases
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _get_test_cases_impl(
    spira_client,
    product_id: int,
    starting_row: int = 1,
    number_of_rows: int = 100,
    sort_field: str = "",
    sort_direction: str = "ASC",
) -> str:
    """
    Implementation of retrieving the list of test cases in the specified
    product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product.
            If the ID is PR:45, just use 45.
        starting_row: The starting row number for pagination (1-based
            index)
        number_of_rows: The number of rows to return
        sort_field: The field to sort by (optional)
        sort_direction: The sort direction - "ASC" or "DESC"

    Returns:
        JSON string containing the list of test cases with data structure
    """
    try:
        # Build the search endpoint URL with query parameters
        test_cases_url = (
            f"projects/{product_id}/test-cases/search?"
            f"starting_row={starting_row}&number_of_rows={number_of_rows}"
        )

        # Add optional sort parameters if provided
        if sort_field:
            test_cases_url += f"&sort_field={sort_field}&sort_direction={sort_direction}"

        # Make POST request with empty filter array (no filtering)
        test_cases = spira_client.make_spira_api_post_request(test_cases_url, [])

        # Return JSON response with data structure
        return format_success_response(data=test_cases)

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve test cases",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e), "product_id": product_id},
            suggestion=("Check API connectivity, authentication, and that the product_id is valid"),
        )


def register_tools(mcp) -> None:
    """
    Register product test cases tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_test_cases(
        product_id: int,
        starting_row: int = 1,
        number_of_rows: int = 100,
        sort_field: str = "",
        sort_direction: str = "ASC",
    ) -> str:
        """
        Retrieves a list of the test cases in the specified product

        Maps to Spira API: POST /projects/{product_id}/test-cases/search

        This tool returns test cases from the specified product using
        server-side pagination. Use this for retrieving product-level
        test case lists with filtering and sorting capabilities.

        **API Endpoint**: POST /projects/{product_id}/test-cases/search
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
            sort_field: The field to sort by (optional, e.g., "TestCaseId",
                "Name", "TestCaseStatusName")
            sort_direction: The sort direction - "ASC" or "DESC"
                (default: "ASC")

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
                ]
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
            - Getting test case list for a specific product
            - Retrieving test cases with server-side pagination
            - Sorting test cases by specific fields
            - Analyzing product-level test case data

        Related Tools:
            - get_my_testcases: Get test cases assigned to current user
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
            # Get first 100 test cases from product 55
            test_cases_json = get_test_cases(product_id=55)
            test_cases = json.loads(test_cases_json)

            # Get next page of test cases
            test_cases_json = get_test_cases(
                product_id=55, starting_row=101, number_of_rows=100
            )

            # Get test cases sorted by priority
            test_cases_json = get_test_cases(
                product_id=55,
                sort_field="TestCasePriorityId",
                sort_direction="ASC"
            )

            # Process and filter results
            test_cases = json.loads(test_cases_json)
            failed_tests = [
                tc for tc in test_cases["data"]
                if tc["ExecutionStatusName"] == "Failed"
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

            # Get Spira client and retrieve test cases
            spira_client = get_spira_client()
            return _get_test_cases_impl(
                spira_client,
                product_id,
                starting_row,
                number_of_rows,
                sort_field,
                sort_direction,
            )
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve test cases",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
