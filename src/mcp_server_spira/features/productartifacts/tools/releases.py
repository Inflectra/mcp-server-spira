"""
Provides operations for working with the Spira product releases

This module provides MCP tools for retrieving and updating product releases
"""

from mcp_server_spira.config import resolve_product_id
from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _get_releases_impl(
    spira_client,
    product_id: int,
    start_row: int = 1,
    number_rows: int = 100,
) -> str:
    """
    Implementation of retrieving the list of releases in the specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product.
            If the ID is PR:45, just use 45.
        start_row: The starting row number for pagination (1-based index)
        number_rows: The number of rows to return

    Returns:
        JSON string containing the list of releases with data structure
    """
    try:
        # Build the search endpoint URL with query parameters
        releases_url = (
            f"projects/{product_id}/releases/search?start_row={start_row}&number_rows={number_rows}"
        )

        # Make POST request with empty filter array (no filtering for now)
        releases = spira_client.make_spira_api_post_request(releases_url, [])

        # Return JSON response with data structure
        return format_success_response(data=releases)

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve releases",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e), "product_id": product_id},
            suggestion=("Check API connectivity, authentication, and that the product_id is valid"),
        )


def _get_release_by_id_impl(spira_client, product_id: int, release_id: int) -> str:
    """
    Implementation of retrieving a single release in the specified
    product with the specified ID

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product.
            If the ID is PR:45, just use 45.
        release_id: The numeric ID of the release.
            If the ID is RL:12, just use 12.

    Returns:
        JSON string containing the details of the release
    """
    try:
        # Get the release in the product
        release_url = f"projects/{product_id}/releases/{release_id}"
        release = spira_client.make_spira_api_get_request(release_url)

        # Return JSON response with data structure (single item as array)
        return format_success_response(data=[release])

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve release",
            error_code=ErrorCodes.API_ERROR,
            details={
                "message": str(e),
                "product_id": product_id,
                "release_id": release_id,
            },
            suggestion=(
                "Check API connectivity, authentication, and that "
                "the product_id and release_id are valid"
            ),
        )


def register_tools(mcp) -> None:
    """
    Register product releases tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool(
        name="product_get_releases",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    )
    def get_releases(
        product_id: int | None = None,
        start_row: int = 1,
        number_rows: int = 100,
    ) -> str:
        """
        Retrieves a list of the releases in the specified product

        Maps to Spira API: POST /projects/{product_id}/releases/search

        This tool returns releases from the specified product using
        server-side pagination. Use this for retrieving product-level
        release lists with filtering and sorting capabilities.

        Args:
            product_id: The numeric ID of the product. If the ID is PR:45,
                just use 45. If omitted, uses SPIRA_PROJECT_ID from
                environment.
            start_row: The starting row number for pagination
                (default: 1, 1-based index)
            number_rows: The number of rows to return (default: 100)

        Returns:
            JSON string with structure: {"data": [release objects]}
            Call system_get_artifact_schema(artifact_type='release') to see available fields.
        Related Tools:
            - get_release_by_id: Get single release with full details
            - format_artifacts_as_markdown: Format filtered/processed results for display
        Error Responses:
            Returns structured JSON with error, error_code, details, and suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND
        Example Usage:
            releases_json = get_releases(product_id=55)

            # Get next page
            releases_json = get_releases(product_id=55, start_row=101, number_rows=100)
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

            # Validate start_row
            validation_error = ParameterValidator.validate_positive_integer(
                start_row, "start_row", min_value=1
            )
            if validation_error:
                return format_error_response(**validation_error)

            # Validate number_rows
            validation_error = ParameterValidator.validate_positive_integer(
                number_rows, "number_rows", min_value=1
            )
            if validation_error:
                return format_error_response(**validation_error)

            # Get Spira client and retrieve releases
            spira_client = get_spira_client()
            return _get_releases_impl(
                spira_client,
                product_id,
                start_row,
                number_rows,
            )
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve releases",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )

    @mcp.tool(
        name="product_get_release_by_id",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    )
    def get_release_by_id(
        product_id: int | None = None,
        release_id: int = 0,
    ) -> str:
        """
        Retrieves the details of a single release in the specified product

        Maps to Spira API: GET /projects/{product_id}/releases/{release_id}

        Use this tool when you need to view the details of a single release
        in the specified product.

        Args:
            product_id: The numeric ID of the product. If the ID is PR:45,
                just use 45. If omitted, uses SPIRA_PROJECT_ID from
                environment.
            release_id: The numeric ID of the release.
                If the ID is RL:12, just use 12.

        Returns:
            JSON string with structure: {"data": [release object]}
            Call system_get_artifact_schema(artifact_type='release') to see available fields.
            Full response structure documented in API.

        Related Tools:
            - get_releases: Get list of releases for a product
            - format_artifacts_as_markdown: Format for display

        Error Responses:
            Returns structured JSON with error, error_code, details, and suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            release_json = get_release_by_id(product_id=55, release_id=10)
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

            # Validate release_id
            validation_error = ParameterValidator.validate_positive_integer(
                release_id, "release_id", min_value=1
            )
            if validation_error:
                return format_error_response(**validation_error)

            # Get Spira client and retrieve release
            spira_client = get_spira_client()
            return _get_release_by_id_impl(spira_client, product_id, release_id)
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve release",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
