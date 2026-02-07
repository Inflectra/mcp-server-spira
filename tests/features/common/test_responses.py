"""Unit tests for response formatting utilities."""

import json

from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)


class TestFormatSuccessResponse:
    """Tests for format_success_response function."""

    def test_format_success_with_list_data(self):
        """Test formatting success response with list data."""
        data = [{"TaskId": 1, "Name": "Task 1"}, {"TaskId": 2, "Name": "Task 2"}]
        result = format_success_response(data)

        parsed = json.loads(result)
        assert "data" in parsed
        assert parsed["data"] == data
        assert "pagination" not in parsed

    def test_format_success_with_dict_data(self):
        """Test formatting success response with dict data."""
        data = {"TaskId": 1, "Name": "Task 1"}
        result = format_success_response(data)

        parsed = json.loads(result)
        assert "data" in parsed
        assert parsed["data"] == data

    def test_format_success_with_pagination(self):
        """Test formatting success response with pagination metadata."""
        data = [{"TaskId": 1, "Name": "Task 1"}]
        pagination = {
            "limit": 25,
            "offset": 0,
            "returned_count": 1,
            "total_count": 100,
            "has_more": True,
            "pagination_type": "client-side",
        }
        result = format_success_response(data, pagination)

        parsed = json.loads(result)
        assert "data" in parsed
        assert "pagination" in parsed
        assert parsed["data"] == data
        assert parsed["pagination"] == pagination

    def test_format_success_with_empty_list(self):
        """Test formatting success response with empty list."""
        data: list[dict] = []
        result = format_success_response(data)

        parsed = json.loads(result)
        assert parsed["data"] == []

    def test_format_success_with_none_pagination(self):
        """Test formatting success response with None pagination."""
        data = [{"TaskId": 1}]
        result = format_success_response(data, None)

        parsed = json.loads(result)
        assert "pagination" not in parsed

    def test_format_success_handles_datetime(self):
        """Test that datetime objects are converted to strings."""
        from datetime import datetime

        data = [{"TaskId": 1, "CreatedDate": datetime(2024, 1, 15, 10, 30, 0)}]
        result = format_success_response(data)

        parsed = json.loads(result)
        # Should not raise an error and datetime should be converted to string
        assert "data" in parsed
        assert isinstance(parsed["data"][0]["CreatedDate"], str)

    def test_format_success_proper_indentation(self):
        """Test that output has proper 2-space indentation."""
        data = [{"TaskId": 1}]
        result = format_success_response(data)

        # Check that it's properly formatted with indentation
        assert "{\n" in result
        assert "  " in result  # 2-space indentation


class TestFormatErrorResponse:
    """Tests for format_error_response function."""

    def test_format_error_minimal(self):
        """Test formatting error response with minimal parameters."""
        result = format_error_response(error="Something went wrong", error_code="API_ERROR")

        parsed = json.loads(result)
        assert parsed["error"] == "Something went wrong"
        assert parsed["error_code"] == "API_ERROR"
        assert "details" not in parsed
        assert "suggestion" not in parsed

    def test_format_error_with_details(self):
        """Test formatting error response with details."""
        details = {"parameter": "limit", "value": 1000, "expected": "1-500"}
        result = format_error_response(
            error="Invalid limit parameter",
            error_code="INVALID_PARAMETER",
            details=details,
        )

        parsed = json.loads(result)
        assert parsed["error"] == "Invalid limit parameter"
        assert parsed["error_code"] == "INVALID_PARAMETER"
        assert parsed["details"] == details
        assert "suggestion" not in parsed

    def test_format_error_with_suggestion(self):
        """Test formatting error response with suggestion."""
        result = format_error_response(
            error="Invalid limit parameter",
            error_code="INVALID_PARAMETER",
            suggestion="Use limit between 1 and 500",
        )

        parsed = json.loads(result)
        assert parsed["suggestion"] == "Use limit between 1 and 500"

    def test_format_error_with_all_fields(self):
        """Test formatting error response with all fields."""
        details = {"parameter": "limit", "value": 1000, "expected": "1-500"}
        result = format_error_response(
            error="Invalid limit parameter",
            error_code="INVALID_PARAMETER",
            details=details,
            suggestion="Use limit between 1 and 500",
        )

        parsed = json.loads(result)
        assert parsed["error"] == "Invalid limit parameter"
        assert parsed["error_code"] == "INVALID_PARAMETER"
        assert parsed["details"] == details
        assert parsed["suggestion"] == "Use limit between 1 and 500"

    def test_format_error_with_none_details(self):
        """Test formatting error response with None details."""
        result = format_error_response(error="Error message", error_code="ERROR_CODE", details=None)

        parsed = json.loads(result)
        assert "details" not in parsed

    def test_format_error_with_none_suggestion(self):
        """Test formatting error response with None suggestion."""
        result = format_error_response(
            error="Error message", error_code="ERROR_CODE", suggestion=None
        )

        parsed = json.loads(result)
        assert "suggestion" not in parsed

    def test_format_error_proper_indentation(self):
        """Test that error output has proper 2-space indentation."""
        result = format_error_response(error="Error", error_code="ERROR")

        # Check that it's properly formatted with indentation
        assert "{\n" in result
        assert "  " in result  # 2-space indentation


