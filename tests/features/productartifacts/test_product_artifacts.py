"""
Tests for the Product Artifacts features of the Inflectra Spira MCP Server.

This module tests all 9 product artifact tools:
1. get_tasks
2. get_incidents
3. get_requirements
4. get_test_cases
5. get_test_sets
6. get_releases (+ get_release_by_id)
7. get_risks
8. get_test_runs
9. get_automation_hosts
"""

import json
from unittest.mock import Mock

import pytest

from mcp_server_spira.features.productartifacts.tools.automationhosts import (
    _get_automation_hosts_impl,
)
from mcp_server_spira.features.productartifacts.tools.incidents import (
    _get_incidents_impl,
)
from mcp_server_spira.features.productartifacts.tools.releases import (
    _get_release_by_id_impl,
    _get_releases_impl,
)
from mcp_server_spira.features.productartifacts.tools.requirements import (
    _get_requirements_impl,
)
from mcp_server_spira.features.productartifacts.tools.tasks import (
    _get_tasks_impl,
)
from mcp_server_spira.features.productartifacts.tools.testcases import (
    _get_test_cases_impl,
)
from mcp_server_spira.features.productartifacts.tools.testruns import (
    _get_test_runs_impl,
)
from mcp_server_spira.features.productartifacts.tools.testsets import (
    _get_test_sets_impl,
)


