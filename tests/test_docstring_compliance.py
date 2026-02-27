"""
Docstring compliance tests for all registered MCP tools.

Asserts that every tool docstring is <= 50 lines, per AC-1.10.1.
Reports line counts for all tools to aid remediation.

Final Per-Tool Line Counts (Task 10 - All tools pass 50-line limit, scope-prefixed names):
  product_get_test_runs                            50  OK
  product_get_risks                                50  OK
  product_get_tasks                                47  OK
  product_get_test_cases                           47  OK
  product_get_test_sets                            47  OK
  product_get_incidents                            45  OK
  product_get_releases                             44  OK
  my_get_test_sets                                 44  OK
  my_get_test_cases                                44  OK
  my_get_requirements                              44  OK
  my_get_incidents                                 44  OK
  my_get_tasks                                     44  OK
  product_get_requirements                         43  OK
  system_get_product_by_id                         46  OK
  system_get_product_template                      46  OK
  format_artifacts_as_markdown                     40  OK
  product_get_automation_hosts                     40  OK
  template_get_custom_properties                   39  OK
  system_get_programs                              39  OK
  program_get_capabilities                         37  OK
  system_get_products                              42  OK
  program_get_milestones                           36  OK
  system_get_artifact_types                        36  OK
  system_get_product_templates                     36  OK
  product_get_release_by_id                        32  OK
  product_create_automated_test_run                28  OK
  product_create_build                             28  OK
  spec_get_test_cases                              24  OK
  spec_get_tasks                                   24  OK
  spec_get_requirements                            24  OK
  spec_get_design                                  24  OK
  system_get_program_products                      47  OK

  Total tools: 32
  Over 50 lines: 0
"""

import pytest

from mcp_server_spira.server import mcp

pytestmark = pytest.mark.unit

# Maximum allowed lines per tool docstring (AC-1.10.1)
MAX_DOCSTRING_LINES = 50


def _get_tool_docstring_lengths() -> dict[str, int]:
    """Return a mapping of tool name -> docstring line count."""
    tools = mcp._tool_manager._tools
    return {name: len((tool.fn.__doc__ or "").splitlines()) for name, tool in tools.items()}


def test_all_tool_docstring_line_counts():
    """Report docstring line counts for every registered tool (informational)."""
    counts = _get_tool_docstring_lengths()
    print("\nTool docstring line counts:")
    print(f"  {'Tool':<45} {'Lines':>5}  {'Status'}")
    print(f"  {'-' * 45}  {'-' * 5}  {'-' * 6}")
    for name, lines in sorted(counts.items(), key=lambda x: -x[1]):
        status = "OK" if lines <= MAX_DOCSTRING_LINES else "OVER"
        print(f"  {name:<45} {lines:>5}  {status}")
    print(f"\n  Total tools: {len(counts)}")
    over = {n: line_count for n, line_count in counts.items() if line_count > MAX_DOCSTRING_LINES}
    print(f"  Over {MAX_DOCSTRING_LINES} lines: {len(over)}")


@pytest.mark.parametrize(
    "tool_name,line_count",
    sorted(_get_tool_docstring_lengths().items()),
)
def test_tool_docstring_within_limit(tool_name: str, line_count: int):
    """Each tool docstring must be <= 50 lines (AC-1.10.1)."""
    assert line_count <= MAX_DOCSTRING_LINES, (
        f"Tool '{tool_name}' docstring is {line_count} lines "
        f"(limit: {MAX_DOCSTRING_LINES}). "
        f"Reduce by {line_count - MAX_DOCSTRING_LINES} lines."
    )
