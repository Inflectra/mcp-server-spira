"""
Template configuration tools for Spira by Inflectra
"""
from mcp_server_spira.features.templateconfiguration.tools import (
    artifacttypes, customproperties
)


def register_tools(mcp) -> None:
    """
    Register all template configurationspace tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    artifacttypes.register_tools(mcp)
    customproperties.register_tools(mcp)
    