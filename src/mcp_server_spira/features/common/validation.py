"""Input validation utilities for MCP tools."""

from typing import Any


class ParameterValidator:
    """Validates tool input parameters."""

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
    def validate_pagination_params(limit: Any, offset: Any) -> dict | None:
        """
        Validates pagination parameters.

        Args:
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            None if valid, error dict if invalid

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
