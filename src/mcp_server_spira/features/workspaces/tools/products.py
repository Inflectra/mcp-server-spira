"""
Provides operations for working with the Spira product workspace

This module provides MCP tools for retrieving and updating products (also known as projects).
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.formatting import format_product


def _get_product_by_id_impl(spira_client, product_id: int) -> str:
    """
    Implementation of retrieving a single Spira product by its ID

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45.

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
        Formatted string containing the list of available products
    """
    try:
        # Get the list of available products for the current user
        products_url = "projects"
        products = spira_client.make_spira_api_get_request(products_url)

        if not products:
            return "There are no products available for the current user."

        # Format the products into human readable data
        formatted_results = []
        for product in products[:100]:  # Only show first 100 products
            product_info = format_product(product)
            formatted_results.append(product_info)

        return "\n\n".join(formatted_results)
    except Exception as e:
        return f"There was a problem using this tool: {e}"


def _get_program_products_impl(spira_client, program_id: int) -> str:
    """
    Implementation of retrieving the list of Spira products (projects)
    the current user has access to

    Args:
        spira_client: The Inflectra Spira API client instance
        program_id: The numeric ID of the program. If the ID is PG:45, just use 45.

    Returns:
        Formatted string containing the list of available products
    """
    try:
        # Get the list of available products for the current user
        products_url = "projects"
        products = spira_client.make_spira_api_get_request(products_url)

        if not products:
            return "The program does not contain any products."

        # Loop through and only include the products that are part of the specified program
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
        Retrieves a list of the products (projects) that the current user has access to

        Use this tool when you need to:
        - View the list of products that a user has access to
        - Get information about multiple products at once
        - Access the full description and selected fields of products

        Returns:
            Formatted string containing comprehensive information for the
            requested list of products, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_products_impl(spira_client)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def get_product_by_id(product_id: int) -> str:
        """
        Retrieves a single product by its ID value

        Use this tool when you need to:
        - View the details of a single product
        - Access the full description and selected fields of products

        Args:
            product_id: The numeric ID of the product. If the ID is PR:45, just use 45.

        Returns:
            Formatted string containing comprehensive information for the
            requested product, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_product_by_id_impl(spira_client, product_id)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def get_program_products(program_id: int) -> str:
        """
        Retrieves a list of the products (projects) that belong to the specified program

        Use this tool when you need to:
        - View the list of products that belong to a specific program
        - Get information about multiple products at once
        - Access the full description and selected fields of products

        Args:
            program_id: The numeric ID of the program. If the ID is PG:45, just use 45.

        Returns:
            Formatted string containing comprehensive information for the
            requested list of products, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_program_products_impl(spira_client, program_id)
        except Exception as e:
            return f"Error: {str(e)}"