class TestErrorCodes:
    """Tests for ErrorCodes constants class."""

    def test_error_codes_exist(self):
        """Test that all expected error codes are defined."""
        assert hasattr(ErrorCodes, "INVALID_PARAMETER")
        assert hasattr(ErrorCodes, "INVALID_TYPE")
        assert hasattr(ErrorCodes, "INVALID_VALUE")
        assert hasattr(ErrorCodes, "API_ERROR")
        assert hasattr(ErrorCodes, "NOT_FOUND")
        assert hasattr(ErrorCodes, "AUTHENTICATION_ERROR")
        assert hasattr(ErrorCodes, "PERMISSION_DENIED")
        assert hasattr(ErrorCodes, "RATE_LIMIT_EXCEEDED")

    def test_error_codes_are_strings(self):
        """Test that all error codes are strings."""
        assert isinstance(ErrorCodes.INVALID_PARAMETER, str)
        assert isinstance(ErrorCodes.INVALID_TYPE, str)
        assert isinstance(ErrorCodes.INVALID_VALUE, str)
        assert isinstance(ErrorCodes.API_ERROR, str)
        assert isinstance(ErrorCodes.NOT_FOUND, str)
        assert isinstance(ErrorCodes.AUTHENTICATION_ERROR, str)
        assert isinstance(ErrorCodes.PERMISSION_DENIED, str)
        assert isinstance(ErrorCodes.RATE_LIMIT_EXCEEDED, str)

    def test_error_codes_values(self):
        """Test that error codes have expected values."""
        assert ErrorCodes.INVALID_PARAMETER == "INVALID_PARAMETER"
        assert ErrorCodes.INVALID_TYPE == "INVALID_TYPE"
        assert ErrorCodes.INVALID_VALUE == "INVALID_VALUE"
        assert ErrorCodes.API_ERROR == "API_ERROR"
        assert ErrorCodes.NOT_FOUND == "NOT_FOUND"
        assert ErrorCodes.AUTHENTICATION_ERROR == "AUTHENTICATION_ERROR"
        assert ErrorCodes.PERMISSION_DENIED == "PERMISSION_DENIED"
        assert ErrorCodes.RATE_LIMIT_EXCEEDED == "RATE_LIMIT_EXCEEDED"

    def test_error_codes_can_be_used_in_format_error_response(self):
        """Test that ErrorCodes constants work with format_error_response."""
        result = format_error_response(error="Test error", error_code=ErrorCodes.INVALID_PARAMETER)

        parsed = json.loads(result)
        assert parsed["error_code"] == "INVALID_PARAMETER"


class TestIntegration:
    """Integration tests for response formatting."""

    def test_success_and_error_responses_are_distinct(self):
        """Test that success and error responses have different structures."""
        success = format_success_response([{"id": 1}])
        error = format_error_response("Error", "ERROR_CODE")

        success_parsed = json.loads(success)
        error_parsed = json.loads(error)

        # Success has 'data', error has 'error'
        assert "data" in success_parsed
        assert "error" not in success_parsed
        assert "error" in error_parsed
        assert "data" not in error_parsed

    def test_responses_are_valid_json(self):
        """Test that all responses produce valid JSON."""
        # Success response
        success = format_success_response([{"id": 1}])
        json.loads(success)  # Should not raise

        # Error response
        error = format_error_response("Error", "ERROR_CODE")
        json.loads(error)  # Should not raise

    def test_complex_nested_data(self):
        """Test formatting with complex nested data structures."""
        data = [
            {
                "TaskId": 1,
                "Name": "Task 1",
                "CustomProperties": [
                    {"PropertyId": 1, "Value": "Test"},
                    {"PropertyId": 2, "Value": 123},
                ],
                "Tags": ["bug", "critical"],
            }
        ]
        result = format_success_response(data)

        parsed = json.loads(result)
        assert parsed["data"] == data
