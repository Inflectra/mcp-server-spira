"""
Unit tests for product automation hosts tools
"""

import json
from unittest.mock import Mock, patch

import pytest

from mcp_server_spira.features.productartifacts.tools.automationhosts import (
    _get_automation_hosts_impl,
    register_tools,
)


def capture_registered_tool(mcp_mock, tool_name):
    """Helper to capture a tool registered via decorator."""
    captured_func = None

    def mock_tool(**kwargs):
        def decorator(func):
            nonlocal captured_func
            captured_func = func
            return func

        return decorator

    mcp_mock.tool = mock_tool
    register_tools(mcp_mock)
    return captured_func


class TestGetAutomationHostsImpl:
    """Test suite for _get_automation_hosts_impl helper function."""

    @pytest.fixture
    def mock_spira_client(self):
        """Create mock SpiraClient."""
        return Mock()

    def test_successful_retrieval(self, mock_spira_client):
        """Test successful automation host retrieval."""
        mock_hosts = [
            {
                "AutomationHostId": 1,
                "Name": "Build Server 01",
                "Active": True,
                "ProjectId": 55,
            }
        ]
        mock_spira_client.make_spira_api_post_request.return_value = mock_hosts

        result = _get_automation_hosts_impl(mock_spira_client, product_id=55)
        response = json.loads(result)

        assert "data" in response
        assert len(response["data"]) == 1
        assert response["data"][0]["AutomationHostId"] == 1

    def test_pagination_parameters(self, mock_spira_client):
        """Test pagination parameters are passed correctly."""
        mock_spira_client.make_spira_api_post_request.return_value = []

        _get_automation_hosts_impl(
            mock_spira_client,
            product_id=55,
            starting_row=10,
            number_of_rows=50,
        )

        call_args = mock_spira_client.make_spira_api_post_request.call_args
        assert "starting_row=10" in call_args[0][0]
        assert "number_of_rows=50" in call_args[0][0]

    def test_api_error_handling(self, mock_spira_client):
        """Test API error handling."""
        mock_spira_client.make_spira_api_post_request.side_effect = Exception("API error")

        result = _get_automation_hosts_impl(mock_spira_client, product_id=55)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "API_ERROR"


class TestGetAutomationHostsMCPWrapper:
    """Test suite for MCP tool wrapper."""

    def test_tool_registration(self):
        """Test that get_automation_hosts tool is registered."""
        mock_mcp = Mock()
        captured_tool = capture_registered_tool(mock_mcp, "get_automation_hosts")
        assert captured_tool is not None

    @patch("mcp_server_spira.features.productartifacts.tools.automationhosts.get_spira_client")
    def test_successful_call_through_wrapper(self, mock_get_client):
        """Test successful call through MCP wrapper."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []
        mock_get_client.return_value = mock_client

        mock_mcp = Mock()
        get_automation_hosts = capture_registered_tool(mock_mcp, "get_automation_hosts")

        result = get_automation_hosts(product_id=55)
        response = json.loads(result)

        assert "data" in response

    @patch("mcp_server_spira.features.productartifacts.tools.automationhosts.get_spira_client")
    def test_validation_error_invalid_product_id(self, mock_get_client):
        """Test validation error for invalid product_id."""
        mock_mcp = Mock()
        get_automation_hosts = capture_registered_tool(mock_mcp, "get_automation_hosts")

        result = get_automation_hosts(product_id=-1)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"

    @patch("mcp_server_spira.features.productartifacts.tools.automationhosts.get_spira_client")
    def test_validation_error_invalid_starting_row(self, mock_get_client):
        """Test validation error for invalid starting_row."""
        mock_mcp = Mock()
        get_automation_hosts = capture_registered_tool(mock_mcp, "get_automation_hosts")

        result = get_automation_hosts(product_id=55, starting_row=0)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"

    @patch("mcp_server_spira.features.productartifacts.tools.automationhosts.get_spira_client")
    def test_validation_error_invalid_number_of_rows(self, mock_get_client):
        """Test validation error for invalid number_of_rows."""
        mock_mcp = Mock()
        get_automation_hosts = capture_registered_tool(mock_mcp, "get_automation_hosts")

        result = get_automation_hosts(product_id=55, number_of_rows=0)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"

    @patch("mcp_server_spira.features.productartifacts.tools.automationhosts.get_spira_client")
    def test_exception_handling_in_wrapper(self, mock_get_client):
        """Test exception handling in wrapper."""
        mock_get_client.side_effect = Exception("Client error")

        mock_mcp = Mock()
        get_automation_hosts = capture_registered_tool(mock_mcp, "get_automation_hosts")

        result = get_automation_hosts(product_id=55)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "API_ERROR"

    @patch("mcp_server_spira.features.productartifacts.tools.automationhosts.get_spira_client")
    def test_all_parameters_passed_through(self, mock_get_client):
        """Test all parameters are passed through correctly."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []
        mock_get_client.return_value = mock_client

        mock_mcp = Mock()
        get_automation_hosts = capture_registered_tool(mock_mcp, "get_automation_hosts")

        get_automation_hosts(
            product_id=55,
            starting_row=10,
            number_of_rows=50,
        )

        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        assert "projects/55/automation-hosts/search" in url
        assert "starting_row=10" in url
        assert "number_of_rows=50" in url
