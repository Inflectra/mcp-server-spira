"""
Unit tests for create_build tool
"""

import json
from unittest.mock import MagicMock

from mcp_server_spira.features.automation.tools.builds import _create_build_url_impl


class TestCreateBuild:
    """Test suite for create_build tool"""

    def test_create_build_success(self):
        """Test successful build creation"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_post_request.return_value = {"BuildId": 123}

        # Act
        result = _create_build_url_impl(
            mock_client,
            product_id=55,
            release_id=10,
            build_status_id=2,
            name="Build 2024-02-13 v1.5.0",
            description="Production build with bug fixes",
            commits=["abc123def", "456ghi789"],
        )

        # Assert
        result_data = json.loads(result)
        assert result_data["data"]["build_id"] == "BL:123"
        assert result_data["data"]["message"] == "Build created successfully"
        mock_client.make_spira_api_post_request.assert_called_once()

    def test_create_build_failed_status(self):
        """Test creating a build with failed status"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_post_request.return_value = {"BuildId": 456}

        # Act
        result = _create_build_url_impl(
            mock_client,
            product_id=55,
            release_id=10,
            build_status_id=1,
            name="Build 2024-02-13 v1.5.0",
            description="Build failed due to compilation errors",
            commits=[],
        )

        # Assert
        result_data = json.loads(result)
        assert result_data["data"]["build_id"] == "BL:456"
        assert result_data["data"]["message"] == "Build created successfully"

    def test_create_build_no_commits(self):
        """Test creating a build with no commits"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_post_request.return_value = {"BuildId": 789}

        # Act
        result = _create_build_url_impl(
            mock_client,
            product_id=55,
            release_id=10,
            build_status_id=2,
            name="Build 2024-02-13 v1.5.0",
            description="Build with no commits",
            commits=[],
        )

        # Assert
        result_data = json.loads(result)
        assert result_data["data"]["build_id"] == "BL:789"
        assert result_data["data"]["message"] == "Build created successfully"

    def test_create_build_invalid_product_id_negative(self):
        """Test validation error for negative product_id"""
        # Arrange
        mock_client = MagicMock()

        # Act
        result = _create_build_url_impl(
            mock_client,
            product_id=-1,
            release_id=10,
            build_status_id=2,
            name="Build 2024-02-13 v1.5.0",
            description="Test build",
            commits=[],
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "INVALID_PARAMETER"
        assert "product_id" in result_data["details"]["parameter"]

    def test_create_build_invalid_product_id_zero(self):
        """Test validation error for zero product_id"""
        # Arrange
        mock_client = MagicMock()

        # Act
        result = _create_build_url_impl(
            mock_client,
            product_id=0,
            release_id=10,
            build_status_id=2,
            name="Build 2024-02-13 v1.5.0",
            description="Test build",
            commits=[],
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "INVALID_PARAMETER"

    def test_create_build_invalid_release_id_negative(self):
        """Test validation error for negative release_id"""
        # Arrange
        mock_client = MagicMock()

        # Act
        result = _create_build_url_impl(
            mock_client,
            product_id=55,
            release_id=-1,
            build_status_id=2,
            name="Build 2024-02-13 v1.5.0",
            description="Test build",
            commits=[],
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "INVALID_PARAMETER"
        assert "release_id" in result_data["details"]["parameter"]

    def test_create_build_invalid_release_id_zero(self):
        """Test validation error for zero release_id"""
        # Arrange
        mock_client = MagicMock()

        # Act
        result = _create_build_url_impl(
            mock_client,
            product_id=55,
            release_id=0,
            build_status_id=2,
            name="Build 2024-02-13 v1.5.0",
            description="Test build",
            commits=[],
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "INVALID_PARAMETER"

    def test_create_build_invalid_build_status_zero(self):
        """Test validation error for invalid build_status_id (0)"""
        # Arrange
        mock_client = MagicMock()

        # Act
        result = _create_build_url_impl(
            mock_client,
            product_id=55,
            release_id=10,
            build_status_id=0,
            name="Build 2024-02-13 v1.5.0",
            description="Test build",
            commits=[],
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "INVALID_PARAMETER"
        assert "build_status_id" in result_data["details"]["parameter"]

    def test_create_build_invalid_build_status_three(self):
        """Test validation error for invalid build_status_id (3)"""
        # Arrange
        mock_client = MagicMock()

        # Act
        result = _create_build_url_impl(
            mock_client,
            product_id=55,
            release_id=10,
            build_status_id=3,
            name="Build 2024-02-13 v1.5.0",
            description="Test build",
            commits=[],
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "INVALID_PARAMETER"
        assert "build_status_id" in result_data["details"]["parameter"]

    def test_create_build_empty_name(self):
        """Test validation error for empty name"""
        # Arrange
        mock_client = MagicMock()

        # Act
        result = _create_build_url_impl(
            mock_client,
            product_id=55,
            release_id=10,
            build_status_id=2,
            name="",
            description="Test build",
            commits=[],
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "INVALID_PARAMETER"
        assert "name" in result_data["details"]["parameter"]

    def test_create_build_whitespace_name(self):
        """Test validation error for whitespace-only name"""
        # Arrange
        mock_client = MagicMock()

        # Act
        result = _create_build_url_impl(
            mock_client,
            product_id=55,
            release_id=10,
            build_status_id=2,
            name="   ",
            description="Test build",
            commits=[],
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "INVALID_PARAMETER"
        assert "name" in result_data["details"]["parameter"]

    def test_create_build_api_returns_none(self):
        """Test error handling when API returns None"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_post_request.return_value = None

        # Act
        result = _create_build_url_impl(
            mock_client,
            product_id=55,
            release_id=10,
            build_status_id=2,
            name="Build 2024-02-13 v1.5.0",
            description="Test build",
            commits=[],
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "API_ERROR"
        assert "not created successfully" in result_data["error"]

    def test_create_build_api_missing_build_id(self):
        """Test error handling when API response missing BuildId"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_post_request.return_value = {"SomeOtherField": "value"}

        # Act
        result = _create_build_url_impl(
            mock_client,
            product_id=55,
            release_id=10,
            build_status_id=2,
            name="Build 2024-02-13 v1.5.0",
            description="Test build",
            commits=[],
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "API_ERROR"
        assert "ID not returned" in result_data["error"]

    def test_create_build_api_exception(self):
        """Test error handling when API raises exception"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_post_request.side_effect = Exception("Connection timeout")

        # Act
        result = _create_build_url_impl(
            mock_client,
            product_id=55,
            release_id=10,
            build_status_id=2,
            name="Build 2024-02-13 v1.5.0",
            description="Test build",
            commits=[],
        )

        # Assert
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["error_code"] == "API_ERROR"
        assert "Connection timeout" in result_data["error"]

    def test_create_build_multiple_commits(self):
        """Test creating a build with multiple commits"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_post_request.return_value = {"BuildId": 999}
        commits = ["abc123", "def456", "ghi789", "jkl012"]

        # Act
        result = _create_build_url_impl(
            mock_client,
            product_id=55,
            release_id=10,
            build_status_id=2,
            name="Build 2024-02-13 v1.5.0",
            description="Build with multiple commits",
            commits=commits,
        )

        # Assert
        result_data = json.loads(result)
        assert result_data["data"]["build_id"] == "BL:999"
        assert result_data["data"]["message"] == "Build created successfully"

        # Verify the API was called with correct revisions
        call_args = mock_client.make_spira_api_post_request.call_args
        body = call_args[0][1]
        assert len(body["Revisions"]) == 4
        assert all(rev["RevisionKey"] in commits for rev in body["Revisions"])

    def test_create_build_preserves_all_fields(self):
        """Test that all input fields are preserved in API request"""
        # Arrange
        mock_client = MagicMock()
        mock_client.make_spira_api_post_request.return_value = {"BuildId": 111}

        # Act
        result = _create_build_url_impl(
            mock_client,
            product_id=55,
            release_id=10,
            build_status_id=2,
            name="Test Build",
            description="Test Description",
            commits=["commit1"],
        )

        # Assert
        result_data = json.loads(result)
        assert result_data["data"]["build_id"] == "BL:111"

        # Verify API call
        call_args = mock_client.make_spira_api_post_request.call_args
        url = call_args[0][0]
        body = call_args[0][1]

        assert url == "projects/55/releases/10/builds"
        assert body["ProjectId"] == 55
        assert body["ReleaseId"] == 10
        assert body["BuildStatusId"] == 2
        assert body["Name"] == "Test Build"
        assert body["Description"] == "Test Description"
        assert len(body["Revisions"]) == 1
        assert body["Revisions"][0]["RevisionKey"] == "commit1"


class TestCreateBuildMCPWrapper:
    """Test suite for MCP wrapper of create_build"""

    def test_mcp_wrapper_success(self):
        """Test MCP wrapper with successful execution"""
        from unittest.mock import MagicMock, patch

        from mcp_server_spira.features.automation.tools.builds import register_tools

        # Create mock MCP server
        mock_mcp = MagicMock()
        tool_func = None

        def capture_tool(**kwargs):
            def decorator(func):
                nonlocal tool_func
                tool_func = func
                return func

            return decorator

        mock_mcp.tool = capture_tool
        register_tools(mock_mcp)

        # Mock the Spira client
        with patch(
            "mcp_server_spira.features.automation.tools.builds.get_spira_client"
        ) as mock_get_client:
            mock_client = MagicMock()
            mock_client.make_spira_api_post_request.return_value = {"BuildId": 123}
            mock_get_client.return_value = mock_client

            # Call the tool
            assert tool_func is not None
            result = tool_func(
                product_id=55,
                release_id=10,
                build_status_id=2,
                name="Build v1.0",
                description="Test build",
                commits=["abc123"],
            )

            # Verify result
            result_data = json.loads(result)
            assert result_data["data"]["build_id"] == "BL:123"

    def test_mcp_wrapper_exception_handling(self):
        """Test MCP wrapper handles exceptions from implementation"""
        from unittest.mock import MagicMock, patch

        from mcp_server_spira.features.automation.tools.builds import register_tools

        # Create mock MCP server
        mock_mcp = MagicMock()
        tool_func = None

        def capture_tool(**kwargs):
            def decorator(func):
                nonlocal tool_func
                tool_func = func
                return func

            return decorator

        mock_mcp.tool = capture_tool
        register_tools(mock_mcp)

        # Mock get_spira_client to raise exception
        with patch(
            "mcp_server_spira.features.automation.tools.builds.get_spira_client"
        ) as mock_get_client:
            mock_get_client.side_effect = Exception("Connection failed")

            # Call the tool
            assert tool_func is not None
            result = tool_func(
                product_id=55,
                release_id=10,
                build_status_id=2,
                name="Build v1.0",
                description="Test build",
                commits=[],
            )

            # Verify error response
            result_data = json.loads(result)
            assert "error" in result_data
            assert result_data["error_code"] == "API_ERROR"
            assert "Connection failed" in result_data["error"]
