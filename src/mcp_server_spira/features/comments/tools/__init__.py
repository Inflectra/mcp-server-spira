"""Comment tools for Spira artifacts."""

from mcp_server_spira.features.comments.tools import create


def register_tools(mcp) -> None:
    """Register all comment tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    create.register_tools(mcp)
