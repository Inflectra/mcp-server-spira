"""
Provides operations for working with the Spira product requirements

This module provides MCP tools for retrieving and updating product requirements
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _get_requirements_impl(
    spira_client,
    product_id: int,
    starting_row: int = 1,
    number_of_rows: int = 100,
) -> str:
    """
    Implementation of retrieving the list of requirements in the
    specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product.
            If the ID is PR:45, just use 45.
        starting_row: The starting row number for pagination
            (1-based index)
        number_of_rows: The number of rows to return

    Returns:
        JSON string containing the list of requirements with
        data structure
    """
    try:
        # Build the search endpoint URL with query parameters
        requirements_url = (
            f"projects/{product_id}/requirements/search?"
            f"starting_row={starting_row}&number_of_rows={number_of_rows}"
        )

        # Make POST request with empty filter array (no filtering for now)
        requirements = spira_client.make_spira_api_post_request(requirements_url, [])

        # Return JSON response with data structure
        return format_success_response(data=requirements)

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve requirements",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e), "product_id": product_id},
            suggestion=("Check API connectivity, authentication, and that the product_id is valid"),
        )


def register_tools(mcp) -> None:
    """
    Register product requirements tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_requirements(
        product_id: int,
        starting_row: int = 1,
        number_of_rows: int = 100,
    ) -> str:
        """
        Retrieves a list of the requirements in the specified product

        Maps to Spira API: POST /projects/{product_id}/requirements/search

        This tool returns requirements from the specified product using
        server-side pagination. Use this for retrieving product-level
        requirement lists with filtering and sorting capabilities.

        Args:
            product_id: The numeric ID of the product.
                If the ID is PR:45, just use 45.
            starting_row: The starting row number for pagination
                (default: 1, 1-based index)
            number_of_rows: The number of rows to return (default: 100)

        Returns:
            JSON string with structure: {"data": [requirement objects]}
            See Key Fields section below for important requirement fields.
        Key Fields:
            - RequirementId: Unique identifier for the requirement
            - Name: The name of the requirement
            - StatusId/StatusName: Current status
            - ImportanceId/ImportanceName: Priority/importance level
            - OwnerId/OwnerName: User the requirement is assigned to
            - EstimatePoints: Story points estimate
            - TaskCount: Number of associated tasks
            - CoverageCountTotal: Total test cases covering this requirement
            - PercentComplete: Percentage complete
            - ReleaseId/ReleaseVersionNumber: Sprint/iteration assignment

            Additional fields available: Description, RequirementTypeId/RequirementTypeName, AuthorId/AuthorName, EstimatedEffort, TaskEstimatedEffort, TaskActualEffort, CoverageCountPassed/Failed/Caution/Blocked, StartDate, EndDate, CreationDate, LastUpdateDate, ComponentId, Summary, IsSuspect, CustomProperties, Tags, IsAttachments
        Related Tools:
            - get_my_requirements: Get requirements assigned to current user (with client-side pagination)
            - format_artifacts_as_markdown: Format filtered/processed results for display
        Error Responses:
            Returns structured JSON with error, error_code, details, and suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND
        Example Usage:
            requirements_json = get_requirements(product_id=55)

            # Get next page
            requirements_json = get_requirements(product_id=55, starting_row=101, number_of_rows=100)
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

            # Get Spira client and retrieve requirements
            spira_client = get_spira_client()
            return _get_requirements_impl(
                spira_client,
                product_id,
                starting_row,
                number_of_rows,
            )
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve requirements",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
