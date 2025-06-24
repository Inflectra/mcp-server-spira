"""
Provides operations for working with the Spira product test sets

This module provides MCP tools for retrieving and updating product test sets
"""

from mcp_server_spira.features.formatting import format_test_set
from mcp_server_spira.features.formatting import format_test_set_folder
from mcp_server_spira.features.common import get_spira_client

def _get_test_sets_impl(spira_client, product_id: int) -> str:
    """
    Implementation of retrieving the list of test sets in the specified product, grouped by folder

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45. 
                
    Returns:
        Formatted string containing the list of test sets, grouped by folder
    """
    try:
        formatted_results = []

        # First we need to get any test sets not in a folder
        _get_test_sets_in_folder(spira_client, product_id, formatted_results, None)

        # Get the entire test set folder hierarchy in the product
        test_set_folders_url = f"projects/{product_id}/test-set-folders"
        test_set_folders = spira_client.make_spira_api_get_request(test_set_folders_url)

        # Loop through all the test set folders and format
        for test_set_folder in test_set_folders:
            test_set_folder_info = format_test_set_folder(test_set_folder)
            formatted_results.append(test_set_folder_info)

            # Now get all of the test sets in the folder
            _get_test_sets_in_folder(spira_client, product_id, formatted_results, test_set_folder)

        return "\n\n".join(formatted_results)
    
    except Exception as e:
        return f"There was a problem using this tool: {e}"

def _get_test_sets_in_folder(spira_client, product_id: int, formatted_results: list[str], test_set_folder):
    """
    Implementation of retrieving the list of test sets in the specified product, grouped by folder

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45. 
                
    Returns:
        Formatted string containing the list of test sets, grouped by folder
    """
    try:
        # Get the test set folder id
        test_set_folder_id = 'null'
        release_id = 'null'
        if test_set_folder:
            test_set_folder_id = str(test_set_folder['TestSetFolderId'])

        # Get the test sets in the folder
        test_sets_url = f"projects/{product_id}/test-set-folders/{test_set_folder_id}/test-sets/search?starting_row=1&number_of_rows=1000&sort_field=Name&sort_direction=ASC&release_id={release_id}"
        test_sets = spira_client.make_spira_api_get_request(test_sets_url)

        # Loop through all the test sets and format
        for test_set in test_sets:
            test_set_info = format_test_set(test_set)
            formatted_results.append(test_set_info)

    except Exception as e:
        raise Exception(f"Error returned when getting the test sets in the folder. The error message was: {e}")

def register_tools(mcp) -> None:
    """
    Register product test sets tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_test_sets(product_id: int) -> str:
        """
        Retrieves a list of the test sets in the specified product, grouped by folder
        
        Use this tool when you need to:
        - View the list of test sets in the specified product
        - Get information about multiple test sets at once
        - Access the full description and selected fields of test sets

        Args:
            product_id: The numeric ID of the product. If the ID is PG:45, just use 45. 
        
        Returns:
            Formatted string containing comprehensive information for the
            requested list of test sets, including name, id, description and key fields,
            grouped by the test set folder, formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_test_sets_impl(spira_client, product_id)
        except Exception as e:
            return f"Error: {str(e)}"
