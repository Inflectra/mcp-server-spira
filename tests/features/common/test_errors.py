"""Unit tests for error classes module."""

import pytest

from mcp_server_spira.features.common.errors import (
    APIError,
    AuthenticationError,
    SpiraMCPError,
    ValidationError,
)


class TestSpiraMCPError:
    """Tests for SpiraMCPError base exception class."""

    def test_init_with_minimal_params(self):
        """Test initialization with only required parameters."""
        error = SpiraMCPError(message="Something went wrong", error_code="GENERIC_ERROR")

        assert error.message == "Something went wrong"
        assert error.error_code == "GENERIC_ERROR"
        assert error.details == {}
        assert str(error) == "Something went wrong"

    def test_init_with_details(self):
        """Test initialization with details parameter."""
        details = {"field": "value", "count": 42}
        error = SpiraMCPError(
            message="Error with details", error_code="DETAILED_ERROR", details=details
        )

        assert error.message == "Error with details"
        assert error.error_code == "DETAILED_ERROR"
        assert error.details == details

    def test_to_dict_minimal(self):
        """Test to_dict() with minimal parameters."""
        error = SpiraMCPError(message="Test error", error_code="TEST_ERROR")

        result = error.to_dict()

        assert result == {"error": "Test error", "error_code": "TEST_ERROR", "details": {}}

    def test_to_dict_with_details(self):
        """Test to_dict() with details."""
        error = SpiraMCPError(
            message="Test error", error_code="TEST_ERROR", details={"key": "value", "number": 123}
        )

        result = error.to_dict()

        assert result == {
            "error": "Test error",
            "error_code": "TEST_ERROR",
            "details": {"key": "value", "number": 123},
        }

    def test_is_exception(self):
        """Test that SpiraMCPError is an Exception."""
        error = SpiraMCPError("Test", "TEST")
        assert isinstance(error, Exception)

    def test_can_be_raised(self):
        """Test that SpiraMCPError can be raised and caught."""
        with pytest.raises(SpiraMCPError) as exc_info:
            raise SpiraMCPError("Test error", "TEST_CODE")

        assert exc_info.value.message == "Test error"
        assert exc_info.value.error_code == "TEST_CODE"


class TestValidationError:
    """Tests for ValidationError exception class."""

    def test_init(self):
        """Test ValidationError initialization."""
        error = ValidationError(
            message="Invalid parameter value", parameter="limit", value=1000, expected="1-500"
        )

        assert error.message == "Invalid parameter value"
        assert error.error_code == "INVALID_PARAMETER"
        assert error.details == {"parameter": "limit", "value": 1000, "expected": "1-500"}

    def test_to_dict(self):
        """Test ValidationError to_dict() method."""
        error = ValidationError(
            message="Invalid offset", parameter="offset", value=-5, expected=">= 0"
        )

        result = error.to_dict()

        assert result == {
            "error": "Invalid offset",
            "error_code": "INVALID_PARAMETER",
            "details": {"parameter": "offset", "value": -5, "expected": ">= 0"},
        }

    def test_is_spira_mcp_error(self):
        """Test that ValidationError is a SpiraMCPError."""
        error = ValidationError("Test", "param", "value", "expected")
        assert isinstance(error, SpiraMCPError)

    def test_with_various_value_types(self):
        """Test ValidationError with different value types."""
        # String value
        error1 = ValidationError("Test", "name", "invalid", "alphanumeric")
        assert error1.details["value"] == "invalid"

        # None value
        error2 = ValidationError("Test", "id", None, "positive integer")
        assert error2.details["value"] is None

        # List value
        error3 = ValidationError("Test", "ids", [1, 2, 3], "single integer")
        assert error3.details["value"] == [1, 2, 3]


class TestAPIError:
    """Tests for APIError exception class."""

    def test_init_without_status_code(self):
        """Test APIError initialization without status code."""
        error = APIError(message="Failed to retrieve tasks", endpoint="/tasks")

        assert error.message == "Failed to retrieve tasks"
        assert error.error_code == "API_ERROR"
        assert error.details == {"endpoint": "/tasks"}

    def test_init_with_status_code(self):
        """Test APIError initialization with status code."""
        error = APIError(message="Not found", endpoint="/projects/55/tasks/999", status_code=404)

        assert error.message == "Not found"
        assert error.error_code == "API_ERROR"
        assert error.details == {"endpoint": "/projects/55/tasks/999", "status_code": 404}

    def test_to_dict_without_status_code(self):
        """Test APIError to_dict() without status code."""
        error = APIError(message="Connection failed", endpoint="/incidents")

        result = error.to_dict()

        assert result == {
            "error": "Connection failed",
            "error_code": "API_ERROR",
            "details": {"endpoint": "/incidents"},
        }

    def test_to_dict_with_status_code(self):
        """Test APIError to_dict() with status code."""
        error = APIError(message="Unauthorized", endpoint="/requirements", status_code=401)

        result = error.to_dict()

        assert result == {
            "error": "Unauthorized",
            "error_code": "API_ERROR",
            "details": {"endpoint": "/requirements", "status_code": 401},
        }

    def test_is_spira_mcp_error(self):
        """Test that APIError is a SpiraMCPError."""
        error = APIError("Test", "/endpoint")
        assert isinstance(error, SpiraMCPError)

    def test_with_various_status_codes(self):
        """Test APIError with different HTTP status codes."""
        codes = [400, 401, 403, 404, 500, 502, 503]
        for code in codes:
            error = APIError("Error", "/test", status_code=code)
            assert error.details["status_code"] == code