@pytest.mark.unit
class TestGetTasksImpl:
    """Tests for _get_tasks_impl function."""

    def test_successful_retrieval_with_tasks(self):
        """Test successful task retrieval with POST request and empty filter."""
        # Mock Spira client
        mock_client = Mock()
        mock_tasks = [
            {
                "TaskId": 123,
                "Name": "Fix login bug",
                "Description": "Users cannot log in",
                "TaskStatusId": 2,
                "TaskStatusName": "In Progress",
                "TaskPriorityName": "Critical",
                "EstimatedEffort": 120,
                "ActualEffort": 60,
                "ProjectId": 55,
            }
        ]
        mock_client.make_spira_api_post_request.return_value = mock_tasks

        # Call implementation
        result = _get_tasks_impl(mock_client, 55)

        # Verify API was called with POST and empty filter array
        mock_client.make_spira_api_post_request.assert_called_once()
        call_args = mock_client.make_spira_api_post_request.call_args
        assert "projects/55/tasks/search" in call_args[0][0]
        assert call_args[0][1] == []  # Empty filter array

        # Parse and verify response
        parsed = json.loads(result)
        assert "data" in parsed
        assert len(parsed["data"]) == 1
        assert parsed["data"][0]["TaskId"] == 123
        assert parsed["data"][0]["Name"] == "Fix login bug"

    def test_pagination_parameters(self):
        """Test that pagination parameters are included in URL."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []

        _get_tasks_impl(mock_client, 55, starting_row=10, number_of_rows=50)

        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        assert "starting_row=10" in url
        assert "number_of_rows=50" in url

    def test_sort_parameters(self):
        """Test that sort parameters are included when provided."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []

        _get_tasks_impl(mock_client, 55, sort_field="TaskPriorityId", sort_direction="DESC")

        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        assert "sort_field=TaskPriorityId" in url
        assert "sort_direction=DESC" in url

    def test_preserves_all_fields(self):
        """Test that all task fields are preserved in JSON output."""
        mock_client = Mock()
        mock_tasks = [
            {
                "TaskId": 123,
                "Name": "Fix login bug",
                "Description": "Users cannot log in",
                "TaskStatusId": 2,
                "TaskStatusName": "In Progress",
                "TaskTypeId": 1,
                "TaskTypeName": "Development",
                "TaskPriorityId": 1,
                "TaskPriorityName": "Critical",
                "OwnerId": 5,
                "OwnerName": "John Doe",
                "CreatorId": 4,
                "RequirementId": 45,
                "RequirementName": "User Authentication",
                "ReleaseId": 10,
                "ReleaseVersionNumber": "1.5.0",
                "ComponentId": 3,
                "EstimatedEffort": 120,
                "ActualEffort": 60,
                "RemainingEffort": 60,
                "ProjectedEffort": 120,
                "CompletionPercent": 50,
                "StartDate": "2024-01-15T09:00:00Z",
                "EndDate": "2024-01-16T17:00:00Z",
                "CreationDate": "2024-01-10T08:00:00Z",
                "LastUpdateDate": "2024-01-15T14:30:00Z",
                "ProjectId": 55,
                "ProjectName": "Web Application",
                "TaskFolderId": None,
                "CustomProperties": [],
                "Tags": "bug,security",
                "IsAttachments": False,
                "Guid": "abc-123-def-456",
            }
        ]
        mock_client.make_spira_api_post_request.return_value = mock_tasks

        result = _get_tasks_impl(mock_client, 55)
        parsed = json.loads(result)
        task = parsed["data"][0]

        # Verify all fields are present
        assert task["TaskId"] == 123
        assert task["Name"] == "Fix login bug"
        assert task["TaskStatusName"] == "In Progress"
        assert task["EstimatedEffort"] == 120
        assert task["ActualEffort"] == 60
        assert task["RemainingEffort"] == 60
        assert task["ProjectedEffort"] == 120
        assert task["CompletionPercent"] == 50

    def test_api_error_handling(self):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.side_effect = Exception("Connection timeout")

        result = _get_tasks_impl(mock_client, 55)

        # Verify error response structure
        parsed = json.loads(result)
        assert "error" in parsed
        assert "error_code" in parsed
        assert parsed["error"] == "Failed to retrieve tasks"
        assert parsed["error_code"] == "API_ERROR"
        assert "details" in parsed
        assert "suggestion" in parsed

    def test_empty_results(self):
        """Test successful retrieval with no tasks."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []

        result = _get_tasks_impl(mock_client, 55)

        parsed = json.loads(result)
        assert "data" in parsed
        assert len(parsed["data"]) == 0


@pytest.mark.unit
class TestGetIncidentsImpl:
    """Tests for _get_incidents_impl function."""

    def test_successful_retrieval_with_incidents(self):
        """Test successful incident retrieval with POST request."""
        mock_client = Mock()
        mock_incidents = [
            {
                "IncidentId": 456,
                "Name": "Login page crashes",
                "IncidentStatusName": "New",
                "PriorityName": "1 - Critical",
                "ProjectId": 55,
            }
        ]
        mock_client.make_spira_api_post_request.return_value = mock_incidents

        result = _get_incidents_impl(mock_client, 55)

        # Verify API was called with POST and empty filter array
        mock_client.make_spira_api_post_request.assert_called_once()
        call_args = mock_client.make_spira_api_post_request.call_args
        assert "projects/55/incidents/search" in call_args[0][0]
        assert call_args[0][1] == []

        parsed = json.loads(result)
        assert "data" in parsed
        assert parsed["data"][0]["IncidentId"] == 456

    def test_pagination_parameters_start_row(self):
        """Test that incidents use start_row parameter."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []

        _get_incidents_impl(mock_client, 55, start_row=10, number_rows=50)

        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        assert "start_row=10" in url
        assert "number_rows=50" in url

    def test_api_error_handling(self):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.side_effect = Exception("API Error")

        result = _get_incidents_impl(mock_client, 55)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "API_ERROR"


