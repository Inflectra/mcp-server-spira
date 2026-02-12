"""Formatting features for converting artifacts to markdown."""

# Export all formatting functions from common module
from mcp_server_spira.features.formatting import tools
from mcp_server_spira.features.formatting.common import (
    format_automation_host,
    format_capability,
    format_incident,
    format_milestone,
    format_product,
    format_product_template,
    format_program,
    format_release,
    format_requirement,
    format_risk,
    format_task,
    format_test_case,
    format_test_case_folder,
    format_test_run,
    format_test_set,
    format_test_set_folder,
)

__all__ = [
    "format_automation_host",
    "format_capability",
    "format_incident",
    "format_milestone",
    "format_product",
    "format_product_template",
    "format_program",
    "format_release",
    "format_requirement",
    "format_risk",
    "format_task",
    "format_test_case",
    "format_test_case_folder",
    "format_test_run",
    "format_test_set",
    "format_test_set_folder",
]


def register(mcp) -> None:
    """
    Register formatting features with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    tools.register_tools(mcp)
