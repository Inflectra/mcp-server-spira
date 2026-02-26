"""
Provides operations for working with the Spira product incidents

This module provides MCP tools for retrieving and updating product incidents
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _get_incidents_impl(
    spira_client,
    product_id: int,
    start_row: int = 1,
    number_rows: int = 100,
    sort_by: str = "",
) -> str:
    """
    Implementation of retrieving the list of incidents in the specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product.
            If the ID is PR:45, just use 45.
        start_row: The starting row number for pagination (1-based index)
        number_rows: The number of rows to return
        sort_by: The field to sort by (optional)

    Returns:
        JSON string containing the list of incidents with data structure
    """
    try:
        # Build the search endpoint URL with query parameters
        incidents_url = (
            f"projects/{product_id}/incidents/search?"
            f"start_row={start_row}&number_rows={number_rows}"
        )

        # Add optional sort parameter if provided
        if sort_by:
            incidents_url += f"&sort_by={sort_by}"

        # Make POST request with empty filter array (no filtering for now)
        incidents = spira_client.make_spira_api_post_request(incidents_url, [])

        # Return JSON response with data structure
        return format_success_response(data=incidents)

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve incidents",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e), "product_id": product_id},
            suggestion=("Check API connectivity, authentication, and that the product_id is valid"),
        )


def register_tools(mcp) -> None:
    """
    Register product incidents tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool(
        name="product_get_incidents",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    )
    def get_incidents(
        product_id: int,
        start_row: int = 1,
        number_rows: int = 100,
        sort_by: str = "",
    ) -> str:
        """
        Retrieves a list of the incidents in the specified product

        Maps to Spira API: POST /projects/{product_id}/incidents/search

        This tool returns incidents from the specified product using
        server-side pagination. Use this for retrieving product-level
        incident lists with filtering and sorting capabilities.

        Args:
            product_id: The numeric ID of the product.
                If the ID is PR:45, just use 45.
            start_row: The starting row number for pagination
                (default: 1, 1-based index)
            number_rows: The number of rows to return (default: 100)
            sort_by: The field to sort by (optional, e.g., "IncidentId",
                "Name", "IncidentStatusName")

        Returns:
            JSON string with structure: {"data": [incident objects]}
            See Key Fields section below for important incident fields.
        Key Fields:
            - IncidentId: Unique identifier for the incident
            - Name: The name/title of the incident
            - IncidentStatusId/IncidentStatusName: Current status
            - PriorityId/PriorityName: Priority level (1-Critical to 5-Low)
            - SeverityId/SeverityName: Severity level (1-Critical to 4-Low)
            - OwnerId/OwnerName: User the incident is assigned to
            - DetectedReleaseId/DetectedReleaseVersionNumber: Release where found
            - ResolvedReleaseId/ResolvedReleaseVersionNumber: Release where fixed
            - ClosedDate: When closed (null if still open)
            - ProjectId/ProjectName: Project the incident belongs to

            Additional fields available: Description, IncidentTypeId/IncidentTypeName, OpenerId/OpenerName, EstimatedEffort, ActualEffort, RemainingEffort, ProjectedEffort, CompletionPercent, StartDate, EndDate, CreationDate, LastUpdateDate, VerifiedReleaseId/VerifiedReleaseVersionNumber, DetectedBuildId/DetectedBuildName, FixedBuildId/FixedBuildName, ComponentIds, TestRunStepIds, CustomProperties, Tags, IsAttachments, Guid
        Related Tools:
            - get_my_incidents: Get incidents assigned to current user (with client-side pagination)
            - format_artifacts_as_markdown: Format filtered/processed results for display
        Error Responses:
            Returns structured JSON with error, error_code, details, and suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND
        Example Usage:
            incidents_json = get_incidents(product_id=55)

            # Get incidents sorted by priority
            incidents_json = get_incidents(product_id=55, sort_by="PriorityId")
        """
        try:
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

            # Get Spira client and retrieve incidents
            spira_client = get_spira_client()
            return _get_incidents_impl(
                spira_client,
                product_id,
                start_row,
                number_rows,
                sort_by,
            )
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve incidents",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
