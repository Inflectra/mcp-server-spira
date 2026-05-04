"""Formatting features — local-only tools (no Spira API calls)."""

from mcp_server_spira.features.formatting import tools


def register(mcp) -> None:
    """
    Register formatting features with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    tools.register_tools(mcp)
