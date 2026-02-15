"""
Tests for the Product Templates workspace features of the Inflectra Spira MCP Server.
"""

import json
from unittest.mock import Mock, patch

import pytest

from mcp_server_spira.features.workspaces.tools.product_templates import (
    _get_product_template_impl,
    _get_product_templates_impl,
    register_tools,
)


@pytest.mark.unit
class TestGetProductTemplatesImpl:
    """Tests for _get_product_templates_impl function."""

    def test_successful_retrieval_with_templates(self):
        """Test successful product template retrieval with data."""
        # Mock Spira client
        mock_client = Mock()
        mock_templates = [
            {
                "ProjectTemplateId": 1,
                "Name": "Scrum Template",
                "Description": "Agile Scrum project template",
                "IsActive": True,
                "WorkspaceTypeId": 1,
                "Guid": "abc-123-def-456",
                "LastUpdatedDate": "2024-01-15T10:00:00Z",
                "ArtifactTypeId": 1,
                "ConcurrencyGuid": "xyz-789",
                "CustomProperties": [],
            },
            {
                "ProjectTemplateId": 2,
                "Name": "Kanban Template",
                "Description": "Kanban project template",
                "IsActive": False,
                "WorkspaceTypeId": 1,
                "Guid": "def-456-ghi-789",
                "LastUpdatedDate": "2024-02-20T10:00:00Z",
                "ArtifactTypeId": 1,
                "ConcurrencyGuid": "uvw-123",
                "CustomProperties": [],
            },
        ]
        mock_client.make_spira_api_get_request.return_value = mock_templates

        # Call implementation
        result = _get_product_templates_impl(mock_client)

        # Verify API was called correctly
        mock_client.make_spira_api_get_request.assert_called_once_with("project-templates")

        # Parse and verify response
        parsed = json.loads(result)
        assert "data" in parsed
        assert len(parsed["data"]) == 2
        assert parsed["data"][0]["ProjectTemplateId"] == 1
        assert parsed["data"][0]["Name"] == "Scrum Template"
        assert parsed["data"][0]["IsActive"] is True
        assert parsed["data"][1]["ProjectTemplateId"] == 2
        assert parsed["data"][1]["Name"] == "Kanban Template"
        assert parsed["data"][1]["IsActive"] is False

    def test_successful_retrieval_empty_templates(self):
        """Test successful retrieval with no product templates."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.return_value = []

        result = _get_product_templates_impl(mock_client)

        parsed = json.loads(result)
        assert "data" in parsed
        assert len(parsed["data"]) == 0
        assert parsed["data"] == []

    def test_api_error_handling(self):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.side_effect = Exception("Connection timeout")

        result = _get_product_templates_impl(mock_client)

        # Verify error response structure
        parsed = json.loads(result)
        assert "error" in parsed
        assert "error_code" in parsed
        assert parsed["error"] == "Failed to retrieve product templates"
        assert parsed["error_code"] == "API_ERROR"
        assert "details" in parsed
        assert "message" in parsed["details"]
        assert "suggestion" in parsed

    def test_preserves_all_fields(self):
        """Test that all product template fields are preserved in JSON output."""
        mock_client = Mock()
        mock_templates = [
            {
                "ProjectTemplateId": 1,
                "Name": "Scrum Template",
                "Description": "Agile Scrum project template",
                "IsActive": True,
                "WorkspaceTypeId": 1,
                "Guid": "abc-123-def-456",
                "LastUpdatedDate": "2024-01-15T10:00:00Z",
                "ArtifactTypeId": 1,
                "ConcurrencyGuid": "xyz-789",
                "CustomProperties": [],
            }
        ]
        mock_client.make_spira_api_get_request.return_value = mock_templates

        result = _get_product_templates_impl(mock_client)

        parsed = json.loads(result)
        template = parsed["data"][0]

        # Verify all fields are present
        assert template["ProjectTemplateId"] == 1
        assert template["Name"] == "Scrum Template"
        assert template["Description"] == "Agile Scrum project template"
        assert template["IsActive"] is True
        assert template["WorkspaceTypeId"] == 1
        assert template["Guid"] == "abc-123-def-456"
        assert template["LastUpdatedDate"] == "2024-01-15T10:00:00Z"
        assert template["ArtifactTypeId"] == 1
        assert template["ConcurrencyGuid"] == "xyz-789"
        assert template["CustomProperties"] == []

    def test_json_formatting(self):
        """Test that JSON is properly formatted with indentation."""
        mock_client = Mock()
        mock_templates = [
            {
                "ProjectTemplateId": 1,
                "Name": "Scrum Template",
                "IsActive": True,
            }
        ]
        mock_client.make_spira_api_get_request.return_value = mock_templates

        result = _get_product_templates_impl(mock_client)

        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed is not None

        # Verify formatting (should have newlines and indentation)
        assert "\n" in result
        assert "  " in result  # 2-space indentation

    def test_no_truncation(self):
        """Test that all templates are returned without truncation."""
        mock_client = Mock()
        # Create 150 templates to test no truncation
        mock_templates = [
            {
                "ProjectTemplateId": i,
                "Name": f"Template {i}",
                "Description": f"Description {i}",
                "IsActive": True,
                "WorkspaceTypeId": 1,
                "Guid": f"guid-{i}",
                "LastUpdatedDate": "2024-01-15T10:00:00Z",
                "ArtifactTypeId": 1,
                "ConcurrencyGuid": f"concurrency-{i}",
                "CustomProperties": [],
            }
            for i in range(1, 151)
        ]
        mock_client.make_spira_api_get_request.return_value = mock_templates

        result = _get_product_templates_impl(mock_client)

        parsed = json.loads(result)
        # Verify all 150 templates are returned (no truncation at 100)
        assert len(parsed["data"]) == 150
        assert parsed["data"][0]["ProjectTemplateId"] == 1
        assert parsed["data"][149]["ProjectTemplateId"] == 150


@pytest.mark.unit
class TestGetProductTemplateImpl:
    """Tests for _get_product_template_impl function."""

    def test_successful_retrieval_valid_id(self):
        """Test successful product template retrieval with valid ID."""
        mock_client = Mock()
        mock_template = {
            "ProjectTemplateId": 1,
            "Name": "Scrum Template",
            "Description": "Agile Scrum project template",
            "IsActive": True,
            "WorkspaceTypeId": 1,
            "Guid": "abc-123-def-456",
        }
        mock_client.make_spira_api_get_request.return_value = mock_template

        result = _get_product_template_impl(mock_client, 1)

        # Verify API was called correctly
        mock_client.make_spira_api_get_request.assert_called_once_with("project-templates/1")

        # Verify result contains template information
        assert "Scrum Template" in result
        assert "Agile Scrum project template" in result

    def test_template_not_found(self):
        """Test handling when template ID doesn't exist."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.return_value = None

        result = _get_product_template_impl(mock_client, 999)

        assert "Unable to fetch product template details" in result
        assert "999" in result

    def test_api_error_handling(self):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.side_effect = Exception("Connection timeout")

        result = _get_product_template_impl(mock_client, 1)

        assert "problem using this tool" in result
        assert "Connection timeout" in result

    def test_various_template_ids(self):
        """Test with various template IDs."""
        mock_client = Mock()
        mock_template = {
            "ProjectTemplateId": 1,
            "Name": "Test Template",
            "Description": "Test",
            "IsActive": True,
        }
        mock_client.make_spira_api_get_request.return_value = mock_template

        # Test with different IDs
        for template_id in [1, 5, 10, 99]:
            result = _get_product_template_impl(mock_client, template_id)
            mock_client.make_spira_api_get_request.assert_called_with(
                f"project-templates/{template_id}"
            )
            assert "Test Template" in result

    def test_inactive_template(self):
        """Test retrieval of inactive template."""
        mock_client = Mock()
        mock_template = {
            "ProjectTemplateId": 2,
            "Name": "Inactive Template",
            "Description": "This template is inactive",
            "IsActive": False,
            "WorkspaceTypeId": 1,
        }
        mock_client.make_spira_api_get_request.return_value = mock_template

        result = _get_product_template_impl(mock_client, 2)

        # Should still return the template even if inactive
        assert "Inactive Template" in result


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
        # Should register 2 tools: get_product_templates and get_product_template
        assert mock_mcp.tool.call_count == 2

    def test_get_product_templates_mcp_wrapper_calls_implementation(self):
        """Test that get_product_templates MCP wrapper properly calls implementation."""
        with patch(
            "mcp_server_spira.features.workspaces.tools.product_templates.get_spira_client"
        ) as mock_get_client:
            mock_client = Mock()
            mock_templates = [{"ProjectTemplateId": 1, "Name": "Scrum Template", "IsActive": True}]
            mock_client.make_spira_api_get_request.return_value = mock_templates
            mock_get_client.return_value = mock_client

            # Create a real MCP-like object that stores the decorated function
            class MockMCP:
                def __init__(self):
                    self.tools = []

                def tool(self):
                    def decorator(func):
                        self.tools.append(func)
                        return func

                    return decorator

            mock_mcp = MockMCP()
            register_tools(mock_mcp)

            # Call the first registered tool (get_product_templates)
            get_product_templates_func = mock_mcp.tools[0]
            result = get_product_templates_func()

            # Verify successful response
            parsed = json.loads(result)
            assert "data" in parsed
            assert len(parsed["data"]) == 1

    def test_get_product_templates_mcp_wrapper_handles_exception(self):
        """Test that get_product_templates MCP wrapper handles exceptions."""
        with patch(
            "mcp_server_spira.features.workspaces.tools.product_templates.get_spira_client"
        ) as mock_get_client:
            mock_get_client.side_effect = Exception("Client error")

            # Create a real MCP-like object
            class MockMCP:
                def __init__(self):
                    self.tools = []

                def tool(self):
                    def decorator(func):
                        self.tools.append(func)
                        return func

                    return decorator

            mock_mcp = MockMCP()
            register_tools(mock_mcp)

            # Call the first registered tool (get_product_templates)
            get_product_templates_func = mock_mcp.tools[0]
            result = get_product_templates_func()

            # Verify error response
            parsed = json.loads(result)
            assert "error" in parsed
            assert parsed["error_code"] == "API_ERROR"

    def test_get_product_template_mcp_wrapper_calls_implementation(self):
        """Test that get_product_template MCP wrapper properly calls implementation."""
        with patch(
            "mcp_server_spira.features.workspaces.tools.product_templates.get_spira_client"
        ) as mock_get_client:
            mock_client = Mock()
            mock_template = {"ProjectTemplateId": 1, "Name": "Test Template", "IsActive": True}
            mock_client.make_spira_api_get_request.return_value = mock_template
            mock_get_client.return_value = mock_client

            # Create a real MCP-like object
            class MockMCP:
                def __init__(self):
                    self.tools = []

                def tool(self):
                    def decorator(func):
                        self.tools.append(func)
                        return func

                    return decorator

            mock_mcp = MockMCP()
            register_tools(mock_mcp)

            # Call the second registered tool (get_product_template)
            get_product_template_func = mock_mcp.tools[1]
            result = get_product_template_func(1)

            # Verify result contains template info
            assert "Test Template" in result

    def test_get_product_template_mcp_wrapper_handles_exception(self):
        """Test that get_product_template MCP wrapper handles exceptions."""
        with patch(
            "mcp_server_spira.features.workspaces.tools.product_templates.get_spira_client"
        ) as mock_get_client:
            mock_get_client.side_effect = Exception("Client error")

            # Create a real MCP-like object
            class MockMCP:
                def __init__(self):
                    self.tools = []

                def tool(self):
                    def decorator(func):
                        self.tools.append(func)
                        return func

                    return decorator

            mock_mcp = MockMCP()
            register_tools(mock_mcp)

            # Call the second registered tool (get_product_template)
            get_product_template_func = mock_mcp.tools[1]
            result = get_product_template_func(1)

            # Verify error response
            assert "Error:" in result
            assert "Client error" in result
