"""
Provides operations for recording automated test run results into Spira

This module provides MCP tools for recording the results of automated
test against a matching test case in Spira 
"""

import datetime

from mcp_server_spira.features.common import get_spira_client

def _record_automated_test_run_impl(spira_client, product_id: int, test_name: str, short_message: str, long_message: str, error_count: int, test_case_id: int, execution_status_id: int) -> str:
    """
    Records an automated test result in Spira

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PG:45, just use 45.
        test_name: The name of the test being run
        short_message: A short description (50 characters or less) of the result of the test execution
        long_message: The full description of the testing outcome, in plain text format
        error_count: The number of errors that happened during the test (0 if none)
        test_case_id: The ID of the test case in Spira being executed, without the TC prefix (e.g. TC:12 would be 12)
        execution_status_id: The ID of the execution status of the test (1 = Failed, 2 = Passed, 3 = Not Run, 4 = N/A, 5 = Blocked and 6 = Caution)
                
    Returns:
        The ID of the new test run that was created (with 'TR' prefix)
    """
    try:
        # Make the start/end time right now
        start_time = datetime.datetime.now()
        end_time = datetime.datetime.now()

        # The body we are sending
        body = {
            # Constant for plain text
            'TestRunFormatId': 1,
            'StartDate': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'EndDate': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'RunnerName': "MCP Server",
            'RunnerTestName': test_name,
            'RunnerMessage': short_message,
            'RunnerStackTrace': long_message,
            'RunnerAssertCount': error_count,
            'TestCaseId': test_case_id,
            # Passes (2) if the stack trace length is 0
            'ExecutionStatusId': execution_status_id
        }

        # Record the test run using the API method
        record_automated_url = "projects/" + str(product_id) + "/test-runs/record "
        testrun = spira_client.make_spira_api_post_request(record_automated_url, body)

        if not testrun:
            return "The test run was not recorded successfully."

        # Extract the new test run
        test_run_id = testrun['TestRunId']

        return "TR:" + str(test_run_id)
    except Exception as e:
        return f"There was a problem using this tool: {e}"
    
def register_tools(mcp) -> None:
    """
    Register tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def record_automated_test_run(product_id: int, test_name: str, short_message: str, long_message: str, error_count: int, test_case_id: int, execution_status_id: int) -> str:
        """
        Records an automated test result in Spira
        
        Use this tool when you need to:
        - Push the results of an automated software test into Spira
                    
        Args:
            product_id: The numeric ID of the product. If the ID is PG:45, just use 45.
            test_name: The name of the test being run
            short_message: A short description (50 characters or less) of the result of the test execution
            long_message: The full description of the testing outcome, in plain text format
            error_count: The number of errors that happened during the test (0 if none)
            test_case_id: The ID of the test case in Spira being executed, without the TC prefix (e.g. TC:12 would be 12)
            execution_status_id: The ID of the execution status of the test (1 = Failed, 2 = Passed, 3 = Not Run, 4 = N/A, 5 = Blocked and 6 = Caution)

        Returns:
            The ID of the newly created test run in Spira, with a TR prefix added (for example TR:123)
        """
        try:
            spira_client = get_spira_client()
            return _record_automated_test_run_impl(spira_client, product_id, test_name, short_message, long_message, error_count, test_case_id, execution_status_id)
        except Exception as e:
            return f"Error: {str(e)}"
        