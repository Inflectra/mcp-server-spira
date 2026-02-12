"""
Tests for the Programs workspace features of the Inflectra Spira MCP Server.
"""

import json
from unittest.mock import Mock, patch

import pytest

from mcp_server_spira.features.workspaces.tools.programs import (
    _get_programs_impl,
    register_tools,
)


@pytest.mark.unit
class TestGetProgramsImpl:
    """Tests for _get_programs_impl function."""

    def test_successful_retrieval_with_programs(self):
        """Test successful program retrieval with data."""
        # Mock Spira client
        mock_client = Mock()
        mock_programs = [
            {
                "ProgramId": 1,
                "Name": "Program 1",
                "Description": "Test program 1",
                "isActive": True,
                "isDefault": False,
                "Website": "https://program1.example.com",
                "PortfolioId": 5,
                "ProjectTemplateId": 1,
                "WorkspaceTypeId": 2,
            },
            {
                "ProgramId": 2,
                "Name": "Program 2",
                "Description": "Test program 2",
                "isActive": False,
                "isDefault": True,
                "Website": "https://program2.example.com",
                "PortfolioId": 5,
                "ProjectTemplateId": 2,
                "WorkspaceTypeId": 2,
            },
        ]
        mock_client.make_spira_api_get_request.return_value = mock_programs

        # Call implementation
        result = _get_programs_impl(mock_client)

        # Verify API was called correctly
        mock_client.make_spira_api_get_request.assert_called_once_with("programs")

        # Parse and verify response
        parsed = json.loads(result)
        assert "data" in parsed
        assert len(parsed["data"]) == 2
        assert parsed["data"][0]["ProgramId"] == 1
        assert parsed["data"][0]["Name"] == "Program 1"
        assert parsed["data"][0]["isActive"] is True
        assert parsed["data"][0]["isDefault"] is False
        assert parsed["data"][1]["ProgramId"] == 2
        assert parsed["data"][1]["Name"] == "Program 2"
        assert parsed["data"][1]["isActive"] is False
        assert parsed["data"][1]["isDefault"] is True

    def test_successful_retrieval_empty_programs(self):
        """Test successful retrieval with no programs."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.return_value = []

        result = _get_programs_impl(mock_client)

        parsed = json.loads(result)
        assert "data" in parsed
        assert len(parsed["data"]) == 0
        assert parsed["data"] == []

    def test_api_error_handling(self):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.side_effect = Exception("Connection timeout")

        result = _get_programs_impl(mock_client)

        # Verify error response structure
        parsed = json.loads(result)
        assert "error" in parsed
        assert "error_code" in parsed
        assert parsed["error"] == "Failed to retrieve programs"
        assert parsed["error_code"] == "API_ERROR"
        assert "details" in parsed
        assert "message" in parsed["details"]
        assert "suggestion" in parsed

    def test_preserves_all_fields(self):
        """Test that all program fields are preserved in JSON output."""
        mock_client = Mock()
        mock_programs = [
            {
                "ProgramId": 10,
                "Name": "Engineering Programs",
                "Description": "All engineering-related programs",
                "Website": "https://engineering.example.com",
                "PortfolioId": 5,
                "ProjectTemplateId": 1,
                "isActive": True,
                "isDefault": False,
                "WorkspaceTypeId": 2,
                "Guid": "abc-123-def-456",
                "LastUpdatedDate": "2024-01-15T10:00:00Z",
                "ArtifactTypeId": 7,
                "ConcurrencyGuid": "xyz-789",
                "CustomProperties": [],
            }
        ]
        mock_client.make_spira_api_get_request.return_value = mock_programs

        result = _get_programs_impl(mock_client)

        parsed = json.loads(result)
        program = parsed["data"][0]

        # Verify all fields are present
        assert program["ProgramId"] == 10
        assert program["Name"] == "Engineering Programs"
        assert program["Description"] == "All engineering-related programs"
        assert program["Website"] == "https://engineering.example.com"
        assert program["PortfolioId"] == 5
        assert program["ProjectTemplateId"] == 1
        assert program["isActive"] is True
        assert program["isDefault"] is False
        assert program["WorkspaceTypeId"] == 2
        assert program["Guid"] == "abc-123-def-456"
        assert program["LastUpdatedDate"] == "2024-01-15T10:00:00Z"
        assert program["ArtifactTypeId"] == 7
        assert program["ConcurrencyGuid"] == "xyz-789"
        assert program["CustomProperties"] == []

    def test_json_formatting(self):
        """Test that JSON is properly formatted with indentation."""
        mock_client = Mock()
        mock_programs = [{"ProgramId": 1, "Name": "Program 1", "isActive": True}]
        mock_client.make_spira_api_get_request.return_value = mock_programs

        result = _get_programs_impl(mock_client)

        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed is not None

        # Verify formatting (should have newlines and indentation)
        assert "\n" in result
        assert "  " in result  # 2-space indentation

    def test_null_values_preserved(self):
        """Test that null values are preserved as JSON null."""
        mock_client = Mock()
        mock_programs = [
            {
                "ProgramId": 1,
                "Name": "Program 1",
                "Description": None,  # Null description
                "PortfolioId": None,  # Null portfolio
                "ProjectTemplateId": None,  # Null template
                "isActive": True,
                "isDefault": False,
            }
        ]
        mock_client.make_spira_api_get_request.return_value = mock_programs

        result = _get_programs_impl(mock_client)

        parsed = json.loads(result)
        program = parsed["data"][0]

        # Verify null values are preserved as None (JSON null)
        assert program["Description"] is None
        assert program["PortfolioId"] is None
        assert program["ProjectTemplateId"] is None


@pytest.mark.unit
class TestRegisterTools:
    """Tests for tool registration and MCP tool wrappers."""

    def test_register_tools_creates_tools(self):
        """Test that register_tools creates the expected tools."""
        mock_mcp = Mock()

        # Call register_tools
        register_tools(mock_mcp)

        # Verify that mcp.tool() was called (decorator pattern)
        assert mock_mcp.tool.called

    @patch("mcp_server_spira.features.workspaces.tools.programs.get_spira_client")
    def test_get_programs_wrapper_success(self, mock_get_client):
        """Test get_programs MCP tool wrapper with successful call."""
        mock_client = Mock()
        mock_programs = [
            {
                "ProgramId": 1,
                "Name": "Program 1",
                "Description": "Test program",
                "isActive": True,
                "isDefault": False,
            }
        ]
        mock_client.make_spira_api_get_request.return_value = mock_programs
        mock_get_client.return_value = mock_client

        result = _get_programs_impl(mock_client)

        # Verify successful response
        parsed = json.loads(result)
        assert "data" in parsed
        assert len(parsed["data"]) == 1
        assert parsed["data"][0]["ProgramId"] == 1

    @patch("mcp_server_spira.features.workspaces.tools.programs.get_spira_client")
    def test_get_programs_wrapper_error(self, mock_get_client):
        """Test get_programs MCP tool wrapper with error."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client

        result = _get_programs_impl(mock_client)

        # Verify error response
        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "API_ERROR"
        assert "API Error" in parsed["details"]["message"]

    @patch("mcp_server_spira.features.workspaces.tools.programs.get_spira_client")
    def test_get_programs_wrapper_empty_result(self, mock_get_client):
        """Test get_programs MCP tool wrapper with empty result."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.return_value = []
        mock_get_client.return_value = mock_client

        result = _get_programs_impl(mock_client)

        # Verify empty data array
        parsed = json.loads(result)
        assert "data" in parsed
        assert len(parsed["data"]) == 0

    def test_multiple_tool_registrations(self):
        """Test that multiple calls to register_tools don't cause issues."""
        mock_mcp = Mock()

        # Call register_tools multiple times
        register_tools(mock_mcp)
        first_call_count = mock_mcp.tool.call_count

        register_tools(mock_mcp)
        second_call_count = mock_mcp.tool.call_count

        # Each call should register the same number of tools
        assert second_call_count == first_call_count * 2

    @patch("mcp_server_spira.features.workspaces.tools.programs.get_spira_client")
    def test_get_programs_preserves_field_types(self, mock_get_client):
        """Test that field types are preserved correctly."""
        mock_client = Mock()
        mock_programs = [
            {
                "ProgramId": 10,  # integer
                "Name": "Engineering",  # string
                "Description": "Engineering programs",  # string
                "isActive": True,  # boolean
                "isDefault": False,  # boolean
                "WorkspaceTypeId": 2,  # integer
                "PortfolioId": 5,  # integer
                "ProjectTemplateId": 1,  # integer
            }
        ]
        mock_client.make_spira_api_get_request.return_value = mock_programs
        mock_get_client.return_value = mock_client

        result = _get_programs_impl(mock_client)

        parsed = json.loads(result)
        program = parsed["data"][0]

        # Verify types are preserved
        assert isinstance(program["ProgramId"], int)
        assert isinstance(program["Name"], str)
        assert isinstance(program["isActive"], bool)
        assert isinstance(program["isDefault"], bool)
        assert isinstance(program["WorkspaceTypeId"], int)
