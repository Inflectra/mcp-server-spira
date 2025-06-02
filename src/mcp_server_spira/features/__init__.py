# Inflectra Spira MCP features package
from mcp_server_spira.features import mywork


def register_all(mcp):
    """
    Register all features with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    mywork.register(mcp)