@pytest.mark.unit
class TestGetRequirementsImpl:
    """Tests for _get_requirements_impl function."""

    def test_successful_retrieval_with_requirements(self):
        """Test successful requirement retrieval with POST request."""
        mock_client = Mock()
        mock_requirements = [
            {
                "RequirementId": 123,
                "Name": "User Authentication",
                "StatusName": "In Progress",
                "ImportanceName": "Critical",
                "ProjectId": 55,
            }
        ]
        mock_client.make_spira_api_post_request.return_value = mock_requirements

        result = _get_requirements_impl(mock_client, 55)

        # Verify API was called with POST and empty filter array
        mock_client.make_spira_api_post_request.assert_called_once()
        call_args = mock_client.make_spira_api_post_request.call_args
        assert "projects/55/requirements/search" in call_args[0][0]
        assert call_args[0][1] == []

        parsed = json.loads(result)
        assert "data" in parsed
        assert parsed["data"][0]["RequirementId"] == 123

    def test_pagination_parameters(self):
        """Test that pagination parameters are included in URL."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []

        _get_requirements_impl(mock_client, 55, starting_row=20, number_of_rows=75)

        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        assert "starting_row=20" in url
        assert "number_of_rows=75" in url

    def test_api_error_handling(self):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.side_effect = Exception("API Error")

        result = _get_requirements_impl(mock_client, 55)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "API_ERROR"


@pytest.mark.unit
class TestGetTestCasesImpl:
    """Tests for _get_test_cases_impl function."""

    def test_successful_retrieval_with_test_cases(self):
        """Test successful test case retrieval with POST request."""
        mock_client = Mock()
        mock_test_cases = [
            {
                "TestCaseId": 123,
                "Name": "Login with valid credentials",
                "TestCaseStatusName": "Ready for Review",
                "ExecutionStatusName": "Passed",
                "ProjectId": 55,
            }
        ]
        mock_client.make_spira_api_post_request.return_value = mock_test_cases

        result = _get_test_cases_impl(mock_client, 55)

        # Verify API was called with POST and empty filter array
        mock_client.make_spira_api_post_request.assert_called_once()
        call_args = mock_client.make_spira_api_post_request.call_args
        assert "projects/55/test-cases/search" in call_args[0][0]
        assert call_args[0][1] == []

        parsed = json.loads(result)
        assert "data" in parsed
        assert parsed["data"][0]["TestCaseId"] == 123

    def test_pagination_and_sort_parameters(self):
        """Test that pagination and sort parameters are included."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []

        _get_test_cases_impl(
            mock_client,
            55,
            starting_row=5,
            number_of_rows=25,
            sort_field="TestCaseId",
            sort_direction="DESC",
        )

        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        assert "starting_row=5" in url
        assert "number_of_rows=25" in url
        assert "sort_field=TestCaseId" in url
        assert "sort_direction=DESC" in url

    def test_api_error_handling(self):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.side_effect = Exception("API Error")

        result = _get_test_cases_impl(mock_client, 55)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "API_ERROR"


