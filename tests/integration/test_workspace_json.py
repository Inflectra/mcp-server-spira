"""
Integration tests for JSON-based workspace tools.

These tests verify the workspace tools against a real Spira instance:
- get_products
- get_programs
- get_product_templates

Tests verify:
- JSON output format
- Data structure preservation
- Error handling
- Field completeness

Prerequisites:
1. .env file with valid Spira credentials
2. Spira instance with test data

Run with: pytest tests/integration/test_workspace_json.py -v -s
"""

import json
import os

import pytest

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.workspaces.tools.product_templates import (
    _get_product_templates_impl,
)
from mcp_server_spira.features.workspaces.tools.products import (
    _get_products_impl,
)
from mcp_server_spira.features.workspaces.tools.programs import (
    _get_programs_impl,
)

# Mark all tests as integration tests and skip if no credentials
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.environ.get("INFLECTRA_SPIRA_BASE_URL"),
        reason="Requires Spira credentials (set in .env file)",
    ),
]


class TestGetProductsIntegration:
    """Integration tests for get_products implementation."""

    @pytest.fixture(scope="class")
    def spira_client(self):
        """Get a real Spira client."""
        return get_spira_client()

    @pytest.fixture(scope="class")
    def raw_products(self, spira_client):
        """Get raw products from API for comparison."""
        return spira_client.make_spira_api_get_request("projects")

    def test_returns_valid_json(self, spira_client):
        """Test that implementation returns valid JSON."""
        result = _get_products_impl(spira_client)

        print("\n📋 JSON validation test (products):")
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
        print("   ✓ Has required structure (data)")

    def test_json_structure(self, spira_client):
        """Test the structure of JSON response."""
        result = _get_products_impl(spira_client)
        parsed = json.loads(result)

        print("\n🔍 JSON structure test (products):")

        # Check data field
        assert "data" in parsed
        assert isinstance(parsed["data"], list)
        print("   ✓ data field is a list")

        # Should not have pagination (workspace tools don't paginate)
        assert "pagination" not in parsed
        print("   ✓ No pagination field (workspace tool)")

    def test_data_preservation(self, spira_client, raw_products):
        """Test that all product fields are preserved in JSON output."""
        if len(raw_products) == 0:
            pytest.skip("No products available for data preservation test")

        result = _get_products_impl(spira_client)
        parsed = json.loads(result)

        print("\n🔍 Data preservation test (products):")

        # Get first product from both sources
        json_product = parsed["data"][0]
        raw_product = raw_products[0]

        print(f"   Raw product keys: {len(raw_product.keys())}")
        print(f"   JSON product keys: {len(json_product.keys())}")

        # All fields from raw product should be in JSON product
        for key in raw_product:
            assert key in json_product, f"Missing field: {key}"

        print("   ✓ All fields preserved")

        # Verify some key fields
        key_fields = ["ProjectId", "Name"]
        for field in key_fields:
            if field in raw_product:
                assert json_product[field] == raw_product[field]
                print(f"   ✓ {field}: {json_product[field]}")

    def test_no_truncation(self, spira_client, raw_products):
        """Test that all products are returned without truncation."""
        result = _get_products_impl(spira_client)
        parsed = json.loads(result)

        print("\n✂️  No truncation test (products):")
        print(f"   Raw API products: {len(raw_products)}")
        print(f"   JSON products: {len(parsed['data'])}")

        # Should return all products
        assert len(parsed["data"]) == len(raw_products)
        print("   ✓ All products returned (no truncation)")

    def test_comparison_with_raw_api(self, spira_client, raw_products):
        """Test that JSON output matches raw API data."""
        if len(raw_products) == 0:
            pytest.skip("No products available for comparison test")

        result = _get_products_impl(spira_client)
        parsed = json.loads(result)

        print("\n🔄 Comparison with raw API test (products):")
        print(f"   Raw API products: {len(raw_products)}")
        print(f"   JSON products: {len(parsed['data'])}")

        # Should have same number of products
        assert len(parsed["data"]) == len(raw_products)

        # Product IDs should match
        json_ids = {p["ProjectId"] for p in parsed["data"]}
        raw_ids = {p["ProjectId"] for p in raw_products}
        assert json_ids == raw_ids

        print("   ✓ JSON output matches raw API data")

    def test_json_formatting(self, spira_client):
        """Test that JSON is properly formatted."""
        result = _get_products_impl(spira_client)

        print("\n📝 JSON formatting test (products):")

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
        result = _get_products_impl(spira_client)

        print("\n⚠️  Error handling test (products):")

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


