"""
Provides operations for working with the Spira requirements I have been assigned

This module provides MCP tools for retrieving and updating my assigned requirements.
"""

from mcp_server_spira.features.formatting import format_requirement
from mcp_server_spira.features.mywork.common import get_spira_client

def _get_my_requirements_impl(spira_client) -> str:
    """
    Implementation of retrieving my assigned Spira requirements.

    Args:
        spira_client: The Inflectra Spira API client instance
                
    Returns:
        Formatted string containing the list of assigned requirements
    """
    # Get the list of open requirements for the current user
    requirements_url = "requirements"
    requirements = spira_client.make_spira_api_get_request(requirements_url)

    if not requirements:
        return "Unable to fetch requirement data for the current user."

    # Format the requirements into human readable data
    formatted_results = []
    for requirement in requirements[:25]:  # Only show first 25 requirements
        requirement_info = format_requirement(requirement)
        formatted_results.append(requirement_info)

    return "\n\n".join(formatted_results)

def register_tools(mcp) -> None:
    """
    Register my work tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_my_requirements() -> str:
        """
        Retrieves a list of the open requirements that are assigned to me
        
        Use this tool when you need to:
        - View the complete details of a specific requirement
        - Examine the current state, assigned user, and other properties
        - Get information about multiple requirements at once
        - Access the full description and selected fields of requirements
                    
        Returns:
            Formatted string containing comprehensive information for the
            requested list of requirements, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_my_requirements_impl(spira_client)
        except Exception as e:
            return f"Error: {str(e)}"
        