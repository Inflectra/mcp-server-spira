"""
Provides operations for working with the Spira product automation hosts

This module provides MCP tools for retrieving and updating product
automation hosts
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _get_automation_hosts_impl(
    spira_client,
    product_id: int,
    starting_row: int = 1,
    number_of_rows: int = 100,
) -> str:
    """
    Implementation of retrieving the list of automation hosts in the
    specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product.
            If the ID is PR:45, just use 45.
        starting_row: The starting row number for pagination
            (1-based index)
        number_of_rows: The number of rows to return

    Returns:
        JSON string containing the list of automation hosts with
        data structure
    """
    try:
        # Build the search endpoint URL with query parameters
        automation_hosts_url = (
            f"projects/{product_id}/automation-hosts/search?"
            f"starting_row={starting_row}&"
            f"number_of_rows={number_of_rows}"
        )

        # Make POST request with empty filter array (no filtering for now)
        automation_hosts = spira_client.make_spira_api_post_request(automation_hosts_url, [])

        # Return JSON response with data structure
        return format_success_response(data=automation_hosts)

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve automation hosts",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e), "product_id": product_id},
            suggestion=("Check API connectivity, authentication, and that the product_id is valid"),
        )


def register_tools(mcp) -> None:
    """
    Register product automation hosts tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_automation_hosts(
        product_id: int,
        starting_row: int = 1,
        number_of_rows: int = 100,
    ) -> str:
        """
        Retrieves a list of the automation hosts in the specified product

        Maps to Spira API:
            POST /projects/{product_id}/automation-hosts/search

        This tool returns automation hosts from the specified product using
        server-side pagination. Use this for retrieving product-level
        automation host lists.

        **API Endpoint**: POST /projects/{product_id}/automation-hosts/search
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
                        "AutomationHostId": 123,
                        "Name": "Build Server 01",
                        "Token": "host-token-abc123",
                        "Description": "Primary build and test automation host",
                        "LastUpdateDate": "2024-01-15T14:30:00Z",
                        "Active": true,
                        "LastContactDate": "2024-01-16T10:00:00Z",
                        "ProjectId": 55,
                        "ProjectGuid": "abc-123-def-456",
                        "ArtifactTypeId": 9,
                        "ConcurrencyDate": "2024-01-15T14:30:00Z",
                        "CustomProperties": [],
                        "IsAttachments": false,
                        "Tags": "ci,automation",
                        "Guid": "xyz-789-ghi-012"
                    }
                ]
            }

        Key Fields:
            - AutomationHostId: Unique identifier for the automation host
            - Name: The name of the host
            - Token: The authentication token for the host
            - Description: Detailed description of the host
            - LastUpdateDate: When the host was last modified
            - Active: Whether this host is active for the project
            - LastContactDate: The last time this host was contacted
                (null if never contacted)
            - ProjectId/ProjectGuid: Project the host belongs to
            - ArtifactTypeId: Type of artifact (9 for automation hosts)
            - ConcurrencyDate: Timestamp for optimistic concurrency control
            - CustomProperties: List of custom fields for this host
            - IsAttachments: Whether the host has attachments
            - Tags: Meta-tags associated with the host
            - Guid: Unique global identifier for the host

        When to Use:
            - Getting automation host list for a specific product
            - Retrieving hosts with server-side pagination
            - Analyzing product-level automation infrastructure
            - Finding available hosts for test execution

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
            # Get first 100 automation hosts from product 55
            hosts_json = get_automation_hosts(product_id=55)
            hosts = json.loads(hosts_json)

            # Get next page of hosts
            hosts_json = get_automation_hosts(
                product_id=55, starting_row=101, number_of_rows=100
            )

            # Process and filter results
            hosts = json.loads(hosts_json)
            active_hosts = [
                h for h in hosts["data"]
                if h["Active"]
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

            # Get Spira client and retrieve automation hosts
            spira_client = get_spira_client()
            return _get_automation_hosts_impl(
                spira_client,
                product_id,
                starting_row,
                number_of_rows,
            )
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve automation hosts",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
