"""
Tool annotation tests for all registered MCP tools.

Validates that every tool has correct MCP annotations matching its behavior,
as defined in the tool-discovery-scalability feature spec.

Properties tested:
  Property 3: All tools have correct annotations matching their behavior
    - readOnlyHint is true for read-only tools and false for write tools
    - openWorldHint is true for tools that call the Spira API and false for local-only tools
    - destructiveHint is false for all current tools

# Feature: tool-discovery-scalability, Property 3: All tools have correct annotations matching their behavior
"""

import pytest

from mcp_server_spira.server import mcp

pytestmark = pytest.mark.unit

# Expected annotations for all 33 registered tools.
# Format: tool_name -> {"readOnlyHint": bool, "destructiveHint": bool, "openWorldHint": bool}
EXPECTED_ANNOTATIONS: dict[str, dict[str, bool]] = {
    # my_ scope — current user's personal work items (read-only, external API)
    "my_get_tasks": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    "my_get_incidents": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    "my_get_requirements": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "my_get_test_cases": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "my_get_test_sets": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    # product_ scope — product-scoped artifacts (read-only, external API)
    "product_get_tasks": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "product_get_incidents": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "product_get_requirements": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "product_get_releases": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "product_get_release_by_id": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "product_get_risks": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "product_get_test_runs": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "product_get_test_cases": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "product_get_test_sets": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "product_get_automation_hosts": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    # product_ scope — write operations (create new records, external API)
    "product_create_automated_test_run": {
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "product_create_build": {
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    # program_ scope — program-scoped artifacts (read-only, external API)
    "program_get_milestones": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "program_get_capabilities": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    # system_ scope — instance-wide operations (read-only, external API)
    "system_get_products": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "system_get_product_by_id": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "system_get_programs": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "system_get_program_products": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "system_get_product_templates": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "system_get_product_template": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "system_get_artifact_types": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    # template_ scope — product template configuration (read-only, external API)
    "template_get_custom_properties": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    # spec_ scope — specification document structures (read-only, external API)
    "spec_get_requirements": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "spec_get_design": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "spec_get_tasks": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    "spec_get_test_cases": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
    # format_ scope — local-only data transformation (read-only, NO external API call)
    "format_artifacts_as_markdown": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": False,
    },
    # system_ scope — local-only schema introspection (read-only, NO external API call)
    "system_get_artifact_schema": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": False,
    },
}


def get_all_tool_names() -> list[str]:
    """Return all registered tool names from the MCP server."""
    return list(mcp._tool_manager._tools.keys())


# Feature: tool-discovery-scalability, Property 3: All tools have correct annotations matching their behavior
@pytest.mark.parametrize("tool_name", get_all_tool_names())
def test_tool_has_annotations(tool_name: str):
    """Every registered tool must have annotations set (not None)."""
    tool = mcp._tool_manager._tools[tool_name]
    assert tool.annotations is not None, (
        f"Tool '{tool_name}' has no annotations. "
        "All tools must have readOnlyHint, destructiveHint, and openWorldHint set."
    )


# Feature: tool-discovery-scalability, Property 3: All tools have correct annotations matching their behavior
@pytest.mark.parametrize("tool_name", get_all_tool_names())
def test_tool_annotations_match_expected(tool_name: str):
    """Each tool's annotations must match the expected values defined in EXPECTED_ANNOTATIONS."""
    assert tool_name in EXPECTED_ANNOTATIONS, (
        f"Tool '{tool_name}' is not in EXPECTED_ANNOTATIONS. "
        "Add it to the expected annotations dict in this test file."
    )
    tool = mcp._tool_manager._tools[tool_name]
    annotations = tool.annotations
    assert annotations is not None, f"Tool '{tool_name}' has no annotations set."
    expected = EXPECTED_ANNOTATIONS[tool_name]

    assert annotations.readOnlyHint == expected["readOnlyHint"], (
        f"Tool '{tool_name}': readOnlyHint={annotations.readOnlyHint}, "
        f"expected {expected['readOnlyHint']}"
    )
    assert annotations.destructiveHint == expected["destructiveHint"], (
        f"Tool '{tool_name}': destructiveHint={annotations.destructiveHint}, "
        f"expected {expected['destructiveHint']}"
    )
    assert annotations.openWorldHint == expected["openWorldHint"], (
        f"Tool '{tool_name}': openWorldHint={annotations.openWorldHint}, "
        f"expected {expected['openWorldHint']}"
    )


def test_all_expected_tools_are_registered():
    """Every tool in EXPECTED_ANNOTATIONS must be registered with the MCP server."""
    registered = set(mcp._tool_manager._tools.keys())
    missing = set(EXPECTED_ANNOTATIONS.keys()) - registered
    assert not missing, (
        f"The following tools are in EXPECTED_ANNOTATIONS but not registered: {sorted(missing)}"
    )


# Feature: artifact-schema-tool, Property 3: No registered tool description contains "Key Fields"
# Validates: Requirements 3.1, 3.3
@pytest.mark.parametrize("tool_name", get_all_tool_names())
def test_no_tool_description_contains_key_fields(tool_name: str):
    """No registered tool's docstring should contain an inline 'Key Fields' section."""
    tool = mcp._tool_manager._tools[tool_name]
    description = tool.fn.__doc__ or ""
    assert "Key Fields" not in description, (
        f"Tool '{tool_name}' still contains a 'Key Fields' section in its docstring. "
        "Replace it with a pointer to system_get_artifact_schema."
    )
