# Feature: tool-discovery-scalability, Property 5: Token estimation uses the 4-character-per-token ratio
"""
Token budget monitoring test for the MCP tools/list response.

Estimates the total token footprint of all registered tools (names + docstrings +
parameter schemas) using the 4-characters-per-token approximation.

Thresholds:
  - > 40,000 tokens: emit a warning
  - > 60,000 tokens: fail the test

Requirements: 7.1, 7.2, 7.3, 7.4
"""

import json
import warnings

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from mcp_server_spira.server import mcp

pytestmark = pytest.mark.unit

# Token estimation thresholds (Requirements 7.2, 7.3)
WARN_THRESHOLD = 40_000
FAIL_THRESHOLD = 60_000

# Characters per token approximation (Requirement 7.4)
CHARS_PER_TOKEN = 4


def _build_tools_list_text() -> str:
    """Build a text representation of all tools (name + docstring + parameter schema).

    This approximates the full tools/list response that an LLM client would receive.
    """
    parts: list[str] = []
    for tool_name, tool in mcp._tool_manager._tools.items():
        parts.append(tool_name)
        if tool.description:
            parts.append(tool.description)
        if tool.parameters:
            parts.append(json.dumps(tool.parameters))
    return "\n".join(parts)


def _estimate_tokens(text: str) -> int:
    """Estimate token count using the 4-characters-per-token ratio (Requirement 7.4)."""
    return len(text) // CHARS_PER_TOKEN


def test_token_budget():
    """Estimate the token footprint of the tools/list response and enforce budget thresholds.

    Warns at 40,000 tokens and fails at 60,000 tokens (Requirements 7.2, 7.3).
    Uses the 4-character-per-token approximation (Requirement 7.4).
    """
    text = _build_tools_list_text()
    tokens = _estimate_tokens(text)

    print(f"\ntools/list token estimate: {tokens:,} tokens ({len(text):,} chars)")
    print(f"  Warn threshold:  {WARN_THRESHOLD:,} tokens")
    print(f"  Fail threshold:  {FAIL_THRESHOLD:,} tokens")

    if tokens > FAIL_THRESHOLD:
        pytest.fail(
            f"tools/list token estimate ({tokens:,}) exceeds the failure threshold "
            f"({FAIL_THRESHOLD:,}). Reduce tool docstrings or split into sub-servers."
        )

    if tokens > WARN_THRESHOLD:
        warnings.warn(
            f"tools/list token estimate ({tokens:,}) exceeds the warning threshold "
            f"({WARN_THRESHOLD:,}). Consider reducing docstring verbosity.",
            UserWarning,
            stacklevel=2,
        )


# Feature: tool-discovery-scalability, Property 5: Token estimation uses the 4-character-per-token ratio


@given(st.text())
@settings(max_examples=100)
def test_token_estimation_formula(s: str):
    """Property 5: Token estimation uses the 4-character-per-token ratio.

    For any string input, _estimate_tokens must return len(s) // 4,
    consistent with the defined approximation method (Requirement 7.4).
    """
    assert _estimate_tokens(s) == len(s) // CHARS_PER_TOKEN
