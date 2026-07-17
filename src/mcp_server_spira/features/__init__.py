"""Feature packages for the Spira MCP Server.

Owns: all MCP tool registrations and their _impl functions.
Exports: register_all(mcp) — the single entry point for server.py.
Key packages: search, create, update, metadata, workspaces, formatting, comments.
"""

# Inflectra Spira MCP features package
from mcp_server_spira.features import (
    associations,  # noqa: F401 — registers enrichment strategies at import time
    comments,
    create,
    formatting,
    metadata,
    update,
    workspaces,
)
from mcp_server_spira.features.search import tools as search_tools


def register_all(mcp):
    """
    Register all features with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    metadata.register(mcp)
    workspaces.register(mcp)
    create.register(mcp)
    update.register(mcp)
    comments.register(mcp)
    associations.register(mcp)
    formatting.register(mcp)
    search_tools.register_tools(mcp)
