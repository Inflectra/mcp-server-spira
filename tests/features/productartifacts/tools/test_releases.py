"""
Unit tests for product releases tools
"""

import json
from unittest.mock import Mock, patch

import pytest

from mcp_server_spira.features.productartifacts.tools.releases import (
    _get_release_by_id_impl,
    _get_releases_impl,
    register_tools,
)


def capture_registered_tool(mcp_mock, tool_name):
    """Helper to capture a tool registered via decorator."""
    captured_tools = {}

    def mock_tool():
        def decorator(func):
            captured_tools[func.__name__] = func
            return func

        return decorator

    mcp_mock.tool = mock_tool
    register_tools(mcp_mock)
    return captured_tools.get(tool_name)


class TestGetReleasesImpl:
    """Test suite for _get_releases_impl helper function."""

    @pytest.fixture
    def mock_spira_client(self):
        """Create mock SpiraClient."""
        return Mock()

    def test_successful_retrieval(self, mock_spira_client):
        """Test successful release retrieval."""
        mock_releases = [
            {
                "ReleaseId": 1,
                "Name": "Release 1.0",
                "VersionNumber": "1.0.0",
                "ProjectId": 55,
            }
        ]
        mock_spira_client.make_spira_api_post_request.return_value = mock_releases

        result = _get_releases_impl(mock_spira_client, product_id=55)
        response = json.loads(result)

        assert "data" in response
        assert len(response["data"]) == 1
        assert response["data"][0]["ReleaseId"] == 1

    def test_pagination_parameters(self, mock_spira_client):
        """Test pagination parameters are passed correctly."""
        mock_spira_client.make_spira_api_post_request.return_value = []

        _get_releases_impl(
            mock_spira_client,
            product_id=55,
            start_row=10,
            number_rows=50,
        )

        call_args = mock_spira_client.make_spira_api_post_request.call_args
        assert "start_row=10" in call_args[0][0]
        assert "number_rows=50" in call_args[0][0]

    def test_api_error_handling(self, mock_spira_client):
        """Test API error handling."""
        mock_spira_client.make_spira_api_post_request.side_effect = Exception("API error")

        result = _get_releases_impl(mock_spira_client, product_id=55)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "API_ERROR"


class TestGetReleaseByIdImpl:
    """Test suite for _get_release_by_id_impl helper function."""

    @pytest.fixture
    def mock_spira_client(self):
        """Create mock SpiraClient."""
        return Mock()

    def test_successful_retrieval(self, mock_spira_client):
        """Test successful single release retrieval."""
        mock_release = {
            "ReleaseId": 10,
            "Name": "Release 1.5.0",
            "VersionNumber": "1.5.0",
            "ProjectId": 55,
        }
        mock_spira_client.make_spira_api_get_request.return_value = mock_release

        result = _get_release_by_id_impl(mock_spira_client, product_id=55, release_id=10)
        response = json.loads(result)

        assert "data" in response
        assert len(response["data"]) == 1
        assert response["data"][0]["ReleaseId"] == 10

    def test_api_error_handling(self, mock_spira_client):
        """Test API error handling."""
        mock_spira_client.make_spira_api_get_request.side_effect = Exception("Release not found")

        result = _get_release_by_id_impl(mock_spira_client, product_id=55, release_id=999)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "API_ERROR"


