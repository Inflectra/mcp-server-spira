"""Formatting tools for the MCP server."""

from . import artifact_schema, format_artifacts


def register_tools(mcp) -> None:
    """
    Register all formatting tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    format_artifacts.register_tools(mcp)
    artifact_schema.register_tools(mcp)
