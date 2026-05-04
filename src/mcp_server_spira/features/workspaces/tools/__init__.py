"""
Workspace tools for Spira by Inflectra
"""

from mcp_server_spira.features.workspaces.tools import get, search


def register_tools(mcp) -> None:
    """
    Register all workspace tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    search.register_tools(mcp)
    get.register_tools(mcp)
