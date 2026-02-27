"""
Naming convention tests for all registered MCP tools.

Validates that every tool name follows the scope-prefix + verb convention
defined in the tool-discovery-scalability feature spec.

Properties tested:
  Property 1: All tool names start with a valid scope prefix
  Property 2: All tool names follow the prefix-verb convention
"""

import pytest

from mcp_server_spira.server import mcp

pytestmark = pytest.mark.unit

# Valid scope prefixes as defined in Requirements 2.2 and design.md
VALID_PREFIXES = (
    "my_",
    "product_",
    "program_",
    "template_",
    "system_",
    "automation_",
    "spec_",
    "format_",
)

# Recognized verbs that must follow the scope prefix (Requirements 2.4)
VALID_VERBS = ("get_", "create_", "record_", "format_", "list_")


def get_all_tool_names() -> list[str]:
    """Return all registered tool names from the MCP server."""
    return list(mcp._tool_manager._tools.keys())


# Feature: tool-discovery-scalability, Property 1: All tool names start with a valid scope prefix
@pytest.mark.parametrize("tool_name", get_all_tool_names())
def test_tool_name_has_valid_prefix(tool_name: str):
    """Every registered tool name must start with a valid scope prefix."""
    assert any(tool_name.startswith(p) for p in VALID_PREFIXES), (
        f"Tool '{tool_name}' does not start with a valid prefix. Valid prefixes: {VALID_PREFIXES}"
    )


# Feature: tool-discovery-scalability, Property 2: All tool names follow the prefix-verb convention
@pytest.mark.parametrize("tool_name", get_all_tool_names())
def test_tool_name_has_valid_verb_after_prefix(tool_name: str):
    """After stripping the scope prefix, the remaining name must start with a recognized verb.

    Special case: when the prefix itself is a verb (e.g., 'format_'), the prefix
    satisfies the verb requirement and the remainder is the object (e.g., 'artifacts_as_markdown').
    """
    matched_prefix = next((p for p in VALID_PREFIXES if tool_name.startswith(p)), None)
    assert matched_prefix is not None, (
        f"Tool '{tool_name}' does not start with a valid prefix: {VALID_PREFIXES}"
    )
    remainder = tool_name[len(matched_prefix) :]
    # The prefix itself may be a verb (e.g., 'format_'), in which case the convention is satisfied
    prefix_is_verb = any(
        v in {matched_prefix, matched_prefix.rstrip("_") + "_"} for v in VALID_VERBS
    )
    assert prefix_is_verb or any(remainder.startswith(v) for v in VALID_VERBS), (
        f"Tool '{tool_name}': after stripping prefix '{matched_prefix}', "
        f"the remainder '{remainder}' does not start with a recognized verb. "
        f"Valid verbs: {VALID_VERBS}"
    )
