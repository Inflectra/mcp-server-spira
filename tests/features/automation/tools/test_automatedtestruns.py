"""
Unit tests for record_automated_test_run tool
"""

import json
from unittest.mock import MagicMock

from mcp_server_spira.features.automation.tools.automatedtestruns import (
    _record_automated_test_run_impl,
)


class TestRecordAutomatedTestRun:
    """Test suite for record_automated_test_run tool"""

    def test_record_test_run_success(self):
        """Test successful test run recording"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_post_request.return_value = {"TestRunId": 123}

        # Act
        result = _record_automated_test_run_impl(
            mock_client,
            product_id=55,
            test_name="test_user_login",
            short_message="Login test passed",
            long_message="User successfully logged in with valid credentials",
            error_count=0,
            test_case_id=456,
            execution_status_id=2,
        )

        # Assert
        result_data = json.loads(result)
        assert result_data["data"]["test_run_id"] == "TR:123"
        assert result_data["data"]["message"] == "Test run recorded successfully"
        mock_client.make_spira_api_post_request.assert_called_once()

    def test_record_test_run_failed_test(self):
        """Test recording a failed test run"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_post_request.return_value = {"TestRunId": 789}

        # Act
        result = _record_automated_test_run_impl(
            mock_client,
            product_id=55,
            test_name="test_user_login",
            short_message="Login test failed",
            long_message="AssertionError: Expected status 200, got 500",
            error_count=1,
            test_case_id=456,
            execution_status_id=1,
        )

        # Assert
        result_data = json.loads(result)
        assert result_data["data"]["test_run_id"] == "TR:789"
        assert result_data["data"]["message"] == "Test run recorded successfully"

    def test_record_test_run_invalid_product_id_negative(self):
        """Test validation error for negative product_id"""
        # Arrange
        mock_client = MagicMock()

        # Act
        result = _record_automated_test_run_impl(
            mock_client,
            product_id=-1,
            test_name="test_user_login",
            short_message="Login test passed",
            long_message="Test passed",
            error_count=0,
            test_case_id=456,
            execution_status_id=2,
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "INVALID_PARAMETER"
        assert "product_id" in result_data["details"]["parameter"]

    def test_record_test_run_invalid_product_id_zero(self):
        """Test validation error for zero product_id"""
        # Arrange
        mock_client = MagicMock()

        # Act
        result = _record_automated_test_run_impl(
            mock_client,
            product_id=0,
            test_name="test_user_login",
            short_message="Login test passed",
            long_message="Test passed",
            error_count=0,
            test_case_id=456,
            execution_status_id=2,
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "INVALID_PARAMETER"

    def test_record_test_run_invalid_test_case_id(self):
        """Test validation error for invalid test_case_id"""
        # Arrange
        mock_client = MagicMock()

        # Act
        result = _record_automated_test_run_impl(
            mock_client,
            product_id=55,
            test_name="test_user_login",
            short_message="Login test passed",
            long_message="Test passed",
            error_count=0,
            test_case_id=-1,
            execution_status_id=2,
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "INVALID_PARAMETER"
        assert "test_case_id" in result_data["details"]["parameter"]

    def test_record_test_run_invalid_error_count(self):
        """Test validation error for negative error_count"""
        # Arrange
        mock_client = MagicMock()

        # Act
        result = _record_automated_test_run_impl(
            mock_client,
            product_id=55,
            test_name="test_user_login",
            short_message="Login test passed",
            long_message="Test passed",
            error_count=-1,
            test_case_id=456,
            execution_status_id=2,
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "INVALID_PARAMETER"
        assert "error_count" in result_data["details"]["parameter"]

    def test_record_test_run_invalid_execution_status_too_low(self):
        """Test validation error for execution_status_id < 1"""
        # Arrange
        mock_client = MagicMock()

        # Act
        result = _record_automated_test_run_impl(
            mock_client,
            product_id=55,
            test_name="test_user_login",
            short_message="Login test passed",
            long_message="Test passed",
            error_count=0,
            test_case_id=456,
            execution_status_id=0,
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "INVALID_PARAMETER"
        assert "execution_status_id" in result_data["details"]["parameter"]

    def test_record_test_run_invalid_execution_status_too_high(self):
        """Test validation error for execution_status_id > 6"""
        # Arrange
        mock_client = MagicMock()

        # Act
        result = _record_automated_test_run_impl(
            mock_client,
            product_id=55,
            test_name="test_user_login",
            short_message="Login test passed",
            long_message="Test passed",
            error_count=0,
            test_case_id=456,
            execution_status_id=7,
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "INVALID_PARAMETER"
        assert "execution_status_id" in result_data["details"]["parameter"]

    def test_record_test_run_empty_test_name(self):
        """Test validation error for empty test_name"""
        # Arrange
        mock_client = MagicMock()

        # Act
        result = _record_automated_test_run_impl(
            mock_client,
            product_id=55,
            test_name="",
            short_message="Login test passed",
            long_message="Test passed",
            error_count=0,
            test_case_id=456,
            execution_status_id=2,
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "INVALID_PARAMETER"
        assert "test_name" in result_data["details"]["parameter"]

    def test_record_test_run_empty_short_message(self):
        """Test validation error for empty short_message"""
        # Arrange
        mock_client = MagicMock()

        # Act
        result = _record_automated_test_run_impl(
            mock_client,
            product_id=55,
            test_name="test_user_login",
            short_message="",
            long_message="Test passed",
            error_count=0,
            test_case_id=456,
            execution_status_id=2,
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "INVALID_PARAMETER"
        assert "short_message" in result_data["details"]["parameter"]

    def test_record_test_run_api_returns_none(self):
        """Test error handling when API returns None"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_post_request.return_value = None

        # Act
        result = _record_automated_test_run_impl(
            mock_client,
            product_id=55,
            test_name="test_user_login",
            short_message="Login test passed",
            long_message="Test passed",
            error_count=0,
            test_case_id=456,
            execution_status_id=2,
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "API_ERROR"
        assert "not recorded successfully" in result_data["error"]

    def test_record_test_run_api_missing_test_run_id(self):
        """Test error handling when API response missing TestRunId"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_post_request.return_value = {"SomeOtherField": "value"}

        # Act
        result = _record_automated_test_run_impl(
            mock_client,
            product_id=55,
            test_name="test_user_login",
            short_message="Login test passed",
            long_message="Test passed",
            error_count=0,
            test_case_id=456,
            execution_status_id=2,
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "API_ERROR"
        assert "ID not returned" in result_data["error"]

    def test_record_test_run_api_exception(self):
        """Test error handling when API raises exception"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_post_request.side_effect = Exception("Connection timeout")

        # Act
        result = _record_automated_test_run_impl(
            mock_client,
            product_id=55,
            test_name="test_user_login",
            short_message="Login test passed",
            long_message="Test passed",
            error_count=0,
            test_case_id=456,
            execution_status_id=2,
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "API_ERROR"
        assert "Connection timeout" in result_data["error"]

    def test_record_test_run_all_execution_statuses(self):
        """Test recording test runs with all valid execution statuses"""
        # Arrange
        mock_client = MagicMock()
        execution_statuses = [1, 2, 3, 4, 5, 6]

        for status_id in execution_statuses:
            mock_client.make_spira_api_post_request.return_value = {"TestRunId": 100 + status_id}

            # Act
            result = _record_automated_test_run_impl(
                mock_client,
                product_id=55,
                test_name="test_user_login",
                short_message="Test result",
                long_message="Test details",
                error_count=0,
                test_case_id=456,
                execution_status_id=status_id,
            )

            # Assert
            result_data = json.loads(result)
            assert result_data["data"]["test_run_id"] == f"TR:{100 + status_id}"
            assert result_data["data"]["message"] == "Test run recorded successfully"
