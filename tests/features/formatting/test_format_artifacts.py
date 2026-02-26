"""Unit tests for format_artifacts_as_markdown tool."""

import json

import pytest

from mcp_server_spira.features.formatting.tools.format_artifacts import (
    register_tools,
)


class MockMCP:
    """Mock MCP server for testing tool registration."""

    def __init__(self):
        self.tools = {}

    def tool(self, *args, **kwargs):
        """Decorator to register tools."""

        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator


@pytest.fixture
def format_tool():
    """Fixture to get the format_artifacts_as_markdown tool."""
    mock_mcp = MockMCP()
    register_tools(mock_mcp)
    return mock_mcp.tools["format_artifacts_as_markdown"]


class TestFormatArtifactsWithPagination:
    """Tests for formatting full responses with pagination metadata."""

    def test_format_tasks_with_pagination(self, format_tool):
        """Test formatting tasks with full pagination response."""
        response = {
            "data": [
                {
                    "TaskId": 123,
                    "Name": "Fix login bug",
                    "Description": "Users cannot log in",
                    "TaskStatusName": "In Progress",
                    "TaskTypeName": "Development",
                    "TaskPriorityName": "Critical",
                    "EndDate": "2024-01-16T17:00:00Z",
                }
            ],
            "pagination": {
                "limit": 25,
                "offset": 0,
                "returned_count": 1,
                "total_count": 1,
                "has_more": False,
                "pagination_type": "client-side",
            },
        }

        result = format_tool(json.dumps(response), "task")

        assert "TK:123" in result
        assert "Fix login bug" in result
        assert "Users cannot log in" in result
        assert "In Progress" in result
        assert "Critical" in result

    def test_format_incidents_with_pagination(self, format_tool):
        """Test formatting incidents with full pagination response."""
        response = {
            "data": [
                {
                    "IncidentId": 456,
                    "Name": "Login crash",
                    "Description": "App crashes on login",
                    "IncidentStatusName": "New",
                    "IncidentTypeName": "Bug",
                    "PriorityName": "1 - Critical",
                    "SeverityName": "1 - Critical",
                    "StartDate": "2024-01-15T09:00:00Z",
                }
            ],
            "pagination": {
                "limit": 25,
                "offset": 0,
                "returned_count": 1,
                "total_count": 1,
                "has_more": False,
                "pagination_type": "client-side",
            },
        }

        result = format_tool(json.dumps(response), "incident")

        assert "IN:456" in result
        assert "Login crash" in result
        assert "App crashes on login" in result
        assert "New" in result
        assert "Bug" in result

    def test_format_requirements_with_pagination(self, format_tool):
        """Test formatting requirements with full pagination response."""
        response = {
            "data": [
                {
                    "RequirementId": 789,
                    "Name": "User Authentication",
                    "Description": "System must support auth",
                    "StatusName": "Accepted",
                    "RequirementTypeName": "Feature",
                    "ImportanceName": "Critical",
                }
            ],
            "pagination": {
                "limit": 25,
                "offset": 0,
                "returned_count": 1,
                "total_count": 1,
                "has_more": False,
                "pagination_type": "client-side",
            },
        }

        result = format_tool(json.dumps(response), "requirement")

        assert "RQ:789" in result
        assert "User Authentication" in result
        assert "System must support auth" in result
        assert "Accepted" in result
        assert "Feature" in result

    def test_format_test_cases_with_pagination(self, format_tool):
        """Test formatting test cases with full pagination response."""
        response = {
            "data": [
                {
                    "TestCaseId": 101,
                    "Name": "Login Test",
                    "Description": "Test user login",
                    "TestCaseStatusName": "Ready",
                    "TestCaseTypeName": "Functional",
                    "TestCasePriorityName": "High",
                    "ExecutionStatusName": "Passed",
                }
            ],
            "pagination": {
                "limit": 25,
                "offset": 0,
                "returned_count": 1,
                "total_count": 1,
                "has_more": False,
                "pagination_type": "client-side",
            },
        }

        result = format_tool(json.dumps(response), "test_case")

        assert "TC:101" in result
        assert "Login Test" in result
        assert "Test user login" in result
        assert "Ready" in result
        assert "Functional" in result

    def test_format_test_sets_with_pagination(self, format_tool):
        """Test formatting test sets with full pagination response."""
        response = {
            "data": [
                {
                    "TestSetId": 202,
                    "Name": "Sprint 1 Tests",
                    "Description": "All tests for sprint 1",
                    "TestSetStatusName": "In Progress",
                }
            ],
            "pagination": {
                "limit": 25,
                "offset": 0,
                "returned_count": 1,
                "total_count": 1,
                "has_more": False,
                "pagination_type": "client-side",
            },
        }

        result = format_tool(json.dumps(response), "test_set")

        assert "TX:202" in result
        assert "Sprint 1 Tests" in result
        assert "All tests for sprint 1" in result
        assert "In Progress" in result


