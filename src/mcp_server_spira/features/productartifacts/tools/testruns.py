"""
Provides operations for working with the Spira product test runs

This module provides MCP tools for retrieving and updating product test runs
"""

from mcp_server_spira.features.formatting import format_test_run
from mcp_server_spira.features.common import get_spira_client

def _get_test_runs_impl(spira_client, product_id: int) -> str:
    """
    Implementation of retrieving the list of test runs in the specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45. 
                
    Returns:
        Formatted string containing the list of test runs
    """
    try:
        # Get the list of test runs in the product
        starting_row = 1
        number_of_rows = 500  # Only show first 500 test runs
        sort_field = "EndDate"
        sort_direction = "DESC"
        test_runs_url = f"projects/{product_id}/test-runs?starting_row={starting_row}&number_of_rows={number_of_rows}&sort_field={sort_field}&sort_direction={sort_direction}"
        test_runs = spira_client.make_spira_api_get_request(test_runs_url)

        if not test_runs:
            return "There are no test runs for the product."

        # Format the test runs into human readable data
        formatted_results = []
        for test_run in test_runs:
            test_run_info = format_test_run(test_run)
            formatted_results.append(test_run_info)

        return "\n\n".join(formatted_results)
    
    except Exception as e:
        return f"There was a problem using this tool: {e}"

def register_tools(mcp) -> None:
    """
    Register product test runs tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_test_runs(product_id: int) -> str:
        """
        Retrieves a list of the test runs in the specified product
        
        Use this tool when you need to:
        - View the list of test runs in the specified product
        - Get information about multiple test runs at once
        - Access the full description and selected fields of test runs

        Args:
            product_id: The numeric ID of the product. If the ID is PR:45, just use 45. 
        
        Returns:
            Formatted string containing comprehensive information for the
            requested list of test runs, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_test_runs_impl(spira_client, product_id)
        except Exception as e:
            return f"Error: {str(e)}"
