"""
Provides operations for working with the Spira test sets I have been assigned

This module provides MCP tools for retrieving and updating my assigned test sets.
"""

from mcp_server_spira.features.formatting import format_test_set
from mcp_server_spira.features.common import get_spira_client

def _get_my_testsets_impl(spira_client) -> str:
    """
    Implementation of retrieving my assigned Spira test sets.

    Args:
        spira_client: The Inflectra Spira API client instance
                
    Returns:
        Formatted string containing the list of assigned testsets
    """
    try:
        # Get the list of open testsets for the current user
        testsets_url = "test-sets"
        testsets = spira_client.make_spira_api_get_request(testsets_url)

        if not testsets:
            return "The current user does not have any test sets."

        # Format the testsets into human readable data
        formatted_results = []
        for testset in testsets[:25]:  # Only show first 25 testsets
            testset_info = format_test_set(testset)
            formatted_results.append(testset_info)

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
    def get_my_testsets() -> str:
        """
        Retrieves a list of the open testsets that are assigned to me
        
        Use this tool when you need to:
        - View the complete details of a specific testset
        - Examine the current state, assigned user, and other properties
        - Get information about multiple testsets at once
        - Access the full description and selected fields of testsets
                    
        Returns:
            Formatted string containing comprehensive information for the
            requested list of testsets, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_my_testsets_impl(spira_client)
        except Exception as e:
            return f"Error: {str(e)}"
        