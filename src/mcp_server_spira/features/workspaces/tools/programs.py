"""
Provides operations for working with the Spira program workspace

This module provides MCP tools for retrieving and updating programs (also known as projects).
"""

from mcp_server_spira.features.formatting import format_program
from mcp_server_spira.features.workspaces.common import get_spira_client

def _get_programs_impl(spira_client) -> str:
    """
    Implementation of retrieving the list of Spira programs
    the current user has access to

    Args:
        spira_client: The Inflectra Spira API client instance
                
    Returns:
        Formatted string containing the list of available programs
    """
    # Get the list of available programs for the current user
    programs_url = "programs"
    programs = spira_client.make_spira_api_get_request(programs_url)

    if not programs:
        return "Unable to fetch programs list for the current user."

    # Format the programs into human readable data
    formatted_results = []
    for program in programs[:100]:  # Only show first 100 programs
        program_info = format_program(program)
        formatted_results.append(program_info)

    return "\n\n".join(formatted_results)

def register_tools(mcp) -> None:
    """
    Register my work tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_programs() -> str:
        """
        Retrieves a list of the programs (projects) that the current user has access to
        
        Use this tool when you need to:
        - View the list of programs that a user has access to
        - Get information about multiple programs at once
        - Access the full description and selected fields of programs
                    
        Returns:
            Formatted string containing comprehensive information for the
            requested list of programs, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_programs_impl(spira_client)
        except Exception as e:
            return f"Error: {str(e)}"
        