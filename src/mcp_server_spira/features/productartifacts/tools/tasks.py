"""
Provides operations for working with the Spira product tasks

This module provides MCP tools for retrieving and updating product tasks
"""

from mcp_server_spira.features.formatting import format_task
from mcp_server_spira.features.common import get_spira_client

def _get_tasks_impl(spira_client, product_id: int) -> str:
    """
    Implementation of retrieving the list of tasks in the specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PG:45, just use 45. 
                
    Returns:
        Formatted string containing the list of tasks
    """
    try:
        # Get the list of tasks in the product
        tasks_url = f"projects/{product_id}/tasks"
        tasks = spira_client.make_spira_api_get_request(tasks_url)

        if not tasks:
            return "There are no tasks for the product."

        # Format the tasks into human readable data
        formatted_results = []
        for task in tasks[:25]:  # Only show first 25 tasks
            task_info = format_task(task)
            formatted_results.append(task_info)

        return "\n\n".join(formatted_results)
    
    except Exception as e:
        return f"There was a problem using this tool: {e}"

def register_tools(mcp) -> None:
    """
    Register product tasks tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_tasks(product_id: int) -> str:
        """
        Retrieves a list of the tasks in the specified product
        
        Use this tool when you need to:
        - View the list of tasks in the specified product
        - Get information about multiple tasks at once
        - Access the full description and selected fields of tasks

        Args:
            product_id: The numeric ID of the product. If the ID is PG:45, just use 45. 
        
        Returns:
            Formatted string containing comprehensive information for the
            requested list of tasks, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_tasks_impl(spira_client, product_id)
        except Exception as e:
            return f"Error: {str(e)}"
