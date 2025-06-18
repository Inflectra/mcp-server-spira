"""
Provides operations for working with the Spira product releases

This module provides MCP tools for retrieving and updating product releases
"""

from mcp_server_spira.features.formatting import format_release
from mcp_server_spira.features.common import get_spira_client

def _get_releases_impl(spira_client, product_id: int) -> str:
    """
    Implementation of retrieving the list of releases in the specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PG:45, just use 45. 
                
    Returns:
        Formatted string containing the list of releases
    """
    # Get the list of releases in the product
    releases_url = "projects/" + str(product_id) + "/releases?active_only=true"
    releases = spira_client.make_spira_api_get_request(releases_url)

    if not releases:
        return "Unable to fetch releases list for the product."

    # Format the releases into human readable data
    formatted_results = []
    for release in releases:
        release_info = format_release(release)
        formatted_results.append(release_info)

    return "\n\n".join(formatted_results)

def register_tools(mcp) -> None:
    """
    Register my work tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_releases(product_id: int) -> str:
        """
        Retrieves a list of the releases in the specified product
        
        Use this tool when you need to:
        - View the list of releases in the specified product
        - Get information about multiple releases at once
        - Access the full description and selected fields of releases

        Args:
            product_id: The numeric ID of the product. If the ID is PG:45, just use 45. 
        
        Returns:
            Formatted string containing comprehensive information for the
            requested list of releases, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_releases_impl(spira_client, product_id)
        except Exception as e:
            return f"Error: {str(e)}"
        