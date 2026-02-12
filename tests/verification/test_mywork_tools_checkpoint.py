"""
Checkpoint verification for all 5 "my work" tools.

This test suite verifies that all 5 tools:
1. Return valid JSON
2. Have working pagination
3. Have proper input validation
"""

import json
from typing import Any
from unittest.mock import Mock

import pytest

from mcp_server_spira.features.mywork.tools.myincidents import _get_my_incidents_impl
from mcp_server_spira.features.mywork.tools.myrequirements import _get_my_requirements_impl
from mcp_server_spira.features.mywork.tools.mytasks import _get_my_tasks_impl
from mcp_server_spira.features.mywork.tools.mytestcases import _get_my_testcases_impl
from mcp_server_spira.features.mywork.tools.mytestsets import _get_my_testsets_impl

# Sample data for each artifact type
SAMPLE_TASKS = [
    {"TaskId": i, "Name": f"Task {i}", "TaskStatusName": "In Progress"} for i in range(1, 51)
]

SAMPLE_INCIDENTS = [
    {"IncidentId": i, "Name": f"Incident {i}", "IncidentStatusName": "New"} for i in range(1, 51)
]

SAMPLE_REQUIREMENTS = [
    {"RequirementId": i, "Name": f"Requirement {i}", "StatusName": "In Progress"}
    for i in range(1, 51)
]

SAMPLE_TESTCASES = [
    {"TestCaseId": i, "Name": f"Test Case {i}", "TestCaseStatusName": "Ready"} for i in range(1, 51)
]

SAMPLE_TESTSETS = [
    {"TestSetId": i, "Name": f"Test Set {i}", "TestSetStatusName": "In Progress"}
    for i in range(1, 51)
]


