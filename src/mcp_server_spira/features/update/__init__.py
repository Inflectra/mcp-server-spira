"""Update feature package — tools for updating Spira artifacts."""

from mcp_server_spira.features.update import tools


def register(mcp) -> None:
    """
    Register all update features with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    tools.register_tools(mcp)
