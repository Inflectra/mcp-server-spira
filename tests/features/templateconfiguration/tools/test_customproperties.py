"""
Unit tests for get_custom_properties tool
"""

import json
from unittest.mock import MagicMock

from mcp_server_spira.features.templateconfiguration.tools.customproperties import (
    _get_custom_properties_for_artifact_type,
    _get_custom_properties_impl,
)


class TestGetCustomProperties:
    """Test suite for get_custom_properties tool"""

    def test_get_custom_properties_success_all_types(self):
        """Test successful retrieval of custom properties for all artifact types"""
        # Arrange
        mock_client = MagicMock()

        # Mock responses for each artifact type
        mock_responses = [
            # Requirement
            [
                {
                    "CustomPropertyId": 1,
                    "PropertyNumber": 1,
                    "Name": "Business Unit",
                    "CustomPropertyTypeId": 1,
                    "CustomPropertyTypeName": "Text",
                    "IsDeleted": False,
                    "IsRequired": False,
                    "IsRichText": False,
                    "Options": None,
                }
            ],
            # Release
            [
                {
                    "CustomPropertyId": 2,
                    "PropertyNumber": 1,
                    "Name": "Release Type",
                    "CustomPropertyTypeId": 2,
                    "CustomPropertyTypeName": "List",
                    "IsDeleted": False,
                    "IsRequired": True,
                    "IsRichText": False,
                    "Options": [
                        {"CustomPropertyValueId": 1, "Name": "Major"},
                        {"CustomPropertyValueId": 2, "Name": "Minor"},
                    ],
                }
            ],
            # TestCase
            [
                {
                    "CustomPropertyId": 3,
                    "PropertyNumber": 1,
                    "Name": "Test Environment",
                    "CustomPropertyTypeId": 2,
                    "CustomPropertyTypeName": "List",
                    "IsDeleted": False,
                    "IsRequired": True,
                    "IsRichText": False,
                    "Options": [
                        {"CustomPropertyValueId": 3, "Name": "Development"},
                        {"CustomPropertyValueId": 4, "Name": "Staging"},
                    ],
                }
            ],
            # Task
            [],
            # Risk
            [],
            # Incident
            [
                {
                    "CustomPropertyId": 4,
                    "PropertyNumber": 1,
                    "Name": "Root Cause",
                    "CustomPropertyTypeId": 1,
                    "CustomPropertyTypeName": "Text",
                    "IsDeleted": False,
                    "IsRequired": False,
                    "IsRichText": True,
                    "Options": None,
                }
            ],
            # TestSet
            [],
            # TestStep
            [],
            # TestRun
            [],
            # AutomationHost
            [],
            # Document
            [],
        ]

        mock_client.make_spira_api_get_request.side_effect = mock_responses

        # Act
        result = _get_custom_properties_impl(mock_client, template_id=1)

        # Assert
        result_data = json.loads(result)
        assert "data" in result_data
        assert len(result_data["data"]) == 4  # Only 4 types with custom properties

        # Verify artifact types with custom properties are present
        artifact_names = [item["ArtifactTypeName"] for item in result_data["data"]]
        assert "Requirement" in artifact_names
        assert "Release" in artifact_names
        assert "TestCase" in artifact_names
        assert "Incident" in artifact_names

        # Verify API was called 11 times (once for each artifact type)
        assert mock_client.make_spira_api_get_request.call_count == 11

    def test_get_custom_properties_success_requirement_structure(self):
        """Test that requirement custom properties are structured correctly"""
        # Arrange
        mock_client = MagicMock()
        mock_responses = [
            # Requirement
            [
                {
                    "CustomPropertyId": 1,
                    "PropertyNumber": 1,
                    "Name": "Business Unit",
                    "CustomPropertyTypeId": 1,
                    "CustomPropertyTypeName": "Text",
                    "IsDeleted": False,
                    "IsRequired": False,
                    "IsRichText": False,
                    "Options": None,
                },
                {
                    "CustomPropertyId": 2,
                    "PropertyNumber": 2,
                    "Name": "Priority Score",
                    "CustomPropertyTypeId": 3,
                    "CustomPropertyTypeName": "Integer",
                    "IsDeleted": False,
                    "IsRequired": True,
                    "IsRichText": False,
                    "Options": None,
                },
            ],
        ]
        # Add empty responses for other artifact types
        mock_responses.extend([[] for _ in range(10)])
        mock_client.make_spira_api_get_request.side_effect = mock_responses

        # Act
        result = _get_custom_properties_impl(mock_client, template_id=1)

        # Assert
        result_data = json.loads(result)
        requirement_artifact = next(
            item for item in result_data["data"] if item["ArtifactTypeName"] == "Requirement"
        )
        assert len(requirement_artifact["CustomProperties"]) == 2
        assert requirement_artifact["CustomProperties"][0]["CustomPropertyId"] == 1
        assert requirement_artifact["CustomProperties"][0]["Name"] == "Business Unit"
        assert requirement_artifact["CustomProperties"][1]["CustomPropertyId"] == 2
        assert requirement_artifact["CustomProperties"][1]["Name"] == "Priority Score"

    def test_get_custom_properties_empty_properties(self):
        """Test when all artifact types return empty arrays"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.return_value = []

        # Act
        result = _get_custom_properties_impl(mock_client, template_id=1)

        # Assert
        result_data = json.loads(result)
        assert len(result_data["data"]) == 0  # No artifact types with custom properties

    def test_get_custom_properties_none_response(self):
        """Test when API returns None for some types"""
        # Arrange
        mock_client = MagicMock()
        mock_responses = [
            [{"CustomPropertyId": 1, "Name": "Test Property"}],  # Requirement
            None,  # Release
            None,  # TestCase
            None,  # Task
            None,  # Risk
            None,  # Incident
            None,  # TestSet
            None,  # TestStep
            None,  # TestRun
            None,  # AutomationHost
            None,  # Document
        ]
        mock_client.make_spira_api_get_request.side_effect = mock_responses

        # Act
        result = _get_custom_properties_impl(mock_client, template_id=1)

        # Assert
        result_data = json.loads(result)
        assert len(result_data["data"]) == 1
        assert result_data["data"][0]["ArtifactTypeName"] == "Requirement"

    def test_get_custom_properties_correct_urls(self):
        """Test that correct API URLs are called"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.return_value = []

        # Act
        _get_custom_properties_impl(mock_client, template_id=42)

        # Assert
        calls = mock_client.make_spira_api_get_request.call_args_list
        assert len(calls) == 11

        expected_artifact_types = [
            "Requirement",
            "Release",
            "TestCase",
            "Task",
            "Risk",
            "Incident",
            "TestSet",
            "TestStep",
            "TestRun",
            "AutomationHost",
            "Document",
        ]

        for i, artifact_type in enumerate(expected_artifact_types):
            expected_url = f"project-templates/42/custom-properties/{artifact_type}"
            assert calls[i][0][0] == expected_url

    def test_get_custom_properties_api_exception(self):
        """Test error handling when API raises exception in helper function"""
        # Arrange
        mock_client = MagicMock()
        # The helper function catches exceptions and returns empty list
        # So individual API failures don't propagate to main function
        mock_client.make_spira_api_get_request.side_effect = Exception("Connection timeout")

        # Act
        result = _get_custom_properties_impl(mock_client, template_id=1)

        # Assert
        # Since helper catches exceptions, we get empty data array
        result_data = json.loads(result)
        assert "data" in result_data
        assert len(result_data["data"]) == 0

    def test_get_custom_properties_preserves_all_fields(self):
        """Test that all fields from API response are preserved"""
        # Arrange
        mock_client = MagicMock()
        mock_responses = [
            [
                {
                    "CustomPropertyId": 1,
                    "PropertyNumber": 1,
                    "Name": "Business Unit",
                    "CustomPropertyTypeId": 1,
                    "CustomPropertyTypeName": "Text",
                    "IsDeleted": False,
                    "IsRequired": False,
                    "IsRichText": False,
                    "Options": None,
                    "CustomField": "CustomValue",
                }
            ]
        ]
        mock_responses.extend([[] for _ in range(10)])
        mock_client.make_spira_api_get_request.side_effect = mock_responses

        # Act
        result = _get_custom_properties_impl(mock_client, template_id=1)

        # Assert
        result_data = json.loads(result)
        custom_prop = result_data["data"][0]["CustomProperties"][0]
        assert custom_prop["CustomPropertyId"] == 1
        assert custom_prop["Name"] == "Business Unit"
        assert custom_prop["CustomPropertyTypeId"] == 1
        assert custom_prop["CustomPropertyTypeName"] == "Text"
        assert custom_prop["IsDeleted"] is False
        assert custom_prop["IsRequired"] is False
        assert custom_prop["IsRichText"] is False
        assert custom_prop["Options"] is None
        assert custom_prop["CustomField"] == "CustomValue"

    def test_get_custom_properties_multiple_properties_per_artifact(self):
        """Test handling multiple custom properties for each artifact"""
        # Arrange
        mock_client = MagicMock()
        mock_responses = [
            # Requirement - 3 properties
            [
                {"CustomPropertyId": 1, "Name": "Business Unit"},
                {"CustomPropertyId": 2, "Name": "Priority Score"},
                {"CustomPropertyId": 3, "Name": "Customer Impact"},
            ],
            # Release - 2 properties
            [
                {"CustomPropertyId": 4, "Name": "Release Type"},
                {"CustomPropertyId": 5, "Name": "Release Notes"},
            ],
            # TestCase - 1 property
            [{"CustomPropertyId": 6, "Name": "Test Environment"}],
        ]
        mock_responses.extend([[] for _ in range(8)])
        mock_client.make_spira_api_get_request.side_effect = mock_responses

        # Act
        result = _get_custom_properties_impl(mock_client, template_id=1)

        # Assert
        result_data = json.loads(result)
        assert len(result_data["data"]) == 3

        # Check requirement properties count
        requirement_artifact = next(
            item for item in result_data["data"] if item["ArtifactTypeName"] == "Requirement"
        )
        assert len(requirement_artifact["CustomProperties"]) == 3

        # Check release properties count
        release_artifact = next(
            item for item in result_data["data"] if item["ArtifactTypeName"] == "Release"
        )
        assert len(release_artifact["CustomProperties"]) == 2

        # Check test case properties count
        testcase_artifact = next(
            item for item in result_data["data"] if item["ArtifactTypeName"] == "TestCase"
        )
        assert len(testcase_artifact["CustomProperties"]) == 1

    def test_get_custom_properties_list_type_with_options(self):
        """Test custom properties with list type and options"""
        # Arrange
        mock_client = MagicMock()
        mock_responses = [
            [
                {
                    "CustomPropertyId": 1,
                    "Name": "Priority",
                    "CustomPropertyTypeId": 2,
                    "CustomPropertyTypeName": "List",
                    "Options": [
                        {"CustomPropertyValueId": 1, "Name": "High"},
                        {"CustomPropertyValueId": 2, "Name": "Medium"},
                        {"CustomPropertyValueId": 3, "Name": "Low"},
                    ],
                }
            ]
        ]
        mock_responses.extend([[] for _ in range(10)])
        mock_client.make_spira_api_get_request.side_effect = mock_responses

        # Act
        result = _get_custom_properties_impl(mock_client, template_id=1)

        # Assert
        result_data = json.loads(result)
        custom_prop = result_data["data"][0]["CustomProperties"][0]
        assert custom_prop["CustomPropertyTypeName"] == "List"
        assert custom_prop["Options"] is not None
        assert len(custom_prop["Options"]) == 3
        assert custom_prop["Options"][0]["CustomPropertyValueId"] == 1
        assert custom_prop["Options"][0]["Name"] == "High"

    def test_get_custom_properties_different_template_ids(self):
        """Test with different template IDs"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.return_value = []

        # Act
        _get_custom_properties_impl(mock_client, template_id=999)

        # Assert
        calls = mock_client.make_spira_api_get_request.call_args_list
        for call in calls:
            url = call[0][0]
            assert "project-templates/999/" in url

    def test_get_custom_properties_json_structure(self):
        """Test that response has correct JSON structure"""
        # Arrange
        mock_client = MagicMock()
        mock_responses = [[{"CustomPropertyId": 1, "Name": "Test Property"}]]
        mock_responses.extend([[] for _ in range(10)])
        mock_client.make_spira_api_get_request.side_effect = mock_responses

        # Act
        result = _get_custom_properties_impl(mock_client, template_id=1)

        # Assert
        result_data = json.loads(result)
        assert "data" in result_data
        assert isinstance(result_data["data"], list)
        assert len(result_data["data"]) > 0
        assert "ArtifactTypeName" in result_data["data"][0]
        assert "CustomProperties" in result_data["data"][0]
        assert isinstance(result_data["data"][0]["CustomProperties"], list)

    def test_get_custom_properties_error_response_structure(self):
        """Test that error responses have correct structure when main function fails"""
        # Arrange
        from unittest.mock import patch

        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.return_value = []

        # Patch format_success_response to raise an exception
        with patch(
            "mcp_server_spira.features.templateconfiguration.tools.customproperties.format_success_response"
        ) as mock_format:
            mock_format.side_effect = Exception("Formatting error")

            # Act
            result = _get_custom_properties_impl(mock_client, template_id=1)

            # Assert
            result_data = json.loads(result)
            assert "error" in result_data
            assert "error_code" in result_data
            assert "details" in result_data
            assert "suggestion" in result_data
            assert result_data["error_code"] == "API_ERROR"
            assert "message" in result_data["details"]
            assert "template_id" in result_data["details"]

    def test_get_custom_properties_required_and_optional_fields(self):
        """Test custom properties with required and optional fields"""
        # Arrange
        mock_client = MagicMock()
        mock_responses = [
            [
                {
                    "CustomPropertyId": 1,
                    "Name": "Required Field",
                    "IsRequired": True,
                },
                {
                    "CustomPropertyId": 2,
                    "Name": "Optional Field",
                    "IsRequired": False,
                },
            ]
        ]
        mock_responses.extend([[] for _ in range(10)])
        mock_client.make_spira_api_get_request.side_effect = mock_responses

        # Act
        result = _get_custom_properties_impl(mock_client, template_id=1)

        # Assert
        result_data = json.loads(result)
        props = result_data["data"][0]["CustomProperties"]
        assert props[0]["IsRequired"] is True
        assert props[1]["IsRequired"] is False

    def test_get_custom_properties_rich_text_field(self):
        """Test custom properties with rich text support"""
        # Arrange
        mock_client = MagicMock()
        mock_responses = [
            [
                {
                    "CustomPropertyId": 1,
                    "Name": "Description",
                    "IsRichText": True,
                },
                {
                    "CustomPropertyId": 2,
                    "Name": "Notes",
                    "IsRichText": False,
                },
            ]
        ]
        mock_responses.extend([[] for _ in range(10)])
        mock_client.make_spira_api_get_request.side_effect = mock_responses

        # Act
        result = _get_custom_properties_impl(mock_client, template_id=1)

        # Assert
        result_data = json.loads(result)
        props = result_data["data"][0]["CustomProperties"]
        assert props[0]["IsRichText"] is True
        assert props[1]["IsRichText"] is False

    def test_get_custom_properties_deleted_field(self):
        """Test custom properties with deleted flag"""
        # Arrange
        mock_client = MagicMock()
        mock_responses = [
            [
                {
                    "CustomPropertyId": 1,
                    "Name": "Active Field",
                    "IsDeleted": False,
                },
                {
                    "CustomPropertyId": 2,
                    "Name": "Deleted Field",
                    "IsDeleted": True,
                },
            ]
        ]
        mock_responses.extend([[] for _ in range(10)])
        mock_client.make_spira_api_get_request.side_effect = mock_responses

        # Act
        result = _get_custom_properties_impl(mock_client, template_id=1)

        # Assert
        result_data = json.loads(result)
        props = result_data["data"][0]["CustomProperties"]
        assert props[0]["IsDeleted"] is False
        assert props[1]["IsDeleted"] is True


class TestGetCustomPropertiesForArtifactType:
    """Test suite for _get_custom_properties_for_artifact_type helper function"""

    def test_get_custom_properties_for_artifact_type_success(self):
        """Test successful retrieval of custom properties for a specific artifact type"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.return_value = [
            {"CustomPropertyId": 1, "Name": "Test Property"}
        ]

        # Act
        result = _get_custom_properties_for_artifact_type(
            mock_client, template_id=1, artifact_type_name="Requirement"
        )

        # Assert
        assert len(result) == 1
        assert result[0]["CustomPropertyId"] == 1
        assert result[0]["Name"] == "Test Property"
        mock_client.make_spira_api_get_request.assert_called_once_with(
            "project-templates/1/custom-properties/Requirement"
        )

    def test_get_custom_properties_for_artifact_type_empty_response(self):
        """Test when API returns empty array"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.return_value = []

        # Act
        result = _get_custom_properties_for_artifact_type(
            mock_client, template_id=1, artifact_type_name="Task"
        )

        # Assert
        assert result == []

    def test_get_custom_properties_for_artifact_type_none_response(self):
        """Test when API returns None"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.return_value = None

        # Act
        result = _get_custom_properties_for_artifact_type(
            mock_client, template_id=1, artifact_type_name="Task"
        )

        # Assert
        assert result == []

    def test_get_custom_properties_for_artifact_type_exception(self):
        """Test error handling when API raises exception"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.side_effect = Exception("API Error")

        # Act
        result = _get_custom_properties_for_artifact_type(
            mock_client, template_id=1, artifact_type_name="Requirement"
        )

        # Assert
        assert result == []

    def test_get_custom_properties_for_artifact_type_correct_url_format(self):
        """Test that URL is formatted correctly"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.return_value = []

        # Act
        _get_custom_properties_for_artifact_type(
            mock_client, template_id=42, artifact_type_name="TestCase"
        )

        # Assert
        mock_client.make_spira_api_get_request.assert_called_once_with(
            "project-templates/42/custom-properties/TestCase"
        )

    def test_get_custom_properties_for_artifact_type_multiple_properties(self):
        """Test retrieval of multiple custom properties"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_get_request.return_value = [
            {"CustomPropertyId": 1, "Name": "Property 1"},
            {"CustomPropertyId": 2, "Name": "Property 2"},
            {"CustomPropertyId": 3, "Name": "Property 3"},
        ]

        # Act
        result = _get_custom_properties_for_artifact_type(
            mock_client, template_id=1, artifact_type_name="Incident"
        )

        # Assert
        assert len(result) == 3
        assert result[0]["CustomPropertyId"] == 1
        assert result[1]["CustomPropertyId"] == 2
        assert result[2]["CustomPropertyId"] == 3


class TestGetCustomPropertiesValidation:
    """Test suite for get_custom_properties input validation"""

    def test_get_custom_properties_invalid_template_id_negative(self):
        """Test validation error when template_id is negative"""
        # Arrange
        from collections.abc import Callable
        from typing import Any
        from unittest.mock import MagicMock

        from mcp_server_spira.features.templateconfiguration.tools.customproperties import (
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

    def test_get_custom_properties_invalid_template_id_zero(self):
        """Test validation error when template_id is zero"""
        # Arrange
        from collections.abc import Callable
        from typing import Any
        from unittest.mock import MagicMock

        from mcp_server_spira.features.templateconfiguration.tools.customproperties import (
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

    def test_get_custom_properties_invalid_template_id_string(self):
        """Test validation error when template_id is a string"""
        # Arrange
        from collections.abc import Callable
        from typing import Any
        from unittest.mock import MagicMock

        from mcp_server_spira.features.templateconfiguration.tools.customproperties import (
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

    def test_get_custom_properties_valid_template_id_positive(self):
        """Test that positive template_id passes validation"""
        # Arrange
        from collections.abc import Callable
        from typing import Any
        from unittest.mock import MagicMock, patch

        from mcp_server_spira.features.templateconfiguration.tools.customproperties import (
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
            "mcp_server_spira.features.templateconfiguration.tools.customproperties.get_spira_client"
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


class TestGetCustomPropertiesMCPWrapper:
    """Test suite for MCP wrapper of get_custom_properties"""

    def test_mcp_wrapper_success(self):
        """Test MCP wrapper with successful execution"""
        from collections.abc import Callable
        from typing import Any
        from unittest.mock import MagicMock, patch

        from mcp_server_spira.features.templateconfiguration.tools.customproperties import (
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
            "mcp_server_spira.features.templateconfiguration.tools.customproperties.get_spira_client"
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

        from mcp_server_spira.features.templateconfiguration.tools.customproperties import (
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
            "mcp_server_spira.features.templateconfiguration.tools.customproperties.get_spira_client"
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
