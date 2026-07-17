"""Workspaces feature — workspace_search and workspace_get tools.

Owns: discovery and retrieval of products, programs, and product templates.
Exports: register(mcp).
Key modules: tools/search.py, tools/get.py.
"""

# Workspaces feature package for Inflectra Spira MCP
from mcp_server_spira.features.workspaces import tools


def register(mcp):
    """
    Register all Workspaces components with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    tools.register_tools(mcp)
