"""
Specifications tools for Spira by Inflectra
"""

from mcp_server_spira.features.specifications.tools import productspecification


def register_tools(mcp) -> None:
    """
    Register all specification tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    productspecification.register_tools(mcp)
