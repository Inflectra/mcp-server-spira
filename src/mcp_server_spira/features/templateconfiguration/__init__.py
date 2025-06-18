# Template configuration feature package for Inflectra Spira MCP
from mcp_server_spira.features.mywork import tools


def register(mcp):
    """
    Register all template configuration components with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    tools.register_tools(mcp)