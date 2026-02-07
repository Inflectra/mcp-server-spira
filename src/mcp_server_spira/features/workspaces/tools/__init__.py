"""
Workspace tools for Spira by Inflectra
"""

from mcp_server_spira.features.workspaces.tools import product_templates, products, programs


def register_tools(mcp) -> None:
    """
    Register all workspace tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    products.register_tools(mcp)
    programs.register_tools(mcp)
    product_templates.register_tools(mcp)
