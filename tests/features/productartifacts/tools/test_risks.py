"""
Unit tests for product risks tools
"""

import json
from unittest.mock import Mock, patch

import pytest

from mcp_server_spira.features.productartifacts.tools.risks import (
    _get_risks_impl,
    register_tools,
)


def capture_registered_tool(mcp_mock, tool_name):
    """Helper to capture a tool registered via decorator."""
    captured_func = None

    def mock_tool():
        def decorator(func):
            nonlocal captured_func
            captured_func = func
            return func

        return decorator

    mcp_mock.tool = mock_tool
    register_tools(mcp_mock)
    return captured_func


class TestGetRisksImpl:
    """Test suite for _get_risks_impl helper function."""

    @pytest.fixture
    def mock_spira_client(self):
        """Create mock SpiraClient."""
        return Mock()

    def test_successful_retrieval(self, mock_spira_client):
        """Test successful risk retrieval."""
        mock_risks = [
            {
                "RiskId": 1,
                "Name": "Database Performance Risk",
                "RiskStatusId": 2,
                "RiskProbability": 3,
                "RiskImpact": 4,
            }
        ]
        mock_spira_client.make_spira_api_post_request.return_value = mock_risks

        result = _get_risks_impl(mock_spira_client, product_id=55)
        response = json.loads(result)

        assert "data" in response
        assert len(response["data"]) == 1
        assert response["data"][0]["RiskId"] == 1

    def test_pagination_parameters(self, mock_spira_client):
        """Test pagination parameters are passed correctly."""
        mock_spira_client.make_spira_api_post_request.return_value = []

        _get_risks_impl(
            mock_spira_client,
            product_id=55,
            starting_row=10,
            number_of_rows=50,
        )

        call_args = mock_spira_client.make_spira_api_post_request.call_args
        assert "starting_row=10" in call_args[0][0]
        assert "number_of_rows=50" in call_args[0][0]

    def test_sort_parameters(self, mock_spira_client):
        """Test sort parameters are passed correctly."""
        mock_spira_client.make_spira_api_post_request.return_value = []

        _get_risks_impl(
            mock_spira_client,
            product_id=55,
            sort_field="RiskExposure",
            sort_direction="DESC",
        )

        call_args = mock_spira_client.make_spira_api_post_request.call_args
        assert "sort_field=RiskExposure" in call_args[0][0]
        assert "sort_direction=DESC" in call_args[0][0]

    def test_api_error_handling(self, mock_spira_client):
        """Test API error handling."""
        mock_spira_client.make_spira_api_post_request.side_effect = Exception("API error")

        result = _get_risks_impl(mock_spira_client, product_id=55)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "API_ERROR"


class TestGetRisksMCPWrapper:
    """Test suite for MCP tool wrapper."""

    def test_tool_registration(self):
        """Test that get_risks tool is registered."""
        mock_mcp = Mock()
        captured_tool = capture_registered_tool(mock_mcp, "get_risks")
        assert captured_tool is not None

    @patch("mcp_server_spira.features.productartifacts.tools.risks.get_spira_client")
    def test_successful_call_through_wrapper(self, mock_get_client):
        """Test successful call through MCP wrapper."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []
        mock_get_client.return_value = mock_client

        mock_mcp = Mock()
        get_risks = capture_registered_tool(mock_mcp, "get_risks")

        result = get_risks(product_id=55)
        response = json.loads(result)

        assert "data" in response

    @patch("mcp_server_spira.features.productartifacts.tools.risks.get_spira_client")
    def test_validation_error_invalid_product_id(self, mock_get_client):
        """Test validation error for invalid product_id."""
        mock_mcp = Mock()
        get_risks = capture_registered_tool(mock_mcp, "get_risks")

        result = get_risks(product_id=-1)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"

    @patch("mcp_server_spira.features.productartifacts.tools.risks.get_spira_client")
    def test_validation_error_invalid_starting_row(self, mock_get_client):
        """Test validation error for invalid starting_row."""
        mock_mcp = Mock()
        get_risks = capture_registered_tool(mock_mcp, "get_risks")

        result = get_risks(product_id=55, starting_row=0)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"

    @patch("mcp_server_spira.features.productartifacts.tools.risks.get_spira_client")
    def test_validation_error_invalid_number_of_rows(self, mock_get_client):
        """Test validation error for invalid number_of_rows."""
        mock_mcp = Mock()
        get_risks = capture_registered_tool(mock_mcp, "get_risks")

        result = get_risks(product_id=55, number_of_rows=0)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"

    @patch("mcp_server_spira.features.productartifacts.tools.risks.get_spira_client")
    def test_exception_handling_in_wrapper(self, mock_get_client):
        """Test exception handling in wrapper."""
        mock_get_client.side_effect = Exception("Client error")

        mock_mcp = Mock()
        get_risks = capture_registered_tool(mock_mcp, "get_risks")

        result = get_risks(product_id=55)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "API_ERROR"

    @patch("mcp_server_spira.features.productartifacts.tools.risks.get_spira_client")
    def test_all_parameters_passed_through(self, mock_get_client):
        """Test all parameters are passed through correctly."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []
        mock_get_client.return_value = mock_client

        mock_mcp = Mock()
        get_risks = capture_registered_tool(mock_mcp, "get_risks")

        get_risks(
            product_id=55,
            starting_row=10,
            number_of_rows=50,
            sort_field="RiskExposure",
            sort_direction="ASC",
        )

        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        assert "projects/55/risks/search" in url
        assert "starting_row=10" in url
        assert "number_of_rows=50" in url
        assert "sort_field=RiskExposure" in url
        assert "sort_direction=ASC" in url
