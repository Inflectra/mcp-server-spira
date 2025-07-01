"""
Provides operations for working with the Spira product risks

This module provides MCP tools for retrieving and updating product risks
"""

from mcp_server_spira.features.formatting import format_risk
from mcp_server_spira.features.common import get_spira_client

def _get_risks_impl(spira_client, product_id: int) -> str:
    """
    Implementation of retrieving the list of risks in the specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45. 
                
    Returns:
        Formatted string containing the list of risks
    """
    try:
        # Get the list of risks in the product
        risks_url = f"projects/{product_id}/risks?starting_row=1&number_of_rows=500&sort_field=CreationDate&sort_direction=DESC"
        risks = spira_client.make_spira_api_post_request(risks_url, None)

        if not risks:
            return "There are no risks for the product."

        # Format the risks into human readable data
        formatted_results = []
        for risk in risks:
            risk_info = format_risk(risk)
            formatted_results.append(risk_info)

        return "\n\n".join(formatted_results)
    
    except Exception as e:
        return f"There was a problem using this tool: {e}"

def register_tools(mcp) -> None:
    """
    Register product risks tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_risks(product_id: int) -> str:
        """
        Retrieves a list of the risks in the specified product
        
        Use this tool when you need to:
        - View the list of risks in the specified product
        - Get information about multiple risks at once
        - Access the full description and selected fields of risks

        Args:
            product_id: The numeric ID of the product. If the ID is PR:45, just use 45. 
        
        Returns:
            Formatted string containing comprehensive information for the
            requested list of risks, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_risks_impl(spira_client, product_id)
        except Exception as e:
            return f"Error: {str(e)}"
