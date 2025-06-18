"""
Provides operations for getting a list of custom properties defined in the current product template

This module provides MCP tools for retrieving artifact types, and their associated custom properties
"""

from mcp_server_spira.features.formatting import format_milestone
from mcp_server_spira.features.common import get_spira_client

def _get_custom_properties_impl(spira_client, template_id: int) -> str:
    """
    Implementation of retrieving the list of artifact types and custom properties in the product template

    Args:
        spira_client: The Inflectra Spira API client instance
        template_id: The numeric ID of the product template. If the ID is PT:45, just use 45. 
                
    Returns:
        Formatted string containing the list of artifact types and associated custom properties
    """
    # Get the list of milestones in the program
    milestones_url = "project-templates/" + str(template_id) + "/milestones"
    milestones = spira_client.make_spira_api_get_request(milestones_url)

    if not milestones:
        return "Unable to fetch programs list for the current user."

    # Format the milestones into human readable data
    formatted_results = []
    for milestone in milestones:
        milestone_info = format_milestone(milestone)
        formatted_results.append(milestone_info)

    return "\n\n".join(formatted_results)

def register_tools(mcp) -> None:
    """
    Register custom property tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_custom_properties(template_id: int) -> str:
        """
        Retrieves a list of the artifact types and associated custom properties for the current product template
        
        Use this tool when you need to:
        - View the list of artifact types in the product template
        - For each artifact type (e.g. test case), get the list of custom properties
        - Access the name and ID of each type

        Args:
            template_id: The numeric ID of the product template. If the ID is PT:45, just use 45. 
        
        Returns:
            Formatted string containing comprehensive information for the
            requested list of artifact types and corresponding custom properties
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_custom_properties_impl(spira_client, template_id)
        except Exception as e:
            return f"Error: {str(e)}"
        