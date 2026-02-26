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


def _get_product_by_id_impl(spira_client, product_id: int) -> str:
    """
    Implementation of retrieving a single Spira product by its ID

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45,
            just use 45.

    Returns:
        JSON string containing the product details
    """
    try:
        # Get the product by its ID
        product_url = f"projects/{product_id}"
        product = spira_client.make_spira_api_get_request(product_url)

        if not product:
            return format_error_response(
                error="Product not found",
                error_code=ErrorCodes.NOT_FOUND,
                details={"product_id": product_id},
                suggestion=("Verify the product ID is correct and you have access to it"),
            )

        # Return product as JSON
        return format_success_response(data=[product])
    except Exception as e:
        return format_error_response(
            error="Failed to retrieve product",
            error_code=ErrorCodes.API_ERROR,
            details={"product_id": product_id, "message": str(e)},
            suggestion="Check API connectivity and authentication",
        )


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
    that belong to a specific program

    Args:
        spira_client: The Inflectra Spira API client instance
        program_id: The numeric ID of the program. If the ID is PG:45,
            just use 45.

    Returns:
        JSON string containing the list of products in the program
    """
    try:
        # Get the list of available products for the current user
        products_url = "projects"
        products = spira_client.make_spira_api_get_request(products_url)

        if not products:
            return format_success_response(data=[])

        # Filter products that belong to the specified program
        program_products = [
            product for product in products if product.get("ProjectGroupId") == program_id
        ]

        return format_success_response(data=program_products)
    except Exception as e:
        return format_error_response(
            error="Failed to retrieve program products",
            error_code=ErrorCodes.API_ERROR,
            details={"program_id": program_id, "message": str(e)},
            suggestion="Check API connectivity and authentication",
        )


def register_tools(mcp) -> None:
    """
    Register my work tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool(
        name="system_get_products",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    )
    def get_products() -> str:
        """
        Retrieves a list of the products (projects) that the current
        user has access to

        Maps to Spira API: GET /projects

        Use this to discover available products before querying
        product-specific data.

        Returns:
            JSON string with structure: {"data": [product objects]}
            See Key Fields section below for important product fields.
            Full response structure documented in API.

        Key Fields:
            - ProjectId: Unique identifier (use in other tool calls)
            - Name: Display name of the product
            - Active: Whether the product is currently active
            - ProjectGroupId: Program/group this product belongs to
            - CreationDate: When the product was created
            - PercentComplete: Overall completion percentage
            - RequirementCount: Total number of requirements

            Additional fields available: Description, ProjectTemplateId,
            Website, WorkingHours, WorkingDays, NonWorkingHours,
            StartDate, EndDate, LastUpdatedDate, CustomProperties, Guid

        Related Tools:
            - get_programs: Get program-level groupings
            - get_product_templates: Get available templates

        Error Responses:
            Returns structured JSON with error, error_code, details, and
            suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            products_json = get_products()
            products = json.loads(products_json)
            for product in products["data"]:
                print(f"Product {product['ProjectId']}: "
                      f"{product['Name']}")
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

    @mcp.tool(
        name="system_get_product_by_id",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    )
    def get_product_by_id(product_id: int) -> str:
        """
        Retrieves the details of a single product in the specified
        product

        Maps to Spira API: GET /projects/{product_id}

        Use this tool when you need to:
        - View the details of a single product in the specified product
        - Access the full description and selected fields of the product

        Args:
            product_id: The numeric ID of the product.
                If the ID is PR:45, just use 45.

        Returns:
            JSON string with structure: {"data": [product object]}
            See Key Fields section below for important product fields.
            Full response structure documented in API.

        Key Fields:
            - ProjectId: Unique identifier (use in other tool calls)
            - Name: Display name of the product
            - Active: Whether the product is currently active
            - ProjectGroupId: Program/group this product belongs to
            - CreationDate: When the product was created
            - PercentComplete: Overall completion percentage
            - RequirementCount: Total number of requirements

            Additional fields available: Description, ProjectTemplateId,
            Website, WorkingHours, WorkingDays, NonWorkingHours,
            StartDate, EndDate, LastUpdatedDate, CustomProperties, Guid

        Related Tools:
            - get_products: Get list of products for a product
            - get_programs: Get program-level groupings

        Error Responses:
            Returns structured JSON with error, error_code, details, and
            suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            product_json = get_product_by_id(product_id=55)
            product = json.loads(product_json)
            product_data = product["data"][0]
            print(f"Product: {product_data['Name']}")
        """
        try:
            spira_client = get_spira_client()
            return _get_product_by_id_impl(spira_client, product_id)
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve product",
                error_code=ErrorCodes.API_ERROR,
                details={"product_id": product_id, "message": str(e)},
                suggestion="Check API connectivity and authentication",
            )

    @mcp.tool(
        name="system_get_program_products",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    )
    def get_program_products(program_id: int) -> str:
        """
        Retrieves a list of the products (projects) that belong to the
        specified program

        Maps to Spira API: GET /projects (filtered by program)

        Use this tool when you need to:
        - View the list of products that belong to a specific program
        - Get information about multiple products at once
        - Access the full description and selected fields of products

        Args:
            program_id: The numeric ID of the program.
                If the ID is PG:45, just use 45.

        Returns:
            JSON string with structure: {"data": [product objects]}
            See Key Fields section below for important product fields.
            Full response structure documented in API.

        Key Fields:
            - ProjectId: Unique identifier (use in other tool calls)
            - Name: Display name of the product
            - Active: Whether the product is currently active
            - ProjectGroupId: Program/group this product belongs to
            - CreationDate: When the product was created
            - PercentComplete: Overall completion percentage
            - RequirementCount: Total number of requirements

            Additional fields available: Description, ProjectTemplateId,
            Website, WorkingHours, WorkingDays, NonWorkingHours,
            StartDate, EndDate, LastUpdatedDate, CustomProperties, Guid

        Related Tools:
            - get_products: Get all products user has access to
            - get_programs: Get program-level groupings

        Error Responses:
            Returns structured JSON with error, error_code, details, and
            suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            products_json = get_program_products(program_id=10)
            products = json.loads(products_json)
            for product in products["data"]:
                print(f"Product: {product['Name']}")
        """
        try:
            spira_client = get_spira_client()
            return _get_program_products_impl(spira_client, program_id)
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve program products",
                error_code=ErrorCodes.API_ERROR,
                details={"program_id": program_id, "message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
