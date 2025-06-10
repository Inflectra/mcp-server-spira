"""
My assigned work tools for Spira by Inflectra
"""
from mcp_server_spira.features.mywork.tools import (
    mytasks,myincidents,myrequirements,mytestcases,mytestsets
)


def register_tools(mcp) -> None:
    """
    Register all work item tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    mytasks.register_tools(mcp)
    myincidents.register_tools(mcp)
    myrequirements.register_tools(mcp)
    mytestcases.register_tools(mcp)
    mytestsets.register_tools(mcp)
    