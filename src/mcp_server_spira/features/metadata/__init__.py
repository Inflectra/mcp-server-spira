"""Template metadata feature — template_get_metadata tool.

Owns: retrieval of types, statuses, priorities, severities, custom properties,
importances, probabilities, and impacts for a product template.
Exports: register(mcp).
Key module: tools/template.py (tool + _impl).
"""

# Template metadata feature package for Inflectra Spira MCP
from mcp_server_spira.features.metadata import tools


def register(mcp):
    """
    Register all template configuration components with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    tools.register_tools(mcp)
