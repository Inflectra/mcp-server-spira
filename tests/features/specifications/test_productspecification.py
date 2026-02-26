"""
Unit tests for product specification tools
"""

import json
from unittest.mock import Mock, patch

from mcp_server_spira.features.specifications.tools.productspecification import (
    register_tools,
)


def capture_registered_tool(mcp_mock, tool_name):
    """Helper to capture a tool registered via decorator."""
    captured_func = None

    def mock_tool(*args, **kwargs):
        def decorator(func):
            nonlocal captured_func
            captured_func = func
            return func

        return decorator

    mcp_mock.tool = mock_tool
    register_tools(mcp_mock)
    return captured_func


class TestGetSpecificationRequirementsMCPWrapper:
    """Test suite for get_specification_requirements MCP tool wrapper."""

    def test_tool_registration(self):
        """Test that get_specification_requirements tool is registered."""
        mock_mcp = Mock()
        captured_tool = capture_registered_tool(mock_mcp, "get_specification_requirements")
        assert captured_tool is not None

    @patch("mcp_server_spira.features.specifications.tools.productspecification.get_spira_client")
    def test_validation_error_invalid_product_id(self, mock_get_client):
        """Test validation error for invalid product_id."""
        mock_mcp = Mock()
        get_specification_requirements = capture_registered_tool(
            mock_mcp, "get_specification_requirements"
        )

        result = get_specification_requirements(product_id=-1, release_id=None)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"
        assert "product_id" in response["details"]["parameter"]

    @patch("mcp_server_spira.features.specifications.tools.productspecification.get_spira_client")
    def test_validation_error_invalid_release_id(self, mock_get_client):
        """Test validation error for invalid release_id."""
        mock_mcp = Mock()
        get_specification_requirements = capture_registered_tool(
            mock_mcp, "get_specification_requirements"
        )

        result = get_specification_requirements(product_id=55, release_id=-1)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"
        assert "release_id" in response["details"]["parameter"]

    @patch("mcp_server_spira.features.specifications.tools.productspecification.get_spira_client")
    def test_validation_error_zero_product_id(self, mock_get_client):
        """Test validation error for zero product_id."""
        mock_mcp = Mock()
        get_specification_requirements = capture_registered_tool(
            mock_mcp, "get_specification_requirements"
        )

        result = get_specification_requirements(product_id=0, release_id=None)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"

    @patch("mcp_server_spira.features.specifications.tools.productspecification.get_spira_client")
    def test_exception_handling_in_wrapper(self, mock_get_client):
        """Test exception handling in wrapper."""
        mock_get_client.side_effect = Exception("Client error")

        mock_mcp = Mock()
        get_specification_requirements = capture_registered_tool(
            mock_mcp, "get_specification_requirements"
        )

        result = get_specification_requirements(product_id=55, release_id=None)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "API_ERROR"
        assert "Client error" in response["error"]


class TestGetSpecificationDesignMCPWrapper:
    """Test suite for get_specification_design MCP tool wrapper."""

    def test_tool_registration(self):
        """Test that get_specification_design tool is registered."""
        mock_mcp = Mock()
        captured_tool = capture_registered_tool(mock_mcp, "get_specification_design")
        assert captured_tool is not None

    @patch("mcp_server_spira.features.specifications.tools.productspecification.get_spira_client")
    def test_validation_error_invalid_product_id(self, mock_get_client):
        """Test validation error for invalid product_id."""
        mock_mcp = Mock()
        get_specification_design = capture_registered_tool(mock_mcp, "get_specification_design")

        result = get_specification_design(product_id=0, release_id=None)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"

    @patch("mcp_server_spira.features.specifications.tools.productspecification.get_spira_client")
    def test_validation_error_invalid_release_id(self, mock_get_client):
        """Test validation error for invalid release_id."""
        mock_mcp = Mock()
        get_specification_design = capture_registered_tool(mock_mcp, "get_specification_design")

        result = get_specification_design(product_id=55, release_id=0)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"

    @patch("mcp_server_spira.features.specifications.tools.productspecification.get_spira_client")
    def test_exception_handling_in_wrapper(self, mock_get_client):
        """Test exception handling in wrapper."""
        mock_get_client.side_effect = Exception("Connection failed")

        mock_mcp = Mock()
        get_specification_design = capture_registered_tool(mock_mcp, "get_specification_design")

        result = get_specification_design(product_id=55, release_id=None)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "API_ERROR"