class TestGetProgramsIntegration:
    """Integration tests for get_programs implementation."""

    @pytest.fixture(scope="class")
    def spira_client(self):
        """Get a real Spira client."""
        return get_spira_client()

    @pytest.fixture(scope="class")
    def raw_programs(self, spira_client):
        """Get raw programs from API for comparison."""
        return spira_client.make_spira_api_get_request("programs")

    def test_returns_valid_json(self, spira_client):
        """Test that implementation returns valid JSON."""
        result = _get_programs_impl(spira_client)

        print("\n📋 JSON validation test (programs):")
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
        print("   ✓ Has required structure (data)")

    def test_json_structure(self, spira_client):
        """Test the structure of JSON response."""
        result = _get_programs_impl(spira_client)
        parsed = json.loads(result)

        print("\n🔍 JSON structure test (programs):")

        # Check data field
        assert "data" in parsed
        assert isinstance(parsed["data"], list)
        print("   ✓ data field is a list")

        # Should not have pagination (workspace tools don't paginate)
        assert "pagination" not in parsed
        print("   ✓ No pagination field (workspace tool)")

    def test_data_preservation(self, spira_client, raw_programs):
        """Test that all program fields are preserved in JSON output."""
        if len(raw_programs) == 0:
            pytest.skip("No programs available for data preservation test")

        result = _get_programs_impl(spira_client)
        parsed = json.loads(result)

        print("\n🔍 Data preservation test (programs):")

        # Get first program from both sources
        json_program = parsed["data"][0]
        raw_program = raw_programs[0]

        print(f"   Raw program keys: {len(raw_program.keys())}")
        print(f"   JSON program keys: {len(json_program.keys())}")

        # All fields from raw program should be in JSON program
        for key in raw_program:
            assert key in json_program, f"Missing field: {key}"

        print("   ✓ All fields preserved")

        # Verify some key fields
        key_fields = ["ProgramId", "Name"]
        for field in key_fields:
            if field in raw_program:
                assert json_program[field] == raw_program[field]
                print(f"   ✓ {field}: {json_program[field]}")

    def test_no_truncation(self, spira_client, raw_programs):
        """Test that all programs are returned without truncation."""
        result = _get_programs_impl(spira_client)
        parsed = json.loads(result)

        print("\n✂️  No truncation test (programs):")
        print(f"   Raw API programs: {len(raw_programs)}")
        print(f"   JSON programs: {len(parsed['data'])}")

        # Should return all programs
        assert len(parsed["data"]) == len(raw_programs)
        print("   ✓ All programs returned (no truncation)")

    def test_comparison_with_raw_api(self, spira_client, raw_programs):
        """Test that JSON output matches raw API data."""
        if len(raw_programs) == 0:
            pytest.skip("No programs available for comparison test")

        result = _get_programs_impl(spira_client)
        parsed = json.loads(result)

        print("\n🔄 Comparison with raw API test (programs):")
        print(f"   Raw API programs: {len(raw_programs)}")
        print(f"   JSON programs: {len(parsed['data'])}")

        # Should have same number of programs
        assert len(parsed["data"]) == len(raw_programs)

        # Program IDs should match
        json_ids = {p["ProgramId"] for p in parsed["data"]}
        raw_ids = {p["ProgramId"] for p in raw_programs}
        assert json_ids == raw_ids

        print("   ✓ JSON output matches raw API data")

    def test_json_formatting(self, spira_client):
        """Test that JSON is properly formatted."""
        result = _get_programs_impl(spira_client)

        print("\n📝 JSON formatting test (programs):")

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
        result = _get_programs_impl(spira_client)

        print("\n⚠️  Error handling test (programs):")

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