class TestGetReleasesMCPWrapper:
    """Test suite for get_releases MCP tool wrapper."""

    def test_tool_registration(self):
        """Test that get_releases tool is registered."""
        mock_mcp = Mock()
        captured_tool = capture_registered_tool(mock_mcp, "get_releases")
        assert captured_tool is not None

    @patch("mcp_server_spira.features.productartifacts.tools.releases.get_spira_client")
    def test_successful_call_through_wrapper(self, mock_get_client):
        """Test successful call through MCP wrapper."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []
        mock_get_client.return_value = mock_client

        mock_mcp = Mock()
        get_releases = capture_registered_tool(mock_mcp, "get_releases")

        result = get_releases(product_id=55)
        response = json.loads(result)

        assert "data" in response

    @patch("mcp_server_spira.features.productartifacts.tools.releases.get_spira_client")
    def test_validation_error_invalid_product_id(self, mock_get_client):
        """Test validation error for invalid product_id."""
        mock_mcp = Mock()
        get_releases = capture_registered_tool(mock_mcp, "get_releases")

        result = get_releases(product_id=-1)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"

    @patch("mcp_server_spira.features.productartifacts.tools.releases.get_spira_client")
    def test_validation_error_invalid_start_row(self, mock_get_client):
        """Test validation error for invalid start_row."""
        mock_mcp = Mock()
        get_releases = capture_registered_tool(mock_mcp, "get_releases")

        result = get_releases(product_id=55, start_row=0)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"

    @patch("mcp_server_spira.features.productartifacts.tools.releases.get_spira_client")
    def test_validation_error_invalid_number_rows(self, mock_get_client):
        """Test validation error for invalid number_rows."""
        mock_mcp = Mock()
        get_releases = capture_registered_tool(mock_mcp, "get_releases")

        result = get_releases(product_id=55, number_rows=0)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"

    @patch("mcp_server_spira.features.productartifacts.tools.releases.get_spira_client")
    def test_exception_handling_in_wrapper(self, mock_get_client):
        """Test exception handling in wrapper."""
        mock_get_client.side_effect = Exception("Client error")

        mock_mcp = Mock()
        get_releases = capture_registered_tool(mock_mcp, "get_releases")

        result = get_releases(product_id=55)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "API_ERROR"

    @patch("mcp_server_spira.features.productartifacts.tools.releases.get_spira_client")
    def test_all_parameters_passed_through(self, mock_get_client):
        """Test all parameters are passed through correctly."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []
        mock_get_client.return_value = mock_client

        mock_mcp = Mock()
        get_releases = capture_registered_tool(mock_mcp, "get_releases")

        get_releases(
            product_id=55,
            start_row=10,
            number_rows=50,
        )

        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        assert "projects/55/releases/search" in url
        assert "start_row=10" in url
        assert "number_rows=50" in url


class TestGetReleaseByIdMCPWrapper:
    """Test suite for get_release_by_id MCP tool wrapper."""

    def test_tool_registration(self):
        """Test that get_release_by_id tool is registered."""
        mock_mcp = Mock()
        captured_tool = capture_registered_tool(mock_mcp, "get_release_by_id")
        assert captured_tool is not None

    @patch("mcp_server_spira.features.productartifacts.tools.releases.get_spira_client")
    def test_successful_call_through_wrapper(self, mock_get_client):
        """Test successful call through MCP wrapper."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.return_value = {"ReleaseId": 10}
        mock_get_client.return_value = mock_client

        mock_mcp = Mock()
        get_release_by_id = capture_registered_tool(mock_mcp, "get_release_by_id")

        result = get_release_by_id(product_id=55, release_id=10)
        response = json.loads(result)

        assert "data" in response
        assert len(response["data"]) == 1

    @patch("mcp_server_spira.features.productartifacts.tools.releases.get_spira_client")
    def test_validation_error_invalid_product_id(self, mock_get_client):
        """Test validation error for invalid product_id."""
        mock_mcp = Mock()
        get_release_by_id = capture_registered_tool(mock_mcp, "get_release_by_id")

        result = get_release_by_id(product_id=-1, release_id=10)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"

    @patch("mcp_server_spira.features.productartifacts.tools.releases.get_spira_client")
    def test_validation_error_invalid_release_id(self, mock_get_client):
        """Test validation error for invalid release_id."""
        mock_mcp = Mock()
        get_release_by_id = capture_registered_tool(mock_mcp, "get_release_by_id")

        result = get_release_by_id(product_id=55, release_id=0)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"

    @patch("mcp_server_spira.features.productartifacts.tools.releases.get_spira_client")
    def test_exception_handling_in_wrapper(self, mock_get_client):
        """Test exception handling in wrapper."""
        mock_get_client.side_effect = Exception("Client error")

        mock_mcp = Mock()
        get_release_by_id = capture_registered_tool(mock_mcp, "get_release_by_id")

        result = get_release_by_id(product_id=55, release_id=10)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "API_ERROR"

    @patch("mcp_server_spira.features.productartifacts.tools.releases.get_spira_client")
    def test_parameters_passed_through(self, mock_get_client):
        """Test parameters are passed through correctly."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.return_value = {"ReleaseId": 10}
        mock_get_client.return_value = mock_client

        mock_mcp = Mock()
        get_release_by_id = capture_registered_tool(mock_mcp, "get_release_by_id")

        get_release_by_id(product_id=55, release_id=10)

        call_args = mock_client.make_spira_api_get_request.call_args
        url = call_args[0][0]
        assert "projects/55/releases/10" in url
