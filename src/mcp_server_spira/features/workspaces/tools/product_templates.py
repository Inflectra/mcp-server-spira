"""
Provides operations for working with the Spira product template workspace

This module provides MCP tools for retrieving and updating product templates (also known as projects).
"""

from mcp_server_spira.features.formatting import format_product_template
from mcp_server_spira.features.workspaces.common import get_spira_client

def _get_product_templates_impl(spira_client) -> str:
    """
    Implementation of retrieving the list of Spira product templates
    the current user has access to

    Args:
        spira_client: The Inflectra Spira API client instance
                
    Returns:
        Formatted string containing the list of available product templates
    """
    # Get the list of available product templates for the current user
    product_templates_url = "project-templates"
    product_templates = spira_client.make_spira_api_get_request(product_templates_url)

    if not product_templates:
        return "Unable to fetch product templates list for the current user."

    # Format the product templates into human readable data
    formatted_results = []
    for product_template in product_templates[:100]:  # Only show first 100 product templates
        product_template_info = format_product_template(product_template)
        formatted_results.append(product_template_info)

    return "\n\n".join(formatted_results)

def register_tools(mcp) -> None:
    """
    Register my work tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_product_templates() -> str:
        """
        Retrieves a list of the product templates (projects) that the current user has access to
        
        Use this tool when you need to:
        - View the list of product templates that a user has access to
        - Get information about multiple product templates at once
        - Access the full description and selected fields of product templates
                    
        Returns:
            Formatted string containing comprehensive information for the
            requested list of product templates, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_product_templates_impl(spira_client)
        except Exception as e:
            return f"Error: {str(e)}"
        