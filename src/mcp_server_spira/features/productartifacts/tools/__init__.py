"""
Product artifact tools for Spira by Inflectra
"""
from mcp_server_spira.features.productartifacts.tools import (
    releases,
    requirements,
    incidents,
    tasks,
    risks,
    testruns,
    automationhosts
)


def register_tools(mcp) -> None:
    """
    Register all product artifact tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    releases.register_tools(mcp)
    requirements.register_tools(mcp)
    incidents.register_tools(mcp)
    tasks.register_tools(mcp)
    risks.register_tools(mcp)
    testruns.register_tools(mcp)
    automationhosts.register_tools(mcp)