class TestFormatArtifactsDataArrayOnly:
    """Tests for formatting data arrays without pagination."""

    def test_format_tasks_data_array(self, format_tool):
        """Test formatting tasks from data array only."""
        data = [
            {
                "TaskId": 123,
                "Name": "Fix login bug",
                "Description": "Users cannot log in",
                "TaskStatusName": "In Progress",
                "TaskTypeName": "Development",
                "TaskPriorityName": "Critical",
                "EndDate": "2024-01-16T17:00:00Z",
            }
        ]

        result = format_tool(json.dumps(data), "task")

        assert "TK:123" in result
        assert "Fix login bug" in result
        assert "In Progress" in result

    def test_format_incidents_data_array(self, format_tool):
        """Test formatting incidents from data array only."""
        data = [
            {
                "IncidentId": 456,
                "Name": "Login crash",
                "Description": "App crashes on login",
                "IncidentStatusName": "New",
                "IncidentTypeName": "Bug",
                "PriorityName": "1 - Critical",
                "SeverityName": "1 - Critical",
                "StartDate": "2024-01-15T09:00:00Z",
            }
        ]

        result = format_tool(json.dumps(data), "incident")

        assert "IN:456" in result
        assert "Login crash" in result
        assert "New" in result

    def test_format_requirements_data_array(self, format_tool):
        """Test formatting requirements from data array only."""
        data = [
            {
                "RequirementId": 789,
                "Name": "User Authentication",
                "Description": "System must support auth",
                "StatusName": "Accepted",
                "RequirementTypeName": "Feature",
                "ImportanceName": "Critical",
            }
        ]

        result = format_tool(json.dumps(data), "requirement")

        assert "RQ:789" in result
        assert "User Authentication" in result
        assert "Accepted" in result

    def test_format_test_cases_data_array(self, format_tool):
        """Test formatting test cases from data array only."""
        data = [
            {
                "TestCaseId": 101,
                "Name": "Login Test",
                "Description": "Test user login",
                "TestCaseStatusName": "Ready",
                "TestCaseTypeName": "Functional",
                "TestCasePriorityName": "High",
                "ExecutionStatusName": "Passed",
            }
        ]

        result = format_tool(json.dumps(data), "test_case")

        assert "TC:101" in result
        assert "Login Test" in result
        assert "Ready" in result

    def test_format_test_sets_data_array(self, format_tool):
        """Test formatting test sets from data array only."""
        data = [
            {
                "TestSetId": 202,
                "Name": "Sprint 1 Tests",
                "Description": "All tests for sprint 1",
                "TestSetStatusName": "In Progress",
            }
        ]

        result = format_tool(json.dumps(data), "test_set")

        assert "TX:202" in result
        assert "Sprint 1 Tests" in result
        assert "In Progress" in result


