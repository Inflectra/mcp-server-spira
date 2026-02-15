"""
Tests for the Products workspace features of the Inflectra Spira MCP Server.
"""

import json
from unittest.mock import Mock, patch

import pytest

from mcp_server_spira.features.workspaces.tools.products import (
    _get_product_by_id_impl,
    _get_products_impl,
    _get_program_products_impl,
    register_tools,
)


@pytest.mark.unit
class TestGetProductsImpl:
    """Tests for _get_products_impl function."""

    def test_successful_retrieval_with_products(self):
        """Test successful product retrieval with data."""
        # Mock Spira client
        mock_client = Mock()
        mock_products = [
            {
                "ProjectId": 1,
                "Name": "Product 1",
                "Description": "Test product 1",
                "Active": True,
                "CreationDate": "2023-01-15T10:00:00Z",
                "ProjectGroupId": 10,
            },
            {
                "ProjectId": 2,
                "Name": "Product 2",
                "Description": "Test product 2",
                "Active": False,
                "CreationDate": "2023-02-20T10:00:00Z",
                "ProjectGroupId": 10,
            },
        ]
        mock_client.make_spira_api_get_request.return_value = mock_products

        # Call implementation
        result = _get_products_impl(mock_client)

        # Verify API was called correctly
        mock_client.make_spira_api_get_request.assert_called_once_with("projects")

        # Parse and verify response
        parsed = json.loads(result)
        assert "data" in parsed
        assert len(parsed["data"]) == 2
        assert parsed["data"][0]["ProjectId"] == 1
        assert parsed["data"][0]["Name"] == "Product 1"
        assert parsed["data"][0]["Active"] is True
        assert parsed["data"][1]["ProjectId"] == 2
        assert parsed["data"][1]["Name"] == "Product 2"
        assert parsed["data"][1]["Active"] is False

    def test_successful_retrieval_empty_products(self):
        """Test successful retrieval with no products."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.return_value = []

        result = _get_products_impl(mock_client)

        parsed = json.loads(result)
        assert "data" in parsed
        assert len(parsed["data"]) == 0
        assert parsed["data"] == []

    def test_api_error_handling(self):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.side_effect = Exception("Connection timeout")

        result = _get_products_impl(mock_client)

        # Verify error response structure
        parsed = json.loads(result)
        assert "error" in parsed
        assert "error_code" in parsed
        assert parsed["error"] == "Failed to retrieve products"
        assert parsed["error_code"] == "API_ERROR"
        assert "details" in parsed
        assert "message" in parsed["details"]
        assert "suggestion" in parsed

    def test_preserves_all_fields(self):
        """Test that all product fields are preserved in JSON output."""
        mock_client = Mock()
        mock_products = [
            {
                "ProjectId": 55,
                "ProjectTemplateId": 1,
                "ProjectGroupId": 10,
                "Name": "Web Application",
                "Description": "Main web application project",
                "Website": "https://example.com",
                "CreationDate": "2023-01-15T10:00:00Z",
                "Active": True,
                "WorkingHours": 8,
                "WorkingDays": 5,
                "NonWorkingHours": 0,
                "StartDate": "2023-01-01T00:00:00Z",
                "EndDate": "2024-12-31T00:00:00Z",
                "PercentComplete": 45,
                "RequirementCount": 150,
                "WorkspaceTypeId": 1,
                "Guid": "abc-123-def-456",
                "LastUpdatedDate": "2024-01-15T10:00:00Z",
                "ArtifactTypeId": 1,
                "ConcurrencyGuid": "xyz-789",
                "CustomProperties": [],
            }
        ]
        mock_client.make_spira_api_get_request.return_value = mock_products

        result = _get_products_impl(mock_client)

        parsed = json.loads(result)
        product = parsed["data"][0]

        # Verify all fields are present
        assert product["ProjectId"] == 55
        assert product["ProjectTemplateId"] == 1
        assert product["ProjectGroupId"] == 10
        assert product["Name"] == "Web Application"
        assert product["Description"] == "Main web application project"
        assert product["Website"] == "https://example.com"
        assert product["CreationDate"] == "2023-01-15T10:00:00Z"
        assert product["Active"] is True
        assert product["WorkingHours"] == 8
        assert product["WorkingDays"] == 5
        assert product["NonWorkingHours"] == 0
        assert product["StartDate"] == "2023-01-01T00:00:00Z"
        assert product["EndDate"] == "2024-12-31T00:00:00Z"
        assert product["PercentComplete"] == 45
        assert product["RequirementCount"] == 150
        assert product["WorkspaceTypeId"] == 1
        assert product["Guid"] == "abc-123-def-456"
        assert product["LastUpdatedDate"] == "2024-01-15T10:00:00Z"
        assert product["ArtifactTypeId"] == 1
        assert product["ConcurrencyGuid"] == "xyz-789"
        assert product["CustomProperties"] == []

    def test_json_formatting(self):
        """Test that JSON is properly formatted with indentation."""
        mock_client = Mock()
        mock_products = [{"ProjectId": 1, "Name": "Product 1", "Active": True}]
        mock_client.make_spira_api_get_request.return_value = mock_products

        result = _get_products_impl(mock_client)

        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed is not None

        # Verify formatting (should have newlines and indentation)
        assert "\n" in result
        assert "  " in result  # 2-space indentation


@pytest.mark.unit
class TestGetProductByIdImpl:
    """Tests for _get_product_by_id_impl function."""

    def test_successful_retrieval_valid_id(self):
        """Test successful product retrieval with valid ID."""
        mock_client = Mock()
        mock_product = {
            "ProjectId": 55,
            "Name": "Web Application",
            "Description": "Main web application project",
            "Active": True,
            "CreationDate": "2023-01-15T10:00:00Z",
            "ProjectGroupId": 10,
        }
        mock_client.make_spira_api_get_request.return_value = mock_product

        result = _get_product_by_id_impl(mock_client, 55)

        # Verify API was called correctly
        mock_client.make_spira_api_get_request.assert_called_once_with("projects/55")

        # Verify result contains product information
        assert "Web Application" in result
        assert "Main web application project" in result

    def test_product_not_found(self):
        """Test handling when product ID doesn't exist."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.return_value = None

        result = _get_product_by_id_impl(mock_client, 999)

        assert "no product with that ID" in result

    def test_api_error_handling(self):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.side_effect = Exception("Connection timeout")

        result = _get_product_by_id_impl(mock_client, 55)

        assert "problem using this tool" in result
        assert "Connection timeout" in result

    def test_various_product_ids(self):
        """Test with various product IDs."""
        mock_client = Mock()
        mock_product = {
            "ProjectId": 1,
            "Name": "Test Product",
            "Description": "Test",
            "Active": True,
        }
        mock_client.make_spira_api_get_request.return_value = mock_product

        # Test with different IDs
        for product_id in [1, 10, 100, 999]:
            result = _get_product_by_id_impl(mock_client, product_id)
            mock_client.make_spira_api_get_request.assert_called_with(f"projects/{product_id}")
            assert "Test Product" in result


