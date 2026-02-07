"""Response formatting utilities for MCP tools."""

import json
from typing import Any


def format_success_response(data: Any, pagination: dict | None = None) -> str:
    """
    Formats a successful response as JSON string.

    Args:
        data: The data to return (list or dict)
        pagination: Optional pagination metadata

    Returns:
        JSON string with proper formatting

    Example:
        >>> data = [{"TaskId": 1, "Name": "Task 1"}]
        >>> pagination = {"limit": 25, "offset": 0, "total_count": 100}
        >>> result = format_success_response(data, pagination)
        >>> print(result)
        {
          "data": [
            {
              "TaskId": 1,
              "Name": "Task 1"
            }
          ],
          "pagination": {
            "limit": 25,
            "offset": 0,
            "total_count": 100
          }
        }
    """
    response = {"data": data}
    if pagination:
        response["pagination"] = pagination

    return json.dumps(response, indent=2, default=str)


def format_error_response(
    error: str, error_code: str, details: dict | None = None, suggestion: str | None = None
) -> str:
    """
    Formats an error response as JSON string.

    Args:
        error: Human-readable error message
        error_code: Machine-readable error code
        details: Additional error context
        suggestion: Actionable suggestion for resolution

    Returns:
        JSON string with error information

    Example:
        >>> result = format_error_response(
        ...     error="Invalid limit parameter",
        ...     error_code="INVALID_PARAMETER",
        ...     details={"parameter": "limit", "value": 1000, "expected": "1-500"},
        ...     suggestion="Use limit between 1 and 500"
        ... )
        >>> print(result)
        {
          "error": "Invalid limit parameter",
          "error_code": "INVALID_PARAMETER",
          "details": {
            "parameter": "limit",
            "value": 1000,
            "expected": "1-500"
          },
          "suggestion": "Use limit between 1 and 500"
        }
    """
    response: dict[str, Any] = {"error": error, "error_code": error_code}

    if details:
        response["details"] = details
    if suggestion:
        response["suggestion"] = suggestion

    return json.dumps(response, indent=2)


class ErrorCodes:
    """Standard error codes used across all tools."""

    INVALID_PARAMETER = "INVALID_PARAMETER"
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    API_ERROR = "API_ERROR"
    NOT_FOUND = "NOT_FOUND"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
