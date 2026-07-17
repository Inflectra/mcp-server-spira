"""Create tools for Spira artifacts."""

from mcp_server_spira.features.create.tools import product, test_run


def register_tools(mcp) -> None:
    """
    Register all create tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    product.register_tools(mcp)
    test_run.register_tools(mcp)
