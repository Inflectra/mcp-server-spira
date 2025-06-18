# Program Artifacts feature package for Inflectra Spira MCP
from mcp_server_spira.features.programartifacts import tools


def register(mcp):
    """
    Register all program artifact components with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    tools.register_tools(mcp)