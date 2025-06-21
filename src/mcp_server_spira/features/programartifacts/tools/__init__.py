"""
Program artifact tools for Spira by Inflectra
"""
from mcp_server_spira.features.programartifacts.tools import (
    milestones,
    capabilities
)


def register_tools(mcp) -> None:
    """
    Register all program artifact tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    milestones.register_tools(mcp)
    capabilities.register_tools(mcp)
