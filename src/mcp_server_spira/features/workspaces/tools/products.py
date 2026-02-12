"""
Provides operations for working with the Spira product workspace

This module provides MCP tools for retrieving and updating products
(also known as projects).
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.formatting import format_product


def _get_product_by_id_impl(spira_client, product_id: int) -> str:
    """
    Implementation of retrieving a single Spira product by its ID

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45,
            just use 45.

    Returns:
        Formatted string containing the product definition
    """
    try:
        # Get the product by its ID
        product_url = f"projects/{product_id}"
        product = spira_client.make_spira_api_get_request(product_url)

        if not product:
            return "There was no product with that ID available"

        # Format the product into human readable data
        product_info = format_product(product)

        return product_info
    except Exception as e:
        return f"There was a problem using this tool: {e}"


def _get_products_impl(spira_client) -> str:
    """
    Implementation of retrieving the list of Spira products (projects)
    the current user has access to

    Args:
        spira_client: The Inflectra Spira API client instance

    Returns:
        JSON string containing the list of available products
    """
    try:
        # Get the list of available products for the current user
        products_url = "projects"
        products = spira_client.make_spira_api_get_request(products_url)

        if not products:
            # Return empty data array if no products
            return format_success_response(data=[])

        # Return all products as JSON (no truncation)
        return format_success_response(data=products)
    except Exception as e:
        return format_error_response(
            error="Failed to retrieve products",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e)},
            suggestion="Check API connectivity and authentication",
        )


def _get_program_products_impl(spira_client, program_id: int) -> str:
    """
    Implementation of retrieving the list of Spira products (projects)
    the current user has access to

    Args:
        spira_client: The Inflectra Spira API client instance
        program_id: The numeric ID of the program. If the ID is PG:45,
            just use 45.

    Returns:
        Formatted string containing the list of available products
    """
    try:
        # Get the list of available products for the current user
        products_url = "projects"
        products = spira_client.make_spira_api_get_request(products_url)

        if not products:
            return "The program does not contain any products."

        # Loop through and only include the products that are part of
        # the specified program
        # Format the products into human readable data
        formatted_results = []
        for product in products:
            if product["ProjectGroupId"] == program_id:
                product_info = format_product(product)
                formatted_results.append(product_info)

        return "\n\n".join(formatted_results)
    except Exception as e:
        return f"There was a problem using this tool: {e}"


def register_tools(mcp) -> None:
    """
    Register my work tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_products() -> str:
        """
        Retrieves a list of the products (projects) that the current
        user has access to

        Use this tool when you need to:
        - View the list of products that a user has access to
        - Get information about multiple products at once
        - Access the full description and selected fields of products

        Returns:
            JSON string with structure:
            {
                "data": [
                    {
                        "ProjectId": 55,
                        "Name": "Web Application",
                        "Description": "Main web application project",
                        "Active": true,
                        "CreationDate": "2023-01-15T10:00:00Z",
                        "ProjectGroupId": 10,
                        "ProjectTemplateId": 1,
                        "Website": "https://example.com",
                        "WorkingHours": 8,
                        "WorkingDays": 5,
                        "NonWorkingHours": 0,
                        "StartDate": "2023-01-01T00:00:00Z",
                        "EndDate": "2024-12-31T00:00:00Z",
                        "PercentComplete": 45,
                        "RequirementCount": 150,
                        "WorkspaceTypeId": 1,
                        "Guid": "abc-123-def-456",
                        "LastUpdatedDate": "2024-01-15T10:00:00Z",
                        "ArtifactTypeId": 1,
                        "ConcurrencyGuid": "xyz-789",
                        "CustomProperties": []
                    }
                ]
            }

        Key Fields:
            - ProjectId: Unique identifier for the product (use this in
                other tool calls)
            - Name: Display name of the product
            - Description: Detailed description of the product
            - Active: Whether the product is currently active (boolean)
            - CreationDate: When the product was created
                (ISO 8601 datetime)
            - ProjectGroupId: ID of the program/group this product
                belongs to (null if none)
            - ProjectTemplateId: ID of the template used for this
                product
            - Website: URL associated with the product
            - WorkingHours: Number of working hours per day (integer)
            - WorkingDays: Number of working days per week (integer)
            - NonWorkingHours: Special non-working hours per month
                (integer)
            - StartDate: Planned start date for the product
                (ISO 8601 datetime, nullable)
            - EndDate: Planned end date for the product
                (ISO 8601 datetime, nullable)
            - PercentComplete: Overall completion percentage (integer)
            - RequirementCount: Total number of requirements in the
                product (integer)
            - WorkspaceTypeId: Type of workspace (integer)
            - Guid: Unique global identifier (string)
            - LastUpdatedDate: Last modification timestamp
                (ISO 8601 datetime, nullable)
            - ArtifactTypeId: Type of artifact (integer)
            - ConcurrencyGuid: Used for optimistic concurrency control
                (string)
            - CustomProperties: Array of custom fields for this product

        When to Use:
            - Discovering available products for the current user
            - Listing products for user selection
            - Validating product IDs before other operations
            - Getting product metadata for reporting

        Related Tools:
            - get_product_by_id: Get detailed information for a single
                product
            - get_programs: Get program-level groupings
            - get_product_templates: Get available templates

        Error Responses:
            {
                "error": "Failed to retrieve products",
                "error_code": "API_ERROR",
                "details": {
                    "message": "Connection timeout"
                },
                "suggestion": "Check API connectivity and authentication"
            }

        Example Usage:
            # Get all products
            products_json = get_products()
            products = json.loads(products_json)

            # Filter active products
            active_products = [p for p in products["data"]
                               if p["Active"]]

            # Find product by name
            web_app = next((p for p in products["data"]
                            if "Web" in p["Name"]), None)
        """
        try:
            spira_client = get_spira_client()
            return _get_products_impl(spira_client)
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve products",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )

    @mcp.tool()
    def get_product_by_id(product_id: int) -> str:
        """
        Retrieves a single product by its ID value

        Use this tool when you need to:
        - View the details of a single product
        - Access the full description and selected fields of products

        Args:
            product_id: The numeric ID of the product. If the ID is
                PR:45, just use 45.

        Returns:
            Formatted string containing comprehensive information for the
            requested product, including name, id, description and key
            fields, formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_product_by_id_impl(spira_client, product_id)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def get_program_products(program_id: int) -> str:
        """
        Retrieves a list of the products (projects) that belong to the
        specified program

        Use this tool when you need to:
        - View the list of products that belong to a specific program
        - Get information about multiple products at once
        - Access the full description and selected fields of products

        Args:
            program_id: The numeric ID of the program. If the ID is
                PG:45, just use 45.

        Returns:
            Formatted string containing comprehensive information for the
            requested list of products, including name, id, description
            and key fields, formatted as markdown with clear section
            headings
        """
        try:
            spira_client = get_spira_client()
            return _get_program_products_impl(spira_client, program_id)
        except Exception as e:
            return f"Error: {str(e)}"
