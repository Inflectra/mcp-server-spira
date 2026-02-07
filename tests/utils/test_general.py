"""Unit tests for general utility functions."""

from mcp_server_spira.utils.general import get_execution_status_name


class TestGetExecutionStatusName:
    """Tests for get_execution_status_name function."""

    def test_status_failed(self):
        """Test that status ID 1 returns 'Failed'."""
        assert get_execution_status_name(1) == "Failed"

    def test_status_passed(self):
        """Test that status ID 2 returns 'Passed'."""
        assert get_execution_status_name(2) == "Passed"

    def test_status_not_run(self):
        """Test that status ID 3 returns 'Not Run'."""
        assert get_execution_status_name(3) == "Not Run"

    def test_status_na(self):
        """Test that status ID 4 returns 'N/A'."""
        assert get_execution_status_name(4) == "N/A"

    def test_status_blocked(self):
        """Test that status ID 5 returns 'Blocked'."""
        assert get_execution_status_name(5) == "Blocked"

    def test_status_caution(self):
        """Test that status ID 6 returns 'Caution'."""
        assert get_execution_status_name(6) == "Caution"

    def test_status_none(self):
        """Test that None returns empty string."""
        assert get_execution_status_name(None) == ""

    def test_status_unknown(self):
        """Test that unknown status ID returns '(Unknown)'."""
        assert get_execution_status_name(99) == "(Unknown)"
        assert get_execution_status_name(0) == "(Unknown)"
        assert get_execution_status_name(-1) == "(Unknown)"
        assert get_execution_status_name(7) == "(Unknown)"

    def test_all_valid_statuses(self):
        """Test all valid status IDs return expected values."""
        expected = {
            1: "Failed",
            2: "Passed",
            3: "Not Run",
            4: "N/A",
            5: "Blocked",
            6: "Caution",
        }

        for status_id, expected_name in expected.items():
            assert get_execution_status_name(status_id) == expected_name
