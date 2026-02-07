"""Tests for validation module."""

from mcp_server_spira.features.common.validation import ParameterValidator


class TestParameterValidator:
    """Tests for ParameterValidator class."""

    # Tests for validate_positive_integer

    def test_validate_positive_integer_valid(self):
        """Test validation passes for valid positive integer."""
        error = ParameterValidator.validate_positive_integer(5, "product_id")
        assert error is None

    def test_validate_positive_integer_valid_with_custom_min(self):
        """Test validation passes with custom minimum value."""
        error = ParameterValidator.validate_positive_integer(10, "task_id", min_value=10)
        assert error is None

    def test_validate_positive_integer_invalid_type_string(self):
        """Test validation fails for string value."""
        error = ParameterValidator.validate_positive_integer("5", "product_id")
        assert error is not None
        assert error["error_code"] == "INVALID_TYPE"
        assert error["details"]["parameter"] == "product_id"
        assert error["details"]["value"] == "5"
        assert error["details"]["expected_type"] == "integer"
        assert "must be an integer" in error["suggestion"]

    def test_validate_positive_integer_invalid_type_float(self):
        """Test validation fails for float value."""
        error = ParameterValidator.validate_positive_integer(5.5, "product_id")
        assert error is not None
        assert error["error_code"] == "INVALID_TYPE"

    def test_validate_positive_integer_invalid_type_none(self):
        """Test validation fails for None value."""
        error = ParameterValidator.validate_positive_integer(None, "product_id")
        assert error is not None
        assert error["error_code"] == "INVALID_TYPE"

    def test_validate_positive_integer_zero(self):
        """Test validation fails for zero."""
        error = ParameterValidator.validate_positive_integer(0, "product_id")
        assert error is not None
        assert error["error_code"] == "INVALID_VALUE"
        assert error["details"]["parameter"] == "product_id"
        assert error["details"]["value"] == 0
        assert error["details"]["expected"] == ">= 1"
        assert "must be >= 1" in error["suggestion"]

    def test_validate_positive_integer_negative(self):
        """Test validation fails for negative value."""
        error = ParameterValidator.validate_positive_integer(-5, "product_id")
        assert error is not None
        assert error["error_code"] == "INVALID_VALUE"
        assert error["details"]["value"] == -5

    def test_validate_positive_integer_below_custom_min(self):
        """Test validation fails when value is below custom minimum."""
        error = ParameterValidator.validate_positive_integer(5, "task_id", min_value=10)
        assert error is not None
        assert error["error_code"] == "INVALID_VALUE"
        assert error["details"]["expected"] == ">= 10"

    # Tests for validate_pagination_params

    def test_validate_pagination_params_valid_defaults(self):
        """Test validation passes for default pagination values."""
        error = ParameterValidator.validate_pagination_params(25, 0)
        assert error is None

    def test_validate_pagination_params_valid_custom(self):
        """Test validation passes for custom valid values."""
        error = ParameterValidator.validate_pagination_params(100, 50)
        assert error is None

    def test_validate_pagination_params_valid_max_limit(self):
        """Test validation passes for maximum limit."""
        error = ParameterValidator.validate_pagination_params(500, 0)
        assert error is None

    def test_validate_pagination_params_valid_min_limit(self):
        """Test validation passes for minimum limit."""
        error = ParameterValidator.validate_pagination_params(1, 0)
        assert error is None

    def test_validate_pagination_params_limit_too_high(self):
        """Test validation fails when limit exceeds maximum."""
        error = ParameterValidator.validate_pagination_params(1000, 0)
        assert error is not None
        assert error["error_code"] == "INVALID_PARAMETER"
        assert error["details"]["parameter"] == "limit"
        assert error["details"]["value"] == 1000
        assert error["details"]["expected"] == "1-500"
        assert "between 1 and 500" in error["suggestion"]

    def test_validate_pagination_params_limit_zero(self):
        """Test validation fails when limit is zero."""
        error = ParameterValidator.validate_pagination_params(0, 0)
        assert error is not None
        assert error["error_code"] == "INVALID_PARAMETER"
        assert error["details"]["parameter"] == "limit"

    def test_validate_pagination_params_limit_negative(self):
        """Test validation fails when limit is negative."""
        error = ParameterValidator.validate_pagination_params(-10, 0)
        assert error is not None
        assert error["error_code"] == "INVALID_PARAMETER"
        assert error["details"]["parameter"] == "limit"

    def test_validate_pagination_params_limit_invalid_type(self):
        """Test validation fails when limit is not an integer."""
        error = ParameterValidator.validate_pagination_params("25", 0)
        assert error is not None
        assert error["error_code"] == "INVALID_PARAMETER"
        assert error["details"]["parameter"] == "limit"

    def test_validate_pagination_params_offset_negative(self):
        """Test validation fails when offset is negative."""
        error = ParameterValidator.validate_pagination_params(25, -1)
        assert error is not None
        assert error["error_code"] == "INVALID_PARAMETER"
        assert error["details"]["parameter"] == "offset"
        assert error["details"]["value"] == -1
        assert error["details"]["expected"] == ">= 0"
        assert "offset >= 0" in error["suggestion"]

    def test_validate_pagination_params_offset_invalid_type(self):
        """Test validation fails when offset is not an integer."""
        error = ParameterValidator.validate_pagination_params(25, "0")
        assert error is not None
        assert error["error_code"] == "INVALID_PARAMETER"
        assert error["details"]["parameter"] == "offset"

    def test_validate_pagination_params_both_invalid(self):
        """Test validation fails for limit when both parameters are invalid."""
        # Should fail on limit first (checked first in implementation)
        error = ParameterValidator.validate_pagination_params(1000, -1)
        assert error is not None
        assert error["error_code"] == "INVALID_PARAMETER"
        assert error["details"]["parameter"] == "limit"

    def test_validate_pagination_params_large_offset(self):
        """Test validation passes for large offset value."""
        error = ParameterValidator.validate_pagination_params(25, 10000)
        assert error is None
