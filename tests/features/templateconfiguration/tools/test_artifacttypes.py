"""
Unit tests for get_artifact_types tool
"""

import json
from unittest.mock import MagicMock

from mcp_server_spira.features.templateconfiguration.tools.artifacttypes import (
    _get_artifact_types_impl,
)


class TestGetArtifactTypes:
    """Test suite for get_artifact_types tool"""

    def test_get_artifact_types_success_all_types(self):
        """Test successful retrieval of all artifact types"""
        # Arrange
        mock_client = MagicMock()

        # Mock responses for each artifact type
        mock_client.make_spira_api_get_request.side_effect = [
            [
                {
                    "RequirementTypeId": 1,
                    "Name": "User Story",
                    "WorkflowId": 5,
                    "Active": True,
                    "IsDefault": False,
                }
            ],
            [
                {
                    "TestCaseTypeId": 1,
                    "Name": "Functional",
                    "WorkflowId": 3,
                    "Active": True,
                    "IsDefault": True,
                }
            ],
            [
                {
                    "TaskTypeId": 1,
                    "Name": "Development",
                    "WorkflowId": 2,
                    "Active": True,
                    "IsDefault": False,
                }
            ],
            [
                {
                    "RiskTypeId": 1,
                    "Name": "Technical",
                    "WorkflowId": 6,
                    "Active": True,
                    "IsDefault": True,
                }
            ],
            [
                {
                    "IncidentTypeId": 1,
                    "Name": "Bug",
                    "WorkflowId": 4,
                    "Active": True,
                    "IsDefault": True,
                }
            ],
            [
                {
                    "DocumentTypeId": 1,
                    "Name": "Specification",
                    "Active": True,
                    "IsDefault": False,
                }
            ],
        ]

        # Act
        result = _get_artifact_types_impl(mock_client, template_id=1)

        # Assert
        result_data = json.loads(result)
        assert "data" in result_data
        assert len(result_data["data"]) == 6

        # Verify each artifact type is present
        artifact_names = [item["ArtifactTypeName"] for item in result_data["data"]]
        assert "Requirement" in artifact_names
        assert "Test Case" in artifact_names
        assert "Task" in artifact_names
        assert "Risk" in artifact_names
        assert "Incident" in artifact_names
        assert "Document" in artifact_names

        # Verify API was called 6 times
        assert mock_client.make_spira_api_get_request.call_count == 6

    def test_get_artifact_types_success_requirement_structure(self):
        """Test that requirement types are structured correctly"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.side_effect = [
            [
                {
                    "RequirementTypeId": 1,
                    "Name": "User Story",
                    "WorkflowId": 5,
                    "Active": True,
                    "IsDefault": False,
                },
                {
                    "RequirementTypeId": 2,
                    "Name": "Epic",
                    "WorkflowId": 5,
                    "Active": True,
                    "IsDefault": True,
                },
            ],
            [],  # Test Cases
            [],  # Tasks
            [],  # Risks
            [],  # Incidents
            [],  # Documents
        ]

        # Act
        result = _get_artifact_types_impl(mock_client, template_id=1)

        # Assert
        result_data = json.loads(result)
        requirement_artifact = next(
            item for item in result_data["data"] if item["ArtifactTypeName"] == "Requirement"
        )
        assert len(requirement_artifact["Types"]) == 2
        assert requirement_artifact["Types"][0]["RequirementTypeId"] == 1
        assert requirement_artifact["Types"][0]["Name"] == "User Story"
        assert requirement_artifact["Types"][1]["RequirementTypeId"] == 2
        assert requirement_artifact["Types"][1]["Name"] == "Epic"

    def test_get_artifact_types_empty_types(self):
        """Test when some artifact types return empty arrays"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.side_effect = [
            [{"RequirementTypeId": 1, "Name": "User Story"}],
            [],  # No test case types
            [{"TaskTypeId": 1, "Name": "Development"}],
            [],  # No risk types
            [{"IncidentTypeId": 1, "Name": "Bug"}],
            [],  # No document types
        ]

        # Act
        result = _get_artifact_types_impl(mock_client, template_id=1)

        # Assert
        result_data = json.loads(result)
        assert len(result_data["data"]) == 3  # Only 3 artifact types with data
        artifact_names = [item["ArtifactTypeName"] for item in result_data["data"]]
        assert "Requirement" in artifact_names
        assert "Task" in artifact_names
        assert "Incident" in artifact_names
        assert "Test Case" not in artifact_names
        assert "Risk" not in artifact_names
        assert "Document" not in artifact_names

    def test_get_artifact_types_none_response(self):
        """Test when API returns None for some types"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.side_effect = [
            [{"RequirementTypeId": 1, "Name": "User Story"}],
            None,  # Test Cases returns None
            [{"TaskTypeId": 1, "Name": "Development"}],
            None,  # Risks returns None
            [{"IncidentTypeId": 1, "Name": "Bug"}],
            None,  # Documents returns None
        ]

        # Act
        result = _get_artifact_types_impl(mock_client, template_id=1)

        # Assert
        result_data = json.loads(result)
        assert len(result_data["data"]) == 3
        artifact_names = [item["ArtifactTypeName"] for item in result_data["data"]]
        assert "Requirement" in artifact_names
        assert "Task" in artifact_names
        assert "Incident" in artifact_names

    def test_get_artifact_types_correct_urls(self):
        """Test that correct API URLs are called"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.return_value = []

        # Act
        _get_artifact_types_impl(mock_client, template_id=42)

        # Assert
        calls = mock_client.make_spira_api_get_request.call_args_list
        assert len(calls) == 6

        expected_urls = [
            "project-templates/42/requirements/types",
            "project-templates/42/test-cases/types",
            "project-templates/42/tasks/types",
            "project-templates/42/risks/types",
            "project-templates/42/incidents/types",
            "project-templates/42/document-types?active_only=true",
        ]

        for i, expected_url in enumerate(expected_urls):
            assert calls[i][0][0] == expected_url

    def test_get_artifact_types_api_exception(self):
        """Test error handling when API raises exception"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.side_effect = Exception("Connection timeout")

        # Act
        result = _get_artifact_types_impl(mock_client, template_id=1)

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "API_ERROR"
        assert "Connection timeout" in result_data["details"]["message"]
        assert result_data["details"]["template_id"] == 1

    def test_get_artifact_types_preserves_all_fields(self):
        """Test that all fields from API response are preserved"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.side_effect = [
            [
                {
                    "RequirementTypeId": 1,
                    "Name": "User Story",
                    "WorkflowId": 5,
                    "Active": True,
                    "IsDefault": False,
                    "CustomField": "CustomValue",
                }
            ],
            [],
            [],
            [],
            [],
            [],
        ]

        # Act
        result = _get_artifact_types_impl(mock_client, template_id=1)

        # Assert
        result_data = json.loads(result)
        requirement_type = result_data["data"][0]["Types"][0]
        assert requirement_type["RequirementTypeId"] == 1
        assert requirement_type["Name"] == "User Story"
        assert requirement_type["WorkflowId"] == 5
        assert requirement_type["Active"] is True
        assert requirement_type["IsDefault"] is False
        assert requirement_type["CustomField"] == "CustomValue"

    def test_get_artifact_types_multiple_types_per_artifact(self):
        """Test handling multiple types for each artifact"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.side_effect = [
            [
                {"RequirementTypeId": 1, "Name": "User Story"},
                {"RequirementTypeId": 2, "Name": "Epic"},
                {"RequirementTypeId": 3, "Name": "Feature"},
            ],
            [
                {"TestCaseTypeId": 1, "Name": "Functional"},
                {"TestCaseTypeId": 2, "Name": "Performance"},
            ],
            [{"TaskTypeId": 1, "Name": "Development"}],
            [{"RiskTypeId": 1, "Name": "Technical"}],
            [
                {"IncidentTypeId": 1, "Name": "Bug"},
                {"IncidentTypeId": 2, "Name": "Enhancement"},
            ],
            [{"DocumentTypeId": 1, "Name": "Specification"}],
        ]

        # Act
        result = _get_artifact_types_impl(mock_client, template_id=1)

        # Assert
        result_data = json.loads(result)
        assert len(result_data["data"]) == 6

        # Check requirement types count
        requirement_artifact = next(
            item for item in result_data["data"] if item["ArtifactTypeName"] == "Requirement"
        )
        assert len(requirement_artifact["Types"]) == 3

        # Check test case types count
        testcase_artifact = next(
            item for item in result_data["data"] if item["ArtifactTypeName"] == "Test Case"
        )
        assert len(testcase_artifact["Types"]) == 2

        # Check incident types count
        incident_artifact = next(
            item for item in result_data["data"] if item["ArtifactTypeName"] == "Incident"
        )
        assert len(incident_artifact["Types"]) == 2

    def test_get_artifact_types_document_active_only_parameter(self):
        """Test that document types URL includes active_only parameter"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.return_value = []

        # Act
        _get_artifact_types_impl(mock_client, template_id=1)

        # Assert
        calls = mock_client.make_spira_api_get_request.call_args_list
        document_call = calls[5][0][0]
        assert "document-types?active_only=true" in document_call

    def test_get_artifact_types_different_template_ids(self):
        """Test with different template IDs"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.return_value = []

        # Act
        _get_artifact_types_impl(mock_client, template_id=999)

        # Assert
        calls = mock_client.make_spira_api_get_request.call_args_list
        for call in calls:
            url = call[0][0]
            assert "project-templates/999/" in url or "project-templates/999/" in url

    def test_get_artifact_types_json_structure(self):
        """Test that response has correct JSON structure"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.side_effect = [
            [{"RequirementTypeId": 1, "Name": "User Story"}],
            [],
            [],
            [],
            [],
            [],
        ]

        # Act
        result = _get_artifact_types_impl(mock_client, template_id=1)

        # Assert
        result_data = json.loads(result)
        assert "data" in result_data
        assert isinstance(result_data["data"], list)
        assert len(result_data["data"]) > 0
        assert "ArtifactTypeName" in result_data["data"][0]
        assert "Types" in result_data["data"][0]
        assert isinstance(result_data["data"][0]["Types"], list)

    def test_get_artifact_types_error_response_structure(self):
        """Test that error responses have correct structure"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.side_effect = Exception("API Error")

        # Act
        result = _get_artifact_types_impl(mock_client, template_id=1)

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert "error_code" in result_data
        assert "details" in result_data
        assert "suggestion" in result_data
        assert result_data["error_code"] == "API_ERROR"
        assert "message" in result_data["details"]
        assert "template_id" in result_data["details"]


class TestGetArtifactTypesValidation:
    """Test suite for get_artifact_types input validation"""

    def test_get_artifact_types_invalid_template_id_negative(self):
        """Test validation error when template_id is negative"""
        # Arrange
        from collections.abc import Callable
        from typing import Any
        from unittest.mock import MagicMock

        from mcp_server_spira.features.templateconfiguration.tools.artifacttypes import (
            register_tools,
        )

        mock_mcp = MagicMock()
        tool_func: Callable[..., Any] | None = None

        def capture_tool(name=None):
            def decorator(func):
                nonlocal tool_func
                tool_func = func
                return func

            return decorator

        mock_mcp.tool = capture_tool
        register_tools(mock_mcp)

        # Act
        assert tool_func is not None
        result = tool_func(template_id=-1)

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "INVALID_VALUE"
        assert result_data["details"]["parameter"] == "template_id"
        assert result_data["details"]["value"] == -1

    def test_get_artifact_types_invalid_template_id_zero(self):
        """Test validation error when template_id is zero"""
        # Arrange
        from collections.abc import Callable
        from typing import Any
        from unittest.mock import MagicMock

        from mcp_server_spira.features.templateconfiguration.tools.artifacttypes import (
            register_tools,
        )

        mock_mcp = MagicMock()
        tool_func: Callable[..., Any] | None = None

        def capture_tool(name=None):
            def decorator(func):
                nonlocal tool_func
                tool_func = func
                return func

            return decorator

        mock_mcp.tool = capture_tool
        register_tools(mock_mcp)

        # Act
        assert tool_func is not None
        result = tool_func(template_id=0)

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "INVALID_VALUE"
        assert result_data["details"]["parameter"] == "template_id"
        assert result_data["details"]["value"] == 0

    def test_get_artifact_types_invalid_template_id_string(self):
        """Test validation error when template_id is a string"""
        # Arrange
        from collections.abc import Callable
        from typing import Any
        from unittest.mock import MagicMock

        from mcp_server_spira.features.templateconfiguration.tools.artifacttypes import (
            register_tools,
        )

        mock_mcp = MagicMock()
        tool_func: Callable[..., Any] | None = None

        def capture_tool(name=None):
            def decorator(func):
                nonlocal tool_func
                tool_func = func
                return func

            return decorator

        mock_mcp.tool = capture_tool
        register_tools(mock_mcp)

        # Act
        assert tool_func is not None
        result = tool_func(template_id="invalid")

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "INVALID_TYPE"
        assert result_data["details"]["parameter"] == "template_id"
        assert result_data["details"]["value"] == "invalid"

    def test_get_artifact_types_valid_template_id_positive(self):
        """Test that positive template_id passes validation"""
        # Arrange
        from collections.abc import Callable
        from typing import Any
        from unittest.mock import MagicMock, patch

        from mcp_server_spira.features.templateconfiguration.tools.artifacttypes import (
            register_tools,
        )

        mock_mcp = MagicMock()
        tool_func: Callable[..., Any] | None = None

        def capture_tool(name=None):
            def decorator(func):
                nonlocal tool_func
                tool_func = func
                return func

            return decorator

        mock_mcp.tool = capture_tool
        register_tools(mock_mcp)

        # Mock the Spira client
        with patch(
            "mcp_server_spira.features.templateconfiguration.tools.artifacttypes.get_spira_client"
        ) as mock_get_client:
            mock_client = MagicMock()
            mock_client.make_spira_api_get_request.return_value = []
            mock_get_client.return_value = mock_client

            # Act
            assert tool_func is not None
            result = tool_func(template_id=1)

            # Assert
            result_data = json.loads(result)
            assert "data" in result_data
            assert "error" not in result_data


class TestGetArtifactTypesMCPWrapper:
    """Test suite for MCP wrapper of get_artifact_types"""

    def test_mcp_wrapper_success(self):
        """Test MCP wrapper with successful execution"""
        from collections.abc import Callable
        from typing import Any
        from unittest.mock import MagicMock, patch

        from mcp_server_spira.features.templateconfiguration.tools.artifacttypes import (
            register_tools,
        )

        # Create mock MCP server
        mock_mcp = MagicMock()
        tool_func: Callable[..., Any] | None = None

        def capture_tool(name=None):
            def decorator(func):
                nonlocal tool_func
                tool_func = func
                return func

            return decorator

        mock_mcp.tool = capture_tool
        register_tools(mock_mcp)

        # Mock the Spira client
        with patch(
            "mcp_server_spira.features.templateconfiguration.tools.artifacttypes.get_spira_client"
        ) as mock_get_client:
            mock_client = MagicMock()
            mock_client.make_spira_api_get_request.return_value = []
            mock_get_client.return_value = mock_client

            # Call the tool
            assert tool_func is not None
            result = tool_func(template_id=1)

            # Verify result
            result_data = json.loads(result)
            assert "data" in result_data

    def test_mcp_wrapper_exception_handling(self):
        """Test MCP wrapper handles exceptions from implementation"""
        from collections.abc import Callable
        from typing import Any
        from unittest.mock import MagicMock, patch

        from mcp_server_spira.features.templateconfiguration.tools.artifacttypes import (
            register_tools,
        )

        # Create mock MCP server
        mock_mcp = MagicMock()
        tool_func: Callable[..., Any] | None = None

        def capture_tool(name=None):
            def decorator(func):
                nonlocal tool_func
                tool_func = func
                return func

            return decorator

        mock_mcp.tool = capture_tool
        register_tools(mock_mcp)

        # Mock get_spira_client to raise exception
        with patch(
            "mcp_server_spira.features.templateconfiguration.tools.artifacttypes.get_spira_client"
        ) as mock_get_client:
            mock_get_client.side_effect = Exception("Connection failed")

            # Call the tool
            assert tool_func is not None
            result = tool_func(template_id=1)

            # Verify error response
            result_data = json.loads(result)
            assert "error" in result_data
            assert result_data["error_code"] == "API_ERROR"
            assert "Connection failed" in result_data["details"]["message"]