class TestAuthenticationError:
    """Tests for AuthenticationError exception class."""

    def test_init_with_default_message(self):
        """Test AuthenticationError with default message."""
        error = AuthenticationError()

        assert error.message == "Authentication failed"
        assert error.error_code == "AUTHENTICATION_ERROR"
        assert error.details == {}

    def test_init_with_custom_message(self):
        """Test AuthenticationError with custom message."""
        error = AuthenticationError("Invalid API key")

        assert error.message == "Invalid API key"
        assert error.error_code == "AUTHENTICATION_ERROR"
        assert error.details == {}

    def test_to_dict_default(self):
        """Test AuthenticationError to_dict() with default message."""
        error = AuthenticationError()

        result = error.to_dict()

        assert result == {
            "error": "Authentication failed",
            "error_code": "AUTHENTICATION_ERROR",
            "details": {},
        }

    def test_to_dict_custom(self):
        """Test AuthenticationError to_dict() with custom message."""
        error = AuthenticationError("Token expired")

        result = error.to_dict()

        assert result == {
            "error": "Token expired",
            "error_code": "AUTHENTICATION_ERROR",
            "details": {},
        }

    def test_is_spira_mcp_error(self):
        """Test that AuthenticationError is a SpiraMCPError."""
        error = AuthenticationError()
        assert isinstance(error, SpiraMCPError)


class TestErrorClassHierarchy:
    """Tests for error class inheritance and hierarchy."""

    def test_all_errors_inherit_from_base(self):
        """Test that all error classes inherit from SpiraMCPError."""
        validation_error = ValidationError("Test", "param", "value", "expected")
        api_error = APIError("Test", "/endpoint")
        auth_error = AuthenticationError()

        assert isinstance(validation_error, SpiraMCPError)
        assert isinstance(api_error, SpiraMCPError)
        assert isinstance(auth_error, SpiraMCPError)

    def test_all_errors_inherit_from_exception(self):
        """Test that all error classes inherit from Exception."""
        base_error = SpiraMCPError("Test", "CODE")
        validation_error = ValidationError("Test", "param", "value", "expected")
        api_error = APIError("Test", "/endpoint")
        auth_error = AuthenticationError()

        assert isinstance(base_error, Exception)
        assert isinstance(validation_error, Exception)
        assert isinstance(api_error, Exception)
        assert isinstance(auth_error, Exception)

    def test_error_catching_hierarchy(self):
        """Test that errors can be caught at different levels."""
        # Catch specific error type
        with pytest.raises(ValidationError):
            raise ValidationError("Test", "param", "value", "expected")

        # Catch base error type
        with pytest.raises(SpiraMCPError):
            raise ValidationError("Test", "param", "value", "expected")

        # Catch as generic Exception (specific exception type preferred)
        with pytest.raises(SpiraMCPError):  # More specific than Exception
            raise ValidationError("Test", "param", "value", "expected")


class TestErrorSerialization:
    """Tests for error serialization to JSON-compatible dicts."""

    def test_all_errors_have_to_dict(self):
        """Test that all error classes have to_dict() method."""
        errors = [
            SpiraMCPError("Test", "CODE"),
            ValidationError("Test", "param", "value", "expected"),
            APIError("Test", "/endpoint", 500),
            AuthenticationError("Test"),
        ]

        for error in errors:
            assert hasattr(error, "to_dict")
            assert callable(error.to_dict)

    def test_to_dict_returns_dict(self):
        """Test that to_dict() returns a dictionary."""
        errors = [
            SpiraMCPError("Test", "CODE"),
            ValidationError("Test", "param", "value", "expected"),
            APIError("Test", "/endpoint"),
            AuthenticationError(),
        ]

        for error in errors:
            result = error.to_dict()
            assert isinstance(result, dict)

    def test_to_dict_has_required_keys(self):
        """Test that to_dict() includes required keys."""
        errors = [
            SpiraMCPError("Test", "CODE"),
            ValidationError("Test", "param", "value", "expected"),
            APIError("Test", "/endpoint", 404),
            AuthenticationError("Test"),
        ]

        for error in errors:
            result = error.to_dict()
            assert "error" in result
            assert "error_code" in result
            assert "details" in result

    def test_to_dict_json_serializable(self):
        """Test that to_dict() output is JSON serializable."""
        import json

        errors = [
            SpiraMCPError("Test", "CODE", {"key": "value"}),
            ValidationError("Test", "param", 123, "expected"),
            APIError("Test", "/endpoint", 500),
            AuthenticationError("Test message"),
        ]

        for error in errors:
            result = error.to_dict()
            # Should not raise exception
            json_str = json.dumps(result)
            assert isinstance(json_str, str)
