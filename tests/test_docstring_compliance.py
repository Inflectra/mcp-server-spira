"""
Docstring compliance tests for all registered MCP tools.

Asserts that every tool docstring is <= 50 lines, per AC-1.10.1.
Reports line counts for all tools to aid remediation.

Final Per-Tool Line Counts (Task 24 - All tools pass 50-line limit):
  get_test_runs                                    49  OK
  get_test_sets                                    47  OK
  get_test_cases                                   47  OK
  get_tasks                                        47  OK
  get_risks                                        46  OK
  get_incidents                                    45  OK
  get_my_testsets                                  44  OK
  get_my_testcases                                 44  OK
  get_my_requirements                              44  OK
  get_my_incidents                                 44  OK
  get_my_tasks                                     44  OK
  get_releases                                     43  OK
  get_requirements                                 43  OK
  format_artifacts_as_markdown                     40  OK
  get_automation_hosts                             39  OK
  get_custom_properties                            39  OK
  get_capabilities                                 37  OK
  get_products                                     36  OK
  get_milestones                                   36  OK
  get_artifact_types                               36  OK
  get_programs                                     33  OK
  get_product_templates                            32  OK
  get_release_by_id                                32  OK
  record_automated_test_run                        28  OK
  create_build                                     28  OK
  get_specification_test_cases                     25  OK
  get_specification_tasks                          24  OK
  get_specification_requirements                   24  OK
  get_specification_design                         24  OK
  get_program_products                             18  OK
  get_product_template                             15  OK
  get_product_by_id                                15  OK

  Total tools: 33
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
