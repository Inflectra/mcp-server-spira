"""
Provides operations for working with the Spira product risks

This module provides MCP tools for retrieving and updating product risks
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _get_risks_impl(
    spira_client,
    product_id: int,
    starting_row: int = 1,
    number_of_rows: int = 100,
    sort_field: str = "",
    sort_direction: str = "DESC",
) -> str:
    """
    Implementation of retrieving the list of risks in the specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product.
            If the ID is PR:45, just use 45.
        starting_row: The starting row number for pagination (1-based index)
        number_of_rows: The number of rows to return
        sort_field: The field to sort by (optional)
        sort_direction: The sort direction - "ASC" or "DESC"

    Returns:
        JSON string containing the list of risks with data structure
    """
    try:
        # Build the search endpoint URL with query parameters
        risks_url = (
            f"projects/{product_id}/risks/search?"
            f"starting_row={starting_row}&number_of_rows={number_of_rows}"
        )

        # Add optional sort parameters if provided
        if sort_field:
            risks_url += f"&sort_field={sort_field}&sort_direction={sort_direction}"

        # Make POST request with empty filter array (no filtering for now)
        risks = spira_client.make_spira_api_post_request(risks_url, [])

        # Return JSON response with data structure
        return format_success_response(data=risks)

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve risks",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e), "product_id": product_id},
            suggestion=("Check API connectivity, authentication, and that the product_id is valid"),
        )


def register_tools(mcp) -> None:
    """
    Register product risks tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_risks(
        product_id: int,
        starting_row: int = 1,
        number_of_rows: int = 100,
        sort_field: str = "",
        sort_direction: str = "DESC",
    ) -> str:
        """
        Retrieves a list of the risks in the specified product

        Maps to Spira API: POST /projects/{product_id}/risks/search

        This tool returns risks from the specified product using
        server-side pagination. Use this for retrieving product-level
        risk lists with filtering and sorting capabilities.

        **API Endpoint**: POST /projects/{product_id}/risks/search
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
            sort_field: The field to sort by (optional, e.g., "RiskId",
                "Name", "RiskStatusId", "RiskProbability")
            sort_direction: The sort direction - "ASC" or "DESC"
                (default: "DESC")

        Returns:
            JSON string with structure:
            {
                "data": [
                    {
                        "RiskId": 123,
                        "Name": "Database Performance Risk",
                        "Description": "Risk of database performance degradation",
                        "RiskStatusId": 2,
                        "RiskStatusName": "Open",
                        "RiskTypeId": 1,
                        "RiskTypeName": "Technical",
                        "RiskProbability": 3,
                        "RiskImpact": 4,
                        "RiskExposure": 12,
                        "OwnerId": 5,
                        "OwnerName": "John Doe",
                        "CreationDate": "2024-01-10T08:00:00Z",
                        "LastUpdateDate": "2024-01-15T14:30:00Z",
                        "ClosedDate": null,
                        "RiskMitigations": [],
                        "ProjectId": 55,
                        "ProjectName": "Web Application",
                        "ComponentId": 3,
                        "ArtifactTypeId": 14,
                        "ConcurrencyDate": "2024-01-15T14:30:00Z",
                        "CustomProperties": [],
                        "Tags": "performance,database",
                        "IsAttachments": false
                    }
                ]
            }

        Key Fields:
            - RiskId: Unique identifier for the risk
            - Name: The name of the risk
            - Description: Detailed description of the risk
            - RiskStatusId/RiskStatusName: Current status of the risk
            - RiskTypeId/RiskTypeName: Type of risk
            - RiskProbability: Probability rating (1-5, 1=Very Low, 5=Very High)
            - RiskImpact: Impact rating (1-5, 1=Very Low, 5=Very High)
            - RiskExposure: Calculated exposure (Probability × Impact)
            - OwnerId/OwnerName: User responsible for the risk
            - CreationDate: When the risk was created
            - LastUpdateDate: When the risk was last modified
            - ClosedDate: When the risk was closed (null if still open)
            - RiskMitigations: List of mitigation strategies
            - ProjectId/ProjectName: Project the risk belongs to
            - ComponentId: Component the risk is associated with
            - ArtifactTypeId: Type of artifact (14 for risks)
            - ConcurrencyDate: Timestamp for optimistic concurrency control
            - CustomProperties: List of custom fields for this risk
            - Tags: Meta-tags associated with the risk
            - IsAttachments: Whether the risk has attachments

        When to Use:
            - Getting risk list for a specific product
            - Retrieving risks with server-side pagination
            - Sorting risks by specific fields (e.g., RiskExposure)
            - Analyzing product-level risk management
            - Reviewing high-priority risks

        Related Tools:
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
            # Get first 100 risks from product 55
            risks_json = get_risks(product_id=55)
            risks = json.loads(risks_json)

            # Get next page of risks
            risks_json = get_risks(
                product_id=55, starting_row=101, number_of_rows=100
            )

            # Get risks sorted by exposure (highest first)
            risks_json = get_risks(
                product_id=55,
                sort_field="RiskExposure",
                sort_direction="DESC"
            )

            # Process and filter results
            risks = json.loads(risks_json)
            high_exposure_risks = [
                r for r in risks["data"]
                if r["RiskExposure"] >= 15
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

            # Get Spira client and retrieve risks
            spira_client = get_spira_client()
            return _get_risks_impl(
                spira_client,
                product_id,
                starting_row,
                number_of_rows,
                sort_field,
                sort_direction,
            )
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve risks",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