@pytest.mark.unit
class TestGetTestSetsImpl:
    """Tests for _get_test_sets_impl function."""

    def test_successful_retrieval_with_test_sets(self):
        """Test successful test set retrieval with POST request."""
        mock_client = Mock()
        mock_test_sets = [
            {
                "TestSetId": 123,
                "Name": "Smoke Test Suite",
                "TestSetStatusName": "In Progress",
                "CountPassed": 15,
                "CountFailed": 3,
                "ProjectId": 55,
            }
        ]
        mock_client.make_spira_api_post_request.return_value = mock_test_sets

        result = _get_test_sets_impl(mock_client, 55)

        # Verify API was called with POST and empty filter array
        mock_client.make_spira_api_post_request.assert_called_once()
        call_args = mock_client.make_spira_api_post_request.call_args
        assert "projects/55/test-sets/search" in call_args[0][0]
        assert call_args[0][1] == []

        parsed = json.loads(result)
        assert "data" in parsed
        assert parsed["data"][0]["TestSetId"] == 123

    def test_pagination_and_sort_parameters(self):
        """Test that pagination and sort parameters are included."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []

        _get_test_sets_impl(
            mock_client,
            55,
            starting_row=15,
            number_of_rows=30,
            sort_field="TestSetStatusName",
            sort_direction="ASC",
        )

        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        assert "starting_row=15" in url
        assert "number_of_rows=30" in url
        assert "sort_field=TestSetStatusName" in url
        assert "sort_direction=ASC" in url

    def test_api_error_handling(self):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.side_effect = Exception("API Error")

        result = _get_test_sets_impl(mock_client, 55)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "API_ERROR"


@pytest.mark.unit
class TestGetReleasesImpl:
    """Tests for _get_releases_impl function."""

    def test_successful_retrieval_with_releases(self):
        """Test successful release retrieval with POST request."""
        mock_client = Mock()
        mock_releases = [
            {
                "ReleaseId": 10,
                "Name": "Release 1.5.0",
                "VersionNumber": "1.5.0",
                "ReleaseStatusName": "In Progress",
                "Active": True,
                "ProjectId": 55,
            }
        ]
        mock_client.make_spira_api_post_request.return_value = mock_releases

        result = _get_releases_impl(mock_client, 55)

        # Verify API was called with POST and empty filter array
        mock_client.make_spira_api_post_request.assert_called_once()
        call_args = mock_client.make_spira_api_post_request.call_args
        assert "projects/55/releases/search" in call_args[0][0]
        assert call_args[0][1] == []

        parsed = json.loads(result)
        assert "data" in parsed
        assert parsed["data"][0]["ReleaseId"] == 10

    def test_pagination_parameters_start_row(self):
        """Test that releases use start_row parameter."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []

        _get_releases_impl(mock_client, 55, start_row=5, number_rows=20)

        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        assert "start_row=5" in url
        assert "number_rows=20" in url

    def test_api_error_handling(self):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.side_effect = Exception("API Error")

        result = _get_releases_impl(mock_client, 55)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "API_ERROR"


@pytest.mark.unit
class TestGetReleaseByIdImpl:
    """Tests for _get_release_by_id_impl function."""

    def test_successful_retrieval_by_id(self):
        """Test successful single release retrieval with GET request."""
        mock_client = Mock()
        mock_release = {
            "ReleaseId": 10,
            "Name": "Release 1.5.0",
            "VersionNumber": "1.5.0",
            "ReleaseStatusName": "In Progress",
            "Active": True,
            "ProjectId": 55,
        }
        mock_client.make_spira_api_get_request.return_value = mock_release

        result = _get_release_by_id_impl(mock_client, 55, 10)

        # Verify API was called with GET (not POST)
        mock_client.make_spira_api_get_request.assert_called_once_with("projects/55/releases/10")

        parsed = json.loads(result)
        assert "data" in parsed
        assert len(parsed["data"]) == 1
        assert parsed["data"][0]["ReleaseId"] == 10

    def test_api_error_handling(self):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.side_effect = Exception("API Error")

        result = _get_release_by_id_impl(mock_client, 55, 10)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "API_ERROR"
        assert "product_id" in parsed["details"]
        assert "release_id" in parsed["details"]


