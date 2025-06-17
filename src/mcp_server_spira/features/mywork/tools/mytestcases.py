"""
Provides operations for working with the Spira test cases I have been assigned

This module provides MCP tools for retrieving and updating my assigned test cases.
"""

from mcp_server_spira.features.formatting import format_test_case
from mcp_server_spira.features.common import get_spira_client

def _get_my_testcases_impl(spira_client) -> str:
    """
    Implementation of retrieving my assigned Spira test cases.

    Args:
        spira_client: The Inflectra Spira API client instance
                
    Returns:
        Formatted string containing the list of assigned test cases
    """
    # Get the list of open testcases for the current user
    testcases_url = "test-cases"
    testcases = spira_client.make_spira_api_get_request(testcases_url)

    if not testcases:
        return "Unable to fetch testcase data for the current user."

    # Format the testcases into human readable data
    formatted_results = []
    for testcase in testcases[:25]:  # Only show first 25 testcases
        testcase_info = format_test_case(testcase)
        formatted_results.append(testcase_info)

    return "\n\n".join(formatted_results)

def register_tools(mcp) -> None:
    """
    Register my work tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_my_testcases() -> str:
        """
        Retrieves a list of the open test cases that are assigned to me
        
        Use this tool when you need to:
        - View the complete details of a specific testcase
        - Examine the current state, assigned user, and other properties
        - Get information about multiple testcases at once
        - Access the full description and selected fields of testcases
                    
        Returns:
            Formatted string containing comprehensive information for the
            requested list of testcases, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_my_testcases_impl(spira_client)
        except Exception as e:
            return f"Error: {str(e)}"
        