@pytest.mark.unit
class TestGetProgramProductsImpl:
    """Tests for _get_program_products_impl function."""

    def test_successful_retrieval_with_matching_products(self):
        """Test successful retrieval with products matching program ID."""
        mock_client = Mock()
        mock_products = [
            {
                "ProjectId": 1,
                "Name": "Product 1",
                "Description": "Test product 1",
                "Active": True,
                "ProjectGroupId": 10,
            },
            {
                "ProjectId": 2,
                "Name": "Product 2",
                "Description": "Test product 2",
                "Active": True,
                "ProjectGroupId": 10,
            },
            {
                "ProjectId": 3,
                "Name": "Product 3",
                "Description": "Test product 3",
                "Active": True,
                "ProjectGroupId": 20,  # Different program
            },
        ]
        mock_client.make_spira_api_get_request.return_value = mock_products

        result = _get_program_products_impl(mock_client, 10)

        # Verify API was called correctly
        mock_client.make_spira_api_get_request.assert_called_once_with("projects")

        # Verify only products from program 10 are included
        assert "Product 1" in result
        assert "Product 2" in result
        assert "Product 3" not in result

    def test_no_matching_products(self):
        """Test when no products match the program ID."""
        mock_client = Mock()
        mock_products = [
            {
                "ProjectId": 1,
                "Name": "Product 1",
                "Description": "Test product 1",
                "Active": True,
                "ProjectGroupId": 10,
            },
        ]
        mock_client.make_spira_api_get_request.return_value = mock_products

        result = _get_program_products_impl(mock_client, 999)

        # Should return empty result (no products match)
        # The function returns joined formatted results, so empty list means empty string
        assert result == ""

    def test_empty_products_list(self):
        """Test when API returns no products."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.return_value = []

        result = _get_program_products_impl(mock_client, 10)

        assert "does not contain any products" in result

    def test_api_error_handling(self):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_client.make_spira_api_get_request.side_effect = Exception("Connection timeout")

        result = _get_program_products_impl(mock_client, 10)

        assert "problem using this tool" in result
        assert "Connection timeout" in result

    def test_multiple_programs_filtering(self):
        """Test that filtering correctly handles multiple programs."""
        mock_client = Mock()
        mock_products = [
            {
                "ProjectId": 1,
                "Name": "P1",
                "Description": "D1",
                "Active": True,
                "ProjectGroupId": 5,
            },
            {
                "ProjectId": 2,
                "Name": "P2",
                "Description": "D2",
                "Active": True,
                "ProjectGroupId": 10,
            },
            {
                "ProjectId": 3,
                "Name": "P3",
                "Description": "D3",
                "Active": True,
                "ProjectGroupId": 5,
            },
            {
                "ProjectId": 4,
                "Name": "P4",
                "Description": "D4",
                "Active": True,
                "ProjectGroupId": 15,
            },
        ]
        mock_client.make_spira_api_get_request.return_value = mock_products

        result = _get_program_products_impl(mock_client, 5)

        # Should only include products from program 5
        assert "P1" in result
        assert "P3" in result
        assert "P2" not in result
        assert "P4" not in result


@pytest.mark.unit
class TestRegisterTools:
    """Tests for tool registration and MCP tool wrappers."""

    def test_register_tools_creates_tools(self):
        """Test that register_tools creates the expected tools."""
        mock_mcp = Mock()

        # Call register_tools
        register_tools(mock_mcp)

        # Verify that mcp.tool() was called (decorator pattern)
        assert mock_mcp.tool.called

    def test_get_products_mcp_wrapper_calls_implementation(self):
        """Test that get_products MCP wrapper properly calls implementation."""
        with patch(
            "mcp_server_spira.features.workspaces.tools.products.get_spira_client"
        ) as mock_get_client:
            mock_client = Mock()
            mock_products = [{"ProjectId": 1, "Name": "Product 1", "Active": True}]
            mock_client.make_spira_api_get_request.return_value = mock_products
            mock_get_client.return_value = mock_client

            # Create a real MCP-like object that stores the decorated function
            class MockMCP:
                def __init__(self):
                    self.tools = []

                def tool(self):
                    def decorator(func):
                        self.tools.append(func)
                        return func

                    return decorator

            mock_mcp = MockMCP()
            register_tools(mock_mcp)

            # Call the first registered tool (get_products)
            get_products_func = mock_mcp.tools[0]
            result = get_products_func()

            # Verify successful response
            parsed = json.loads(result)
            assert "data" in parsed
            assert len(parsed["data"]) == 1

    def test_get_products_mcp_wrapper_handles_exception(self):
        """Test that get_products MCP wrapper handles exceptions."""
        with patch(
            "mcp_server_spira.features.workspaces.tools.products.get_spira_client"
        ) as mock_get_client:
            mock_get_client.side_effect = Exception("Client error")

            # Create a real MCP-like object
            class MockMCP:
                def __init__(self):
                    self.tools = []

                def tool(self):
                    def decorator(func):
                        self.tools.append(func)
                        return func

                    return decorator

            mock_mcp = MockMCP()
            register_tools(mock_mcp)

            # Call the first registered tool (get_products)
            get_products_func = mock_mcp.tools[0]
            result = get_products_func()

            # Verify error response
            parsed = json.loads(result)
            assert "error" in parsed
            assert parsed["error_code"] == "API_ERROR"

    def test_get_product_by_id_mcp_wrapper_calls_implementation(self):
        """Test that get_product_by_id MCP wrapper properly calls implementation."""
        with patch(
            "mcp_server_spira.features.workspaces.tools.products.get_spira_client"
        ) as mock_get_client:
            mock_client = Mock()
            mock_product = {"ProjectId": 55, "Name": "Test Product", "Active": True}
            mock_client.make_spira_api_get_request.return_value = mock_product
            mock_get_client.return_value = mock_client

            # Create a real MCP-like object
            class MockMCP:
                def __init__(self):
                    self.tools = []

                def tool(self):
                    def decorator(func):
                        self.tools.append(func)
                        return func

                    return decorator

            mock_mcp = MockMCP()
            register_tools(mock_mcp)

            # Call the second registered tool (get_product_by_id)
            get_product_by_id_func = mock_mcp.tools[1]
            result = get_product_by_id_func(55)

            # Verify result contains product info
            assert "Test Product" in result

    def test_get_product_by_id_mcp_wrapper_handles_exception(self):
        """Test that get_product_by_id MCP wrapper handles exceptions."""
        with patch(
            "mcp_server_spira.features.workspaces.tools.products.get_spira_client"
        ) as mock_get_client:
            mock_get_client.side_effect = Exception("Client error")

            # Create a real MCP-like object
            class MockMCP:
                def __init__(self):
                    self.tools = []

                def tool(self):
                    def decorator(func):
                        self.tools.append(func)
                        return func

                    return decorator

            mock_mcp = MockMCP()
            register_tools(mock_mcp)

            # Call the second registered tool (get_product_by_id)
            get_product_by_id_func = mock_mcp.tools[1]
            result = get_product_by_id_func(55)

            # Verify error response
            assert "Error:" in result
            assert "Client error" in result

    def test_get_program_products_mcp_wrapper_calls_implementation(self):
        """Test that get_program_products MCP wrapper properly calls implementation."""
        with patch(
            "mcp_server_spira.features.workspaces.tools.products.get_spira_client"
        ) as mock_get_client:
            mock_client = Mock()
            mock_products = [{"ProjectId": 1, "Name": "P1", "ProjectGroupId": 10, "Active": True}]
            mock_client.make_spira_api_get_request.return_value = mock_products
            mock_get_client.return_value = mock_client

            # Create a real MCP-like object
            class MockMCP:
                def __init__(self):
                    self.tools = []

                def tool(self):
                    def decorator(func):
                        self.tools.append(func)
                        return func

                    return decorator

            mock_mcp = MockMCP()
            register_tools(mock_mcp)

            # Call the third registered tool (get_program_products)
            get_program_products_func = mock_mcp.tools[2]
            result = get_program_products_func(10)

            # Verify result contains product info
            assert "P1" in result

    def test_get_program_products_mcp_wrapper_handles_exception(self):
        """Test that get_program_products MCP wrapper handles exceptions."""
        with patch(
            "mcp_server_spira.features.workspaces.tools.products.get_spira_client"
        ) as mock_get_client:
            mock_get_client.side_effect = Exception("Client error")

            # Create a real MCP-like object
            class MockMCP:
                def __init__(self):
                    self.tools = []

                def tool(self):
                    def decorator(func):
                        self.tools.append(func)
                        return func

                    return decorator

            mock_mcp = MockMCP()
            register_tools(mock_mcp)

            # Call the third registered tool (get_program_products)
            get_program_products_func = mock_mcp.tools[2]
            result = get_program_products_func(10)

            # Verify error response
            assert "Error:" in result
            assert "Client error" in result
