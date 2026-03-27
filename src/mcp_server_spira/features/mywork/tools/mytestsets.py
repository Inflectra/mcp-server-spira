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


async def _get_my_testsets_impl(spira_client, limit: int, offset: int) -> str:
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
        # Validate pagination parameters
        validation_error = ParameterValidator.validate_pagination_params(limit, offset)
        if validation_error:
            return format_error_response(**validation_error)

        # Get the list of open testsets for the current user
        testsets_url = "test-sets"
        all_testsets = await spira_client.make_spira_api_get_request(testsets_url)

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

    @mcp.tool(
        name="my_get_test_sets",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    )
    async def get_my_testsets(limit: int = 25, offset: int = 0) -> str:
        """
        Retrieves test sets assigned to the current user.

        Maps to Spira API: GET /test-sets

        Use this for personal test set lists, test execution planning, or test suite management.
        **Pagination:** Client-side (API returns all, sliced in Python).

        Args:
            limit: Maximum number of test sets to return (1-500, default: 25)
            offset: Number of test sets to skip (>= 0, default: 0)

        Returns:
            JSON string with structure: {"data": [test set objects], "pagination": {...}}
            Full response structure documented in API.

        Call system_get_artifact_schema(artifact_type='test_set') to see available fields.

        Related Tools:
            - format_artifacts_as_markdown: Format filtered/processed results for display

        Error Responses:
            Returns structured JSON with error, error_code, details, and suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            # Simple display - LLM formats naturally
            testsets_json = get_my_testsets()

            # Pagination - Get next page
            testsets_json = get_my_testsets(limit=25, offset=25)
        """
        try:
            # Validate pagination parameters
            validation_error = ParameterValidator.validate_pagination_params(limit, offset)
            if validation_error:
                return format_error_response(**validation_error)

            # Get Spira client
            spira_client = get_spira_client()

            # Run blocking HTTP call in a thread to avoid blocking the event loop
            return await _get_my_testsets_impl(spira_client, limit, offset)

        except Exception as e:
            return format_error_response(
                error="Failed to retrieve test sets",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
