"""
Automation tools for Spira by Inflectra
"""
from mcp_server_spira.features.automation.tools import (
    automatedtestruns, builds
)


def register_tools(mcp) -> None:
    """
    Register all automation tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    automatedtestruns.register_tools(mcp)
    builds.register_tools(mcp)
    