class TestGetSpecificationTasksMCPWrapper:
    """Test suite for get_specification_tasks MCP tool wrapper."""

    def test_tool_registration(self):
        """Test that get_specification_tasks tool is registered."""
        mock_mcp = Mock()
        captured_tool = capture_registered_tool(mock_mcp, "get_specification_tasks")
        assert captured_tool is not None

    @patch("mcp_server_spira.features.specifications.tools.productspecification.get_spira_client")
    def test_validation_error_invalid_product_id(self, mock_get_client):
        """Test validation error for invalid product_id."""
        mock_mcp = Mock()
        get_specification_tasks = capture_registered_tool(mock_mcp, "get_specification_tasks")

        result = get_specification_tasks(product_id=0, release_id=None)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"

    @patch("mcp_server_spira.features.specifications.tools.productspecification.get_spira_client")
    def test_validation_error_invalid_release_id(self, mock_get_client):
        """Test validation error for invalid release_id."""
        mock_mcp = Mock()
        get_specification_tasks = capture_registered_tool(mock_mcp, "get_specification_tasks")

        result = get_specification_tasks(product_id=55, release_id=-1)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"

    @patch("mcp_server_spira.features.specifications.tools.productspecification.get_spira_client")
    def test_exception_handling_in_wrapper(self, mock_get_client):
        """Test exception handling in wrapper."""
        mock_get_client.side_effect = Exception("API failure")

        mock_mcp = Mock()
        get_specification_tasks = capture_registered_tool(mock_mcp, "get_specification_tasks")

        result = get_specification_tasks(product_id=55, release_id=None)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "API_ERROR"