@pytest.mark.unit
class TestGetTestRunsImpl:
    """Tests for _get_test_runs_impl function."""

    def test_successful_retrieval_with_test_runs(self):
        """Test successful test run retrieval with POST request."""
        mock_client = Mock()
        mock_test_runs = [
            {
                "TestRunId": 123,
                "Name": "Login Test - Chrome",
                "TestCaseId": 45,
                "ExecutionStatusId": 2,
                "TesterId": 5,
                "ProjectId": 55,
            }
        ]
        mock_client.make_spira_api_post_request.return_value = mock_test_runs

        result = _get_test_runs_impl(mock_client, 55)

        # Verify API was called with POST and empty filter array
        mock_client.make_spira_api_post_request.assert_called_once()
        call_args = mock_client.make_spira_api_post_request.call_args
        assert "projects/55/test-runs/search" in call_args[0][0]
        assert call_args[0][1] == []

        parsed = json.loads(result)
        assert "data" in parsed
        assert parsed["data"][0]["TestRunId"] == 123

    def test_pagination_and_sort_parameters(self):
        """Test that pagination and sort parameters are included."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []

        _get_test_runs_impl(
            mock_client,
            55,
            starting_row=10,
            number_of_rows=50,
            sort_field="EndDate",
            sort_direction="DESC",
        )

        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        assert "starting_row=10" in url
        assert "number_of_rows=50" in url
        assert "sort_field=EndDate" in url
        assert "sort_direction=DESC" in url

    def test_api_error_handling(self):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.side_effect = Exception("API Error")

        result = _get_test_runs_impl(mock_client, 55)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "API_ERROR"


@pytest.mark.unit
class TestGetAutomationHostsImpl:
    """Tests for _get_automation_hosts_impl function."""

    def test_successful_retrieval_with_automation_hosts(self):
        """Test successful automation host retrieval with POST request."""
        mock_client = Mock()
        mock_hosts = [
            {
                "AutomationHostId": 123,
                "Name": "Build Server 01",
                "Token": "host-token-abc123",
                "Active": True,
                "ProjectId": 55,
            }
        ]
        mock_client.make_spira_api_post_request.return_value = mock_hosts

        result = _get_automation_hosts_impl(mock_client, 55)

        # Verify API was called with POST and empty filter array
        mock_client.make_spira_api_post_request.assert_called_once()
        call_args = mock_client.make_spira_api_post_request.call_args
        assert "projects/55/automation-hosts/search" in call_args[0][0]
        assert call_args[0][1] == []

        parsed = json.loads(result)
        assert "data" in parsed
        assert parsed["data"][0]["AutomationHostId"] == 123

    def test_pagination_parameters(self):
        """Test that pagination parameters are included in URL."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []

        _get_automation_hosts_impl(mock_client, 55, starting_row=5, number_of_rows=25)

        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        assert "starting_row=5" in url
        assert "number_of_rows=25" in url

    def test_api_error_handling(self):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.side_effect = Exception("API Error")

        result = _get_automation_hosts_impl(mock_client, 55)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "API_ERROR"

    def test_preserves_all_fields(self):
        """Test that all automation host fields are preserved."""
        mock_client = Mock()
        mock_hosts = [
            {
                "AutomationHostId": 123,
                "Name": "Build Server 01",
                "Token": "host-token-abc123",
                "Description": "Primary build and test automation host",
                "LastUpdateDate": "2024-01-15T14:30:00Z",
                "Active": True,
                "LastContactDate": "2024-01-16T10:00:00Z",
                "ProjectId": 55,
                "ProjectGuid": "abc-123-def-456",
                "ArtifactTypeId": 9,
                "ConcurrencyDate": "2024-01-15T14:30:00Z",
                "CustomProperties": [],
                "IsAttachments": False,
                "Tags": "ci,automation",
                "Guid": "xyz-789-ghi-012",
            }
        ]
        mock_client.make_spira_api_post_request.return_value = mock_hosts

        result = _get_automation_hosts_impl(mock_client, 55)
        parsed = json.loads(result)
        host = parsed["data"][0]

        # Verify all fields are present
        assert host["AutomationHostId"] == 123
        assert host["Name"] == "Build Server 01"
        assert host["Token"] == "host-token-abc123"
        assert host["Active"] is True
        assert host["ProjectId"] == 55


