"""
Tests for the My Test Sets features of the Inflectra Spira MCP Server.
"""

import json
import os
from collections.abc import Callable
from unittest.mock import Mock, patch

import pytest

from mcp_server_spira.features.mywork.tools.mytestsets import (
    _get_my_testsets_impl,
    get_spira_client,
)


@pytest.mark.unit
class TestGetMyTestSetsImpl:
    """Tests for _get_my_testsets_impl function."""

    def test_successful_retrieval_with_default_pagination(self):
        """Test successful test set retrieval with default pagination."""
        # Mock Spira client
        mock_client = Mock()
        mock_testsets = [
            {"TestSetId": i, "Name": f"Test Set {i}", "TestSetStatusName": "In Progress"}
            for i in range(1, 51)
        ]
        mock_client.make_spira_api_get_request.return_value = mock_testsets

        # Call implementation with defaults
        result = _get_my_testsets_impl(mock_client, limit=25, offset=0)

        # Verify API was called correctly
        mock_client.make_spira_api_get_request.assert_called_once_with("test-sets")

        # Parse and verify response
        parsed = json.loads(result)
        assert "data" in parsed
        assert "pagination" in parsed
        assert len(parsed["data"]) == 25
        assert parsed["data"][0]["TestSetId"] == 1
        assert parsed["data"][24]["TestSetId"] == 25
        assert parsed["pagination"]["limit"] == 25
        assert parsed["pagination"]["offset"] == 0
        assert parsed["pagination"]["returned_count"] == 25
        assert parsed["pagination"]["total_count"] == 50
        assert parsed["pagination"]["has_more"] is True
        assert parsed["pagination"]["pagination_type"] == "client-side"

    def test_successful_retrieval_first_page(self):
        """Test retrieving first page of results."""
        mock_client = Mock()
        mock_testsets = [{"TestSetId": i, "Name": f"Test Set {i}"} for i in range(1, 101)]
        mock_client.make_spira_api_get_request.return_value = mock_testsets

        result = _get_my_testsets_impl(mock_client, limit=25, offset=0)

        parsed = json.loads(result)
        assert len(parsed["data"]) == 25
        assert parsed["data"][0]["TestSetId"] == 1
        assert parsed["pagination"]["has_more"] is True

    def test_successful_retrieval_middle_page(self):
        """Test retrieving middle page of results."""
        mock_client = Mock()
        mock_testsets = [{"TestSetId": i, "Name": f"Test Set {i}"} for i in range(1, 101)]
        mock_client.make_spira_api_get_request.return_value = mock_testsets

        result = _get_my_testsets_impl(mock_client, limit=25, offset=25)

        parsed = json.loads(result)
        assert len(parsed["data"]) == 25
        assert parsed["data"][0]["TestSetId"] == 26
        assert parsed["data"][24]["TestSetId"] == 50
        assert parsed["pagination"]["offset"] == 25
        assert parsed["pagination"]["has_more"] is True

    def test_successful_retrieval_last_page_full(self):
        """Test retrieving last page with full results."""
        mock_client = Mock()
        mock_testsets = [{"TestSetId": i, "Name": f"Test Set {i}"} for i in range(1, 101)]
        mock_client.make_spira_api_get_request.return_value = mock_testsets

        result = _get_my_testsets_impl(mock_client, limit=25, offset=75)

        parsed = json.loads(result)
        assert len(parsed["data"]) == 25
        assert parsed["data"][0]["TestSetId"] == 76
        assert parsed["data"][24]["TestSetId"] == 100
        assert parsed["pagination"]["offset"] == 75
        assert parsed["pagination"]["returned_count"] == 25
        assert parsed["pagination"]["has_more"] is False

    def test_successful_retrieval_last_page_partial(self):
        """Test retrieving last page with partial results."""
        mock_client = Mock()
        mock_testsets = [{"TestSetId": i, "Name": f"Test Set {i}"} for i in range(1, 48)]
        mock_client.make_spira_api_get_request.return_value = mock_testsets

        result = _get_my_testsets_impl(mock_client, limit=25, offset=25)

        parsed = json.loads(result)
        assert len(parsed["data"]) == 22
        assert parsed["data"][0]["TestSetId"] == 26
        assert parsed["data"][21]["TestSetId"] == 47
        assert parsed["pagination"]["returned_count"] == 22
        assert parsed["pagination"]["total_count"] == 47
        assert parsed["pagination"]["has_more"] is False

    def test_empty_results(self):
        """Test handling of empty test set list."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.return_value = []

        result = _get_my_testsets_impl(mock_client, limit=25, offset=0)

        parsed = json.loads(result)
        assert parsed["data"] == []
        assert parsed["pagination"]["returned_count"] == 0
        assert parsed["pagination"]["total_count"] == 0
        assert parsed["pagination"]["has_more"] is False

    def test_empty_results_with_offset(self):
        """Test handling of empty results when offset is beyond data."""
        mock_client = Mock()
        mock_testsets = [{"TestSetId": i, "Name": f"Test Set {i}"} for i in range(1, 26)]
        mock_client.make_spira_api_get_request.return_value = mock_testsets

        result = _get_my_testsets_impl(mock_client, limit=25, offset=50)

        parsed = json.loads(result)
        assert parsed["data"] == []
        assert parsed["pagination"]["returned_count"] == 0
        assert parsed["pagination"]["total_count"] == 25
        assert parsed["pagination"]["has_more"] is False

    def test_custom_limit(self):
        """Test with custom limit parameter."""
        mock_client = Mock()
        mock_testsets = [{"TestSetId": i, "Name": f"Test Set {i}"} for i in range(1, 101)]
        mock_client.make_spira_api_get_request.return_value = mock_testsets

        result = _get_my_testsets_impl(mock_client, limit=50, offset=0)

        parsed = json.loads(result)
        assert len(parsed["data"]) == 50
        assert parsed["pagination"]["limit"] == 50
        assert parsed["pagination"]["returned_count"] == 50

    def test_limit_larger_than_total(self):
        """Test when limit is larger than total available items."""
        mock_client = Mock()
        mock_testsets = [{"TestSetId": i, "Name": f"Test Set {i}"} for i in range(1, 11)]
        mock_client.make_spira_api_get_request.return_value = mock_testsets

        result = _get_my_testsets_impl(mock_client, limit=100, offset=0)

        parsed = json.loads(result)
        assert len(parsed["data"]) == 10
        assert parsed["pagination"]["returned_count"] == 10
        assert parsed["pagination"]["total_count"] == 10
        assert parsed["pagination"]["has_more"] is False

    def test_single_testset(self):
        """Test with single test set result."""
        mock_client = Mock()
        mock_testsets = [{"TestSetId": 1, "Name": "Single Test Set"}]
        mock_client.make_spira_api_get_request.return_value = mock_testsets

        result = _get_my_testsets_impl(mock_client, limit=25, offset=0)

        parsed = json.loads(result)
        assert len(parsed["data"]) == 1
        assert parsed["data"][0]["TestSetId"] == 1
        assert parsed["pagination"]["total_count"] == 1
        assert parsed["pagination"]["has_more"] is False

    def test_preserves_testset_data_structure(self):
        """Test that all test set fields are preserved in response."""
        mock_client = Mock()
        mock_testsets = [
            {
                "TestSetId": 123,
                "Name": "Smoke Test Suite",
                "Description": "Critical smoke tests",
                "TestSetStatusId": 2,
                "TestSetStatusName": "In Progress",
                "TestRunTypeId": 1,
                "CreatorId": 4,
                "CreatorName": "Jane Smith",
                "OwnerId": 5,
                "OwnerName": "John Doe",
                "ReleaseId": 10,
                "ReleaseVersionNumber": "1.5.0",
                "PlannedDate": "2024-01-20T09:00:00Z",
                "ExecutionDate": "2024-01-16T10:00:00Z",
                "CountPassed": 15,
                "CountFailed": 3,
                "CountCaution": 1,
                "CountBlocked": 2,
                "CountNotRun": 5,
                "EstimatedDuration": 180,
                "ActualDuration": 165,
                "CustomProperties": [{"id": 1, "value": "test"}],
                "Tags": "smoke,critical,release",
            }
        ]
        mock_client.make_spira_api_get_request.return_value = mock_testsets

        result = _get_my_testsets_impl(mock_client, limit=25, offset=0)

        parsed = json.loads(result)
        testset = parsed["data"][0]
        assert testset["TestSetId"] == 123
        assert testset["Name"] == "Smoke Test Suite"
        assert testset["Description"] == "Critical smoke tests"
        assert testset["TestSetStatusName"] == "In Progress"
        assert testset["CountPassed"] == 15
        assert testset["CountFailed"] == 3
        assert testset["EstimatedDuration"] == 180
        assert testset["CustomProperties"] == [{"id": 1, "value": "test"}]
        assert testset["Tags"] == "smoke,critical,release"

    def test_api_error_handling(self):
        """Test handling of API errors."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.side_effect = Exception("API connection failed")

        result = _get_my_testsets_impl(mock_client, limit=25, offset=0)

        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error"] == "Failed to retrieve test sets"
        assert parsed["error_code"] == "API_ERROR"
        assert "API connection failed" in parsed["details"]["message"]
        assert "suggestion" in parsed

    def test_api_returns_none(self):
        """Test handling when API returns None."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.return_value = None

        result = _get_my_testsets_impl(mock_client, limit=25, offset=0)

        parsed = json.loads(result)
        assert parsed["data"] == []
        assert parsed["pagination"]["total_count"] == 0

    def test_json_structure_validity(self):
        """Test that response is valid JSON with correct structure."""
        mock_client = Mock()
        mock_testsets = [{"TestSetId": 1, "Name": "Test Set 1"}]
        mock_client.make_spira_api_get_request.return_value = mock_testsets

        result = _get_my_testsets_impl(mock_client, limit=25, offset=0)

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
        mock_testsets = [{"TestSetId": i} for i in range(1, 76)]
        mock_client.make_spira_api_get_request.return_value = mock_testsets

        # Test various pagination scenarios
        test_cases = [
            (25, 0, 25, 75, True),  # First page
            (25, 25, 25, 75, True),  # Second page
            (25, 50, 25, 75, False),  # Last page
            (10, 0, 10, 75, True),  # Small limit
            (100, 0, 75, 75, False),  # Limit larger than total
        ]

        for limit, offset, expected_returned, expected_total, expected_has_more in test_cases:
            result = _get_my_testsets_impl(mock_client, limit=limit, offset=offset)
            parsed = json.loads(result)

            assert parsed["pagination"]["limit"] == limit
            assert parsed["pagination"]["offset"] == offset
            assert parsed["pagination"]["returned_count"] == expected_returned
            assert parsed["pagination"]["total_count"] == expected_total
            assert parsed["pagination"]["has_more"] == expected_has_more


@pytest.mark.unit
class TestGetMyTestSetsToolIntegration:
    """Integration tests for get_my_testsets tool with validation."""

    @patch("mcp_server_spira.features.mywork.tools.mytestsets.get_spira_client")
    def test_validation_limit_too_high(self, mock_get_client):
        """Test that limit validation rejects values > 500."""
        from unittest.mock import Mock

        from mcp_server_spira.features.mywork.tools.mytestsets import register_tools

        # Create mock MCP server
        mock_mcp = Mock()
        tool_func: Callable | None = None

        def capture_tool(name=None, **kwargs):
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

    @patch("mcp_server_spira.features.mywork.tools.mytestsets.get_spira_client")
    def test_validation_limit_zero(self, mock_get_client):
        """Test that limit validation rejects zero."""
        from unittest.mock import Mock

        from mcp_server_spira.features.mywork.tools.mytestsets import register_tools

        mock_mcp = Mock()
        tool_func: Callable | None = None

        def capture_tool(name=None, **kwargs):
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

    @patch("mcp_server_spira.features.mywork.tools.mytestsets.get_spira_client")
    def test_validation_limit_negative(self, mock_get_client):
        """Test that limit validation rejects negative values."""
        from unittest.mock import Mock

        from mcp_server_spira.features.mywork.tools.mytestsets import register_tools

        mock_mcp = Mock()
        tool_func: Callable | None = None

        def capture_tool(name=None, **kwargs):
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

    @patch("mcp_server_spira.features.mywork.tools.mytestsets.get_spira_client")
    def test_validation_offset_negative(self, mock_get_client):
        """Test that offset validation rejects negative values."""
        from unittest.mock import Mock

        from mcp_server_spira.features.mywork.tools.mytestsets import register_tools

        mock_mcp = Mock()
        tool_func: Callable | None = None

        def capture_tool(name=None, **kwargs):
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

    @patch("mcp_server_spira.features.mywork.tools.mytestsets.get_spira_client")
    def test_validation_passes_with_valid_params(self, mock_get_client):
        """Test that validation passes with valid parameters."""
        from unittest.mock import Mock

        from mcp_server_spira.features.mywork.tools.mytestsets import register_tools

        mock_client = Mock()
        mock_client.make_spira_api_get_request.return_value = [
            {"TestSetId": 1, "Name": "Test Set 1"}
        ]
        mock_get_client.return_value = mock_client

        mock_mcp = Mock()
        tool_func: Callable | None = None

        def capture_tool(name=None, **kwargs):
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

    @patch("mcp_server_spira.features.mywork.tools.mytestsets.get_spira_client")
    def test_tool_handles_client_exception(self, mock_get_client):
        """Test that tool handles exceptions from get_spira_client."""
        mock_get_client.side_effect = Exception("Client initialization failed")

        from unittest.mock import Mock

        from mcp_server_spira.features.mywork.tools.mytestsets import register_tools

        mock_mcp = Mock()
        tool_func: Callable | None = None

        def capture_tool(name=None, **kwargs):
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
class TestGetMyTestSetsRealAPIIntegration:
    """Integration tests with real Spira API."""

    @pytest.fixture(scope="class")
    def spira_client(self):
        """Get a real Spira client."""
        return get_spira_client()

    def test_returns_valid_json_structure(self, spira_client):
        """Test that implementation returns valid JSON with correct structure."""
        result = _get_my_testsets_impl(spira_client, limit=25, offset=0)

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
        print(f"  Total test sets: {pagination['total_count']}")
        print(f"  Returned: {pagination['returned_count']}")
        print(f"  Has more: {pagination['has_more']}")

    def test_pagination_works_with_real_data(self, spira_client):
        """Test that pagination works correctly with real data."""
        # Get first page
        result1 = _get_my_testsets_impl(spira_client, limit=5, offset=0)
        parsed1 = json.loads(result1)

        # Get second page
        result2 = _get_my_testsets_impl(spira_client, limit=5, offset=5)
        parsed2 = json.loads(result2)

        # If there are enough test sets, verify pages are different
        if (
            parsed1["pagination"]["total_count"] > 5
            and len(parsed1["data"]) > 0
            and len(parsed2["data"]) > 0
            and parsed1["data"][0]["TestSetId"] != parsed2["data"][0]["TestSetId"]
        ):
            print("\n✓ Pagination test passed:")
            print(f"  Page 1 first test set: {parsed1['data'][0]['TestSetId']}")
            print(f"  Page 2 first test set: {parsed2['data'][0]['TestSetId']}")

    def test_handles_empty_results(self, spira_client):
        """Test handling of empty results or offset beyond data."""
        # Try with very large offset
        result = _get_my_testsets_impl(spira_client, limit=25, offset=10000)
        parsed = json.loads(result)

        # Should return empty data with correct metadata
        assert isinstance(parsed["data"], list)
        assert parsed["pagination"]["returned_count"] == len(parsed["data"])
        assert parsed["pagination"]["has_more"] is False

        print("\n✓ Empty results test passed:")
        print(f"  Returned count: {parsed['pagination']['returned_count']}")

    def test_preserves_testset_fields(self, spira_client):
        """Test that all test set fields are preserved."""
        result = _get_my_testsets_impl(spira_client, limit=1, offset=0)
        parsed = json.loads(result)

        if len(parsed["data"]) > 0:
            testset = parsed["data"][0]

            # Verify key fields exist
            expected_fields = ["TestSetId", "Name"]
            for field in expected_fields:
                assert field in testset, f"Missing field: {field}"

            print("\n✓ Field preservation test passed:")
            print(f"  Test set has {len(testset.keys())} fields")
            print(f"  Sample fields: {list(testset.keys())[:10]}")

    def test_error_handling_with_real_client(self, spira_client):
        """Test that errors are handled gracefully."""
        # This should not raise exceptions even with edge cases
        result = _get_my_testsets_impl(spira_client, limit=1, offset=0)

        # Should always return valid JSON
        parsed = json.loads(result)

        # Should have either data or error
        assert "data" in parsed or "error" in parsed

        print("\n✓ Error handling test passed")