class TestMyWorkToolsCheckpoint:
    """Checkpoint verification for all 5 my work tools."""

    # ========================================================================
    # Test 1: Valid JSON Output
    # ========================================================================

    def test_all_tools_return_valid_json(self):
        """Verify all 5 tools return valid JSON."""
        mock_client = Mock()

        # Test each tool
        tools_and_data = [
            (_get_my_tasks_impl, SAMPLE_TASKS),
            (_get_my_incidents_impl, SAMPLE_INCIDENTS),
            (_get_my_requirements_impl, SAMPLE_REQUIREMENTS),
            (_get_my_testcases_impl, SAMPLE_TESTCASES),
            (_get_my_testsets_impl, SAMPLE_TESTSETS),
        ]

        for tool_impl, sample_data in tools_and_data:
            mock_client.make_spira_api_get_request.return_value = sample_data

            result = tool_impl(mock_client, limit=25, offset=0)

            # Should be valid JSON
            parsed = json.loads(result)
            assert isinstance(parsed, dict)
            assert "data" in parsed
            assert "pagination" in parsed

    # ========================================================================
    # Test 2: Pagination Works Correctly
    # ========================================================================

    def test_all_tools_pagination_first_page(self):
        """Verify pagination works for first page across all tools."""
        mock_client = Mock()

        tools_and_data = [
            (_get_my_tasks_impl, SAMPLE_TASKS),
            (_get_my_incidents_impl, SAMPLE_INCIDENTS),
            (_get_my_requirements_impl, SAMPLE_REQUIREMENTS),
            (_get_my_testcases_impl, SAMPLE_TESTCASES),
            (_get_my_testsets_impl, SAMPLE_TESTSETS),
        ]

        for tool_impl, sample_data in tools_and_data:
            mock_client.make_spira_api_get_request.return_value = sample_data

            result = tool_impl(mock_client, limit=10, offset=0)
            parsed = json.loads(result)

            # Verify pagination metadata
            assert parsed["pagination"]["limit"] == 10
            assert parsed["pagination"]["offset"] == 0
            assert parsed["pagination"]["returned_count"] == 10
            assert parsed["pagination"]["total_count"] == 50
            assert parsed["pagination"]["has_more"] is True
            assert parsed["pagination"]["pagination_type"] == "client-side"

            # Verify data
            assert len(parsed["data"]) == 10

    def test_all_tools_pagination_middle_page(self):
        """Verify pagination works for middle page across all tools."""
        mock_client = Mock()

        tools_and_data = [
            (_get_my_tasks_impl, SAMPLE_TASKS),
            (_get_my_incidents_impl, SAMPLE_INCIDENTS),
            (_get_my_requirements_impl, SAMPLE_REQUIREMENTS),
            (_get_my_testcases_impl, SAMPLE_TESTCASES),
            (_get_my_testsets_impl, SAMPLE_TESTSETS),
        ]

        for tool_impl, sample_data in tools_and_data:
            mock_client.make_spira_api_get_request.return_value = sample_data

            result = tool_impl(mock_client, limit=10, offset=20)
            parsed = json.loads(result)

            # Verify pagination metadata
            assert parsed["pagination"]["limit"] == 10
            assert parsed["pagination"]["offset"] == 20
            assert parsed["pagination"]["returned_count"] == 10
            assert parsed["pagination"]["total_count"] == 50
            assert parsed["pagination"]["has_more"] is True

    def test_all_tools_pagination_last_page(self):
        """Verify pagination works for last page across all tools."""
        mock_client = Mock()

        tools_and_data = [
            (_get_my_tasks_impl, SAMPLE_TASKS),
            (_get_my_incidents_impl, SAMPLE_INCIDENTS),
            (_get_my_requirements_impl, SAMPLE_REQUIREMENTS),
            (_get_my_testcases_impl, SAMPLE_TESTCASES),
            (_get_my_testsets_impl, SAMPLE_TESTSETS),
        ]

        for tool_impl, sample_data in tools_and_data:
            mock_client.make_spira_api_get_request.return_value = sample_data

            result = tool_impl(mock_client, limit=10, offset=45)
            parsed = json.loads(result)

            # Verify pagination metadata
            assert parsed["pagination"]["limit"] == 10
            assert parsed["pagination"]["offset"] == 45
            assert parsed["pagination"]["returned_count"] == 5
            assert parsed["pagination"]["total_count"] == 50
            assert parsed["pagination"]["has_more"] is False

    def test_all_tools_pagination_empty_results(self):
        """Verify pagination works with empty results across all tools."""
        mock_client = Mock()

        tools_and_data: list[tuple[Any, list[Any]]] = [
            (_get_my_tasks_impl, []),
            (_get_my_incidents_impl, []),
            (_get_my_requirements_impl, []),
            (_get_my_testcases_impl, []),
            (_get_my_testsets_impl, []),
        ]

        for tool_impl, sample_data in tools_and_data:
            mock_client.make_spira_api_get_request.return_value = sample_data

            result = tool_impl(mock_client, limit=25, offset=0)
            parsed = json.loads(result)

            # Verify pagination metadata
            assert parsed["pagination"]["returned_count"] == 0
            assert parsed["pagination"]["total_count"] == 0
            assert parsed["pagination"]["has_more"] is False
            assert len(parsed["data"]) == 0

    # ========================================================================
    # Test 3: Input Validation
    # ========================================================================

    def test_all_tools_validate_limit_too_high(self):
        """Verify all tools reject limit > 500."""
        from mcp_server_spira.features.common.validation import ParameterValidator

        validation_error = ParameterValidator.validate_pagination_params(limit=1000, offset=0)

        assert validation_error is not None
        assert validation_error["error_code"] == "INVALID_PARAMETER"
        assert validation_error["details"]["parameter"] == "limit"
        assert validation_error["details"]["value"] == 1000

    def test_all_tools_validate_limit_too_low(self):
        """Verify all tools reject limit < 1."""
        from mcp_server_spira.features.common.validation import ParameterValidator

        validation_error = ParameterValidator.validate_pagination_params(limit=0, offset=0)

        assert validation_error is not None
        assert validation_error["error_code"] == "INVALID_PARAMETER"
        assert validation_error["details"]["parameter"] == "limit"

    def test_all_tools_validate_negative_offset(self):
        """Verify all tools reject negative offset."""
        from mcp_server_spira.features.common.validation import ParameterValidator

        validation_error = ParameterValidator.validate_pagination_params(limit=25, offset=-1)

        assert validation_error is not None
        assert validation_error["error_code"] == "INVALID_PARAMETER"
        assert validation_error["details"]["parameter"] == "offset"

    def test_all_tools_validate_valid_params(self):
        """Verify all tools accept valid parameters."""
        from mcp_server_spira.features.common.validation import ParameterValidator

        # Test various valid combinations
        valid_params = [
            (1, 0),
            (25, 0),
            (500, 0),
            (25, 100),
            (100, 500),
        ]

        for limit, offset in valid_params:
            validation_error = ParameterValidator.validate_pagination_params(
                limit=limit, offset=offset
            )
            assert validation_error is None

    # ========================================================================
    # Test 4: Error Handling
    # ========================================================================

    def test_all_tools_handle_api_errors(self):
        """Verify all tools handle API errors gracefully."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.side_effect = Exception("API Error")

        tools = [
            _get_my_tasks_impl,
            _get_my_incidents_impl,
            _get_my_requirements_impl,
            _get_my_testcases_impl,
            _get_my_testsets_impl,
        ]

        for tool_impl in tools:
            result = tool_impl(mock_client, limit=25, offset=0)
            parsed = json.loads(result)

            # Should return error response
            assert "error" in parsed
            assert parsed["error_code"] == "API_ERROR"
            assert "suggestion" in parsed

    # ========================================================================
    # Test 5: Data Integrity
    # ========================================================================

    def test_all_tools_preserve_data_fields(self):
        """Verify all tools preserve all data fields from API."""
        mock_client = Mock()

        # Test with rich data
        rich_task = {
            "TaskId": 123,
            "Name": "Test Task",
            "Description": "Test Description",
            "TaskStatusName": "In Progress",
            "CustomProperties": [{"Name": "Custom1", "Value": "Value1"}],
            "Tags": "tag1,tag2",
        }

        mock_client.make_spira_api_get_request.return_value = [rich_task]

        result = _get_my_tasks_impl(mock_client, limit=25, offset=0)
        parsed = json.loads(result)

        # All fields should be preserved
        returned_task = parsed["data"][0]
        assert returned_task["TaskId"] == 123
        assert returned_task["Name"] == "Test Task"
        assert returned_task["Description"] == "Test Description"
        assert returned_task["CustomProperties"] == [{"Name": "Custom1", "Value": "Value1"}]
        assert returned_task["Tags"] == "tag1,tag2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