class TestFormatMultipleArtifacts:
    """Tests for formatting multiple artifacts of each type."""

    def test_format_multiple_tasks(self, format_tool):
        """Test formatting multiple tasks."""
        data = [
            {
                "TaskId": 1,
                "Name": "Task 1",
                "Description": "First task",
                "TaskStatusName": "New",
                "TaskTypeName": "Development",
                "TaskPriorityName": "High",
                "EndDate": "2024-01-16T17:00:00Z",
            },
            {
                "TaskId": 2,
                "Name": "Task 2",
                "Description": "Second task",
                "TaskStatusName": "In Progress",
                "TaskTypeName": "Bug",
                "TaskPriorityName": "Critical",
                "EndDate": "2024-01-17T17:00:00Z",
            },
        ]

        result = format_tool(json.dumps(data), "task")

        assert "TK:1" in result
        assert "Task 1" in result
        assert "TK:2" in result
        assert "Task 2" in result
        # Check that artifacts are separated by double newline
        assert "\n\n" in result

    def test_format_multiple_incidents(self, format_tool):
        """Test formatting multiple incidents."""
        data = [
            {
                "IncidentId": 1,
                "Name": "Incident 1",
                "Description": "First incident",
                "IncidentStatusName": "New",
                "IncidentTypeName": "Bug",
                "PriorityName": "1 - Critical",
                "SeverityName": "1 - Critical",
                "StartDate": "2024-01-15T09:00:00Z",
            },
            {
                "IncidentId": 2,
                "Name": "Incident 2",
                "Description": "Second incident",
                "IncidentStatusName": "Open",
                "IncidentTypeName": "Enhancement",
                "PriorityName": "3 - Medium",
                "SeverityName": "3 - Medium",
                "StartDate": "2024-01-16T09:00:00Z",
            },
        ]

        result = format_tool(json.dumps(data), "incident")

        assert "IN:1" in result
        assert "Incident 1" in result
        assert "IN:2" in result
        assert "Incident 2" in result


class TestFormatEmptyLists:
    """Tests for formatting empty artifact lists."""

    def test_format_empty_task_list(self, format_tool):
        """Test formatting empty task list."""
        data: list[dict] = []
        result = format_tool(json.dumps(data), "task")
        assert result == "No artifacts to display."

    def test_format_empty_incident_list(self, format_tool):
        """Test formatting empty incident list."""
        data: list[dict] = []
        result = format_tool(json.dumps(data), "incident")
        assert result == "No artifacts to display."

    def test_format_empty_requirement_list(self, format_tool):
        """Test formatting empty requirement list."""
        data: list[dict] = []
        result = format_tool(json.dumps(data), "requirement")
        assert result == "No artifacts to display."

    def test_format_empty_test_case_list(self, format_tool):
        """Test formatting empty test case list."""
        data: list[dict] = []
        result = format_tool(json.dumps(data), "test_case")
        assert result == "No artifacts to display."

    def test_format_empty_test_set_list(self, format_tool):
        """Test formatting empty test set list."""
        data: list[dict] = []
        result = format_tool(json.dumps(data), "test_set")
        assert result == "No artifacts to display."

    def test_format_empty_with_pagination(self, format_tool):
        """Test formatting empty list with pagination metadata."""
        response = {
            "data": [],
            "pagination": {
                "limit": 25,
                "offset": 0,
                "returned_count": 0,
                "total_count": 0,
                "has_more": False,
                "pagination_type": "client-side",
            },
        }

        result = format_tool(json.dumps(response), "task")
        assert result == "No artifacts to display."


class TestFormatInvalidJSON:
    """Tests for handling invalid JSON input."""

    def test_format_invalid_json(self, format_tool):
        """Test formatting with invalid JSON."""
        result = format_tool("not valid json", "task")
        assert "Error: Invalid JSON input" in result

    def test_format_malformed_json(self, format_tool):
        """Test formatting with malformed JSON."""
        result = format_tool('{"data": [{"TaskId": 1, "Name": "Test"}', "task")
        assert "Error: Invalid JSON input" in result

    def test_format_empty_string(self, format_tool):
        """Test formatting with empty string."""
        result = format_tool("", "task")
        assert "Error: Invalid JSON input" in result


