"""
Integration tests for the current MCP server against a real Spira instance.

These tests require:
1. A .env file with valid Spira credentials
2. A Spira instance with test data

Run with: pytest tests/integration/test_current_server.py -v
Run only integration tests: pytest -m integration
Skip integration tests: pytest -m "not integration"
"""

import json
import os

import pytest

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.mywork.tools.myincidents import _get_my_incidents_impl
from mcp_server_spira.features.mywork.tools.mytasks import _get_my_tasks_impl
from mcp_server_spira.features.workspaces.tools.products import _get_products_impl

# Mark all tests in this module as integration tests
# Skip all tests if credentials are not available
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.environ.get("INFLECTRA_SPIRA_BASE_URL"),
        reason="Requires Spira credentials (set in .env file)",
    ),
]


class TestCurrentServerIntegration:
    """Integration tests for current server implementation."""

    @pytest.fixture(scope="class")
    def spira_client(self):
        """Get a real Spira client."""
        return get_spira_client()

    def test_connection_to_spira(self, spira_client):
        """Test that we can connect to Spira."""
        # Try to get products - this will fail if connection is bad
        try:
            products = spira_client.make_spira_api_get_request("projects")
            assert products is not None
            print("\n✅ Connected to Spira successfully")
            print(f"   Found {len(products)} products")
        except Exception as e:
            pytest.fail(f"Failed to connect to Spira: {e}")

    def test_get_my_tasks_current(self, spira_client):
        """Test current get_my_tasks implementation."""
        result = _get_my_tasks_impl(spira_client, limit=25, offset=0)

        print("\n📋 get_my_tasks result:")
        print(f"   Type: {type(result)}")
        print(f"   Length: {len(result)} characters")

        # Current implementation returns JSON string
        assert isinstance(result, str)

        # Try to parse as JSON
        try:
            data = json.loads(result)
            print("   Format: JSON ✓")

            # Check structure
            if "data" in data:
                print(f"   Tasks count: {len(data['data'])}")
                if data["data"]:
                    print(f"   First task ID: {data['data'][0].get('TaskId', 'N/A')}")
            elif "error" in data:
                print(f"   Error: {data['error']}")
            else:
                print(f"   Keys: {list(data.keys())}")
        except json.JSONDecodeError:
            pytest.fail(f"Expected JSON but got: {result[:200]}...")

    def test_get_my_incidents_current(self, spira_client):
        """Test current get_my_incidents implementation."""
        result = _get_my_incidents_impl(spira_client, limit=25, offset=0)

        print("\n🐛 get_my_incidents result:")
        print(f"   Type: {type(result)}")
        print(f"   Length: {len(result)} characters")

        # Current implementation returns JSON string
        assert isinstance(result, str)

        # Try to parse as JSON
        try:
            data = json.loads(result)
            print("   Format: JSON ✓")

            # Check structure
            if "data" in data:
                print(f"   Incidents count: {len(data['data'])}")
                if data["data"]:
                    print(f"   First incident ID: {data['data'][0].get('IncidentId', 'N/A')}")
            elif "error" in data:
                print(f"   Error: {data['error']}")
            else:
                print(f"   Keys: {list(data.keys())}")
        except json.JSONDecodeError:
            pytest.fail(f"Expected JSON but got: {result[:200]}...")

    def test_get_products_current(self, spira_client):
        """Test current get_products implementation."""
        result = _get_products_impl(spira_client)

        print("\n🏢 get_products result:")
        print(f"   Type: {type(result)}")
        print(f"   Length: {len(result)} characters")

        # Current implementation returns markdown string
        assert isinstance(result, str)

        # Should have some content
        assert len(result) > 0

        # Check format
        if "##" in result or "**" in result:
            print("   Format: Markdown ✓")
            print(f"   First 200 chars: {result[:200]}...")
        else:
            print("   Format: Plain text")
            print(f"   Content: {result[:200]}...")

    @pytest.mark.slow
    def test_truncation_behavior(self, spira_client):
        """Test that current implementation truncates at 25 items."""
        # Get raw tasks from API
        tasks = spira_client.make_spira_api_get_request("tasks")

        print("\n✂️  Truncation test:")
        print(f"   Total tasks from API: {len(tasks)}")

        # Get formatted result
        result = _get_my_tasks_impl(spira_client, limit=25, offset=0)

        if "The current user does not have any tasks" not in result:
            # Count how many task entries are in the result
            task_count = result.count("[TK:")
            print(f"   Tasks in formatted result: {task_count}")

            if len(tasks) > 25:
                assert task_count <= 25, f"Expected truncation at 25, but got {task_count} tasks"
                print(f"   ⚠️  Truncation confirmed: {len(tasks)} tasks → {task_count} shown")
            else:
                print("   ℹ️  Not enough tasks to test truncation (need > 25)")
        else:
            print("   ℹ️  No tasks to test truncation")

    def test_no_pagination_parameters(self, spira_client):
        """Test that new implementation has pagination parameters."""
        import inspect

        # Check function signature
        sig = inspect.signature(_get_my_tasks_impl)
        params = list(sig.parameters.keys())

        print("\n📄 Pagination parameters test:")
        print(f"   Current parameters: {params}")

        # Should have spira_client, limit, and offset parameters
        assert params == [
            "spira_client",
            "limit",
            "offset",
        ], f"Expected pagination parameters, got {params}"
        print("   ✓ Has pagination parameters (limit and offset)")

    def test_error_handling_current(self, spira_client):
        """Test current error handling."""
        # This should handle errors gracefully
        result = _get_my_tasks_impl(spira_client, limit=25, offset=0)

        print("\n⚠️  Error handling test:")

        # Should always return a string, never raise exception
        assert isinstance(result, str)

        if "problem" in result.lower() or "error" in result.lower():
            print(f"   Error message format: {result[:100]}...")
        else:
            print("   ✓ No errors encountered")


class TestCurrentServerDataStructure:
    """Test the data structure returned by current implementation."""

    @pytest.fixture(scope="class")
    def spira_client(self):
        """Get a real Spira client."""
        return get_spira_client()

    def test_raw_api_response_structure(self, spira_client):
        """Test the structure of raw API responses."""
        tasks = spira_client.make_spira_api_get_request("tasks")

        print("\n🔍 Raw API response structure:")
        print(f"   Type: {type(tasks)}")
        print(f"   Count: {len(tasks)}")

        if tasks:
            task = tasks[0]
            print(f"   Sample task keys: {list(task.keys())[:10]}...")
            print(f"   Sample task: {json.dumps(task, indent=2, default=str)[:500]}...")

            # Verify it's JSON-serializable
            json_str = json.dumps(tasks, default=str)
            assert json_str is not None
            print("   ✓ Data is JSON-serializable")
        else:
            print("   ℹ️  No tasks to examine")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SPIRA MCP SERVER - INTEGRATION TESTS")
    print("=" * 70)
    print("\nThese tests verify the CURRENT server implementation")
    print("against a real Spira instance.\n")
    print("Prerequisites:")
    print("  1. .env file with valid credentials")
    print("  2. Spira instance with test data")
    print("\nRun with: pytest tests/integration/test_current_server.py -v -s")
    print("=" * 70 + "\n")
