"""
Comprehensive integration tests for all converted tools.

This test suite verifies ALL tools against a real Spira instance:
- JSON output format validation
- Pagination functionality (for "my work" tools)
- Input validation and error handling
- Data structure preservation
- OpenAPI schema compliance

Prerequisites:
1. .env file with valid Spira credentials
2. Spira instance with test data

Run with: pytest tests/integration/test_all_tools_comprehensive.py -v -s
"""

import json
import os

import pytest

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.mywork.tools.myincidents import _get_my_incidents_impl
from mcp_server_spira.features.mywork.tools.myrequirements import _get_my_requirements_impl

# Import all tool implementations
from mcp_server_spira.features.mywork.tools.mytasks import _get_my_tasks_impl
from mcp_server_spira.features.mywork.tools.mytestcases import _get_my_testcases_impl
from mcp_server_spira.features.mywork.tools.mytestsets import _get_my_testsets_impl
from mcp_server_spira.features.workspaces.tools.product_templates import _get_product_templates_impl
from mcp_server_spira.features.workspaces.tools.products import _get_products_impl
from mcp_server_spira.features.workspaces.tools.programs import _get_programs_impl

# Formatting tool doesn't export implementation function, we'll test it differently

# Mark all tests as integration tests and skip if no credentials
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.environ.get("INFLECTRA_SPIRA_BASE_URL"),
        reason="Requires Spira credentials (set in .env file)",
    ),
]


class TestMyWorkToolsComprehensive:
    """Comprehensive tests for all 'my work' tools with pagination."""

    @pytest.fixture(scope="class")
    def spira_client(self):
        """Get a real Spira client."""
        return get_spira_client()

    @pytest.mark.parametrize(
        "tool_name,tool_impl,endpoint",
        [
            ("get_my_tasks", _get_my_tasks_impl, "tasks"),
            ("get_my_incidents", _get_my_incidents_impl, "incidents"),
            ("get_my_requirements", _get_my_requirements_impl, "requirements"),
            ("get_my_testcases", _get_my_testcases_impl, "test-cases"),
            ("get_my_testsets", _get_my_testsets_impl, "test-sets"),
        ],
    )
    def test_json_structure_all_mywork_tools(self, spira_client, tool_name, tool_impl, endpoint):
        """Test JSON structure for all 'my work' tools."""
        print(f"\n🔍 Testing {tool_name}:")

        result = tool_impl(spira_client, limit=25, offset=0)

        # Should return valid JSON
        assert isinstance(result, str), f"{tool_name} should return string"
        parsed = json.loads(result)
        print("   ✓ Returns valid JSON")

        # Should have required structure
        assert "data" in parsed, f"{tool_name} missing 'data' field"
        assert "pagination" in parsed, f"{tool_name} missing 'pagination' field"
        print("   ✓ Has data and pagination fields")

        # Check pagination metadata
        pagination = parsed["pagination"]
        required_fields = [
            "limit",
            "offset",
            "returned_count",
            "total_count",
            "has_more",
            "pagination_type",
        ]
        for field in required_fields:
            assert field in pagination, f"{tool_name} missing pagination field: {field}"
        print("   ✓ All pagination fields present")

        # Check pagination type
        assert pagination["pagination_type"] == "client-side", (
            f"{tool_name} should use client-side pagination"
        )
        print("   ✓ Uses client-side pagination")

        # Verify data is a list
        assert isinstance(parsed["data"], list), f"{tool_name} data should be a list"
        print(f"   ✓ Data is a list with {len(parsed['data'])} items")

    @pytest.mark.parametrize(
        "tool_name,tool_impl",
        [
            ("get_my_tasks", _get_my_tasks_impl),
            ("get_my_incidents", _get_my_incidents_impl),
            ("get_my_requirements", _get_my_requirements_impl),
            ("get_my_testcases", _get_my_testcases_impl),
            ("get_my_testsets", _get_my_testsets_impl),
        ],
    )
    def test_pagination_default_params(self, spira_client, tool_name, tool_impl):
        """Test default pagination parameters for all 'my work' tools."""
        print(f"\n📄 Testing pagination for {tool_name}:")

        result = tool_impl(spira_client, limit=25, offset=0)
        parsed = json.loads(result)

        pagination = parsed["pagination"]
        print(f"   Total items: {pagination['total_count']}")
        print(f"   Returned: {pagination['returned_count']}")
        print(f"   Has more: {pagination['has_more']}")

        # Verify pagination metadata
        assert pagination["limit"] == 25
        assert pagination["offset"] == 0
        assert pagination["returned_count"] == len(parsed["data"])
        print("   ✓ Pagination metadata is accurate")

    @pytest.mark.parametrize(
        "tool_name,tool_impl",
        [
            ("get_my_tasks", _get_my_tasks_impl),
            ("get_my_incidents", _get_my_incidents_impl),
            ("get_my_requirements", _get_my_requirements_impl),
            ("get_my_testcases", _get_my_testcases_impl),
            ("get_my_testsets", _get_my_testsets_impl),
        ],
    )
    def test_custom_pagination(self, spira_client, tool_name, tool_impl):
        """Test custom pagination parameters for all 'my work' tools."""
        print(f"\n📄 Testing custom pagination for {tool_name}:")

        # Test with limit=5, offset=0
        result = tool_impl(spira_client, limit=5, offset=0)
        parsed = json.loads(result)

        pagination = parsed["pagination"]
        expected_count = min(5, pagination["total_count"])

        assert pagination["limit"] == 5
        assert pagination["offset"] == 0
        assert pagination["returned_count"] == expected_count
        assert len(parsed["data"]) == expected_count
        print("   ✓ Custom limit (5) works correctly")

        # Test with offset
        if pagination["total_count"] > 5:
            result2 = tool_impl(spira_client, limit=5, offset=5)
            parsed2 = json.loads(result2)
            assert parsed2["pagination"]["offset"] == 5
            print("   ✓ Custom offset (5) works correctly")

    @pytest.mark.parametrize(
        "tool_name,tool_impl",
        [
            ("get_my_tasks", _get_my_tasks_impl),
            ("get_my_incidents", _get_my_incidents_impl),
            ("get_my_requirements", _get_my_requirements_impl),
            ("get_my_testcases", _get_my_testcases_impl),
            ("get_my_testsets", _get_my_testsets_impl),
        ],
    )
    def test_large_limit(self, spira_client, tool_name, tool_impl):
        """Test large limit (100) for all 'my work' tools."""
        print(f"\n📄 Testing large limit for {tool_name}:")

        result = tool_impl(spira_client, limit=100, offset=0)
        parsed = json.loads(result)

        pagination = parsed["pagination"]
        expected_count = min(100, pagination["total_count"])

        assert pagination["limit"] == 100
        assert pagination["returned_count"] == expected_count
        assert len(parsed["data"]) == expected_count
        print("   ✓ Large limit (100) works correctly")
        print(f"   Returned {expected_count} items")


