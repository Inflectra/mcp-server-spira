"""
Product artifact tools for Spira by Inflectra
"""
from mcp_server_spira.features.productartifacts.tools import (
    releases
)


def register_tools(mcp) -> None:
    """
    Register all product artifact tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    releases.register_tools(mcp)
    