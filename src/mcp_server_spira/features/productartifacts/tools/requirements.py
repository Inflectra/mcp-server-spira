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

        **API Endpoint**: POST /projects/{product_id}/requirements/search
        **Query Parameters**: starting_row, number_of_rows
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

        Returns:
            JSON string with structure:
            {
                "data": [
                    {
                        "RequirementId": 123,
                        "Name": "User Authentication",
                        "Description": "Implement secure user login system",
                        "StatusId": 2,
                        "StatusName": "In Progress",
                        "RequirementTypeId": 1,
                        "RequirementTypeName": "Feature",
                        "ImportanceId": 1,
                        "ImportanceName": "Critical",
                        "OwnerId": 5,
                        "OwnerName": "John Doe",
                        "AuthorId": 4,
                        "AuthorName": "Jane Smith",
                        "EstimatePoints": 8.0,
                        "EstimatedEffort": 480,
                        "TaskEstimatedEffort": 450,
                        "TaskActualEffort": 240,
                        "TaskCount": 5,
                        "PercentComplete": 50,
                        "CoverageCountTotal": 10,
                        "CoverageCountPassed": 6,
                        "CoverageCountFailed": 2,
                        "CoverageCountCaution": 1,
                        "CoverageCountBlocked": 1,
                        "StartDate": "2024-01-15T09:00:00Z",
                        "EndDate": "2024-01-30T17:00:00Z",
                        "CreationDate": "2024-01-10T08:00:00Z",
                        "LastUpdateDate": "2024-01-20T14:30:00Z",
                        "ReleaseId": 10,
                        "ReleaseVersionNumber": "1.5.0",
                        "ProjectId": 55,
                        "ProjectName": "Web Application",
                        "ComponentId": 3,
                        "Summary": false,
                        "IsSuspect": false,
                        "CustomProperties": [],
                        "Tags": "security,authentication",
                        "IsAttachments": true
                    }
                ]
            }

        Key Fields:
            - RequirementId: Unique identifier for the requirement
            - Name: The name of the requirement
            - Description: The detailed description of the requirement
            - StatusId/StatusName: Current status of the requirement
            - RequirementTypeId/RequirementTypeName: Type of requirement
                (Feature, Use Case, etc.)
            - ImportanceId/ImportanceName: Priority/importance level
            - OwnerId/OwnerName: User the requirement is assigned to
            - AuthorId/AuthorName: User who created the requirement
            - EstimatePoints: Story points estimate (decimal)
            - EstimatedEffort: Top-down effort estimate in minutes
                (calculated from points)
            - TaskEstimatedEffort: Bottom-up estimated effort from all
                associated tasks (minutes)
            - TaskActualEffort: Bottom-up actual effort from all
                associated tasks (minutes)
            - TaskCount: Number of tasks associated with this requirement
            - PercentComplete: Percentage complete of the requirement
            - CoverageCountTotal: Total number of test cases covering
                this requirement
            - CoverageCountPassed/Failed/Caution/Blocked: Test case
                coverage breakdown by status
            - StartDate: Scheduled start date for planning
            - EndDate: Scheduled end date for planning
            - CreationDate: When the requirement was originally created
            - LastUpdateDate: When the requirement was last modified
            - ReleaseId/ReleaseVersionNumber: Sprint/iteration assignment
            - ProjectId/ProjectName: Project the requirement belongs to
            - ComponentId: Component the requirement belongs to (null if none)
            - Summary: Whether this is a summary requirement (parent)
            - IsSuspect: Whether requirement is marked as suspect due to
                dependent item changes
            - CustomProperties: List of custom fields for this requirement
            - Tags: Meta-tags associated with the requirement
            - IsAttachments: Whether the requirement has attachments

        When to Use:
            - Getting requirement list for a specific product
            - Retrieving requirements with server-side pagination
            - Analyzing product-level requirement data
            - Sprint planning and backlog grooming
            - Tracking test coverage for requirements

        Related Tools:
            - get_my_requirements: Get requirements assigned to current user
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
            # Get first 100 requirements from product 55
            requirements_json = get_requirements(product_id=55)
            requirements = json.loads(requirements_json)

            # Get next page of requirements
            requirements_json = get_requirements(
                product_id=55, starting_row=101, number_of_rows=100
            )

            # Process and filter results
            requirements = json.loads(requirements_json)
            critical_requirements = [
                r for r in requirements["data"]
                if r["ImportanceName"] == "Critical"
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
