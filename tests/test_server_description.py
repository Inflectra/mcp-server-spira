"""
Server instructions tests for the Spira MCP Server.

Validates that the FastMCP server instructions are set, concise, and contain
the expected scope prefixes and tool count, as defined in the
tool-discovery-scalability feature spec.

Requirements tested:
  Requirement 1.1: Server instructions summarize purpose, list scope prefixes, include tool count
  Requirement 1.2: Server instructions are returned as part of server metadata
  Requirement 1.3: Server instructions are no longer than 1000 characters
  Requirement 1.4: Server instructions list each scope prefix with a one-line explanation
"""

import pytest

from mcp_server_spira.server import mcp

pytestmark = pytest.mark.unit

# Active scope prefixes that must appear in the server description (Requirements 1.1, 1.4).
# The automation_ prefix is intentionally omitted — no current tools use it and
# the design doc specifies it should be omitted from the description.
ACTIVE_SCOPE_PREFIXES = (
    "my_",
    "product_",
    "program_",
    "template_",
    "system_",
    "spec_",
    "format_",
)


# Feature: tool-discovery-scalability, Requirement 1.1 / 1.2
def test_server_description_is_set():
    """The MCP server must have a non-None, non-empty description."""
    # Requirement 1.1: Server SHALL include a Server_Description in its initialization
    # Requirement 1.2: Server SHALL return the description as part of server metadata
    assert mcp.instructions is not None, "mcp.instructions must not be None"
    assert mcp.instructions.strip() != "", "mcp.instructions must not be empty"


# Feature: tool-discovery-scalability, Requirement 1.3
def test_server_description_under_1000_characters():
    """The server description must be no longer than 1000 characters."""
    # Requirement 1.3: Server_Description SHALL be no longer than 1000 characters
    description = mcp.instructions
    assert description is not None, "mcp.instructions must not be None"
    char_count = len(description)
    assert char_count < 1000, (
        f"Server description is {char_count} characters, must be under 1000. "
        f"Current description:\n{description}"
    )


# Feature: tool-discovery-scalability, Requirement 1.4
@pytest.mark.parametrize("prefix", ACTIVE_SCOPE_PREFIXES)
def test_server_description_contains_scope_prefix(prefix: str):
    """The server description must mention each active scope prefix."""
    # Requirement 1.4: Server_Description SHALL list each Scope_Prefix with a one-line explanation
    description = mcp.instructions
    assert description is not None, "mcp.instructions must not be None"
    assert prefix in description, (
        f"Server description does not contain scope prefix '{prefix}'. "
        "All active scope prefixes must be listed in the server description."
    )


# Feature: tool-discovery-scalability, Requirement 1.1
def test_server_description_contains_tool_count():
    """The server description must include the total tool count (33)."""
    # Requirement 1.1: Server_Description SHALL include the total tool count
    description = mcp.instructions
    assert description is not None, "mcp.instructions must not be None"
    assert "33" in description, (
        f"Server description does not contain the tool count '33'. "
        f"Current description:\n{description}"
    )
