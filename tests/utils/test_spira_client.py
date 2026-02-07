"""Unit tests for Spira client utilities."""

import os
from unittest.mock import MagicMock, patch

import httpx
import pytest

from mcp_server_spira.utils.spira_client import (
    SpiraClient,
    get_base_url,
    get_client,
    get_credentials,
)


class TestGetBaseUrl:
    """Tests for get_base_url function."""

    def test_returns_base_url_from_env(self):
        """Test that get_base_url returns value from environment variable."""
        with patch.dict(os.environ, {"INFLECTRA_SPIRA_BASE_URL": "https://test.spira.com"}):
            assert get_base_url() == "https://test.spira.com"

    def test_returns_none_when_not_set(self):
        """Test that get_base_url returns None when env var not set."""
        with patch.dict(os.environ, {}, clear=True):
            assert get_base_url() is None


class TestGetCredentials:
    """Tests for get_credentials function."""

    def test_returns_credentials_from_env(self):
        """Test that get_credentials returns values from environment variables."""
        with patch.dict(
            os.environ,
            {
                "INFLECTRA_SPIRA_USERNAME": "testuser",
                "INFLECTRA_SPIRA_API_KEY": "testapikey123",
            },
        ):
            username, api_key = get_credentials()
            assert username == "testuser"
            assert api_key == "testapikey123"

    def test_returns_none_when_not_set(self):
        """Test that get_credentials returns None values when env vars not set."""
        with patch.dict(os.environ, {}, clear=True):
            username, api_key = get_credentials()
            assert username is None
            assert api_key is None


class TestSpiraClientInit:
    """Tests for SpiraClient initialization."""

    def test_client_initialization(self):
        """Test that SpiraClient initializes with correct attributes."""
        client = SpiraClient("https://test.com", "user", "key")
        assert client.base_url == "https://test.com"
        assert client.username == "user"
        assert client.api_key == "key"


class TestSpiraClientGetRequest:
    """Tests for SpiraClient.make_spira_api_get_request method."""

    def test_successful_get_request(self):
        """Test successful GET request returns JSON data."""
        client = SpiraClient("https://test.com", "user", "key")

        mock_response = MagicMock()
        mock_response.json.return_value = {"TaskId": 1, "Name": "Test Task"}

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = client.make_spira_api_get_request("tasks")

            assert result == {"TaskId": 1, "Name": "Test Task"}
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert "https://test.com/Services/v7_0/RestService.svc/tasks" in call_args[0]

    def test_get_request_with_headers(self):
        """Test that GET request includes correct headers."""
        client = SpiraClient("https://test.com", "user", "key")

        mock_response = MagicMock()
        mock_response.json.return_value = []

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            client.make_spira_api_get_request("tasks")

            call_kwargs = mock_client.get.call_args[1]
            headers = call_kwargs["headers"]
            assert headers["username"] == "user"
            assert headers["api-key"] == "key"
            assert headers["Accept"] == "application/json"
            assert headers["Content-Type"] == "application/json"

    def test_get_request_raises_on_missing_base_url(self):
        """Test that GET request raises ValueError when base_url is None."""
        client = SpiraClient(None, "user", "key")

        with pytest.raises(ValueError, match="INFLECTRA_SPIRA_BASE_URL"):
            client.make_spira_api_get_request("tasks")

    def test_get_request_raises_on_missing_username(self):
        """Test that GET request raises ValueError when username is None."""
        client = SpiraClient("https://test.com", None, "key")

        with pytest.raises(ValueError, match="INFLECTRA_SPIRA_USERNAME"):
            client.make_spira_api_get_request("tasks")

    def test_get_request_raises_on_missing_api_key(self):
        """Test that GET request raises ValueError when api_key is None."""
        client = SpiraClient("https://test.com", "user", None)

        with pytest.raises(ValueError, match="INFLECTRA_SPIRA_API_KEY"):
            client.make_spira_api_get_request("tasks")

    def test_get_request_handles_http_error(self):
        """Test that GET request handles HTTP errors properly."""
        client = SpiraClient("https://test.com", "user", "key")

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__.return_value = mock_client
            mock_client.get.side_effect = httpx.HTTPStatusError(
                "404 Not Found", request=MagicMock(), response=MagicMock()
            )
            mock_client_class.return_value = mock_client

            with pytest.raises(Exception, match="Error returned when calling the Spira REST API"):
                client.make_spira_api_get_request("tasks")


