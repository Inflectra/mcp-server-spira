"""Utility layer — HTTP client, response helpers, and MCP prompts.

Owns: SpiraClient (async HTTP), common response/validation/pagination helpers,
and MCP prompt registration.
Exports: register_all_prompts(mcp).
Key modules: spira_client.py, conventions_prompt.py, common/ (subpackage).
"""

from mcp_server_spira.utils.conventions_prompt import register_prompt


def register_all_prompts(mcp):
    """
    Register prompts with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    # Register prompts here
    register_prompt(mcp)
