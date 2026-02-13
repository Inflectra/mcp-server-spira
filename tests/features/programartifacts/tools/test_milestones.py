"""
Unit tests for program milestones tools
"""

import json
from unittest.mock import Mock

import pytest

from mcp_server_spira.features.programartifacts.tools.milestones import _get_milestones_impl


class TestGetMilestones:
    """Test suite for get_milestones tool."""

    @pytest.fixture
    def mock_spira_client(self):
        """Create mock SpiraClient."""
        client = Mock()
        return client

    @pytest.fixture
    def sample_milestones(self):
        """Sample milestone data for testing."""
        return [
            {
                "MilestoneId": 1,
                "Name": "Q1 Release",
                "Description": "First quarter major release",
                "MilestoneStatusId": 2,
                "MilestoneStatusName": "In Progress",
                "MilestoneTypeId": 1,
                "MilestoneTypeName": "Major Release",
                "CreationDate": "2024-01-01T08:00:00Z",
                "LastUpdateDate": "2024-01-20T14:30:00Z",
                "StartDate": "2024-01-01T00:00:00Z",
                "EndDate": "2024-03-31T23:59:59Z",
                "ProgramId": 10,
                "ProgramName": "Engineering Programs",
                "PercentComplete": 45,
            },
            {
                "MilestoneId": 2,
                "Name": "Q2 Release",
                "Description": "Second quarter major release",
                "MilestoneStatusId": 1,
                "MilestoneStatusName": "Planned",
                "MilestoneTypeId": 1,
                "MilestoneTypeName": "Major Release",
                "CreationDate": "2024-01-01T08:00:00Z",
                "LastUpdateDate": "2024-01-15T10:00:00Z",
                "StartDate": "2024-04-01T00:00:00Z",
                "EndDate": "2024-06-30T23:59:59Z",
                "ProgramId": 10,
                "ProgramName": "Engineering Programs",
                "PercentComplete": 0,
            },
        ]

    def test_get_milestones_success(self, mock_spira_client, sample_milestones):
        """Test successful milestone retrieval."""
        mock_spira_client.make_spira_api_get_request.return_value = sample_milestones

        result = _get_milestones_impl(mock_spira_client, program_id=10)

        # Parse response
        response = json.loads(result)

        # Verify structure
        assert "data" in response
        assert isinstance(response["data"], list)

        # Verify data
        assert len(response["data"]) == 2
        assert response["data"][0]["MilestoneId"] == 1
        assert response["data"][0]["Name"] == "Q1 Release"
        assert response["data"][1]["MilestoneId"] == 2

        # Verify API call
        mock_spira_client.make_spira_api_get_request.assert_called_once_with(
            "programs/10/milestones"
        )

    def test_get_milestones_empty_results(self, mock_spira_client):
        """Test empty milestone list."""
        mock_spira_client.make_spira_api_get_request.return_value = []

        result = _get_milestones_impl(mock_spira_client, program_id=10)

        response = json.loads(result)

        assert response["data"] == []

    def test_get_milestones_none_results(self, mock_spira_client):
        """Test None milestone list."""
        mock_spira_client.make_spira_api_get_request.return_value = None

        result = _get_milestones_impl(mock_spira_client, program_id=10)

        response = json.loads(result)

        assert response["data"] == []

    def test_get_milestones_invalid_program_id_negative(self, mock_spira_client):
        """Test validation - negative program_id."""
        result = _get_milestones_impl(mock_spira_client, program_id=-1)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"
        assert response["details"]["parameter"] == "program_id"
        assert response["details"]["value"] == -1

    def test_get_milestones_invalid_program_id_zero(self, mock_spira_client):
        """Test validation - zero program_id."""
        result = _get_milestones_impl(mock_spira_client, program_id=0)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"
        assert response["details"]["parameter"] == "program_id"

    def test_get_milestones_api_error(self, mock_spira_client):
        """Test API error handling."""
        mock_spira_client.make_spira_api_get_request.side_effect = Exception(
            "API connection failed"
        )

        result = _get_milestones_impl(mock_spira_client, program_id=10)

        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "API_ERROR"
        assert "API connection failed" in response["details"]["message"]

    def test_get_milestones_preserves_all_fields(self, mock_spira_client):
        """Test that all fields from API are preserved in JSON output."""
        milestone_with_all_fields = {
            "MilestoneId": 1,
            "Name": "Test Milestone",
            "Description": "Test Description",
            "MilestoneStatusId": 2,
            "MilestoneStatusName": "In Progress",
            "MilestoneTypeId": 1,
            "MilestoneTypeName": "Major Release",
            "CreationDate": "2024-01-01T08:00:00Z",
            "LastUpdateDate": "2024-01-20T14:30:00Z",
            "StartDate": "2024-01-01T00:00:00Z",
            "EndDate": "2024-03-31T23:59:59Z",
            "ProgramId": 10,
            "ProgramName": "Engineering Programs",
            "PercentComplete": 45,
            "CustomProperties": [],
            "Tags": "release,major",
        }

        mock_spira_client.make_spira_api_get_request.return_value = [milestone_with_all_fields]

        result = _get_milestones_impl(mock_spira_client, program_id=10)
        response = json.loads(result)

        # Verify all fields are preserved
        milestone = response["data"][0]
        for key, value in milestone_with_all_fields.items():
            assert key in milestone
            assert milestone[key] == value

    def test_get_milestones_multiple_programs(self, mock_spira_client, sample_milestones):
        """Test retrieving milestones for different programs."""
        mock_spira_client.make_spira_api_get_request.return_value = sample_milestones

        # Test program 10
        result1 = _get_milestones_impl(mock_spira_client, program_id=10)
        response1 = json.loads(result1)
        assert len(response1["data"]) == 2

        # Test program 20
        result2 = _get_milestones_impl(mock_spira_client, program_id=20)
        response2 = json.loads(result2)
        assert len(response2["data"]) == 2

        # Verify different API calls
        assert mock_spira_client.make_spira_api_get_request.call_count == 2
        calls = mock_spira_client.make_spira_api_get_request.call_args_list
        assert calls[0][0][0] == "programs/10/milestones"
        assert calls[1][0][0] == "programs/20/milestones"
