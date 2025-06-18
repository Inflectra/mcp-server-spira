# Product Artifacts feature package for Inflectra Spira MCP
from mcp_server_spira.features.productartifacts import tools


def register(mcp):
    """
    Register all product artifacts components with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    tools.register_tools(mcp)