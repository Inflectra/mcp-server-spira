"""
Unit tests for product artifacts incidents tools.

Tests the get_incidents MCP tool wrapper, validation, and error handling.
"""

import json
from unittest.mock import Mock, patch

import pytest

from mcp_server_spira.features.productartifacts.tools.incidents import (
    _get_incidents_impl,
    register_tools,
)


def capture_registered_tool(register_func):
    """Helper to capture the tool function registered with MCP."""
    captured_func = None

    def capture_tool():
        def decorator(func):
            nonlocal captured_func
            captured_func = func
            return func

        return decorator

    mock_mcp = Mock()
    mock_mcp.tool = capture_tool
    register_func(mock_mcp)
    return captured_func


@pytest.mark.unit
class TestGetIncidentsImpl:
    """Tests for _get_incidents_impl helper function."""

    def test_successful_retrieval(self):
        """Test successful incident retrieval with default parameters."""
        mock_client = Mock()
        mock_incidents = [
            {
                "IncidentId": 456,
                "Name": "Login page crashes",
                "IncidentStatusName": "New",
                "ProjectId": 55,
            }
        ]
        mock_client.make_spira_api_post_request.return_value = mock_incidents

        result = _get_incidents_impl(mock_client, 55)

        # Verify POST request with empty filter array
        mock_client.make_spira_api_post_request.assert_called_once()
        call_args = mock_client.make_spira_api_post_request.call_args
        assert "projects/55/incidents/search" in call_args[0][0]
        assert call_args[0][1] == []

        # Verify JSON response structure
        parsed = json.loads(result)
        assert "data" in parsed
        assert len(parsed["data"]) == 1
        assert parsed["data"][0]["IncidentId"] == 456

    def test_pagination_parameters_start_row(self):
        """Test pagination parameters with start_row naming."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []

        _get_incidents_impl(mock_client, 55, start_row=10, number_rows=50)

        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        assert "start_row=10" in url
        assert "number_rows=50" in url

    def test_sort_parameter(self):
        """Test sort_by parameter is included when provided."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []

        _get_incidents_impl(mock_client, 55, sort_by="PriorityId")

        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        assert "sort_by=PriorityId" in url

    def test_api_error_handling(self):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.side_effect = Exception("API Error")

        result = _get_incidents_impl(mock_client, 55)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error"] == "Failed to retrieve incidents"
        assert parsed["error_code"] == "API_ERROR"


@pytest.mark.unit
class TestGetIncidentsMCPWrapper:
    """Tests for get_incidents MCP tool wrapper."""

    def test_tool_registration(self):
        """Test that get_incidents tool is registered with MCP."""
        mock_mcp = Mock()
        register_tools(mock_mcp)

        assert mock_mcp.tool.called
        assert mock_mcp.tool.call_count == 1

    @patch("mcp_server_spira.features.productartifacts.tools.incidents.get_spira_client")
    def test_successful_call_through_wrapper(self, mock_get_client):
        """Test successful call through MCP wrapper."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = [
            {"IncidentId": 456, "Name": "Test Incident"}
        ]
        mock_get_client.return_value = mock_client

        get_incidents_wrapper = capture_registered_tool(register_tools)
        result = get_incidents_wrapper(product_id=55)

        parsed = json.loads(result)
        assert "data" in parsed
        assert parsed["data"][0]["IncidentId"] == 456

    @patch("mcp_server_spira.features.productartifacts.tools.incidents.get_spira_client")
    def test_validation_error_invalid_product_id(self, mock_get_client):
        """Test validation error for invalid product_id."""
        get_incidents_wrapper = capture_registered_tool(register_tools)
        result = get_incidents_wrapper(product_id=-1)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "INVALID_VALUE"
        assert "product_id" in parsed["details"]["parameter"]

    @patch("mcp_server_spira.features.productartifacts.tools.incidents.get_spira_client")
    def test_validation_error_invalid_start_row(self, mock_get_client):
        """Test validation error for invalid start_row."""
        get_incidents_wrapper = capture_registered_tool(register_tools)
        result = get_incidents_wrapper(product_id=55, start_row=0)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "INVALID_VALUE"
        assert "start_row" in parsed["details"]["parameter"]

    @patch("mcp_server_spira.features.productartifacts.tools.incidents.get_spira_client")
    def test_validation_error_invalid_number_rows(self, mock_get_client):
        """Test validation error for invalid number_rows."""
        get_incidents_wrapper = capture_registered_tool(register_tools)
        result = get_incidents_wrapper(product_id=55, number_rows=0)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "INVALID_VALUE"
        assert "number_rows" in parsed["details"]["parameter"]

    @patch("mcp_server_spira.features.productartifacts.tools.incidents.get_spira_client")
    def test_exception_handling_in_wrapper(self, mock_get_client):
        """Test exception handling in MCP wrapper."""
        mock_get_client.side_effect = Exception("Unexpected error")

        get_incidents_wrapper = capture_registered_tool(register_tools)
        result = get_incidents_wrapper(product_id=55)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "API_ERROR"

    @patch("mcp_server_spira.features.productartifacts.tools.incidents.get_spira_client")
    def test_all_parameters_passed_through(self, mock_get_client):
        """Test that all parameters are passed through correctly."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []
        mock_get_client.return_value = mock_client

        get_incidents_wrapper = capture_registered_tool(register_tools)
        get_incidents_wrapper(product_id=55, start_row=10, number_rows=50, sort_by="PriorityId")

        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        assert "start_row=10" in url
        assert "number_rows=50" in url
        assert "sort_by=PriorityId" in url
