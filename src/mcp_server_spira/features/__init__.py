# Inflectra Spira MCP features package
from mcp_server_spira.features import (
    automation,
    formatting,
    metadata,
    workspaces,
)
from mcp_server_spira.features.search import tools as search_tools


def register_all(mcp):
    """
    Register all features with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    metadata.register(mcp)
    workspaces.register(mcp)
    automation.register(mcp)
    formatting.register(mcp)
    search_tools.register_tools(mcp)
