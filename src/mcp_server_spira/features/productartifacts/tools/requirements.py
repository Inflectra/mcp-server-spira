"""
Provides operations for working with the Spira product requirements

This module provides MCP tools for retrieving and updating product requirements
"""

from mcp_server_spira.features.formatting import format_requirement
from mcp_server_spira.features.common import get_spira_client

def _get_requirements_impl(spira_client, product_id: int) -> str:
    """
    Implementation of retrieving the list of requirements in the specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PG:45, just use 45. 
                
    Returns:
        Formatted string containing the list of requirements
    """
    try:
        # Get the list of requirements in the product
        requirements_url = f"projects/{product_id}/requirements"
        requirements = spira_client.make_spira_api_get_request(requirements_url)

        if not requirements:
            return "There are no requirements for the product."

        # Format the requirements into human readable data
        formatted_results = []
        for requirement in requirements[:25]:  # Only show first 25 requirements
            requirement_info = format_requirement(requirement)
            formatted_results.append(requirement_info)

        return "\n\n".join(formatted_results)
    
    except Exception as e:
        return f"There was a problem using this tool: {e}"

def register_tools(mcp) -> None:
    """
    Register product requirements tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_requirements(product_id: int) -> str:
        """
        Retrieves a list of the requirements in the specified product
        
        Use this tool when you need to:
        - View the list of requirements in the specified product
        - Get information about multiple requirements at once
        - Access the full description and selected fields of requirements

        Args:
            product_id: The numeric ID of the product. If the ID is PG:45, just use 45. 
        
        Returns:
            Formatted string containing comprehensive information for the
            requested list of requirements, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_requirements_impl(spira_client, product_id)
        except Exception as e:
            return f"Error: {str(e)}"
