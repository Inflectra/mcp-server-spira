"""
Tests for the My Task features of the Inflectra Spira MCP Server.
"""

from mcp_server_spira.features.mywork.tools.mytasks import get_spira_client
from mcp_server_spira.features.mywork.tools.mytasks import _get_my_tasks_impl


# Tests that we can get the list of my tasks in markdown format
def test_get_my_tasks_impl():
    spira_client = get_spira_client()
    results = _get_my_tasks_impl(spira_client)

    # Check that we get one of our expected tasks
    assert "[TK:123]" in results
