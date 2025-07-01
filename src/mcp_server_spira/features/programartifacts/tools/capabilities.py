"""
Provides operations for working with the Spira program capabilities

This module provides MCP tools for retrieving program capabilities
"""

from mcp_server_spira.features.formatting import format_capability
from mcp_server_spira.features.common import get_spira_client

def _get_capabilities_impl(spira_client, program_id: int) -> str:
    """
    Implementation of retrieving the list of capabilities in the specified program

    Args:
        spira_client: The Inflectra Spira API client instance
        program_id: The numeric ID of the program. If the ID is PG:45, just use 45. 
                
    Returns:
        Formatted string containing the list of capabilities
    """
    try:
        # Get the list of capabilities in the program
        capabilities_url = f"programs/{program_id}/capabilities/search?current_page=1&page_size=500"
        capabilities = spira_client.make_spira_api_get_request(capabilities_url)

        if not capabilities:
            return "There are no capabilities in the specified program."

        # Format the capabilities into human readable data
        formatted_results = []
        for capability in capabilities:
            capability_info = format_capability(capability)
            formatted_results.append(capability_info)

        return "\n\n".join(formatted_results)
    
    except Exception as e:
        return f"There was a problem using this tool: {e}"

def register_tools(mcp) -> None:
    """
    Register program capabilities tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_capabilities(program_id: int) -> str:
        """
        Retrieves a list of the capabilities in the specified program
        
        Use this tool when you need to:
        - View the list of capabilities in the specified program
        - Get information about multiple capabilities at once
        - Access the full description and selected fields of capabilities

        Args:
            program_id: The numeric ID of the program. If the ID is PG:45, just use 45. 
        
        Returns:
            Formatted string containing comprehensive information for the
            requested list of capabilities, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_capabilities_impl(spira_client, program_id)
        except Exception as e:
            return f"Error: {str(e)}"
