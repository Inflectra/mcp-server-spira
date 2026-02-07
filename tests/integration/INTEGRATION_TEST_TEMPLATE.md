# Integration Test Template

This template provides a standardized structure for creating integration tests for "my work" tools.

## File Naming Convention

- `test_mytasks_json.py` - for get_my_tasks
- `test_myincidents_json.py` - for get_my_incidents
- `test_myrequirements_json.py` - for get_my_requirements
- `test_mytestcases_json.py` - for get_my_test_cases
- `test_mytestsets_json.py` - for get_my_test_sets

## Template Structure

```python
"""
Integration tests for the new JSON-based get_my_<artifact> implementation.

These tests verify the new implementation against a real Spira instance:
- JSON output format
- Client-side pagination
- Input validation
- Error handling
- Data structure preservation

Prerequisites:
1. .env file with valid Spira credentials
2. Spira instance with test data

Run with: pytest tests/integration/test_my<artifact>_json.py -v -s
"""

import json
import os

import pytest

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.mywork.tools.my<artifact> import _get_my_<artifact>_impl


# Mark all tests as integration tests and skip if no credentials
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.environ.get("INFLECTRA_SPIRA_BASE_URL"),
        reason="Requires Spira credentials (set in .env file)",
    ),
]


class TestGetMy<Artifact>JSONIntegration:
    """Integration tests for JSON-based get_my_<artifact> implementation."""

    @pytest.fixture(scope="class")
    def spira_client(self):
        """Get a real Spira client."""
        return get_spira_client()

    @pytest.fixture(scope="class")
    def raw_<artifact>(self, spira_client):
        """Get raw <artifact> from API for comparison."""
        return spira_client.make_spira_api_get_request("<artifact>")

    def test_returns_valid_json(self, spira_client):
        """Test that implementation returns valid JSON."""
        result = _get_my_<artifact>_impl(spira_client, limit=25, offset=0)

        print(f"\n📋 JSON validation test:")
        print(f"   Result type: {type(result)}")
        print(f"   Result length: {len(result)} characters")

        # Should be a string
        assert isinstance(result, str)

        # Should be valid JSON
        try:
            parsed = json.loads(result)
            print(f"   ✓ Valid JSON")
        except json.JSONDecodeError as e:
            pytest.fail(f"Result is not valid JSON: {e}")

        # Should have required structure
        assert "data" in parsed
        assert "pagination" in parsed
        print(f"   ✓ Has required structure (data, pagination)")

    def test_json_structure(self, spira_client):
        """Test the structure of JSON response."""
        result = _get_my_<artifact>_impl(spira_client, limit=25, offset=0)
        parsed = json.loads(result)

        print(f"\n🔍 JSON structure test:")

        # Check data field
        assert "data" in parsed
        assert isinstance(parsed["data"], list)
        print(f"   ✓ data field is a list")

        # Check pagination field
        assert "pagination" in parsed
        pagination = parsed["pagination"]
        assert isinstance(pagination, dict)
        print(f"   ✓ pagination field is a dict")

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
        print(f"   ✓ pagination_type is 'client-side'")

    def test_pagination_default_parameters(self, spira_client, raw_<artifact>):
        """Test pagination with default parameters (limit=25, offset=0)."""
        result = _get_my_<artifact>_impl(spira_client, limit=25, offset=0)
        parsed = json.loads(result)

        print(f"\n📄 Default pagination test:")
        print(f"   Total <artifact> from API: {len(raw_<artifact>)}")

        pagination = parsed["pagination"]
        print(f"   Pagination metadata:")
        print(f"     - limit: {pagination['limit']}")
        print(f"     - offset: {pagination['offset']}")
        print(f"     - returned_count: {pagination['returned_count']}")
        print(f"     - total_count: {pagination['total_count']}")
        print(f"     - has_more: {pagination['has_more']}")

        # Verify pagination metadata
        assert pagination["limit"] == 25
        assert pagination["offset"] == 0
        assert pagination["total_count"] == len(raw_<artifact>)

        # Verify returned count
        expected_returned = min(25, len(raw_<artifact>))
        assert pagination["returned_count"] == expected_returned
        assert len(parsed["data"]) == expected_returned

        # Verify has_more flag
        expected_has_more = len(raw_<artifact>) > 25
        assert pagination["has_more"] == expected_has_more

        print(f"   ✓ Pagination metadata is accurate")

    def test_pagination_first_page(self, spira_client, raw_<artifact>):
        """Test retrieving first page of results."""
        if len(raw_<artifact>) == 0:
            pytest.skip("No <artifact> available for pagination test")

        result = _get_my_<artifact>_impl(spira_client, limit=10, offset=0)
        parsed = json.loads(result)

        print(f"\n📄 First page test (limit=10, offset=0):")
        print(f"   Total <artifact>: {len(raw_<artifact>)}")
        print(f"   Returned: {len(parsed['data'])}")

        # Should return up to 10 items
        expected_count = min(10, len(raw_<artifact>))
        assert len(parsed["data"]) == expected_count

        # Should match first items from raw data
        if len(raw_<artifact>) > 0:
            # Replace <ArtifactId> with actual ID field name (e.g., TaskId, IncidentId)
            assert parsed["data"][0]["<Artifact>Id"] == raw_<artifact>[0]["<Artifact>Id"]
            print(f"   ✓ First <artifact> matches: <Artifact>Id={raw_<artifact>[0]['<Artifact>Id']}")

    def test_data_preservation(self, spira_client, raw_<artifact>):
        """Test that all <artifact> fields are preserved in JSON output."""
        if len(raw_<artifact>) == 0:
            pytest.skip("No <artifact> available for data preservation test")

        result = _get_my_<artifact>_impl(spira_client, limit=1, offset=0)
        parsed = json.loads(result)

        print(f"\n🔍 Data preservation test:")

        # Get first <artifact> from both sources
        json_<artifact> = parsed["data"][0]
        raw_<artifact>_item = raw_<artifact>[0]

        print(f"   Raw <artifact> keys: {len(raw_<artifact>_item.keys())}")
        print(f"   JSON <artifact> keys: {len(json_<artifact>.keys())}")

        # All fields from raw <artifact> should be in JSON <artifact>
        for key in raw_<artifact>_item.keys():
            assert key in json_<artifact>, f"Missing field: {key}"

        print(f"   ✓ All fields preserved")

        # Verify some key fields (customize based on artifact type)
        key_fields = ["<Artifact>Id", "Name", "<Artifact>StatusName"]
        for field in key_fields:
            if field in raw_<artifact>_item:
                assert json_<artifact>[field] == raw_<artifact>_item[field]
                print(f"   ✓ {field}: {json_<artifact>[field]}")

    def test_pagination_metadata_accuracy(self, spira_client, raw_<artifact>):
        """Test that pagination metadata is calculated correctly."""
        result = _get_my_<artifact>_impl(spira_client, limit=25, offset=0)
        parsed = json.loads(result)

        print(f"\n📊 Pagination metadata accuracy test:")

        pagination = parsed["pagination"]
        data = parsed["data"]

        # Verify returned_count matches actual data length
        assert pagination["returned_count"] == len(data)
        print(f"   ✓ returned_count matches data length: {len(data)}")

        # Verify total_count matches raw API data
        assert pagination["total_count"] == len(raw_<artifact>)
        print(f"   ✓ total_count matches API: {len(raw_<artifact>)}")

        # Verify has_more calculation
        expected_has_more = (pagination["offset"] + pagination["returned_count"]) < pagination[
            "total_count"
        ]
        assert pagination["has_more"] == expected_has_more
        print(f"   ✓ has_more calculated correctly: {expected_has_more}")

    def test_comparison_with_raw_api(self, spira_client, raw_<artifact>):
        """Test that JSON output matches raw API data."""
        if len(raw_<artifact>) == 0:
            pytest.skip("No <artifact> available for comparison test")

        result = _get_my_<artifact>_impl(spira_client, limit=len(raw_<artifact>), offset=0)
        parsed = json.loads(result)

        print(f"\n🔄 Comparison with raw API test:")
        print(f"   Raw API <artifact>: {len(raw_<artifact>)}")
        print(f"   JSON <artifact>: {len(parsed['data'])}")

        # Should have same number of <artifact>
        assert len(parsed["data"]) == len(raw_<artifact>)

        # <Artifact> IDs should match in order
        for i, (json_item, raw_item) in enumerate(zip(parsed["data"], raw_<artifact>)):
            assert json_item["<Artifact>Id"] == raw_item["<Artifact>Id"], f"Mismatch at index {i}"

        print(f"   ✓ JSON output matches raw API data")


class TestGetMy<Artifact>Performance:
    """Performance tests for get_my_<artifact>."""

    @pytest.fixture(scope="class")
    def spira_client(self):
        """Get a real Spira client."""
        return get_spira_client()

    @pytest.mark.slow
    def test_performance_with_large_limit(self, spira_client):
        """Test performance with large limit (500)."""
        import time

        print(f"\n⚡ Performance test (limit=500):")

        start_time = time.time()
        result = _get_my_<artifact>_impl(spira_client, limit=500, offset=0)
        elapsed_time = time.time() - start_time

        parsed = json.loads(result)

        print(f"   Elapsed time: {elapsed_time:.2f}s")
        print(f"   <Artifact> returned: {len(parsed['data'])}")
        print(f"   Total <artifact>: {parsed['pagination']['total_count']}")

        # Should complete in reasonable time (< 10 seconds)
        assert elapsed_time < 10.0, f"Too slow: {elapsed_time:.2f}s"
        print(f"   ✓ Performance acceptable")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SPIRA MCP SERVER - JSON GET_MY_<ARTIFACT> INTEGRATION TESTS")
    print("=" * 70)
    print("\nThese tests verify the NEW JSON-based implementation")
    print("against a real Spira instance.\n")
    print("Prerequisites:")
    print("  1. .env file with valid credentials")
    print("  2. Spira instance with test data")
    print("\nRun with: pytest tests/integration/test_my<artifact>_json.py -v -s")
    print("=" * 70 + "\n")
```