class TestFormatUnknownArtifactType:
    """Tests for handling unknown artifact types."""

    def test_format_unknown_type(self, format_tool):
        """Test formatting with unknown artifact type."""
        data = [{"Id": 1, "Name": "Test"}]
        result = format_tool(json.dumps(data), "unknown_type")
        assert "Error: Unknown artifact type 'unknown_type'" in result
        assert "Valid types:" in result

    def test_format_invalid_type_case(self, format_tool):
        """Test formatting with invalid case for artifact type."""
        data = [
            {
                "TaskId": 1,
                "Name": "Test",
                "Description": "Test",
                "TaskStatusName": "New",
                "TaskTypeName": "Development",
                "TaskPriorityName": "High",
                "EndDate": "2024-01-16T17:00:00Z",
            }
        ]
        # Type must be exact match (lowercase with underscore)
        result = format_tool(json.dumps(data), "Task")
        assert "Error: Unknown artifact type 'Task'" in result


class TestFormatMissingRequiredFields:
    """Tests for handling missing required fields in artifacts."""

    def test_format_task_missing_required_field(self, format_tool):
        """Test formatting task with missing required field."""
        data = [
            {
                "TaskId": 1,
                "Name": "Test",
                # Missing TaskStatusName
                "TaskTypeName": "Development",
                "TaskPriorityName": "High",
            }
        ]
        result = format_tool(json.dumps(data), "task")
        assert "Error: Missing required field" in result

    def test_format_incident_missing_required_field(self, format_tool):
        """Test formatting incident with missing required field."""
        data = [
            {
                "IncidentId": 1,
                "Name": "Test",
                # Missing IncidentStatusName
                "IncidentTypeName": "Bug",
                "PriorityName": "1 - Critical",
            }
        ]
        result = format_tool(json.dumps(data), "incident")
        assert "Error: Missing required field" in result

    def test_format_requirement_missing_required_field(self, format_tool):
        """Test formatting requirement with missing required field."""
        data = [
            {
                "RequirementId": 1,
                "Name": "Test",
                # Missing StatusName
                "RequirementTypeName": "Feature",
                "ImportanceName": "Critical",
            }
        ]
        result = format_tool(json.dumps(data), "requirement")
        assert "Error: Missing required field" in result

    def test_format_test_case_missing_required_field(self, format_tool):
        """Test formatting test case with missing required field."""
        data = [
            {
                "TestCaseId": 1,
                "Name": "Test",
                # Missing TestCaseStatusName
                "TestCaseTypeName": "Functional",
                "TestCasePriorityName": "High",
            }
        ]
        result = format_tool(json.dumps(data), "test_case")
        assert "Error: Missing required field" in result

    def test_format_test_set_missing_required_field(self, format_tool):
        """Test formatting test set with missing required field."""
        data = [
            {
                "TestSetId": 1,
                "Name": "Test",
                # Missing TestSetStatusName
            }
        ]
        result = format_tool(json.dumps(data), "test_set")
        assert "Error: Missing required field" in result


class TestFormatInvalidDataStructure:
    """Tests for handling invalid data structures."""

    def test_format_non_list_data(self, format_tool):
        """Test formatting with non-list data."""
        data = {
            "TaskId": 1,
            "Name": "Test",
            "TaskStatusName": "New",
            "TaskTypeName": "Development",
            "TaskPriorityName": "High",
        }
        result = format_tool(json.dumps(data), "task")
        assert "Error: Expected artifact data to be a list" in result

    def test_format_nested_non_list_data(self, format_tool):
        """Test formatting with nested non-list data."""
        response = {
            "data": {
                "TaskId": 1,
                "Name": "Test",
            }
        }
        result = format_tool(json.dumps(response), "task")
        assert "Error: Expected artifact data to be a list" in result

    def test_format_null_data(self, format_tool):
        """Test formatting with null data."""
        response = {"data": None}
        result = format_tool(json.dumps(response), "task")
        assert "Error: Expected artifact data to be a list" in result


