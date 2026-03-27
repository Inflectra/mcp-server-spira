"""
Provides operations for working with the Spira product test runs

This module provides MCP tools for retrieving and updating product test runs
"""

from mcp_server_spira.config import resolve_product_id
from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


async def _get_test_runs_impl(
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
        test_runs = await spira_client.make_spira_api_post_request(test_runs_url, [])

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

    @mcp.tool(
        name="product_get_test_runs",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    )
    async def get_test_runs(
        product_id: int | None = None,
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
        Test runs do not include test run steps in this response.

        Args:
            product_id: The numeric ID of the product. If the ID is PR:45,
                just use 45. If omitted, uses SPIRA_PROJECT_ID from
                environment.
            starting_row: The starting row number for pagination
                (default: 1, 1-based index)
            number_of_rows: The number of rows to return (default: 100)
            sort_field: The field to sort by (optional, e.g., "TestRunId",
                "Name", "ExecutionStatusId", "EndDate")
            sort_direction: The sort direction - "ASC" or "DESC"
                (default: "DESC")

        Returns:
            JSON string with structure: {"data": [test run objects]}
            Call system_get_artifact_schema(artifact_type='test_run') to see available fields.
        Related Tools:
            - format_artifacts_as_markdown: Format filtered/processed results for display
            - get_test_cases: Get test cases in a product
            - get_test_sets: Get test sets in a product
        Error Responses:
            Returns structured JSON with error, error_code, details, and suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND
        Example Usage:
            test_runs_json = get_test_runs(product_id=55)

            # Get test runs sorted by end date (most recent first)
            test_runs_json = get_test_runs(product_id=55, sort_field="EndDate", sort_direction="DESC")
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

            # Get Spira client and retrieve test runs
            spira_client = get_spira_client()
            return await _get_test_runs_impl(
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
