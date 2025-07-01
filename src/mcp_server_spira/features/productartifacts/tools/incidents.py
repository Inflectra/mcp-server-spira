"""
Provides operations for working with the Spira product incidents

This module provides MCP tools for retrieving and updating product incidents
"""

from mcp_server_spira.features.formatting import format_incident
from mcp_server_spira.features.common import get_spira_client

def _get_incidents_impl(spira_client, product_id: int) -> str:
    """
    Implementation of retrieving the list of incidents in the specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45. 
                
    Returns:
        Formatted string containing the list of incidents
    """
    try:
        # Get the list of incidents in the product
        incidents_url = f"projects/{product_id}/incidents"
        incidents = spira_client.make_spira_api_get_request(incidents_url)

        if not incidents:
            return "There are no incidents for the product."

        # Format the incidents into human readable data
        formatted_results = []
        for incident in incidents:
            incident_info = format_incident(incident)
            formatted_results.append(incident_info)

        return "\n\n".join(formatted_results)
    
    except Exception as e:
        return f"There was a problem using this tool: {e}"

def register_tools(mcp) -> None:
    """
    Register product incidents tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_incidents(product_id: int) -> str:
        """
        Retrieves a list of the incidents in the specified product
        
        Use this tool when you need to:
        - View the list of incidents in the specified product
        - Get information about multiple incidents at once
        - Access the full description and selected fields of incidents

        Args:
            product_id: The numeric ID of the product. If the ID is PR:45, just use 45. 
        
        Returns:
            Formatted string containing comprehensive information for the
            requested list of incidents, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_incidents_impl(spira_client, product_id)
        except Exception as e:
            return f"Error: {str(e)}"
