"""
Template configuration tools for Spira by Inflectra
"""
from mcp_server_spira.features.templateconfiguration.tools import (
    products, programs, templates
)


def register_tools(mcp) -> None:
    """
    Register all template configurationspace tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    products.register_tools(mcp)
    programs.register_tools(mcp)
    templates.register_tools(mcp)
    