class TestGetProductTemplatesIntegration:
    """Integration tests for get_product_templates implementation."""

    @pytest.fixture(scope="class")
    def spira_client(self):
        """Get a real Spira client."""
        return get_spira_client()

    @pytest.fixture(scope="class")
    def raw_templates(self, spira_client):
        """Get raw product templates from API for comparison."""
        return spira_client.make_spira_api_get_request("project-templates")

    def test_returns_valid_json(self, spira_client):
        """Test that implementation returns valid JSON."""
        result = _get_product_templates_impl(spira_client)

        print("\n📋 JSON validation test (product templates):")
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
        print("   ✓ Has required structure (data)")

    def test_json_structure(self, spira_client):
        """Test the structure of JSON response."""
        result = _get_product_templates_impl(spira_client)
        parsed = json.loads(result)

        print("\n🔍 JSON structure test (product templates):")

        # Check data field
        assert "data" in parsed
        assert isinstance(parsed["data"], list)
        print("   ✓ data field is a list")

        # Should not have pagination (workspace tools don't paginate)
        assert "pagination" not in parsed
        print("   ✓ No pagination field (workspace tool)")

    def test_data_preservation(self, spira_client, raw_templates):
        """Test that all template fields are preserved in JSON output."""
        if len(raw_templates) == 0:
            pytest.skip("No product templates available for data preservation test")

        result = _get_product_templates_impl(spira_client)
        parsed = json.loads(result)

        print("\n🔍 Data preservation test (product templates):")

        # Get first template from both sources
        json_template = parsed["data"][0]
        raw_template = raw_templates[0]

        print(f"   Raw template keys: {len(raw_template.keys())}")
        print(f"   JSON template keys: {len(json_template.keys())}")

        # All fields from raw template should be in JSON template
        for key in raw_template:
            assert key in json_template, f"Missing field: {key}"

        print("   ✓ All fields preserved")

        # Verify some key fields
        key_fields = ["ProjectTemplateId", "Name"]
        for field in key_fields:
            if field in raw_template:
                assert json_template[field] == raw_template[field]
                print(f"   ✓ {field}: {json_template[field]}")

    def test_no_truncation(self, spira_client, raw_templates):
        """Test that all templates are returned without truncation."""
        result = _get_product_templates_impl(spira_client)
        parsed = json.loads(result)

        print("\n✂️  No truncation test (product templates):")
        print(f"   Raw API templates: {len(raw_templates)}")
        print(f"   JSON templates: {len(parsed['data'])}")

        # Should return all templates
        assert len(parsed["data"]) == len(raw_templates)
        print("   ✓ All templates returned (no truncation)")

    def test_comparison_with_raw_api(self, spira_client, raw_templates):
        """Test that JSON output matches raw API data."""
        if len(raw_templates) == 0:
            pytest.skip("No product templates available for comparison test")

        result = _get_product_templates_impl(spira_client)
        parsed = json.loads(result)

        print("\n🔄 Comparison with raw API test (product templates):")
        print(f"   Raw API templates: {len(raw_templates)}")
        print(f"   JSON templates: {len(parsed['data'])}")

        # Should have same number of templates
        assert len(parsed["data"]) == len(raw_templates)

        # Template IDs should match
        json_ids = {t["ProjectTemplateId"] for t in parsed["data"]}
        raw_ids = {t["ProjectTemplateId"] for t in raw_templates}
        assert json_ids == raw_ids

        print("   ✓ JSON output matches raw API data")

    def test_json_formatting(self, spira_client):
        """Test that JSON is properly formatted."""
        result = _get_product_templates_impl(spira_client)

        print("\n📝 JSON formatting test (product templates):")

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
        result = _get_product_templates_impl(spira_client)

        print("\n⚠️  Error handling test (product templates):")

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


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SPIRA MCP SERVER - WORKSPACE TOOLS INTEGRATION TESTS")
    print("=" * 70)
    print("\nThese tests verify workspace tools (products, programs,")
    print("product templates) against a real Spira instance.\n")
    print("Prerequisites:")
    print("  1. .env file with valid credentials")
    print("  2. Spira instance with test data")
    print("\nRun with: pytest tests/integration/test_workspace_json.py -v -s")
    print("=" * 70 + "\n")
