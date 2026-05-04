"""
Provides operations for recording automated test run results into Spira

This module provides MCP tools for recording the results of automated
test against a matching test case in Spira
"""

import datetime

from mcp_server_spira.config import resolve_product_id
from mcp_server_spira.utils.common import get_spira_client
from mcp_server_spira.utils.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.utils.common.validation import ParameterValidator


async def _record_automated_test_run_impl(
    spira_client,
    product_id: int,
    test_name: str,
    short_message: str,
    long_message: str,
    error_count: int,
    test_case_id: int,
    execution_status_id: int,
) -> str:
    """
    Records an automated test result in Spira

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PG:45, just use 45.
        test_name: The name of the test being run
        short_message: A short description (50 characters or less) of the result of the test execution
        long_message: The full description of the testing outcome, in plain text format
        error_count: The number of errors that happened during the test (0 if none)
        test_case_id: The ID of the test case in Spira being executed, without the TC prefix (e.g. TC:12 would be 12)
        execution_status_id: The ID of the execution status of the test (1 = Failed, 2 = Passed, 3 = Not Run, 4 = N/A, 5 = Blocked and 6 = Caution)

    Returns:
        JSON string with structure:
        {
            "test_run_id": "TR:123",
            "message": "Test run recorded successfully"
        }
    """
    # Validate product_id
    validation_error = ParameterValidator.validate_positive_integer(product_id, "product_id")
    if validation_error:
        return format_error_response(
            error=validation_error["error"],
            error_code=ErrorCodes.INVALID_PARAMETER,
            details=validation_error.get("details", {}),
        )

    # Validate test_case_id
    validation_error = ParameterValidator.validate_positive_integer(test_case_id, "test_case_id")
    if validation_error:
        return format_error_response(
            error=validation_error["error"],
            error_code=ErrorCodes.INVALID_PARAMETER,
            details=validation_error.get("details", {}),
        )

    # Validate error_count (must be non-negative)
    if error_count < 0:
        return format_error_response(
            error="error_count must be non-negative",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "parameter": "error_count",
                "value": error_count,
                "expected": ">= 0",
            },
            suggestion="Use error_count >= 0",
        )

    # Validate execution_status_id (must be 1-6)
    if execution_status_id < 1 or execution_status_id > 6:
        return format_error_response(
            error="execution_status_id must be between 1 and 6",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "parameter": "execution_status_id",
                "value": execution_status_id,
                "expected": "1-6 (1=Failed, 2=Passed, 3=Not Run, 4=N/A, 5=Blocked, 6=Caution)",
            },
            suggestion="Use execution_status_id between 1 and 6",
        )

    # Validate required string parameters
    if not test_name or not test_name.strip():
        return format_error_response(
            error="test_name is required and cannot be empty",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={"parameter": "test_name"},
            suggestion="Provide a non-empty test_name",
        )

    if not short_message or not short_message.strip():
        return format_error_response(
            error="short_message is required and cannot be empty",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={"parameter": "short_message"},
            suggestion="Provide a non-empty short_message",
        )

    try:
        # Make the start/end time right now
        start_time = datetime.datetime.now()
        end_time = datetime.datetime.now()

        # The body we are sending
        body = {
            # Constant for plain text
            "TestRunFormatId": 1,
            "StartDate": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "EndDate": end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "RunnerName": "MCP Server",
            "RunnerTestName": test_name,
            "RunnerMessage": short_message,
            "RunnerStackTrace": long_message,
            "RunnerAssertCount": error_count,
            "TestCaseId": test_case_id,
            "ExecutionStatusId": execution_status_id,
        }

        # Record the test run using the API method
        record_automated_url = f"projects/{product_id}/test-runs/record"
        testrun = await spira_client.make_spira_api_post_request(record_automated_url, body)

        if not testrun:
            return format_error_response(
                error="Test run was not recorded successfully",
                error_code=ErrorCodes.API_ERROR,
                details={"product_id": product_id, "test_case_id": test_case_id},
                suggestion="Verify product_id and test_case_id are valid",
            )

        # Extract the new test run ID
        test_run_id = testrun.get("TestRunId")
        if not test_run_id:
            return format_error_response(
                error="Test run created but ID not returned",
                error_code=ErrorCodes.API_ERROR,
                details={"response": testrun},
            )

        return format_success_response(
            {
                "test_run_id": f"TR:{test_run_id}",
                "message": "Test run recorded successfully",
            }
        )
    except Exception as e:
        return format_error_response(
            error=f"Failed to record test run: {str(e)}",
            error_code=ErrorCodes.API_ERROR,
            details={
                "product_id": product_id,
                "test_case_id": test_case_id,
                "exception": str(e),
            },
        )


def register_tools(mcp) -> None:
    """
    Register tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool(
        name="product_create_automated_test_run",
        annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": True},
    )
    async def record_automated_test_run(
        test_name: str,
        short_message: str,
        long_message: str,
        error_count: int,
        test_case_id: int,
        execution_status_id: int,
        product_id: int | None = None,
    ) -> str:
        """
        Records an automated test result in Spira.

        Maps to Spira API: POST /projects/{product_id}/test-runs/record

        Use this to push automated test results from CI/CD pipelines into Spira for quality tracking.

        Args:
            product_id: The numeric ID of the product (e.g., 55 for PR:55). If omitted, uses SPIRA_PROJECT_ID from environment.
            test_name: The name of the test being run
            short_message: Brief result description (50 chars or less)
            long_message: Full test outcome description in plain text
            error_count: Number of errors during test (0 if none)
            test_case_id: Test case ID without TC prefix (e.g., 12 for TC:12)
            execution_status_id: Status (1=Failed, 2=Passed, 3=Not Run, 4=N/A, 5=Blocked, 6=Caution)

        Returns:
            JSON: {"test_run_id": "TR:123", "message": "Test run recorded successfully"}

        Error Responses:
            Returns structured JSON with error, error_code, details, and suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            result = record_automated_test_run(
                product_id=55, test_name="test_login", short_message="Passed",
                long_message="Login successful", error_count=0, test_case_id=123, execution_status_id=2
            )
        """
        try:
            # Resolve product_id from explicit arg or SPIRA_PROJECT_ID env var
            resolved_id = resolve_product_id(product_id)
            if resolved_id is None:
                return format_error_response(
                    error="product_id is required",
                    error_code=ErrorCodes.INVALID_PARAMETER,
                    details={"parameter": "product_id"},
                    suggestion="Pass product_id explicitly or set SPIRA_PROJECT_ID in your environment",
                )
            product_id = resolved_id
            spira_client = get_spira_client()
            return await _record_automated_test_run_impl(
                spira_client,
                product_id,
                test_name,
                short_message,
                long_message,
                error_count,
                test_case_id,
                execution_status_id,
            )
        except Exception as e:
            return format_error_response(
                error=f"Unexpected error: {str(e)}",
                error_code=ErrorCodes.API_ERROR,
                details={"exception": str(e)},
            )
