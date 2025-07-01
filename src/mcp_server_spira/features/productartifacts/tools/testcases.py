"""
Provides operations for working with the Spira product test cases

This module provides MCP tools for retrieving and updating product test cases
"""

from mcp_server_spira.features.formatting import format_test_case
from mcp_server_spira.features.formatting import format_test_case_folder
from mcp_server_spira.features.common import get_spira_client

def _get_test_cases_impl(spira_client, product_id: int) -> str:
    """
    Implementation of retrieving the list of test cases in the specified product, grouped by folder

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45. 
                
    Returns:
        Formatted string containing the list of test cases, grouped by folder
    """
    try:
        formatted_results = []

        # First we need to get any test cases not in a folder
        _get_test_cases_in_folder(spira_client, product_id, formatted_results, None)

        # Get the entire test case folder hierarchy in the product
        test_case_folders_url = f"projects/{product_id}/test-folders"
        test_case_folders = spira_client.make_spira_api_get_request(test_case_folders_url)

        # Loop through all the test case folders and format
        for test_case_folder in test_case_folders:
            test_case_folder_info = format_test_case_folder(test_case_folder)
            formatted_results.append(test_case_folder_info)

            # Now get all of the test cases in the folder
            _get_test_cases_in_folder(spira_client, product_id, formatted_results, test_case_folder)

        return "\n\n".join(formatted_results)
    
    except Exception as e:
        return f"There was a problem using this tool: {e}"

def _get_test_cases_in_folder(spira_client, product_id: int, formatted_results: list[str], test_case_folder):
    """
    Implementation of retrieving the list of test cases in the specified product, grouped by folder

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45. 
                
    Returns:
        Formatted string containing the list of test cases, grouped by folder
    """
    try:
        # Get the test case folder id
        test_case_folder_id = 'null'
        release_id = 'null'
        if test_case_folder:
            test_case_folder_id = str(test_case_folder['TestCaseFolderId'])

        # Get the test cases in the folder
        test_cases_url = f"projects/{product_id}/test-folders/{test_case_folder_id}/test-cases?starting_row=1&number_of_rows=1000&sort_field=Name&sort_direction=ASC&release_id={release_id}"
        test_cases = spira_client.make_spira_api_get_request(test_cases_url)

        # Loop through all the test cases and format
        for test_case in test_cases:
            test_case_info = format_test_case(test_case)
            formatted_results.append(test_case_info)

    except Exception as e:
        raise Exception(f"Error returned when getting the test cases in the folder. The error message was: {e}")

def register_tools(mcp) -> None:
    """
    Register product test cases tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_test_cases(product_id: int) -> str:
        """
        Retrieves a list of the test cases in the specified product, grouped by folder
        
        Use this tool when you need to:
        - View the list of test cases in the specified product
        - Get information about multiple test cases at once
        - Access the full description and selected fields of test cases

        Args:
            product_id: The numeric ID of the product. If the ID is PG:45, just use 45. 
        
        Returns:
            Formatted string containing comprehensive information for the
            requested list of test cases, including name, id, description and key fields,
            grouped by the test case folder, formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_test_cases_impl(spira_client, product_id)
        except Exception as e:
            return f"Error: {str(e)}"
