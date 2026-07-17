"""Create feature package — tools for creating Spira artifacts."""

from mcp_server_spira.features.create import tools


def register(mcp) -> None:
    """
    Register all create features with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    tools.register_tools(mcp)
