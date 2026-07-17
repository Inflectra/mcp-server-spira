"""Input validation utilities for MCP tools."""

from typing import Any


class ParameterValidator:
    """Validates tool input parameters.

    Spec:
        - All methods are static — no instance state, no side effects
        - All methods return None on success, a dict on failure — never raise
        - Error dicts always contain keys: "error", "error_code", "details",
          "suggestion" — callers unpack with **error_dict into
          format_error_response without checking for missing keys
        - Validation short-circuits: first failing check returns immediately,
          callers depend on this for fast feedback before any API call
    """

    @staticmethod
    def validate_positive_integer(value: Any, param_name: str, min_value: int = 1) -> dict | None:
        """
        Validates that a parameter is a positive integer.

        Args:
            value: The value to validate
            param_name: Name of the parameter (for error messages)
            min_value: Minimum allowed value (default: 1)

        Returns:
            None if valid, error dict if invalid

        Spec:
            - Returns None when value is an int >= min_value
            - Returns error dict with INVALID_TYPE when value is not an int
              (including float, str, None, bool subclass excluded by
              isinstance check)
            - Returns error dict with INVALID_VALUE when value is int but
              below min_value
            - Error dict always has keys: error, error_code, details,
              suggestion — callers unpack directly
            - details always contains: parameter, value, and either
              expected_type (for type errors) or expected (for value errors)

        Example:
            >>> validator = ParameterValidator()
            >>> error = validator.validate_positive_integer(5, "product_id")
            >>> error is None
            True
            >>> error = validator.validate_positive_integer(-1, "product_id")
            >>> error["error_code"]
            'INVALID_VALUE'
        """
        if not isinstance(value, int):
            return {
                "error": f"Invalid {param_name} parameter",
                "error_code": "INVALID_TYPE",
                "details": {"parameter": param_name, "value": value, "expected_type": "integer"},
                "suggestion": f"{param_name} must be an integer",
            }

        if value < min_value:
            return {
                "error": f"Invalid {param_name} parameter",
                "error_code": "INVALID_VALUE",
                "details": {"parameter": param_name, "value": value, "expected": f">= {min_value}"},
                "suggestion": f"{param_name} must be >= {min_value}",
            }

        return None

    @staticmethod
    def validate_type_param(
        value: Any,
        valid_types: tuple[str, ...] | list[str],
        param_name: str,
    ) -> dict | None:
        """
        Validates that a parameter is one of the allowed type strings.

        Args:
            value: The value to validate
            valid_types: Allowed string values (e.g. from config dict keys)
            param_name: Name of the parameter (for error messages)

        Returns:
            None if valid, error dict with INVALID_PARAMETER code if invalid

        Spec:
            - Returns None if and only if value is a member of valid_types
              (uses ``in`` operator — works for any hashable value)
            - Returns error dict with INVALID_PARAMETER for any value not
              in valid_types, including None, int, float, bool, list, dict
            - Error dict details always includes "valid_values" as a list —
              callers use this to show the LLM what options are available
            - Error dict suggestion always includes param_name — helps the
              LLM self-correct

        Example:
            >>> ParameterValidator.validate_type_param("product", ("product", "program"), "workspace_type")
            >>> ParameterValidator.validate_type_param("bad", ("product", "program"), "workspace_type")
            {'error': 'Invalid workspace_type parameter', ...}
        """
        if value in valid_types:
            return None

        return {
            "error": f"Invalid {param_name} parameter",
            "error_code": "INVALID_PARAMETER",
            "details": {
                "parameter": param_name,
                "value": value,
                "valid_values": list(valid_types),
            },
            "suggestion": f"Use one of the valid {param_name} values.",
        }

    @staticmethod
    def validate_pagination_params(limit: Any, offset: Any) -> dict | None:
        """
        Validates pagination parameters.

        Args:
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            None if valid, error dict if invalid

        Spec:
            - Returns None when limit is int in [1, 500] AND offset is
              int >= 0
            - Validates limit first — when both are invalid, the error
              reports limit (callers depend on deterministic first-failure)
            - limit must be int AND in range [1, 500]; non-int types
              (str, float, None) fail with INVALID_PARAMETER
            - offset must be int AND >= 0; non-int types fail with
              INVALID_PARAMETER
            - Error dict always has keys: error, error_code, details,
              suggestion — callers unpack directly

        Example:
            >>> validator = ParameterValidator()
            >>> error = validator.validate_pagination_params(25, 0)
            >>> error is None
            True
            >>> error = validator.validate_pagination_params(1000, 0)
            >>> error["error_code"]
            'INVALID_PARAMETER'
        """
        # Validate limit
        if not isinstance(limit, int) or not (1 <= limit <= 500):
            return {
                "error": "Invalid limit parameter",
                "error_code": "INVALID_PARAMETER",
                "details": {"parameter": "limit", "value": limit, "expected": "1-500"},
                "suggestion": "Use limit between 1 and 500",
            }

        # Validate offset
        if not isinstance(offset, int) or offset < 0:
            return {
                "error": "Invalid offset parameter",
                "error_code": "INVALID_PARAMETER",
                "details": {"parameter": "offset", "value": offset, "expected": ">= 0"},
                "suggestion": "Use offset >= 0",
            }

        return None
