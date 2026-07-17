"""Update tools for Spira artifacts."""

from mcp_server_spira.features.update.tools import product


def register_tools(mcp) -> None:
    """
    Register all update tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    product.register_tools(mcp)
