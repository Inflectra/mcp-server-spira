"""
Unit tests for program artifacts __init__ module
"""

from unittest.mock import Mock, patch

import pytest


@pytest.mark.unit
class TestRegister:
    """Test suite for program artifacts registration."""

    @patch("mcp_server_spira.features.programartifacts.tools.register_tools")
    def test_register_calls_tools_register(self, mock_tools_register):
        """Test that register calls tools.register_tools."""
        from mcp_server_spira.features.programartifacts import register

        mock_mcp = Mock()

        # Call register
        register(mock_mcp)

        # Verify tools.register_tools was called
        mock_tools_register.assert_called_once_with(mock_mcp)

    @patch("mcp_server_spira.features.programartifacts.tools.register_tools")
    def test_register_passes_mcp_instance(self, mock_tools_register):
        """Test that register passes the MCP instance correctly."""
        from mcp_server_spira.features.programartifacts import register

        mock_mcp = Mock()
        mock_mcp.name = "test_mcp_server"

        # Call register
        register(mock_mcp)

        # Verify the same MCP instance was passed
        call_args = mock_tools_register.call_args
        assert call_args[0][0] is mock_mcp
