"""
Unit tests for program capabilities tools
"""

import json
from unittest.mock import Mock

import pytest

from mcp_server_spira.features.programartifacts.tools.capabilities import _get_capabilities_impl


class TestGetCapabilities:
    """Test suite for get_capabilities tool."""

    @pytest.fixture
    def mock_spira_client(self):
        """Create mock SpiraClient."""
        client = Mock()
        return client

    @pytest.fixture
    def sample_capabilities(self):
        """Sample capability data for testing."""
        return [
            {
                "CapabilityId": 1,
                "Name": "User Authentication",
                "Description": "Implement secure user login",
                "CapabilityStatusId": 2,
                "CapabilityStatusName": "In Progress",
                "CapabilityTypeId": 1,
                "CapabilityTypeName": "Feature",
                "CapabilityPriorityId": 1,
                "CapabilityPriorityName": "Critical",
                "OwnerId": 5,
                "OwnerName": "John Doe",
                "ProgramId": 10,
                "ProgramName": "Engineering Programs",
            },
            {
                "CapabilityId": 2,
                "Name": "Payment Processing",
                "Description": "Implement payment gateway",
                "CapabilityStatusId": 1,
                "CapabilityStatusName": "Planned",
                "CapabilityTypeId": 1,
                "CapabilityTypeName": "Feature",
                "CapabilityPriorityId": 2,
                "CapabilityPriorityName": "High",
                "OwnerId": 6,
                "OwnerName": "Jane Smith",
                "ProgramId": 10,
                "ProgramName": "Engineering Programs",
            },
        ]

    def test_get_capabilities_success(self, mock_spira_client, sample_capabilities):
        """Test successful capability retrieval."""
        mock_spira_client.make_spira_api_get_request.return_value = sample_capabilities

        result = _get_capabilities_impl(mock_spira_client, program_id=10)

        # Parse response
        response = json.loads(result)

        # Verify structure
        assert "data" in response
        assert isinstance(response["data"], list)

        # Verify data
        assert len(response["data"]) == 2
        assert response["data"][0]["CapabilityId"] == 1
        assert response["data"][0]["Name"] == "User Authentication"
        assert response["data"][1]["CapabilityId"] == 2

        # Verify API call
        mock_spira_client.make_spira_api_get_request.assert_called_once_with(
            "programs/10/capabilities/search?current_page=1&page_size=500"
        )

    def test_get_capabilities_empty_results(self, mock_spira_client):
        """Test empty capability list."""
        mock_spira_client.make_spira_api_get_request.return_value = []

        result = _get_capabilities_impl(mock_spira_client, program_id=10)

        response = json.loads(result)

        assert response["data"] == []

    def test_get_capabilities_none_results(self, mock_spira_client):
        """Test None capability list."""
        mock_spira_client.make_spira_api_get_request.return_value = None

        result = _get_capabilities_impl(mock_spira_client, program_id=10)

        response = json.loads(result)

        assert response["data"] == []

    def test_get_capabilities_invalid_program_id_negative(self, mock_spira_client):
        """Test validation - negative program_id."""
        result = _get_capabilities_impl(mock_spira_client, program_id=-1)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"
        assert response["details"]["parameter"] == "program_id"
        assert response["details"]["value"] == -1

    def test_get_capabilities_invalid_program_id_zero(self, mock_spira_client):
        """Test validation - zero program_id."""
        result = _get_capabilities_impl(mock_spira_client, program_id=0)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_VALUE"
        assert response["details"]["parameter"] == "program_id"

    def test_get_capabilities_api_error(self, mock_spira_client):
        """Test API error handling."""
        mock_spira_client.make_spira_api_get_request.side_effect = Exception(
            "API connection failed"
        )

        result = _get_capabilities_impl(mock_spira_client, program_id=10)

        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "API_ERROR"
        assert "API connection failed" in response["details"]["message"]

    def test_get_capabilities_preserves_all_fields(self, mock_spira_client):
        """Test that all fields from API are preserved in JSON output."""
        capability_with_all_fields = {
            "CapabilityId": 1,
            "Name": "Test Capability",
            "Description": "Test Description",
            "CapabilityStatusId": 2,
            "CapabilityStatusName": "In Progress",
            "CapabilityTypeId": 1,
            "CapabilityTypeName": "Feature",
            "CapabilityPriorityId": 1,
            "CapabilityPriorityName": "Critical",
            "OwnerId": 5,
            "OwnerName": "John Doe",
            "CreationDate": "2024-01-10T08:00:00Z",
            "LastUpdateDate": "2024-01-20T14:30:00Z",
            "StartDate": "2024-01-15T09:00:00Z",
            "EndDate": "2024-03-30T17:00:00Z",
            "ProgramId": 10,
            "ProgramName": "Engineering Programs",
            "CustomProperties": [],
            "Tags": "feature,critical",
        }

        mock_spira_client.make_spira_api_get_request.return_value = [capability_with_all_fields]

        result = _get_capabilities_impl(mock_spira_client, program_id=10)
        response = json.loads(result)

        # Verify all fields are preserved
        capability = response["data"][0]
        for key, value in capability_with_all_fields.items():
            assert key in capability
            assert capability[key] == value
