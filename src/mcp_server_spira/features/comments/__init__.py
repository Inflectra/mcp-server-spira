"""Comments feature package — tools for creating comments on Spira artifacts."""

from mcp_server_spira.features.comments import tools


def register(mcp) -> None:
    """Register all comment features with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    tools.register_tools(mcp)