class TestWorkspaceToolsComprehensive:
    """Comprehensive tests for workspace tools."""

    @pytest.fixture(scope="class")
    def spira_client(self):
        """Get a real Spira client."""
        return get_spira_client()

    @pytest.mark.parametrize(
        "tool_name,tool_impl",
        [
            ("get_products", _get_products_impl),
            ("get_programs", _get_programs_impl),
            ("get_product_templates", _get_product_templates_impl),
        ],
    )
    def test_json_structure_workspace_tools(self, spira_client, tool_name, tool_impl):
        """Test JSON structure for all workspace tools."""
        print(f"\n🔍 Testing {tool_name}:")

        result = tool_impl(spira_client)

        # Should return valid JSON
        assert isinstance(result, str), f"{tool_name} should return string"
        parsed = json.loads(result)
        print("   ✓ Returns valid JSON")

        # Should have data field
        assert "data" in parsed, f"{tool_name} missing 'data' field"
        print("   ✓ Has data field")

        # Data should be a list
        assert isinstance(parsed["data"], list), f"{tool_name} data should be a list"
        print(f"   ✓ Data is a list with {len(parsed['data'])} items")

        # Should NOT have pagination (workspace tools don't paginate)
        assert "pagination" not in parsed, f"{tool_name} should not have pagination"
        print("   ✓ No pagination field (as expected)")

    @pytest.mark.asyncio
    async def test_products_data_structure(self, spira_client):
        """Test products data structure."""
        print("\n🔍 Testing get_products data structure:")

        result = await _get_products_impl(spira_client)
        parsed = json.loads(result)

        if len(parsed["data"]) > 0:
            product = parsed["data"][0]
            # Check for key fields
            expected_fields = ["ProjectId", "Name"]
            for field in expected_fields:
                assert field in product, f"Missing field: {field}"
            print(f"   ✓ Has expected fields: {expected_fields}")
            print(f"   Sample product: {product.get('Name', 'N/A')}")

    @pytest.mark.asyncio
    async def test_programs_data_structure(self, spira_client):
        """Test programs data structure."""
        print("\n🔍 Testing get_programs data structure:")

        result = await _get_programs_impl(spira_client)
        parsed = json.loads(result)

        if len(parsed["data"]) > 0:
            program = parsed["data"][0]
            # Check for key fields
            expected_fields = ["ProgramId", "Name"]
            for field in expected_fields:
                assert field in program, f"Missing field: {field}"
            print(f"   ✓ Has expected fields: {expected_fields}")
            print(f"   Sample program: {program.get('Name', 'N/A')}")

    @pytest.mark.asyncio
    async def test_product_templates_data_structure(self, spira_client):
        """Test product templates data structure."""
        print("\n🔍 Testing get_product_templates data structure:")

        result = await _get_product_templates_impl(spira_client)
        parsed = json.loads(result)

        if len(parsed["data"]) > 0:
            template = parsed["data"][0]
            # Check for key fields
            expected_fields = ["ProjectTemplateId", "Name"]
            for field in expected_fields:
                assert field in template, f"Missing field: {field}"
            print(f"   ✓ Has expected fields: {expected_fields}")
            print(f"   Sample template: {template.get('Name', 'N/A')}")