class TestSpiraClientPostRequest:
    """Tests for SpiraClient.make_spira_api_post_request method."""

    def test_successful_post_request(self):
        """Test successful POST request returns JSON data."""
        client = SpiraClient("https://test.com", "user", "key")

        mock_response = MagicMock()
        mock_response.json.return_value = {"TaskId": 2, "Name": "New Task"}

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = client.make_spira_api_post_request("projects/1/tasks", {"Name": "New Task"})

            assert result == {"TaskId": 2, "Name": "New Task"}
            mock_client.post.assert_called_once()

    def test_post_request_with_list_json(self):
        """Test POST request with list JSON body."""
        client = SpiraClient("https://test.com", "user", "key")

        mock_response = MagicMock()
        mock_response.json.return_value = [{"TaskId": 1}, {"TaskId": 2}]

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = client.make_spira_api_post_request("tasks/search", [{"filter": "status"}])

            assert result == [{"TaskId": 1}, {"TaskId": 2}]

    def test_post_request_raises_on_missing_credentials(self):
        """Test that POST request raises ValueError when credentials missing."""
        client = SpiraClient(None, "user", "key")

        with pytest.raises(ValueError, match="INFLECTRA_SPIRA_BASE_URL"):
            client.make_spira_api_post_request("tasks", {})


class TestSpiraClientPutRequest:
    """Tests for SpiraClient.make_spira_api_put_request method."""

    def test_successful_put_request(self):
        """Test successful PUT request returns JSON data."""
        client = SpiraClient("https://test.com", "user", "key")

        mock_response = MagicMock()
        mock_response.json.return_value = {"TaskId": 1, "Name": "Updated Task"}

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__.return_value = mock_client
            mock_client.put.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = client.make_spira_api_put_request(
                "projects/1/tasks", {"TaskId": 1, "Name": "Updated Task"}
            )

            assert result == {"TaskId": 1, "Name": "Updated Task"}
            mock_client.put.assert_called_once()

    def test_put_request_raises_on_missing_credentials(self):
        """Test that PUT request raises ValueError when credentials missing."""
        client = SpiraClient("https://test.com", None, "key")

        with pytest.raises(ValueError, match="INFLECTRA_SPIRA_USERNAME"):
            client.make_spira_api_put_request("tasks", {})


class TestSpiraClientDeleteRequest:
    """Tests for SpiraClient.make_spira_api_delete_request method."""

    def test_successful_delete_request(self):
        """Test successful DELETE request returns JSON data."""
        client = SpiraClient("https://test.com", "user", "key")

        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__.return_value = mock_client
            mock_client.delete.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = client.make_spira_api_delete_request("projects/1/tasks/40")

            assert result == {"success": True}
            mock_client.delete.assert_called_once()

    def test_delete_request_raises_on_missing_credentials(self):
        """Test that DELETE request raises ValueError when credentials missing."""
        client = SpiraClient("https://test.com", "user", None)

        with pytest.raises(ValueError, match="INFLECTRA_SPIRA_API_KEY"):
            client.make_spira_api_delete_request("tasks/40")

    def test_delete_request_handles_http_error(self):
        """Test that DELETE request handles HTTP errors properly."""
        client = SpiraClient("https://test.com", "user", "key")

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__.return_value = mock_client
            mock_client.delete.side_effect = httpx.HTTPStatusError(
                "403 Forbidden", request=MagicMock(), response=MagicMock()
            )
            mock_client_class.return_value = mock_client

            with pytest.raises(Exception, match="Error returned when calling the Spira REST API"):
                client.make_spira_api_delete_request("tasks/40")


class TestGetClient:
    """Tests for get_client function."""

    def test_get_client_returns_spira_client(self):
        """Test that get_client returns a SpiraClient instance."""
        with patch.dict(
            os.environ,
            {
                "INFLECTRA_SPIRA_BASE_URL": "https://test.com",
                "INFLECTRA_SPIRA_USERNAME": "user",
                "INFLECTRA_SPIRA_API_KEY": "key",
            },
        ):
            client = get_client()
            assert isinstance(client, SpiraClient)
            assert client.base_url == "https://test.com"
            assert client.username == "user"
            assert client.api_key == "key"

    def test_get_client_with_none_values(self):
        """Test that get_client works even with None values (validation happens on request)."""
        with patch.dict(os.environ, {}, clear=True):
            client = get_client()
            assert isinstance(client, SpiraClient)
            assert client.base_url is None
            assert client.username is None
            assert client.api_key is None