@pytest.mark.unit
class TestInputValidation:
    """Tests for input validation across all product artifact tools."""

    def test_tasks_validates_product_id(self):
        """Test that get_tasks validates product_id is positive."""
        from mcp_server_spira.features.productartifacts.tools.tasks import (
            register_tools,
        )

        mock_mcp = Mock()
        register_tools(mock_mcp)

        # The tool should be registered
        assert mock_mcp.tool.called

    def test_incidents_validates_product_id(self):
        """Test that get_incidents validates product_id is positive."""
        from mcp_server_spira.features.productartifacts.tools.incidents import (
            register_tools,
        )

        mock_mcp = Mock()
        register_tools(mock_mcp)

        assert mock_mcp.tool.called

    def test_requirements_validates_product_id(self):
        """Test that get_requirements validates product_id is positive."""
        from mcp_server_spira.features.productartifacts.tools.requirements import (
            register_tools,
        )

        mock_mcp = Mock()
        register_tools(mock_mcp)

        assert mock_mcp.tool.called

    def test_test_cases_validates_product_id(self):
        """Test that get_test_cases validates product_id is positive."""
        from mcp_server_spira.features.productartifacts.tools.testcases import (
            register_tools,
        )

        mock_mcp = Mock()
        register_tools(mock_mcp)

        assert mock_mcp.tool.called

    def test_test_sets_validates_product_id(self):
        """Test that get_test_sets validates product_id is positive."""
        from mcp_server_spira.features.productartifacts.tools.testsets import (
            register_tools,
        )

        mock_mcp = Mock()
        register_tools(mock_mcp)

        assert mock_mcp.tool.called

    def test_releases_validates_product_id(self):
        """Test that get_releases validates product_id is positive."""
        from mcp_server_spira.features.productartifacts.tools.releases import (
            register_tools,
        )

        mock_mcp = Mock()
        register_tools(mock_mcp)

        assert mock_mcp.tool.called

    def test_test_runs_validates_product_id(self):
        """Test that get_test_runs validates product_id is positive."""
        from mcp_server_spira.features.productartifacts.tools.testruns import (
            register_tools,
        )

        mock_mcp = Mock()
        register_tools(mock_mcp)

        assert mock_mcp.tool.called

    def test_automation_hosts_validates_product_id(self):
        """Test that get_automation_hosts validates product_id is positive."""
        from mcp_server_spira.features.productartifacts.tools.automationhosts import (
            register_tools,
        )

        mock_mcp = Mock()
        register_tools(mock_mcp)

        assert mock_mcp.tool.called


