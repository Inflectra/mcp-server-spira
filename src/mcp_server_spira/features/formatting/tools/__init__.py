"""Formatting tools for the MCP server."""

from . import artifact_schema


def register_tools(mcp) -> None:
    """
    Register all formatting tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    artifact_schema.register_tools(mcp)
