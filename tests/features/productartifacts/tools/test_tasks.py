"""
Unit tests for product artifacts tasks tools.

Tests the get_tasks MCP tool wrapper, validation, and error handling.
"""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from mcp_server_spira.features.productartifacts.tools.tasks import (
    _get_tasks_impl,
    register_tools,
)


def capture_registered_tool(register_func):
    """Helper to capture the tool function registered with MCP."""
    captured_func = None

    def capture_tool(**kwargs):
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
class TestGetTasksImpl:
    """Tests for _get_tasks_impl helper function."""

    @pytest.mark.asyncio
    async def test_successful_retrieval(self):
        """Test successful task retrieval with default parameters."""
        mock_client = AsyncMock()
        mock_tasks = [
            {
                "TaskId": 123,
                "Name": "Fix login bug",
                "TaskStatusName": "In Progress",
                "ProjectId": 55,
            }
        ]
        mock_client.make_spira_api_post_request.return_value = mock_tasks

        result = await _get_tasks_impl(mock_client, 55)

        # Verify POST request with empty filter array
        mock_client.make_spira_api_post_request.assert_called_once()
        call_args = mock_client.make_spira_api_post_request.call_args
        assert "projects/55/tasks/search" in call_args[0][0]
        assert call_args[0][1] == []

        # Verify JSON response structure
        parsed = json.loads(result)
        assert "data" in parsed
        assert len(parsed["data"]) == 1
        assert parsed["data"][0]["TaskId"] == 123

    @pytest.mark.asyncio
    async def test_pagination_parameters(self):
        """Test pagination parameters are included in URL."""
        mock_client = AsyncMock()
        mock_client.make_spira_api_post_request.return_value = []

        await _get_tasks_impl(mock_client, 55, starting_row=10, number_of_rows=50)

        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        assert "starting_row=10" in url
        assert "number_of_rows=50" in url

    @pytest.mark.asyncio
    async def test_sort_parameters(self):
        """Test sort parameters are included when provided."""
        mock_client = AsyncMock()
        mock_client.make_spira_api_post_request.return_value = []

        await _get_tasks_impl(mock_client, 55, sort_field="TaskPriorityId", sort_direction="DESC")

        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        assert "sort_field=TaskPriorityId" in url
        assert "sort_direction=DESC" in url

    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Test error handling when API call fails."""
        mock_client = AsyncMock()
        mock_client.make_spira_api_post_request.side_effect = Exception("Connection timeout")

        result = await _get_tasks_impl(mock_client, 55)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error"] == "Failed to retrieve tasks"
        assert parsed["error_code"] == "API_ERROR"
        assert "details" in parsed
        assert "suggestion" in parsed

    @pytest.mark.asyncio
    async def test_empty_results(self):
        """Test successful retrieval with no tasks."""
        mock_client = AsyncMock()
        mock_client.make_spira_api_post_request.return_value = []

        result = await _get_tasks_impl(mock_client, 55)

        parsed = json.loads(result)
        assert "data" in parsed
        assert len(parsed["data"]) == 0


@pytest.mark.unit
class TestGetTasksMCPWrapper:
    """Tests for get_tasks MCP tool wrapper."""

    def test_tool_registration(self):
        """Test that get_tasks tool is registered with MCP."""
        mock_mcp = Mock()
        register_tools(mock_mcp)

        # Verify tool decorator was called
        assert mock_mcp.tool.called
        assert mock_mcp.tool.call_count == 1

    @patch("mcp_server_spira.features.productartifacts.tools.tasks.get_spira_client")
    @pytest.mark.asyncio
    async def test_successful_call_through_wrapper(self, mock_get_client):
        """Test successful call through MCP wrapper."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_client.make_spira_api_post_request.return_value = [
            {"TaskId": 123, "Name": "Test Task"}
        ]
        mock_get_client.return_value = mock_client

        # Get the wrapper function
        get_tasks_wrapper = capture_registered_tool(register_tools)

        # Call the wrapper
        result = await get_tasks_wrapper(product_id=55)

        # Verify result
        parsed = json.loads(result)
        assert "data" in parsed
        assert parsed["data"][0]["TaskId"] == 123

    @patch("mcp_server_spira.features.productartifacts.tools.tasks.get_spira_client")
    @pytest.mark.asyncio
    async def test_validation_error_invalid_product_id(self, mock_get_client):
        """Test validation error for invalid product_id."""
        get_tasks_wrapper = capture_registered_tool(register_tools)

        # Call with invalid product_id
        result = await get_tasks_wrapper(product_id=-1)

        # Verify error response
        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "INVALID_VALUE"
        assert "product_id" in parsed["details"]["parameter"]

    @patch("mcp_server_spira.features.productartifacts.tools.tasks.get_spira_client")
    @pytest.mark.asyncio
    async def test_validation_error_invalid_starting_row(self, mock_get_client):
        """Test validation error for invalid starting_row."""
        get_tasks_wrapper = capture_registered_tool(register_tools)

        # Call with invalid starting_row
        result = await get_tasks_wrapper(product_id=55, starting_row=0)

        # Verify error response
        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "INVALID_VALUE"
        assert "starting_row" in parsed["details"]["parameter"]

    @patch("mcp_server_spira.features.productartifacts.tools.tasks.get_spira_client")
    @pytest.mark.asyncio
    async def test_validation_error_invalid_number_of_rows(self, mock_get_client):
        """Test validation error for invalid number_of_rows."""
        get_tasks_wrapper = capture_registered_tool(register_tools)

        # Call with invalid number_of_rows
        result = await get_tasks_wrapper(product_id=55, number_of_rows=0)

        # Verify error response
        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "INVALID_VALUE"
        assert "number_of_rows" in parsed["details"]["parameter"]

    @patch("mcp_server_spira.features.productartifacts.tools.tasks.get_spira_client")
    @pytest.mark.asyncio
    async def test_exception_handling_in_wrapper(self, mock_get_client):
        """Test exception handling in MCP wrapper."""
        # Setup mock to raise exception
        mock_get_client.side_effect = Exception("Unexpected error")

        get_tasks_wrapper = capture_registered_tool(register_tools)

        # Call wrapper
        result = await get_tasks_wrapper(product_id=55)

        # Verify error response
        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "API_ERROR"

    @patch("mcp_server_spira.features.productartifacts.tools.tasks.get_spira_client")
    @pytest.mark.asyncio
    async def test_all_parameters_passed_through(self, mock_get_client):
        """Test that all parameters are passed through correctly."""
        mock_client = AsyncMock()
        mock_client.make_spira_api_post_request.return_value = []
        mock_get_client.return_value = mock_client

        get_tasks_wrapper = capture_registered_tool(register_tools)

        # Call with all parameters
        await get_tasks_wrapper(
            product_id=55,
            starting_row=10,
            number_of_rows=50,
            sort_field="TaskId",
            sort_direction="DESC",
        )

        # Verify parameters were passed to API
        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        assert "starting_row=10" in url
        assert "number_of_rows=50" in url
        assert "sort_field=TaskId" in url
        assert "sort_direction=DESC" in url
