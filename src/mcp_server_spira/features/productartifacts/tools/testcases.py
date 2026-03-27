"""
Provides operations for working with the Spira product test cases

This module provides MCP tools for retrieving and updating product test cases
"""

from mcp_server_spira.config import resolve_product_id
from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


async def _get_test_cases_impl(
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
        test_cases = await spira_client.make_spira_api_post_request(test_cases_url, [])

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

    @mcp.tool(
        name="product_get_test_cases",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    )
    async def get_test_cases(
        product_id: int | None = None,
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

        Args:
            product_id: The numeric ID of the product. If the ID is PR:45,
                just use 45. If omitted, uses SPIRA_PROJECT_ID from
                environment.
            starting_row: The starting row number for pagination
                (default: 1, 1-based index)
            number_of_rows: The number of rows to return (default: 100)
            sort_field: The field to sort by (optional, e.g., "TestCaseId",
                "Name", "TestCaseStatusName")
            sort_direction: The sort direction - "ASC" or "DESC"
                (default: "ASC")

        Returns:
            JSON string with structure: {"data": [test case objects]}
            Call system_get_artifact_schema(artifact_type='test_case') to see available fields.
        Related Tools:
            - get_my_testcases: Get test cases assigned to current user (with client-side pagination)
            - format_artifacts_as_markdown: Format filtered/processed results for display
        Error Responses:
            Returns structured JSON with error, error_code, details, and suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND
        Example Usage:
            test_cases_json = get_test_cases(product_id=55)

            # Get test cases sorted by priority
            test_cases_json = get_test_cases(product_id=55, sort_field="TestCasePriorityId")
        """
        try:
            # Resolve product_id from explicit arg or SPIRA_PROJECT_ID env var
            resolved_id = resolve_product_id(product_id)
            if resolved_id is None:
                return format_error_response(
                    error="product_id is required",
                    error_code=ErrorCodes.INVALID_PARAMETER,
                    details={"parameter": "product_id"},
                    suggestion=(
                        "Pass product_id explicitly or set SPIRA_PROJECT_ID in your environment"
                    ),
                )
            product_id = resolved_id

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
            return await _get_test_cases_impl(
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
