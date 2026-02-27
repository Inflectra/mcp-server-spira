"""
Provides operations for working with the Spira incidents I have been assigned

This module provides MCP tools for retrieving and updating my assigned
incidents.
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.pagination import paginate_client_side
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _get_my_incidents_impl(spira_client, limit: int, offset: int) -> str:
    """
    Implementation of retrieving my assigned Spira incidents.

    Args:
        spira_client: The Inflectra Spira API client instance
        limit: Maximum number of incidents to return
        offset: Number of incidents to skip

    Returns:
        JSON string with paginated incident data
    """
    try:
        # Validate pagination parameters
        validation_error = ParameterValidator.validate_pagination_params(limit, offset)
        if validation_error:
            return format_error_response(**validation_error)

        # Get the list of open incidents for the current user
        incidents_url = "incidents"
        all_incidents = spira_client.make_spira_api_get_request(incidents_url)

        # Handle empty results
        if not all_incidents:
            all_incidents = []

        # Apply client-side pagination
        result = paginate_client_side(all_incidents, limit, offset)

        # Return formatted JSON response
        return format_success_response(data=result["data"], pagination=dict(result["pagination"]))

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve incidents",
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
        name="my_get_incidents",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    )
    def get_my_incidents(limit: int = 25, offset: int = 0) -> str:
        """
        Retrieves incidents assigned to the current user.

        Maps to Spira API: GET /incidents

        Use this for personal incident lists, bug tracking, or issue management.
        **Pagination:** Client-side (API returns all, sliced in Python).

        Args:
            limit: Maximum number of incidents to return (1-500, default: 25)
            offset: Number of incidents to skip (>= 0, default: 0)

        Returns:
            JSON string with structure: {"data": [incident objects], "pagination": {...}}
            Full response structure documented in API.

        Call system_get_artifact_schema(artifact_type='incident') to see available fields.

        Related Tools:
            - format_artifacts_as_markdown: Format filtered/processed results for display

        Error Responses:
            Returns structured JSON with error, error_code, details, and suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            # Simple display - LLM formats naturally
            incidents_json = get_my_incidents()

            # Pagination - Get next page
            incidents_json = get_my_incidents(limit=25, offset=25)
        """
        try:
            # Validate pagination parameters
            validation_error = ParameterValidator.validate_pagination_params(limit, offset)
            if validation_error:
                return format_error_response(**validation_error)

            # Get Spira client
            spira_client = get_spira_client()

            # Retrieve and paginate incidents
            return _get_my_incidents_impl(spira_client, limit, offset)

        except Exception as e:
            return format_error_response(
                error="Failed to retrieve incidents",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
