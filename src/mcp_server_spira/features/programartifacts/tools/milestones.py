"""
Provides operations for working with the Spira program milestones

This module provides MCP tools for retrieving and updating program milestones
"""

from mcp_server_spira.features.formatting import format_milestone
from mcp_server_spira.features.common import get_spira_client

def _get_milestones_impl(spira_client, program_id: int) -> str:
    """
    Implementation of retrieving the list of milestones in the specified program

    Args:
        spira_client: The Inflectra Spira API client instance
        program_id: The numeric ID of the program. If the ID is PG:45, just use 45. 
                
    Returns:
        Formatted string containing the list of milestones
    """
    try:
        # Get the list of milestones in the program
        milestones_url = "programs/" + str(program_id) + "/milestones"
        milestones = spira_client.make_spira_api_get_request(milestones_url)

        if not milestones:
            return "There are no milestones in the current program."

        # Format the milestones into human readable data
        formatted_results = []
        for milestone in milestones:
            milestone_info = format_milestone(milestone)
            formatted_results.append(milestone_info)

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
    def get_milestones(program_id: int) -> str:
        """
        Retrieves a list of the milestones in the specified program
        
        Use this tool when you need to:
        - View the list of milestones in the specified program
        - Get information about multiple milestones at once
        - Access the full description and selected fields of milestones

        Args:
            program_id: The numeric ID of the program. If the ID is PG:45, just use 45. 
        
        Returns:
            Formatted string containing comprehensive information for the
            requested list of milestones, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_milestones_impl(spira_client, program_id)
        except Exception as e:
            return f"Error: {str(e)}"
        