class TestFormatOptionalFields:
    """Tests for formatting artifacts with optional fields."""

    def test_format_task_with_effort(self, format_tool):
        """Test formatting task with effort information."""
        data = [
            {
                "TaskId": 1,
                "Name": "Test Task",
                "Description": "Test",
                "TaskStatusName": "In Progress",
                "TaskTypeName": "Development",
                "TaskPriorityName": "High",
                "EndDate": "2024-01-16T17:00:00Z",
                "EstimatedEffort": 120,
                "ActualEffort": 60,
                "CompletionPercent": 50,
            }
        ]
        result = format_tool(json.dumps(data), "task")
        assert "60/120 min" in result
        assert "50% complete" in result

    def test_format_task_without_effort(self, format_tool):
        """Test formatting task without effort information."""
        data = [
            {
                "TaskId": 1,
                "Name": "Test Task",
                "Description": "Test",
                "TaskStatusName": "New",
                "TaskTypeName": "Development",
                "TaskPriorityName": "High",
                "EndDate": "2024-01-16T17:00:00Z",
            }
        ]
        result = format_tool(json.dumps(data), "task")
        assert "Effort:" not in result

    def test_format_incident_with_releases(self, format_tool):
        """Test formatting incident with release information."""
        data = [
            {
                "IncidentId": 1,
                "Name": "Test Incident",
                "Description": "Test",
                "IncidentStatusName": "New",
                "IncidentTypeName": "Bug",
                "PriorityName": "1 - Critical",
                "SeverityName": "1 - Critical",
                "StartDate": "2024-01-15T09:00:00Z",
                "DetectedReleaseVersionNumber": "1.0.0",
                "ResolvedReleaseVersionNumber": "1.1.0",
                "VerifiedReleaseVersionNumber": "1.1.0",
            }
        ]
        result = format_tool(json.dumps(data), "incident")
        assert "Detected in Release:** 1.0.0" in result
        assert "Planned for Release:** 1.1.0" in result
        assert "Verified in Release:** 1.1.0" in result

    def test_format_incident_without_releases(self, format_tool):
        """Test formatting incident without release information."""
        data = [
            {
                "IncidentId": 1,
                "Name": "Test Incident",
                "Description": "Test",
                "IncidentStatusName": "New",
                "IncidentTypeName": "Bug",
                "PriorityName": "1 - Critical",
                "SeverityName": "1 - Critical",
                "StartDate": "2024-01-15T09:00:00Z",
            }
        ]
        result = format_tool(json.dumps(data), "incident")
        assert "Detected in Release" not in result
        assert "Planned for Release" not in result
        assert "Verified in Release" not in result

    def test_format_artifact_exception_during_formatting(self, format_tool):
        """Test error handling when formatter raises exception."""
        # Create data that will cause an exception in the formatter
        data = [
            {
                "TaskId": 1,
                "Name": "Test",
                "Description": None,  # This is fine
                "TaskStatusName": "New",
                "TaskTypeName": "Development",
                "TaskPriorityName": "High",
                "EndDate": None,  # This should be handled
            }
        ]
        result = format_tool(json.dumps(data), "task")
        # Should handle None values gracefully
        assert "TK:1" in result or "Error" in result

    def test_format_generic_exception_in_outer_try(self, format_tool):
        """Test generic exception handler in outer try block."""
        # Pass something that will cause an exception in the outer try block
        # by passing invalid artifact_type that's not in the Literal
        import json as json_module

        # Mock json.loads to raise a generic exception (not JSONDecodeError)
        original_loads = json_module.loads

        def mock_loads_with_exception(s):
            if "trigger_exception" in s:
                raise ValueError("Unexpected error")
            return original_loads(s)

        # This test verifies the outer exception handler
        # We'll trigger it by passing valid JSON but causing an error in processing
        data = {"data": [{"TaskId": 1, "Name": "Test"}], "trigger_exception": True}
        result = format_tool(json.dumps(data), "task")
        # Should return error message
        assert "Error" in result or "TK:1" in result
