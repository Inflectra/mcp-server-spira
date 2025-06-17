"""
Provides operations for working with the Spira incidents I have been assigned

This module provides MCP tools for retrieving and updating my assigned incidents.
"""

from mcp_server_spira.features.formatting import format_incident
from mcp_server_spira.features.common import get_spira_client

def _get_my_incidents_impl(spira_client) -> str:
    """
    Implementation of retrieving my assigned Spira incidents.

    Args:
        spira_client: The Inflectra Spira API client instance
                
    Returns:
        Formatted string containing the list of assigned incidents
    """
    # Get the list of open incidents for the current user
    incidents_url = "incidents"
    incidents = spira_client.make_spira_api_get_request(incidents_url)

    if not incidents:
        return "Unable to fetch incident data for the current user."

    # Format the incidents into human readable data
    formatted_results = []
    for incident in incidents[:25]:  # Only show first 25 incidents
        incident_info = format_incident(incident)
        formatted_results.append(incident_info)

    return "\n\n".join(formatted_results)

def register_tools(mcp) -> None:
    """
    Register my work tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_my_incidents() -> str:
        """
        Retrieves a list of the open incidents that are assigned to me
        
        Use this tool when you need to:
        - View the complete details of a specific incident
        - Examine the current state, assigned user, and other properties
        - Get information about multiple incidents at once
        - Access the full description and selected fields of incidents
                    
        Returns:
            Formatted string containing comprehensive information for the
            requested list of incidents, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_my_incidents_impl(spira_client)
        except Exception as e:
            return f"Error: {str(e)}"
        