## Customization Guide

When creating a new integration test file, replace the following placeholders:

1. **`<artifact>`** → artifact name in lowercase (e.g., `tasks`, `incidents`, `requirements`)
2. **`<Artifact>`** → artifact name capitalized (e.g., `Tasks`, `Incidents`, `Requirements`)
3. **`<ArtifactId>`** → ID field name (e.g., `TaskId`, `IncidentId`, `RequirementId`)
4. **`<Artifact>StatusName`** → Status field name (e.g., `TaskStatusName`, `IncidentStatusName`)

### Example Replacements

For **get_my_incidents**:
- `<artifact>` → `incidents`
- `<Artifact>` → `Incidents`
- `<ArtifactId>` → `IncidentId`
- `<Artifact>StatusName` → `IncidentStatusName`

For **get_my_requirements**:
- `<artifact>` → `requirements`
- `<Artifact>` → `Requirements`
- `<ArtifactId>` → `RequirementId`
- `<Artifact>StatusName` → `RequirementStatusName`

## Test Coverage Checklist

Each integration test file should include:

- ✅ JSON validation test
- ✅ JSON structure test
- ✅ Pagination with default parameters
- ✅ First page retrieval
- ✅ Data preservation test
- ✅ Pagination metadata accuracy
- ✅ Comparison with raw API
- ✅ Performance test (marked as slow)

## Additional Tests (Optional)

Consider adding these tests if the artifact has specific characteristics:

- Second page test (if typically > 10 items)
- Last page test (if typically > 25 items)
- No silent truncation test (if typically > 25 items)
- Custom limit test
- Large limit test
- Empty results test
- Data type preservation test

## Running the Tests

```bash
# Run all integration tests for one artifact
pytest tests/integration/test_my<artifact>_json.py -v -s

# Run specific test class
pytest tests/integration/test_my<artifact>_json.py::TestGetMy<Artifact>JSONIntegration -v -s

# Run specific test
pytest tests/integration/test_my<artifact>_json.py::TestGetMy<Artifact>JSONIntegration::test_returns_valid_json -v -s

# Skip slow tests
pytest tests/integration/test_my<artifact>_json.py -v -s -m "not slow"
```

## Notes

- Integration tests automatically load `.env` file via `conftest.py`
- Tests are skipped if credentials are not available
- Tests adapt to available data (skip if not enough items)
- Use `-s` flag to see detailed output
- Mark slow tests with `@pytest.mark.slow`
