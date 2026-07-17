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

    Spec:
        - ALWAYS returns a valid JSON string — never raises
        - Output always contains a "data" key with the provided data
        - "pagination" key is present only when pagination arg is truthy;
          absent (not null) when pagination is None or empty dict
        - Non-JSON-serializable values (e.g. datetime) are coerced via
          default=str — never raises TypeError
        - Output uses 2-space indentation for LLM readability

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

    Spec:
        - ALWAYS returns a valid JSON string — never raises
        - Output always contains "error" and "error_code" keys
        - "details" key is present only when details arg is truthy (not
          None, not empty dict)
        - "suggestion" key is present only when suggestion arg is truthy
        - Output never contains a "data" key — callers distinguish
          success from error by checking for "error" vs "data"
        - Output uses 2-space indentation for LLM readability

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


def format_search_response(
    data: list,
    artifact_type: str,
    fields_returned: list[str],
    *,
    pagination: dict | None = None,
    fields_available: list[str] | None = None,
    warnings: list[str] | None = None,
    custom_properties_resolved: bool = False,
    includes_fetched: list[str] | None = None,
) -> str:
    """Format a single-product search response envelope.

    Args:
        data: List of artifact dicts matching the search.
        artifact_type: The artifact type string (e.g. "incident").
        fields_returned: Fields present in every object in data.
        pagination: Optional pagination metadata dict.
        fields_available: Delta fields not returned. Omitted when None; included (even if empty list) when explicitly provided.
        warnings: List of warning strings. Defaults to empty list.
        custom_properties_resolved: Whether custom properties were resolved.
        includes_fetched: List of include types that were successfully processed. Omitted when None.

    Returns:
        JSON string with the unified search envelope.

    Spec:
        - ALWAYS returns a valid JSON string — never raises
        - Required keys always present: "data", "artifact_type",
          "fields_returned", "warnings"
        - "warnings" is always a list (never None) — defaults to [] when
          arg is None
        - "fields_available" is present (even as []) when explicitly
          passed as a list; absent when None — this is the delta contract
        - "pagination" is present only when arg is truthy
        - "custom_properties_resolved" is present only when True; absent
          when False or omitted — keeps envelope minimal
        - "includes_fetched" is present only when not None
        - Non-JSON-serializable values coerced via default=str
        - Output uses 2-space indentation for LLM readability
    """
    response: dict[str, Any] = {
        "data": data,
        "artifact_type": artifact_type,
        "fields_returned": fields_returned,
    }
    if pagination:
        response["pagination"] = pagination
    if fields_available is not None:
        response["fields_available"] = fields_available
    if includes_fetched is not None:
        response["includes_fetched"] = includes_fetched
    response["warnings"] = warnings or []
    if custom_properties_resolved:
        response["custom_properties_resolved"] = True
    return json.dumps(response, indent=2, default=str)


def format_multi_product_response(
    artifact_type: str,
    products: list[dict],
    *,
    warnings: list[str] | None = None,
) -> str:
    """Format a multi-product fan-out response envelope.

    Args:
        artifact_type: The artifact type string (e.g. "incident").
        products: List of per-product result dicts.
        warnings: List of warning strings. Defaults to empty list.

    Returns:
        JSON string with the multi-product envelope.

    Spec:
        - ALWAYS returns a valid JSON string — never raises
        - Required keys always present: "artifact_type", "products",
          "warnings"
        - "warnings" is always a list (never None) — defaults to [] when
          arg is None
        - Every product_id in the fan-out gets an entry in "products" —
          failed products have an "error" key, never silently dropped
          (caller responsibility, but this formatter preserves them)
        - Non-JSON-serializable values coerced via default=str
        - Output uses 2-space indentation for LLM readability
    """
    response: dict[str, Any] = {
        "artifact_type": artifact_type,
        "products": products,
        "warnings": warnings or [],
    }
    return json.dumps(response, indent=2, default=str)


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
