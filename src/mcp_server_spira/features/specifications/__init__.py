# Specifications feature package for Inflectra Spira MCP
from mcp_server_spira.features.specifications import tools


def register(mcp):
    """
    Register all Specifications components with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    tools.register_tools(mcp)
