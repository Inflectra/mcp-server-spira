"""
Provides operations for working with the Spira product automation hosts

This module provides MCP tools for retrieving and updating product automation hosts
"""

from mcp_server_spira.features.formatting import format_automation_host
from mcp_server_spira.features.common import get_spira_client

def _get_automation_hosts_impl(spira_client, product_id: int) -> str:
    """
    Implementation of retrieving the list of automation hosts in the specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PG:45, just use 45. 
                
    Returns:
        Formatted string containing the list of automation hosts
    """
    try:
        # Get the list of automation hosts in the product
        automation_hosts_url = f"projects/{product_id}/automation-hosts"
        automation_hosts = spira_client.make_spira_api_get_request(automation_hosts_url)

        if not automation_hosts:
            return "There are no automation hosts for the product."

        # Format the automation hosts into human readable data
        formatted_results = []
        for host in automation_hosts[:25]:  # Only show first 25 automation hosts
            host_info = format_automation_host(host)
            formatted_results.append(host_info)

        return "\n\n".join(formatted_results)
    
    except Exception as e:
        return f"There was a problem using this tool: {e}"

def register_tools(mcp) -> None:
    """
    Register product automation hosts tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_automation_hosts(product_id: int) -> str:
        """
        Retrieves a list of the automation hosts in the specified product
        
        Use this tool when you need to:
        - View the list of automation hosts in the specified product
        - Get information about multiple automation hosts at once
        - Access the full description and selected fields of automation hosts

        Args:
            product_id: The numeric ID of the product. If the ID is PG:45, just use 45. 
        
        Returns:
            Formatted string containing comprehensive information for the
            requested list of automation hosts, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_automation_hosts_impl(spira_client, product_id)
        except Exception as e:
            return f"Error: {str(e)}"