class TestGetSpecificationTestCasesMCPWrapper:
    """Test suite for get_specification_test_cases MCP tool wrapper."""

    def test_tool_registration(self):
        """Test that get_specification_test_cases tool is registered."""
        mock_mcp = Mock()
        captured_tool = capture_registered_tool(mock_mcp, "get_specification_test_cases")
        assert captured_tool is not None

    @patch("mcp_server_spira.features.specifications.tools.productspecification.get_spira_client")
    def test_validation_error_invalid_product_id(self, mock_get_client):
        """Test validation error for invalid product_id."""
        mock_mcp = Mock()
        get_specification_test_cases = capture_registered_tool(
            mock_mcp, "get_specification_test_cases"
        )

        result = get_specification_test_cases(product_id=0, release_id=None)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"

    @patch("mcp_server_spira.features.specifications.tools.productspecification.get_spira_client")
    def test_validation_error_invalid_release_id(self, mock_get_client):
        """Test validation error for invalid release_id."""
        mock_mcp = Mock()
        get_specification_test_cases = capture_registered_tool(
            mock_mcp, "get_specification_test_cases"
        )

        result = get_specification_test_cases(product_id=55, release_id=0)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"

    @patch("mcp_server_spira.features.specifications.tools.productspecification.get_spira_client")
    def test_exception_handling_in_wrapper(self, mock_get_client):
        """Test exception handling in wrapper."""
        mock_get_client.side_effect = Exception("Network error")

        mock_mcp = Mock()
        get_specification_test_cases = capture_registered_tool(
            mock_mcp, "get_specification_test_cases"
        )

        result = get_specification_test_cases(product_id=55, release_id=None)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "API_ERROR"

    @patch(
        "mcp_server_spira.features.specifications.tools.productspecification._get_specification_test_cases_impl"
    )
    @patch("mcp_server_spira.features.specifications.tools.productspecification.get_spira_client")
    def test_successful_call_passes_parameters(self, mock_get_client, mock_impl):
        """Test successful call passes parameters correctly."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_impl.return_value = "# Test Cases"

        mock_mcp = Mock()
        get_specification_test_cases = capture_registered_tool(
            mock_mcp, "get_specification_test_cases"
        )

        result = get_specification_test_cases(product_id=55, release_id=None)

        assert result == "# Test Cases"
        mock_impl.assert_called_once_with(mock_client, 55, None)


class TestAllSpecificationTools:
    """Test suite for all specification tools together."""

    @patch("mcp_server_spira.features.specifications.tools.productspecification.get_spira_client")
    def test_all_tools_validate_product_id(self, mock_get_client):
        """Test that all specification tools validate product_id."""
        mock_mcp = Mock()
        registered_tools = {}

        def mock_tool(*args, **kwargs):
            def decorator(func):
                registered_tools[func.__name__] = func
                return func

            return decorator

        mock_mcp.tool = mock_tool
        register_tools(mock_mcp)

        tool_names = [
            "get_specification_requirements",
            "get_specification_design",
            "get_specification_tasks",
            "get_specification_test_cases",
        ]

        for tool_name in tool_names:
            tool_func = registered_tools[tool_name]
            result = tool_func(product_id=-1, release_id=None)
            response = json.loads(result)
            assert "error" in response, f"{tool_name} should validate product_id"
            assert response["error_code"] == "INVALID_VALUE"

    @patch("mcp_server_spira.features.specifications.tools.productspecification.get_spira_client")
    def test_all_tools_validate_release_id(self, mock_get_client):
        """Test that all specification tools validate release_id."""
        mock_mcp = Mock()
        registered_tools = {}

        def mock_tool(*args, **kwargs):
            def decorator(func):
                registered_tools[func.__name__] = func
                return func

            return decorator

        mock_mcp.tool = mock_tool
        register_tools(mock_mcp)

        tool_names = [
            "get_specification_requirements",
            "get_specification_design",
            "get_specification_tasks",
            "get_specification_test_cases",
        ]

        for tool_name in tool_names:
            tool_func = registered_tools[tool_name]
            result = tool_func(product_id=55, release_id=0)
            response = json.loads(result)
            assert "error" in response, f"{tool_name} should validate release_id"
            assert response["error_code"] == "INVALID_VALUE"

    @patch("mcp_server_spira.features.specifications.tools.productspecification.get_spira_client")
    def test_all_tools_accept_none_release_id(self, mock_get_client):
        """Test that all specification tools accept None for release_id."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        mock_mcp = Mock()
        registered_tools = {}

        def mock_tool(*args, **kwargs):
            def decorator(func):
                registered_tools[func.__name__] = func
                return func

            return decorator

        mock_mcp.tool = mock_tool
        register_tools(mock_mcp)

        # Mock all implementation functions
        with (
            patch(
                "mcp_server_spira.features.specifications.tools.productspecification._get_specification_requirements_impl",
                return_value="# Test",
            ),
            patch(
                "mcp_server_spira.features.specifications.tools.productspecification._get_specification_design_impl",
                return_value="# Test",
            ),
            patch(
                "mcp_server_spira.features.specifications.tools.productspecification._get_specification_tasks_impl",
                return_value="# Test",
            ),
            patch(
                "mcp_server_spira.features.specifications.tools.productspecification._get_specification_test_cases_impl",
                return_value="# Test",
            ),
        ):
            tool_names = [
                "get_specification_requirements",
                "get_specification_design",
                "get_specification_tasks",
                "get_specification_test_cases",
            ]

            for tool_name in tool_names:
                tool_func = registered_tools[tool_name]
                result = tool_func(product_id=55, release_id=None)
                # Should not return JSON error
                assert not result.startswith("{"), f"{tool_name} should accept None release_id"
                assert result == "# Test"