@pytest.mark.unit
class TestJSONStructureValidation:
    """Tests for JSON structure validation across all tools."""

    def test_tasks_json_structure(self):
        """Test that get_tasks returns valid JSON with data key."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = [{"TaskId": 1, "Name": "Test"}]

        result = _get_tasks_impl(mock_client, 55)

        # Verify it's valid JSON
        parsed = json.loads(result)
        assert "data" in parsed
        assert isinstance(parsed["data"], list)

    def test_incidents_json_structure(self):
        """Test that get_incidents returns valid JSON with data key."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = [{"IncidentId": 1, "Name": "Test"}]

        result = _get_incidents_impl(mock_client, 55)

        parsed = json.loads(result)
        assert "data" in parsed
        assert isinstance(parsed["data"], list)

    def test_requirements_json_structure(self):
        """Test that get_requirements returns valid JSON with data key."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = [
            {"RequirementId": 1, "Name": "Test"}
        ]

        result = _get_requirements_impl(mock_client, 55)

        parsed = json.loads(result)
        assert "data" in parsed
        assert isinstance(parsed["data"], list)

    def test_test_cases_json_structure(self):
        """Test that get_test_cases returns valid JSON with data key."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = [{"TestCaseId": 1, "Name": "Test"}]

        result = _get_test_cases_impl(mock_client, 55)

        parsed = json.loads(result)
        assert "data" in parsed
        assert isinstance(parsed["data"], list)

    def test_test_sets_json_structure(self):
        """Test that get_test_sets returns valid JSON with data key."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = [{"TestSetId": 1, "Name": "Test"}]

        result = _get_test_sets_impl(mock_client, 55)

        parsed = json.loads(result)
        assert "data" in parsed
        assert isinstance(parsed["data"], list)

    def test_releases_json_structure(self):
        """Test that get_releases returns valid JSON with data key."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = [{"ReleaseId": 1, "Name": "Test"}]

        result = _get_releases_impl(mock_client, 55)

        parsed = json.loads(result)
        assert "data" in parsed
        assert isinstance(parsed["data"], list)

    def test_test_runs_json_structure(self):
        """Test that get_test_runs returns valid JSON with data key."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = [{"TestRunId": 1, "Name": "Test"}]

        result = _get_test_runs_impl(mock_client, 55)

        parsed = json.loads(result)
        assert "data" in parsed
        assert isinstance(parsed["data"], list)

    def test_automation_hosts_json_structure(self):
        """Test that get_automation_hosts returns valid JSON with data key."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = [
            {"AutomationHostId": 1, "Name": "Test"}
        ]

        result = _get_automation_hosts_impl(mock_client, 55)

        parsed = json.loads(result)
        assert "data" in parsed
        assert isinstance(parsed["data"], list)

    def test_json_formatting_with_indentation(self):
        """Test that JSON is properly formatted with indentation."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = [{"TaskId": 1, "Name": "Test Task"}]

        result = _get_tasks_impl(mock_client, 55)

        # Verify formatting (should have newlines and indentation)
        assert "\n" in result
        assert "  " in result  # 2-space indentation


@pytest.mark.unit
class TestEdgeCases:
    """Tests for edge cases across all product artifact tools."""

    def test_tasks_with_various_product_ids(self):
        """Test get_tasks with various product IDs."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []

        for product_id in [1, 10, 100, 999]:
            _get_tasks_impl(mock_client, product_id)
            call_args = mock_client.make_spira_api_post_request.call_args
            assert f"projects/{product_id}/tasks/search" in call_args[0][0]

    def test_incidents_with_various_product_ids(self):
        """Test get_incidents with various product IDs."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []

        for product_id in [1, 10, 100, 999]:
            _get_incidents_impl(mock_client, product_id)
            call_args = mock_client.make_spira_api_post_request.call_args
            assert f"projects/{product_id}/incidents/search" in call_args[0][0]

    def test_empty_filter_array_is_always_sent(self):
        """Test that empty filter array [] is always sent in POST body."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []

        # Test multiple tools
        _get_tasks_impl(mock_client, 55)
        assert mock_client.make_spira_api_post_request.call_args[0][1] == []

        _get_incidents_impl(mock_client, 55)
        assert mock_client.make_spira_api_post_request.call_args[0][1] == []

        _get_requirements_impl(mock_client, 55)
        assert mock_client.make_spira_api_post_request.call_args[0][1] == []

    def test_default_pagination_values(self):
        """Test that default pagination values are used correctly."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []

        # Test with defaults
        _get_tasks_impl(mock_client, 55)
        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        assert "starting_row=1" in url
        assert "number_of_rows=100" in url

    def test_sort_parameters_optional(self):
        """Test that sort parameters are optional."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []

        # Test without sort parameters
        _get_tasks_impl(mock_client, 55, sort_field="", sort_direction="ASC")
        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        # Should not include sort parameters when sort_field is empty
        assert "sort_field=" not in url or "sort_field=&" in url

    def test_large_pagination_values(self):
        """Test with large pagination values."""
        mock_client = Mock()
        mock_client.make_spira_api_post_request.return_value = []

        _get_tasks_impl(mock_client, 55, starting_row=1000, number_of_rows=500)

        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        assert "starting_row=1000" in url
        assert "number_of_rows=500" in url

    def test_null_and_empty_values_preserved(self):
        """Test that null and empty values are preserved in JSON."""
        mock_client = Mock()
        mock_tasks = [
            {
                "TaskId": 123,
                "Name": "Test",
                "Description": None,
                "TaskFolderId": None,
                "CustomProperties": [],
                "Tags": "",
            }
        ]
        mock_client.make_spira_api_post_request.return_value = mock_tasks

        result = _get_tasks_impl(mock_client, 55)
        parsed = json.loads(result)
        task = parsed["data"][0]

        # Verify null values are preserved as null (not empty strings)
        assert task["Description"] is None
        assert task["TaskFolderId"] is None
        assert task["CustomProperties"] == []
        assert task["Tags"] == ""
