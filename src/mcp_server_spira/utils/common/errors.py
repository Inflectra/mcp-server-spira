"""Custom exception classes for MCP tools."""

from typing import Any


class SpiraMCPError(Exception):
    """Base exception for all Spira MCP errors."""

    def __init__(self, message: str, error_code: str, details: dict[str, Any] | None = None):
        """
        Initialize a Spira MCP error.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error context
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """
        Convert exception to error response dict.

        Returns:
            Dictionary with error information suitable for JSON serialization
        """
        return {"error": self.message, "error_code": self.error_code, "details": self.details}


class ValidationError(SpiraMCPError):
    """Raised when input validation fails."""

    def __init__(self, message: str, parameter: str, value: Any, expected: str):
        """
        Initialize a validation error.

        Args:
            message: Human-readable error message
            parameter: Name of the parameter that failed validation
            value: The invalid value that was provided
            expected: Description of what was expected
        """
        super().__init__(
            message=message,
            error_code="INVALID_PARAMETER",
            details={"parameter": parameter, "value": value, "expected": expected},
        )


class APIError(SpiraMCPError):
    """Raised when Spira API call fails."""

    def __init__(self, message: str, endpoint: str, status_code: int | None = None):
        """
        Initialize an API error.

        Args:
            message: Human-readable error message
            endpoint: The API endpoint that failed
            status_code: HTTP status code if available
        """
        details: dict[str, Any] = {"endpoint": endpoint}
        if status_code is not None:
            details["status_code"] = status_code

        super().__init__(message=message, error_code="API_ERROR", details=details)


class AuthenticationError(SpiraMCPError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        """
        Initialize an authentication error.

        Args:
            message: Human-readable error message (default: "Authentication failed")
        """
        super().__init__(message=message, error_code="AUTHENTICATION_ERROR")