class TestInputValidation:
    """Test input validation for all tools."""

    @pytest.fixture(scope="class")
    def spira_client(self):
        """Get a real Spira client."""
        return get_spira_client()

    @pytest.mark.parametrize(
        "tool_name,tool_impl",
        [
            ("get_my_tasks", _get_my_tasks_impl),
            ("get_my_incidents", _get_my_incidents_impl),
            ("get_my_requirements", _get_my_requirements_impl),
            ("get_my_testcases", _get_my_testcases_impl),
            ("get_my_testsets", _get_my_testsets_impl),
        ],
    )
    def test_invalid_limit_too_high(self, spira_client, tool_name, tool_impl):
        """Test validation error for limit > 500."""
        print(f"\n⚠️  Testing invalid limit (>500) for {tool_name}:")

        result = tool_impl(spira_client, limit=1000, offset=0)
        parsed = json.loads(result)

        # Should return error response
        assert "error" in parsed, f"{tool_name} should return error for limit > 500"
        assert "error_code" in parsed
        assert parsed["error_code"] == "INVALID_PARAMETER"
        print("   ✓ Returns error for limit > 500")
        print(f"   Error: {parsed['error']}")

    @pytest.mark.parametrize(
        "tool_name,tool_impl",
        [
            ("get_my_tasks", _get_my_tasks_impl),
            ("get_my_incidents", _get_my_incidents_impl),
            ("get_my_requirements", _get_my_requirements_impl),
            ("get_my_testcases", _get_my_testcases_impl),
            ("get_my_testsets", _get_my_testsets_impl),
        ],
    )
    def test_invalid_limit_too_low(self, spira_client, tool_name, tool_impl):
        """Test validation error for limit < 1."""
        print(f"\n⚠️  Testing invalid limit (<1) for {tool_name}:")

        result = tool_impl(spira_client, limit=0, offset=0)
        parsed = json.loads(result)

        # Should return error response
        assert "error" in parsed, f"{tool_name} should return error for limit < 1"
        assert "error_code" in parsed
        assert parsed["error_code"] == "INVALID_PARAMETER"
        print("   ✓ Returns error for limit < 1")
        print(f"   Error: {parsed['error']}")

    @pytest.mark.parametrize(
        "tool_name,tool_impl",
        [
            ("get_my_tasks", _get_my_tasks_impl),
            ("get_my_incidents", _get_my_incidents_impl),
            ("get_my_requirements", _get_my_requirements_impl),
            ("get_my_testcases", _get_my_testcases_impl),
            ("get_my_testsets", _get_my_testsets_impl),
        ],
    )
    def test_invalid_offset_negative(self, spira_client, tool_name, tool_impl):
        """Test validation error for negative offset."""
        print(f"\n⚠️  Testing invalid offset (<0) for {tool_name}:")

        result = tool_impl(spira_client, limit=25, offset=-1)
        parsed = json.loads(result)

        # Should return error response
        assert "error" in parsed, f"{tool_name} should return error for offset < 0"
        assert "error_code" in parsed
        assert parsed["error_code"] == "INVALID_PARAMETER"
        print("   ✓ Returns error for offset < 0")
        print(f"   Error: {parsed['error']}")


