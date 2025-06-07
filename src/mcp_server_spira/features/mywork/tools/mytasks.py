"""
Provides operations for working with the Spira tasks I have been assigned

This module provides MCP tools for retrieving and updating my assigned tasks.
"""

from mcp_server_spira.features.formatting import format_task
from mcp_server_spira.features.mywork.common import get_spira_client

def _get_my_tasks_impl(spira_client) -> str:
    """
    Implementation of retrieving my assigned Spira tasks.

    Args:
        spira_client: The Inflectra Spira API client instance
                
    Returns:
        Formatted string containing the list of assigned tasks
    """
    # Get the list of open tasks for the current user
    tasks_url = "tasks"
    tasks = spira_client.make_spira_api_get_request(tasks_url)

    if not tasks:
        return "Unable to fetch task data for the current user."

    # Format the tasks into human readable data
    formatted_results = []
    for task in tasks[:25]:  # Only show first 25 tasks
        task_info = format_task(task)
        formatted_results.append(task_info)

    return "\n\n".join(formatted_results)

def register_tools(mcp) -> None:
    """
    Register my work tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_my_tasks() -> str:
        """
        Retrieves a list of the open tasks that are assigned to me
        
        Use this tool when you need to:
        - View the complete details of a specific work item
        - Examine the current state, assigned user, and other properties
        - Get information about multiple work items at once
        - Access the full description and custom fields of work items
                    
        Returns:
            Formatted string containing comprehensive information for the
            requested list of tasks, including all system and custom fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_my_tasks_impl(spira_client)
        except Exception as e:
            return f"Error: {str(e)}"
        