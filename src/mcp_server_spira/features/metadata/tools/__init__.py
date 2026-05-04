"""
Template metadata tools for Spira by Inflectra
"""

from mcp_server_spira.features.metadata.tools import template


def register_tools(mcp) -> None:
    """
    Register all template configuration tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    template.register_tools(mcp)
