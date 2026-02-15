"""
Unit tests for program artifacts tools __init__ module
"""

from unittest.mock import Mock, patch

import pytest


@pytest.mark.unit
class TestRegisterTools:
    """Test suite for program artifacts tools registration."""

    @patch("mcp_server_spira.features.programartifacts.tools.milestones.register_tools")
    @patch("mcp_server_spira.features.programartifacts.tools.capabilities.register_tools")
    def test_register_tools_calls_all_modules(
        self, mock_capabilities_register, mock_milestones_register
    ):
        """Test that register_tools calls all module registration functions."""
        from mcp_server_spira.features.programartifacts.tools import register_tools

        mock_mcp = Mock()

        # Call register_tools
        register_tools(mock_mcp)

        # Verify both modules were registered
        mock_milestones_register.assert_called_once_with(mock_mcp)
        mock_capabilities_register.assert_called_once_with(mock_mcp)

    @patch("mcp_server_spira.features.programartifacts.tools.milestones.register_tools")
    @patch("mcp_server_spira.features.programartifacts.tools.capabilities.register_tools")
    def test_register_tools_order(self, mock_capabilities_register, mock_milestones_register):
        """Test that tools are registered in the correct order."""
        from mcp_server_spira.features.programartifacts.tools import register_tools

        mock_mcp = Mock()
        call_order = []

        # Track call order
        mock_milestones_register.side_effect = lambda mcp: call_order.append("milestones")
        mock_capabilities_register.side_effect = lambda mcp: call_order.append("capabilities")

        # Call register_tools
        register_tools(mock_mcp)

        # Verify order: milestones first, then capabilities
        assert call_order == ["milestones", "capabilities"]
