"""Associations & coverage feature package.

Owns: enrichment strategies (Tier 2) and the create_association tool.
Exports: register(mcp) — wires the tool into the MCP server.

Enrichment strategies are registered at import time via the strategies module.
"""

# Import strategies to register them in ENRICHMENT_STRATEGIES at import time.
from mcp_server_spira.features.associations import strategies as _strategies  # noqa: F401
from mcp_server_spira.features.associations import tools


def register(mcp) -> None:
    """Register all association features with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    tools.register_tools(mcp)