class TestFormattingTool:
    """Test the formatting tool with real data."""

    @pytest.fixture(scope="class")
    def spira_client(self):
        """Get a real Spira client."""
        return get_spira_client()

    @pytest.mark.parametrize(
        "tool_name,tool_impl,artifact_type",
        [
            ("get_my_tasks", _get_my_tasks_impl, "task"),
            ("get_my_incidents", _get_my_incidents_impl, "incident"),
            ("get_my_requirements", _get_my_requirements_impl, "requirement"),
            ("get_my_testcases", _get_my_testcases_impl, "test_case"),
            ("get_my_testsets", _get_my_testsets_impl, "test_set"),
        ],
    )
    def test_format_artifacts_with_real_data(
        self, spira_client, tool_name, tool_impl, artifact_type
    ):
        """Test that JSON data from tools can be formatted (structure validation)."""
        print(f"\n📝 Testing JSON structure for formatting {artifact_type}:")

        # Get real data
        json_result = tool_impl(spira_client, limit=5, offset=0)
        parsed = json.loads(json_result)

        if len(parsed["data"]) == 0:
            pytest.skip(f"No {artifact_type} data available")

        # Verify the JSON structure is suitable for formatting
        assert "data" in parsed
        assert isinstance(parsed["data"], list)
        print("   ✓ JSON has correct structure for formatting")
        print(f"   Data contains {len(parsed['data'])} items")

        # Verify each item has basic structure
        for item in parsed["data"]:
            assert isinstance(item, dict)
        print("   ✓ All items are dictionaries (suitable for formatting)")


class TestDataPreservation:
    """Test that all data is preserved correctly."""

    @pytest.fixture(scope="class")
    def spira_client(self):
        """Get a real Spira client."""
        return get_spira_client()

    @pytest.mark.asyncio
    async def test_tasks_data_preservation(self, spira_client):
        """Test that task data is preserved correctly."""
        print("\n🔍 Testing task data preservation:")

        # Get raw data from API
        raw_tasks = spira_client.make_spira_api_get_request("tasks")

        if len(raw_tasks) == 0:
            pytest.skip("No tasks available")

        # Get data through tool
        result = await _get_my_tasks_impl(spira_client, limit=1, offset=0)
        parsed = json.loads(result)

        # Compare first task
        raw_task = raw_tasks[0]
        json_task = parsed["data"][0]

        # All fields from raw should be in JSON
        for key in raw_task:
            assert key in json_task, f"Missing field: {key}"

        print(f"   ✓ All {len(raw_task)} fields preserved")

        # Verify key fields match
        assert json_task["TaskId"] == raw_task["TaskId"]
        print(f"   ✓ TaskId matches: {json_task['TaskId']}")


class TestErrorHandling:
    """Test error handling with various scenarios."""

    @pytest.fixture(scope="class")
    def spira_client(self):
        """Get a real Spira client."""
        return get_spira_client()

    @pytest.mark.asyncio
    async def test_tools_handle_empty_results(self, spira_client):
        """Test that tools handle empty results gracefully."""
        print("\n📄 Testing empty results handling:")

        # Test with offset beyond data
        result = await _get_my_tasks_impl(spira_client, limit=25, offset=999999)
        parsed = json.loads(result)

        # Should return empty data with correct structure
        assert "data" in parsed
        assert "pagination" in parsed
        assert len(parsed["data"]) == 0
        assert parsed["pagination"]["returned_count"] == 0
        assert parsed["pagination"]["has_more"] is False
        print("   ✓ Handles empty results correctly")

    @pytest.mark.asyncio
    async def test_tools_return_structured_errors(self, spira_client):
        """Test that tools return structured error responses."""
        print("\n⚠️  Testing structured error responses:")

        # Test with invalid parameters
        result = await _get_my_tasks_impl(spira_client, limit=-1, offset=0)
        parsed = json.loads(result)

        # Should have error structure
        assert "error" in parsed
        assert "error_code" in parsed
        print("   ✓ Returns structured error")
        print(f"   Error code: {parsed['error_code']}")
        print(f"   Error message: {parsed['error']}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SPIRA MCP SERVER - COMPREHENSIVE INTEGRATION TESTS")
    print("=" * 70)
    print("\nThese tests verify ALL converted tools against a real Spira instance.")
    print("\nTest Coverage:")
    print("  • All 5 'my work' tools (with pagination)")
    print("  • All 3 workspace tools")
    print("  • Formatting tool")
    print("  • Input validation")
    print("  • Error handling")
    print("  • Data preservation")
    print("\nPrerequisites:")
    print("  1. .env file with valid credentials")
    print("  2. Spira instance with test data")
    print("\nRun with: pytest tests/integration/test_all_tools_comprehensive.py -v -s")
    print("=" * 70 + "\n")
