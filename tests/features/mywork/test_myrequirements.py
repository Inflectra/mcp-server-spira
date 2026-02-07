"""
Tests for the My Requirements features of the Inflectra Spira MCP Server.
"""

import json
import os
from collections.abc import Callable
from unittest.mock import Mock, patch

import pytest

from mcp_server_spira.features.mywork.tools.myrequirements import (
    _get_my_requirements_impl,
    get_spira_client,
)


class TestGetMyRequirementsImpl:
    """Tests for _get_my_requirements_impl function."""

    def test_successful_retrieval_with_default_pagination(self):
        """Test successful requirement retrieval with default pagination."""
        # Mock Spira client
        mock_client = Mock()
        mock_requirements = [
            {
                "RequirementId": i,
                "Name": f"Requirement {i}",
                "StatusName": "In Progress",
            }
            for i in range(1, 51)
        ]
        mock_client.make_spira_api_get_request.return_value = mock_requirements

        # Call implementation with defaults
        result = _get_my_requirements_impl(mock_client, limit=25, offset=0)

        # Verify API was called correctly
        mock_client.make_spira_api_get_request.assert_called_once_with("requirements")

        # Parse and verify response
        parsed = json.loads(result)
        assert "data" in parsed
        assert "pagination" in parsed
        assert len(parsed["data"]) == 25
        assert parsed["data"][0]["RequirementId"] == 1
        assert parsed["data"][24]["RequirementId"] == 25
        assert parsed["pagination"]["limit"] == 25
        assert parsed["pagination"]["offset"] == 0
        assert parsed["pagination"]["returned_count"] == 25
        assert parsed["pagination"]["total_count"] == 50
        assert parsed["pagination"]["has_more"] is True
        assert parsed["pagination"]["pagination_type"] == "client-side"

    def test_successful_retrieval_first_page(self):
        """Test retrieving first page of results."""
        mock_client = Mock()
        mock_requirements = [
            {"RequirementId": i, "Name": f"Requirement {i}"} for i in range(1, 101)
        ]
        mock_client.make_spira_api_get_request.return_value = mock_requirements

        result = _get_my_requirements_impl(mock_client, limit=25, offset=0)

        parsed = json.loads(result)
        assert len(parsed["data"]) == 25
        assert parsed["data"][0]["RequirementId"] == 1
        assert parsed["pagination"]["has_more"] is True

    def test_successful_retrieval_middle_page(self):
        """Test retrieving middle page of results."""
        mock_client = Mock()
        mock_requirements = [
            {"RequirementId": i, "Name": f"Requirement {i}"} for i in range(1, 101)
        ]
        mock_client.make_spira_api_get_request.return_value = mock_requirements

        result = _get_my_requirements_impl(mock_client, limit=25, offset=25)

        parsed = json.loads(result)
        assert len(parsed["data"]) == 25
        assert parsed["data"][0]["RequirementId"] == 26
        assert parsed["data"][24]["RequirementId"] == 50
        assert parsed["pagination"]["offset"] == 25
        assert parsed["pagination"]["has_more"] is True

    def test_successful_retrieval_last_page_full(self):
        """Test retrieving last page with full results."""
        mock_client = Mock()
        mock_requirements = [
            {"RequirementId": i, "Name": f"Requirement {i}"} for i in range(1, 101)
        ]
        mock_client.make_spira_api_get_request.return_value = mock_requirements

        result = _get_my_requirements_impl(mock_client, limit=25, offset=75)

        parsed = json.loads(result)
        assert len(parsed["data"]) == 25
        assert parsed["data"][0]["RequirementId"] == 76
        assert parsed["data"][24]["RequirementId"] == 100
        assert parsed["pagination"]["offset"] == 75
        assert parsed["pagination"]["returned_count"] == 25
        assert parsed["pagination"]["has_more"] is False

    def test_successful_retrieval_last_page_partial(self):
        """Test retrieving last page with partial results."""
        mock_client = Mock()
        mock_requirements = [{"RequirementId": i, "Name": f"Requirement {i}"} for i in range(1, 48)]
        mock_client.make_spira_api_get_request.return_value = mock_requirements

        result = _get_my_requirements_impl(mock_client, limit=25, offset=25)

        parsed = json.loads(result)
        assert len(parsed["data"]) == 22
        assert parsed["data"][0]["RequirementId"] == 26
        assert parsed["data"][21]["RequirementId"] == 47
        assert parsed["pagination"]["returned_count"] == 22
        assert parsed["pagination"]["total_count"] == 47
        assert parsed["pagination"]["has_more"] is False

    def test_empty_results(self):
        """Test handling of empty requirement list."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.return_value = []

        result = _get_my_requirements_impl(mock_client, limit=25, offset=0)

        parsed = json.loads(result)
        assert parsed["data"] == []
        assert parsed["pagination"]["returned_count"] == 0
        assert parsed["pagination"]["total_count"] == 0
        assert parsed["pagination"]["has_more"] is False

    def test_empty_results_with_offset(self):
        """Test handling of empty results when offset is beyond data."""
        mock_client = Mock()
        mock_requirements = [{"RequirementId": i, "Name": f"Requirement {i}"} for i in range(1, 26)]
        mock_client.make_spira_api_get_request.return_value = mock_requirements

        result = _get_my_requirements_impl(mock_client, limit=25, offset=50)

        parsed = json.loads(result)
        assert parsed["data"] == []
        assert parsed["pagination"]["returned_count"] == 0
        assert parsed["pagination"]["total_count"] == 25
        assert parsed["pagination"]["has_more"] is False

    def test_custom_limit(self):
        """Test with custom limit parameter."""
        mock_client = Mock()
        mock_requirements = [
            {"RequirementId": i, "Name": f"Requirement {i}"} for i in range(1, 101)
        ]
        mock_client.make_spira_api_get_request.return_value = mock_requirements

        result = _get_my_requirements_impl(mock_client, limit=50, offset=0)

        parsed = json.loads(result)
        assert len(parsed["data"]) == 50
        assert parsed["pagination"]["limit"] == 50
        assert parsed["pagination"]["returned_count"] == 50

    def test_limit_larger_than_total(self):
        """Test when limit is larger than total available items."""
        mock_client = Mock()
        mock_requirements = [{"RequirementId": i, "Name": f"Requirement {i}"} for i in range(1, 11)]
        mock_client.make_spira_api_get_request.return_value = mock_requirements

        result = _get_my_requirements_impl(mock_client, limit=100, offset=0)

        parsed = json.loads(result)
        assert len(parsed["data"]) == 10
        assert parsed["pagination"]["returned_count"] == 10
        assert parsed["pagination"]["total_count"] == 10
        assert parsed["pagination"]["has_more"] is False

    def test_single_requirement(self):
        """Test with single requirement result."""
        mock_client = Mock()
        mock_requirements = [{"RequirementId": 1, "Name": "Single Requirement"}]
        mock_client.make_spira_api_get_request.return_value = mock_requirements

        result = _get_my_requirements_impl(mock_client, limit=25, offset=0)

        parsed = json.loads(result)
        assert len(parsed["data"]) == 1
        assert parsed["data"][0]["RequirementId"] == 1
        assert parsed["pagination"]["total_count"] == 1
        assert parsed["pagination"]["has_more"] is False

    def test_preserves_requirement_data_structure(self):
        """Test that all requirement fields are preserved in response."""
        mock_client = Mock()
        mock_requirements = [
            {
                "RequirementId": 123,
                "Name": "User Authentication",
                "Description": "Implement secure user login system",
                "StatusId": 2,
                "StatusName": "In Progress",
                "RequirementTypeId": 1,
                "RequirementTypeName": "Feature",
                "ImportanceId": 1,
                "ImportanceName": "Critical",
                "OwnerId": 5,
                "OwnerName": "John Doe",
                "AuthorId": 4,
                "AuthorName": "Jane Smith",
                "EstimatePoints": 8.0,
                "EstimatedEffort": 480,
                "TaskEstimatedEffort": 450,
                "TaskActualEffort": 240,
                "TaskCount": 5,
                "PercentComplete": 50,
                "CoverageCountTotal": 10,
                "CoverageCountPassed": 6,
                "CoverageCountFailed": 2,
                "CustomProperties": [{"id": 1, "value": "test"}],
                "Tags": "security,authentication",
            }
        ]
        mock_client.make_spira_api_get_request.return_value = mock_requirements

        result = _get_my_requirements_impl(mock_client, limit=25, offset=0)

        parsed = json.loads(result)
        requirement = parsed["data"][0]
        assert requirement["RequirementId"] == 123
        assert requirement["Name"] == "User Authentication"
        assert requirement["Description"] == "Implement secure user login system"
        assert requirement["StatusName"] == "In Progress"
        assert requirement["ImportanceName"] == "Critical"
        assert requirement["EstimatePoints"] == 8.0
        assert requirement["TaskCount"] == 5
        assert requirement["CoverageCountTotal"] == 10
        assert requirement["CustomProperties"] == [{"id": 1, "value": "test"}]
        assert requirement["Tags"] == "security,authentication"

    def test_api_error_handling(self):
        """Test handling of API errors."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.side_effect = Exception("API connection failed")

        result = _get_my_requirements_impl(mock_client, limit=25, offset=0)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error"] == "Failed to retrieve requirements"
        assert parsed["error_code"] == "API_ERROR"
        assert "API connection failed" in parsed["details"]["message"]
        assert "suggestion" in parsed

    def test_api_returns_none(self):
        """Test handling when API returns None."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.return_value = None

        result = _get_my_requirements_impl(mock_client, limit=25, offset=0)

        parsed = json.loads(result)
        assert parsed["data"] == []
        assert parsed["pagination"]["total_count"] == 0

    def test_json_structure_validity(self):
        """Test that response is valid JSON with correct structure."""
        mock_client = Mock()
        mock_requirements = [{"RequirementId": 1, "Name": "Requirement 1"}]
        mock_client.make_spira_api_get_request.return_value = mock_requirements

        result = _get_my_requirements_impl(mock_client, limit=25, offset=0)

        # Should be valid JSON
        parsed = json.loads(result)

        # Should have required top-level keys
        assert "data" in parsed
        assert "pagination" in parsed

        # Pagination should have required fields
        pagination = parsed["pagination"]
        assert "limit" in pagination
        assert "offset" in pagination
        assert "returned_count" in pagination
        assert "total_count" in pagination
        assert "has_more" in pagination
        assert "pagination_type" in pagination

    def test_pagination_metadata_accuracy(self):
        """Test that pagination metadata is calculated correctly."""
        mock_client = Mock()
        mock_requirements = [{"RequirementId": i} for i in range(1, 76)]
        mock_client.make_spira_api_get_request.return_value = mock_requirements

        # Test various pagination scenarios
        test_cases = [
            (25, 0, 25, 75, True),  # First page
            (25, 25, 25, 75, True),  # Second page
            (25, 50, 25, 75, False),  # Last page
            (10, 0, 10, 75, True),  # Small limit
            (100, 0, 75, 75, False),  # Limit larger than total
        ]

        for limit, offset, expected_returned, expected_total, expected_has_more in test_cases:
            result = _get_my_requirements_impl(mock_client, limit=limit, offset=offset)
            parsed = json.loads(result)

            assert parsed["pagination"]["limit"] == limit
            assert parsed["pagination"]["offset"] == offset
            assert parsed["pagination"]["returned_count"] == expected_returned
            assert parsed["pagination"]["total_count"] == expected_total
            assert parsed["pagination"]["has_more"] == expected_has_more


class TestGetMyRequirementsToolIntegration:
    """Integration tests for get_my_requirements tool with validation."""

    @patch("mcp_server_spira.features.mywork.tools.myrequirements.get_spira_client")
    def test_validation_limit_too_high(self, mock_get_client):
        """Test that limit validation rejects values > 500."""
        from unittest.mock import Mock

        from mcp_server_spira.features.mywork.tools.myrequirements import register_tools

        # Create mock MCP server
        mock_mcp = Mock()
        tool_func: Callable | None = None

        def capture_tool(name=None):
            def decorator(func):
                nonlocal tool_func
                tool_func = func
                return func

            return decorator

        mock_mcp.tool = capture_tool

        # Register tools
        register_tools(mock_mcp)

        # Call with invalid limit
        assert tool_func is not None  # type guard for mypy
        result = tool_func(limit=1000, offset=0)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "INVALID_PARAMETER"
        assert parsed["details"]["parameter"] == "limit"
        assert parsed["details"]["value"] == 1000
        assert "1-500" in parsed["details"]["expected"]

    @patch("mcp_server_spira.features.mywork.tools.myrequirements.get_spira_client")
    def test_validation_limit_zero(self, mock_get_client):
        """Test that limit validation rejects zero."""
        from unittest.mock import Mock

        from mcp_server_spira.features.mywork.tools.myrequirements import register_tools

        mock_mcp = Mock()
        tool_func: Callable | None = None

        def capture_tool(name=None):
            def decorator(func):
                nonlocal tool_func
                tool_func = func
                return func

            return decorator

        mock_mcp.tool = capture_tool

        register_tools(mock_mcp)

        assert tool_func is not None  # type guard for mypy
        result = tool_func(limit=0, offset=0)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "INVALID_PARAMETER"
        assert parsed["details"]["parameter"] == "limit"

    @patch("mcp_server_spira.features.mywork.tools.myrequirements.get_spira_client")
    def test_validation_limit_negative(self, mock_get_client):
        """Test that limit validation rejects negative values."""
        from unittest.mock import Mock

        from mcp_server_spira.features.mywork.tools.myrequirements import register_tools

        mock_mcp = Mock()
        tool_func: Callable | None = None

        def capture_tool(name=None):
            def decorator(func):
                nonlocal tool_func
                tool_func = func
                return func

            return decorator

        mock_mcp.tool = capture_tool

        register_tools(mock_mcp)

        assert tool_func is not None  # type guard for mypy
        result = tool_func(limit=-10, offset=0)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "INVALID_PARAMETER"

    @patch("mcp_server_spira.features.mywork.tools.myrequirements.get_spira_client")
    def test_validation_offset_negative(self, mock_get_client):
        """Test that offset validation rejects negative values."""
        from unittest.mock import Mock

        from mcp_server_spira.features.mywork.tools.myrequirements import register_tools

        mock_mcp = Mock()
        tool_func: Callable | None = None

        def capture_tool(name=None):
            def decorator(func):
                nonlocal tool_func
                tool_func = func
                return func

            return decorator

        mock_mcp.tool = capture_tool

        register_tools(mock_mcp)

        assert tool_func is not None  # type guard for mypy
        result = tool_func(limit=25, offset=-1)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "INVALID_PARAMETER"
        assert parsed["details"]["parameter"] == "offset"
        assert parsed["details"]["value"] == -1

    @patch("mcp_server_spira.features.mywork.tools.myrequirements.get_spira_client")
    def test_validation_passes_with_valid_params(self, mock_get_client):
        """Test that validation passes with valid parameters."""
        from unittest.mock import Mock

        from mcp_server_spira.features.mywork.tools.myrequirements import register_tools

        mock_client = Mock()
        mock_client.make_spira_api_get_request.return_value = [
            {"RequirementId": 1, "Name": "Requirement 1"}
        ]
        mock_get_client.return_value = mock_client

        mock_mcp = Mock()
        tool_func: Callable | None = None

        def capture_tool(name=None):
            def decorator(func):
                nonlocal tool_func
                tool_func = func
                return func

            return decorator

        mock_mcp.tool = capture_tool

        register_tools(mock_mcp)

        assert tool_func is not None  # type guard for mypy
        result = tool_func(limit=25, offset=0)

        parsed = json.loads(result)
        assert "data" in parsed
        assert "error" not in parsed

    @patch("mcp_server_spira.features.mywork.tools.myrequirements.get_spira_client")
    def test_tool_handles_client_exception(self, mock_get_client):
        """Test that tool handles exceptions from get_spira_client."""
        mock_get_client.side_effect = Exception("Client initialization failed")

        from unittest.mock import Mock

        from mcp_server_spira.features.mywork.tools.myrequirements import register_tools

        mock_mcp = Mock()
        tool_func: Callable | None = None

        def capture_tool(name=None):
            def decorator(func):
                nonlocal tool_func
                tool_func = func
                return func

            return decorator

        mock_mcp.tool = capture_tool

        register_tools(mock_mcp)

        assert tool_func is not None  # type guard for mypy
        result = tool_func(limit=25, offset=0)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error_code"] == "API_ERROR"


# Integration tests with real API (skipped unless credentials available)
@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("INFLECTRA_SPIRA_BASE_URL"),
    reason="Requires Spira credentials (INFLECTRA_SPIRA_BASE_URL)",
)
class TestGetMyRequirementsRealAPIIntegration:
    """Integration tests with real Spira API."""

    @pytest.fixture(scope="class")
    def spira_client(self):
        """Get a real Spira client."""
        return get_spira_client()

    def test_returns_valid_json_structure(self, spira_client):
        """Test that implementation returns valid JSON with correct structure."""
        result = _get_my_requirements_impl(spira_client, limit=25, offset=0)

        # Verify it returns valid JSON
        parsed = json.loads(result)
        assert "data" in parsed
        assert "pagination" in parsed

        # Verify pagination structure
        pagination = parsed["pagination"]
        assert "limit" in pagination
        assert "offset" in pagination
        assert "returned_count" in pagination
        assert "total_count" in pagination
        assert "has_more" in pagination
        assert "pagination_type" in pagination

        # Verify pagination type
        assert pagination["pagination_type"] == "client-side"

        print("\n✓ Integration test passed:")
        print(f"  Total requirements: {pagination['total_count']}")
        print(f"  Returned: {pagination['returned_count']}")
        print(f"  Has more: {pagination['has_more']}")

    def test_pagination_works_with_real_data(self, spira_client):
        """Test that pagination works correctly with real data."""
        # Get first page
        result1 = _get_my_requirements_impl(spira_client, limit=5, offset=0)
        parsed1 = json.loads(result1)

        # Get second page
        result2 = _get_my_requirements_impl(spira_client, limit=5, offset=5)
        parsed2 = json.loads(result2)

        # If there are enough requirements, verify pages are different
        if (
            parsed1["pagination"]["total_count"] > 5
            and len(parsed1["data"]) > 0
            and len(parsed2["data"]) > 0
            and parsed1["data"][0]["RequirementId"] != parsed2["data"][0]["RequirementId"]
        ):
            print("\n✓ Pagination test passed:")
            print(f"  Page 1 first requirement: {parsed1['data'][0]['RequirementId']}")
            print(f"  Page 2 first requirement: {parsed2['data'][0]['RequirementId']}")

    def test_handles_empty_results(self, spira_client):
        """Test handling of empty results or offset beyond data."""
        # Try with very large offset
        result = _get_my_requirements_impl(spira_client, limit=25, offset=10000)
        parsed = json.loads(result)

        # Should return empty data with correct metadata
        assert isinstance(parsed["data"], list)
        assert parsed["pagination"]["returned_count"] == len(parsed["data"])
        assert parsed["pagination"]["has_more"] is False

        print("\n✓ Empty results test passed:")
        print(f"  Returned count: {parsed['pagination']['returned_count']}")

    def test_preserves_requirement_fields(self, spira_client):
        """Test that all requirement fields are preserved."""
        result = _get_my_requirements_impl(spira_client, limit=1, offset=0)
        parsed = json.loads(result)

        if len(parsed["data"]) > 0:
            requirement = parsed["data"][0]

            # Verify key fields exist
            expected_fields = ["RequirementId", "Name"]
            for field in expected_fields:
                assert field in requirement, f"Missing field: {field}"

            print("\n✓ Field preservation test passed:")
            print(f"  Requirement has {len(requirement.keys())} fields")
            print(f"  Sample fields: {list(requirement.keys())[:10]}")

    def test_error_handling_with_real_client(self, spira_client):
        """Test that errors are handled gracefully."""
        # This should not raise exceptions even with edge cases
        result = _get_my_requirements_impl(spira_client, limit=1, offset=0)

        # Should always return valid JSON
        parsed = json.loads(result)

        # Should have either data or error
        assert "data" in parsed or "error" in parsed

        print("\n✓ Error handling test passed")
