# Inflectra Spira MCP features package
from mcp_server_spira.features import (
    mywork, productartifacts, programartifacts, templateconfiguration, workspaces, automation
)



def register_all(mcp):
    """
    Register all features with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    mywork.register(mcp)
    productartifacts.register(mcp)
    programartifacts.register(mcp)
    templateconfiguration.register(mcp)
    workspaces.register(mcp)
    automation.register(mcp)
