# Workspaces feature package for Inflectra Spira MCP
from mcp_server_spira.features.workspaces import tools


def register(mcp):
    """
    Register all Workspaces components with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    tools.register_tools(mcp)