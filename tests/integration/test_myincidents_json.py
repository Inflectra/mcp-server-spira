"""
Integration tests for the new JSON-based get_my_incidents implementation.

These tests verify the new implementation against a real Spira instance:
- JSON output format
- Client-side pagination
- Input validation
- Error handling
- Data structure preservation

Prerequisites:
1. .env file with valid Spira credentials
2. Spira instance with test data

Run with: pytest tests/integration/test_myincidents_json.py -v -s
"""

import json
import os

import pytest

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.mywork.tools.myincidents import _get_my_incidents_impl

# Mark all tests as integration tests and skip if no credentials
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.environ.get("INFLECTRA_SPIRA_BASE_URL"),
        reason="Requires Spira credentials (set in .env file)",
    ),
]


class TestGetMyIncidentsJSONIntegration:
    """Integration tests for JSON-based get_my_incidents implementation."""

    @pytest.fixture(scope="class")
    def spira_client(self):
        """Get a real Spira client."""
        return get_spira_client()

    @pytest.fixture(scope="class")
    def raw_incidents(self, spira_client):
        """Get raw incidents from API for comparison."""
        return spira_client.make_spira_api_get_request("incidents")

    def test_returns_valid_json(self, spira_client):
        """Test that implementation returns valid JSON."""
        result = _get_my_incidents_impl(spira_client, limit=25, offset=0)

        print("\n📋 JSON validation test:")
        print(f"   Result type: {type(result)}")
        print(f"   Result length: {len(result)} characters")

        # Should be a string
        assert isinstance(result, str)

        # Should be valid JSON
        try:
            parsed = json.loads(result)
            print("   ✓ Valid JSON")
        except json.JSONDecodeError as e:
            pytest.fail(f"Result is not valid JSON: {e}")

        # Should have required structure
        assert "data" in parsed
        assert "pagination" in parsed
        print("   ✓ Has required structure (data, pagination)")

    def test_json_structure(self, spira_client):
        """Test the structure of JSON response."""
        result = _get_my_incidents_impl(spira_client, limit=25, offset=0)
        parsed = json.loads(result)

        print("\n🔍 JSON structure test:")

        # Check data field
        assert "data" in parsed
        assert isinstance(parsed["data"], list)
        print("   ✓ data field is a list")

        # Check pagination field
        assert "pagination" in parsed
        pagination = parsed["pagination"]
        assert isinstance(pagination, dict)
        print("   ✓ pagination field is a dict")

        # Check pagination metadata
        required_pagination_fields = [
            "limit",
            "offset",
            "returned_count",
            "total_count",
            "has_more",
            "pagination_type",
        ]
        for field in required_pagination_fields:
            assert field in pagination, f"Missing pagination field: {field}"
        print(f"   ✓ All pagination fields present: {required_pagination_fields}")

        # Check pagination type
        assert pagination["pagination_type"] == "client-side"
        print("   ✓ pagination_type is 'client-side'")

    def test_pagination_default_parameters(self, spira_client, raw_incidents):
        """Test pagination with default parameters (limit=25, offset=0)."""
        result = _get_my_incidents_impl(spira_client, limit=25, offset=0)
        parsed = json.loads(result)

        print("\n📄 Default pagination test:")
        print(f"   Total incidents from API: {len(raw_incidents)}")

        pagination = parsed["pagination"]
        print("   Pagination metadata:")
        print(f"     - limit: {pagination['limit']}")
        print(f"     - offset: {pagination['offset']}")
        print(f"     - returned_count: {pagination['returned_count']}")
        print(f"     - total_count: {pagination['total_count']}")
        print(f"     - has_more: {pagination['has_more']}")

        # Verify pagination metadata
        assert pagination["limit"] == 25
        assert pagination["offset"] == 0
        assert pagination["total_count"] == len(raw_incidents)

        # Verify returned count
        expected_returned = min(25, len(raw_incidents))
        assert pagination["returned_count"] == expected_returned
        assert len(parsed["data"]) == expected_returned

        # Verify has_more flag
        expected_has_more = len(raw_incidents) > 25
        assert pagination["has_more"] == expected_has_more

        print("   ✓ Pagination metadata is accurate")

    def test_pagination_first_page(self, spira_client, raw_incidents):
        """Test retrieving first page of results."""
        if len(raw_incidents) == 0:
            pytest.skip("No incidents available for pagination test")

        result = _get_my_incidents_impl(spira_client, limit=10, offset=0)
        parsed = json.loads(result)

        print("\n📄 First page test (limit=10, offset=0):")
        print(f"   Total incidents: {len(raw_incidents)}")
        print(f"   Returned: {len(parsed['data'])}")

        # Should return up to 10 items
        expected_count = min(10, len(raw_incidents))
        assert len(parsed["data"]) == expected_count

        # Should match first items from raw data
        if len(raw_incidents) > 0:
            assert parsed["data"][0]["IncidentId"] == raw_incidents[0]["IncidentId"]
            print(f"   ✓ First incident matches: IncidentId={raw_incidents[0]['IncidentId']}")

    def test_pagination_second_page(self, spira_client, raw_incidents):
        """Test retrieving second page of results."""
        if len(raw_incidents) < 11:
            pytest.skip("Not enough incidents for second page test (need > 10)")

        result = _get_my_incidents_impl(spira_client, limit=10, offset=10)
        parsed = json.loads(result)

        print("\n📄 Second page test (limit=10, offset=10):")
        print(f"   Total incidents: {len(raw_incidents)}")
        print(f"   Returned: {len(parsed['data'])}")

        # Should return up to 10 items starting from index 10
        expected_count = min(10, len(raw_incidents) - 10)
        assert len(parsed["data"]) == expected_count

        # Should match items from raw data at offset 10
        if len(raw_incidents) > 10:
            assert parsed["data"][0]["IncidentId"] == raw_incidents[10]["IncidentId"]
            print(
                f"   ✓ First incident on page 2 matches: IncidentId={raw_incidents[10]['IncidentId']}"
            )

    def test_pagination_last_page(self, spira_client, raw_incidents):
        """Test retrieving last page with partial results."""
        if len(raw_incidents) < 26:
            pytest.skip("Not enough incidents for last page test (need > 25)")

        # Calculate offset for last page
        offset = (len(raw_incidents) // 25) * 25

        result = _get_my_incidents_impl(spira_client, limit=25, offset=offset)
        parsed = json.loads(result)

        print(f"\n📄 Last page test (limit=25, offset={offset}):")
        print(f"   Total incidents: {len(raw_incidents)}")
        print(f"   Returned: {len(parsed['data'])}")

        # Should have has_more = False
        assert parsed["pagination"]["has_more"] is False
        print("   ✓ has_more is False (last page)")

        # Should return remaining items
        expected_count = len(raw_incidents) - offset
        assert len(parsed["data"]) == expected_count
        print(f"   ✓ Returned {expected_count} remaining incidents")

    def test_pagination_beyond_end(self, spira_client, raw_incidents):
        """Test pagination with offset beyond available data."""
        offset = len(raw_incidents) + 100

        result = _get_my_incidents_impl(spira_client, limit=25, offset=offset)
        parsed = json.loads(result)

        print(f"\n📄 Beyond end test (offset={offset}):")
        print(f"   Total incidents: {len(raw_incidents)}")
        print(f"   Returned: {len(parsed['data'])}")

        # Should return empty data
        assert len(parsed["data"]) == 0
        assert parsed["pagination"]["returned_count"] == 0
        assert parsed["pagination"]["has_more"] is False
        print("   ✓ Returns empty data with correct metadata")

    def test_custom_limit(self, spira_client, raw_incidents):
        """Test with custom limit parameter."""
        if len(raw_incidents) == 0:
            pytest.skip("No incidents available for custom limit test")

        result = _get_my_incidents_impl(spira_client, limit=5, offset=0)
        parsed = json.loads(result)

        print("\n📄 Custom limit test (limit=5):")
        print(f"   Total incidents: {len(raw_incidents)}")
        print(f"   Returned: {len(parsed['data'])}")

        # Should return up to 5 items
        expected_count = min(5, len(raw_incidents))
        assert len(parsed["data"]) == expected_count
        assert parsed["pagination"]["limit"] == 5
        print("   ✓ Respects custom limit")

    def test_large_limit(self, spira_client, raw_incidents):
        """Test with large limit (100)."""
        result = _get_my_incidents_impl(spira_client, limit=100, offset=0)
        parsed = json.loads(result)

        print("\n📄 Large limit test (limit=100):")
        print(f"   Total incidents: {len(raw_incidents)}")
        print(f"   Returned: {len(parsed['data'])}")

        # Should return all incidents up to 100
        expected_count = min(100, len(raw_incidents))
        assert len(parsed["data"]) == expected_count
        print("   ✓ Returns up to 100 incidents")

    def test_empty_results(self, spira_client):
        """Test handling of empty results (if user has no incidents)."""
        result = _get_my_incidents_impl(spira_client, limit=25, offset=0)
        parsed = json.loads(result)

        print("\n📄 Empty results test:")
        print(f"   Total incidents: {parsed['pagination']['total_count']}")

        if parsed["pagination"]["total_count"] == 0:
            assert len(parsed["data"]) == 0
            assert parsed["pagination"]["returned_count"] == 0
            assert parsed["pagination"]["has_more"] is False
            print("   ✓ Handles empty results correctly")
        else:
            print("   ℹ️  User has incidents, skipping empty test")

    def test_data_preservation(self, spira_client, raw_incidents):
        """Test that all incident fields are preserved in JSON output."""
        if len(raw_incidents) == 0:
            pytest.skip("No incidents available for data preservation test")

        result = _get_my_incidents_impl(spira_client, limit=1, offset=0)
        parsed = json.loads(result)

        print("\n🔍 Data preservation test:")

        # Get first incident from both sources
        json_incident = parsed["data"][0]
        raw_incident = raw_incidents[0]

        print(f"   Raw incident keys: {len(raw_incident.keys())}")
        print(f"   JSON incident keys: {len(json_incident.keys())}")

        # All fields from raw incident should be in JSON incident
        for key in raw_incident:
            assert key in json_incident, f"Missing field: {key}"

        print("   ✓ All fields preserved")

        # Verify some key fields
        key_fields = ["IncidentId", "Name", "IncidentStatusName"]
        for field in key_fields:
            if field in raw_incident:
                assert json_incident[field] == raw_incident[field]
                print(f"   ✓ {field}: {json_incident[field]}")

    def test_incident_data_types(self, spira_client, raw_incidents):
        """Test that data types are preserved correctly."""
        if len(raw_incidents) == 0:
            pytest.skip("No incidents available for data type test")

        result = _get_my_incidents_impl(spira_client, limit=1, offset=0)
        parsed = json.loads(result)

        print("\n🔍 Data type preservation test:")

        incident = parsed["data"][0]

        # Check integer fields
        if "IncidentId" in incident:
            assert isinstance(incident["IncidentId"], int)
            print(f"   ✓ IncidentId is int: {incident['IncidentId']}")

        # Check string fields
        if "Name" in incident:
            assert isinstance(incident["Name"], str | type(None))
            print(f"   ✓ Name is string: {incident['Name']}")

        # Check nullable fields
        if "Description" in incident:
            assert isinstance(incident["Description"], str | type(None))
            print("   ✓ Description handles null")

    def test_pagination_metadata_accuracy(self, spira_client, raw_incidents):
        """Test that pagination metadata is calculated correctly."""
        result = _get_my_incidents_impl(spira_client, limit=25, offset=0)
        parsed = json.loads(result)

        print("\n📊 Pagination metadata accuracy test:")

        pagination = parsed["pagination"]
        data = parsed["data"]

        # Verify returned_count matches actual data length
        assert pagination["returned_count"] == len(data)
        print(f"   ✓ returned_count matches data length: {len(data)}")

        # Verify total_count matches raw API data
        assert pagination["total_count"] == len(raw_incidents)
        print(f"   ✓ total_count matches API: {len(raw_incidents)}")

        # Verify has_more calculation
        expected_has_more = (pagination["offset"] + pagination["returned_count"]) < pagination[
            "total_count"
        ]
        assert pagination["has_more"] == expected_has_more
        print(f"   ✓ has_more calculated correctly: {expected_has_more}")

    def test_no_silent_truncation(self, spira_client, raw_incidents):
        """Test that there is no silent truncation (all data accessible via pagination)."""
        if len(raw_incidents) <= 25:
            pytest.skip("Not enough incidents to test truncation (need > 25)")

        print("\n✂️  No silent truncation test:")
        print(f"   Total incidents: {len(raw_incidents)}")

        # Retrieve all incidents via pagination
        all_retrieved_incidents = []
        offset = 0
        limit = 25

        while True:
            result = _get_my_incidents_impl(spira_client, limit=limit, offset=offset)
            parsed = json.loads(result)

            all_retrieved_incidents.extend(parsed["data"])

            if not parsed["pagination"]["has_more"]:
                break

            offset += limit

        print(f"   Retrieved via pagination: {len(all_retrieved_incidents)}")

        # Should be able to retrieve all incidents
        assert len(all_retrieved_incidents) == len(raw_incidents)
        print("   ✓ All incidents accessible via pagination (no silent truncation)")

    def test_json_formatting(self, spira_client):
        """Test that JSON is properly formatted."""
        result = _get_my_incidents_impl(spira_client, limit=25, offset=0)

        print("\n📝 JSON formatting test:")

        # Should be indented (contains newlines and spaces)
        assert "\n" in result
        assert "  " in result
        print("   ✓ JSON is indented (human-readable)")

        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed is not None
        print("   ✓ JSON is valid")

    def test_error_handling_with_real_api(self, spira_client):
        """Test error handling with real API."""
        # This should not raise exceptions
        result = _get_my_incidents_impl(spira_client, limit=25, offset=0)

        print("\n⚠️  Error handling test:")

        # Should always return a string
        assert isinstance(result, str)

        # Should be valid JSON (either success or error)
        parsed = json.loads(result)

        if "error" in parsed:
            print(f"   Error response: {parsed['error']}")
            assert "error_code" in parsed
            print("   ✓ Error response has proper structure")
        else:
            print("   ✓ Success response")

    def test_comparison_with_raw_api(self, spira_client, raw_incidents):
        """Test that JSON output matches raw API data."""
        if len(raw_incidents) == 0:
            pytest.skip("No incidents available for comparison test")

        result = _get_my_incidents_impl(spira_client, limit=len(raw_incidents), offset=0)
        parsed = json.loads(result)

        print("\n🔄 Comparison with raw API test:")
        print(f"   Raw API incidents: {len(raw_incidents)}")
        print(f"   JSON incidents: {len(parsed['data'])}")

        # Should have same number of incidents
        assert len(parsed["data"]) == len(raw_incidents)

        # Incident IDs should match in order
        for i, (json_incident, raw_incident) in enumerate(
            zip(parsed["data"], raw_incidents, strict=False)
        ):
            assert (
                json_incident["IncidentId"] == raw_incident["IncidentId"]
            ), f"Mismatch at index {i}"

        print("   ✓ JSON output matches raw API data")


class TestGetMyIncidentsPerformance:
    """Performance tests for get_my_incidents."""

    @pytest.fixture(scope="class")
    def spira_client(self):
        """Get a real Spira client."""
        return get_spira_client()

    @pytest.mark.slow
    def test_performance_with_large_limit(self, spira_client):
        """Test performance with large limit (500)."""
        import time

        print("\n⚡ Performance test (limit=500):")

        start_time = time.time()
        result = _get_my_incidents_impl(spira_client, limit=500, offset=0)
        elapsed_time = time.time() - start_time

        parsed = json.loads(result)

        print(f"   Elapsed time: {elapsed_time:.2f}s")
        print(f"   Incidents returned: {len(parsed['data'])}")
        print(f"   Total incidents: {parsed['pagination']['total_count']}")

        # Should complete in reasonable time (< 10 seconds)
        assert elapsed_time < 10.0, f"Too slow: {elapsed_time:.2f}s"
        print("   ✓ Performance acceptable")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SPIRA MCP SERVER - JSON GET_MY_INCIDENTS INTEGRATION TESTS")
    print("=" * 70)
    print("\nThese tests verify the NEW JSON-based implementation")
    print("against a real Spira instance.\n")
    print("Prerequisites:")
    print("  1. .env file with valid credentials")
    print("  2. Spira instance with test data")
    print("\nRun with: pytest tests/integration/test_myincidents_json.py -v -s")
    print("=" * 70 + "\n")
