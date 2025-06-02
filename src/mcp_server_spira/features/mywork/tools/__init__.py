"""
My assigned work tools for Spira by Inflectra
"""
from mcp_server_spira.features.mywork.tools import (
    mytasks,
)


def register_tools(mcp) -> None:
    """
    Register all work item tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    mytasks.register_tools(mcp)