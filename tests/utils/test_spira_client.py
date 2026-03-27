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
        with patch.dict(
            os.environ,
            {"INFLECTRA_SPIRA_BASE_URL": "https://test.spira.com"},
        ):
            assert get_base_url() == "https://test.spira.com"

    def test_returns_none_when_not_set(self):
        """Test that get_base_url returns None when env var not set."""
        with patch.dict(os.environ, {}, clear=True):
            assert get_base_url() is None


class TestGetCredentials:
    """Tests for get_credentials function."""

    def test_returns_credentials_from_env(self):
        """Test that get_credentials returns values from env variables."""
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
        """Test get_credentials returns None values when env vars not set."""
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

    def test_client_stores_persistent_http_client(self):
        """Test that SpiraClient stores a persistent _http_client."""
        client = SpiraClient("https://test.com", "user", "key")
        assert hasattr(client, "_http_client")

    def test_client_stores_headers(self):
        """Test that SpiraClient builds headers once in __init__."""
        client = SpiraClient("https://test.com", "user", "key")
        assert hasattr(client, "_headers")
        assert client._headers["username"] == "user"
        assert client._headers["api-key"] == "key"


class TestSpiraClientGetRequest:
    """Tests for SpiraClient.make_spira_api_get_request method."""

    @pytest.mark.asyncio
    async def test_successful_get_request(self):
        """Test successful GET request returns JSON data."""
        client = SpiraClient("https://test.com", "user", "key")

        mock_response = MagicMock()
        mock_response.json.return_value = {"TaskId": 1, "Name": "Test Task"}

        client._http_client = MagicMock()
        client._http_client.get.return_value = mock_response

        result = await client.make_spira_api_get_request("tasks")

        assert result == {"TaskId": 1, "Name": "Test Task"}
        client._http_client.get.assert_called_once()
        call_args = client._http_client.get.call_args
        assert "https://test.com/Services/v7_0/RestService.svc/tasks" in call_args[0]

    @pytest.mark.asyncio
    async def test_get_request_with_headers(self):
        """Test that GET request includes correct headers."""
        client = SpiraClient("https://test.com", "user", "key")

        mock_response = MagicMock()
        mock_response.json.return_value = []

        client._http_client = MagicMock()
        client._http_client.get.return_value = mock_response

        await client.make_spira_api_get_request("tasks")

        call_kwargs = client._http_client.get.call_args[1]
        headers = call_kwargs["headers"]
        assert headers["username"] == "user"
        assert headers["api-key"] == "key"
        assert headers["Accept"] == "application/json"
        assert headers["Content-Type"] == "application/json"

    def test_get_request_raises_on_missing_base_url(self):
        """Test that constructing with None base_url raises ValueError."""
        with pytest.raises(ValueError, match="INFLECTRA_SPIRA_BASE_URL"):
            SpiraClient(None, "user", "key")  # type: ignore[arg-type]

    def test_get_request_raises_on_missing_username(self):
        """Test that constructing with None username raises ValueError."""
        with pytest.raises(ValueError, match="INFLECTRA_SPIRA_USERNAME"):
            SpiraClient("https://test.com", None, "key")  # type: ignore[arg-type]

    def test_get_request_raises_on_missing_api_key(self):
        """Test that constructing with None api_key raises ValueError."""
        with pytest.raises(ValueError, match="INFLECTRA_SPIRA_API_KEY"):
            SpiraClient("https://test.com", "user", None)  # type: ignore[arg-type]

    @pytest.mark.asyncio
    async def test_get_request_handles_http_error(self):
        """Test that GET request handles HTTP errors properly."""
        client = SpiraClient("https://test.com", "user", "key")
        client._http_client = MagicMock()
        client._http_client.get.side_effect = httpx.HTTPStatusError(
            "404 Not Found",
            request=MagicMock(),
            response=MagicMock(),
        )
        with pytest.raises(
            Exception,
            match="Error returned when calling the Spira REST API",
        ):
            await client.make_spira_api_get_request("tasks")


class TestSpiraClientPostRequest:
    """Tests for SpiraClient.make_spira_api_post_request method."""

    @pytest.mark.asyncio
    async def test_successful_post_request(self):
        """Test successful POST request returns JSON data."""
        client = SpiraClient("https://test.com", "user", "key")

        mock_response = MagicMock()
        mock_response.json.return_value = {"TaskId": 2, "Name": "New Task"}

        client._http_client = MagicMock()
        client._http_client.post.return_value = mock_response

        result = await client.make_spira_api_post_request("projects/1/tasks", {"Name": "New Task"})

        assert result == {"TaskId": 2, "Name": "New Task"}
        client._http_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_request_with_list_json(self):
        """Test POST request with list JSON body."""
        client = SpiraClient("https://test.com", "user", "key")

        mock_response = MagicMock()
        mock_response.json.return_value = [{"TaskId": 1}, {"TaskId": 2}]

        client._http_client = MagicMock()
        client._http_client.post.return_value = mock_response

        result = await client.make_spira_api_post_request("tasks/search", [{"filter": "status"}])

        assert result == [{"TaskId": 1}, {"TaskId": 2}]

    def test_post_request_raises_on_missing_credentials(self):
        """Test that constructing with None base_url raises ValueError."""
        with pytest.raises(ValueError, match="INFLECTRA_SPIRA_BASE_URL"):
            SpiraClient(None, "user", "key")  # type: ignore[arg-type]


class TestSpiraClientPutRequest:
    """Tests for SpiraClient.make_spira_api_put_request method."""

    @pytest.mark.asyncio
    async def test_successful_put_request(self):
        """Test successful PUT request returns JSON data."""
        client = SpiraClient("https://test.com", "user", "key")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "TaskId": 1,
            "Name": "Updated Task",
        }

        client._http_client = MagicMock()
        client._http_client.put.return_value = mock_response

        result = await client.make_spira_api_put_request(
            "projects/1/tasks", {"TaskId": 1, "Name": "Updated Task"}
        )

        assert result == {"TaskId": 1, "Name": "Updated Task"}
        client._http_client.put.assert_called_once()

    def test_put_request_raises_on_missing_credentials(self):
        """Test that constructing with None username raises ValueError."""
        with pytest.raises(ValueError, match="INFLECTRA_SPIRA_USERNAME"):
            SpiraClient("https://test.com", None, "key")  # type: ignore[arg-type]


class TestSpiraClientDeleteRequest:
    """Tests for SpiraClient.make_spira_api_delete_request method."""

    @pytest.mark.asyncio
    async def test_successful_delete_request(self):
        """Test successful DELETE request returns JSON data."""
        client = SpiraClient("https://test.com", "user", "key")

        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}

        client._http_client = MagicMock()
        client._http_client.delete.return_value = mock_response

        result = await client.make_spira_api_delete_request("projects/1/tasks/40")

        assert result == {"success": True}
        client._http_client.delete.assert_called_once()

    def test_delete_request_raises_on_missing_credentials(self):
        """Test that constructing with None api_key raises ValueError."""
        with pytest.raises(ValueError, match="INFLECTRA_SPIRA_API_KEY"):
            SpiraClient("https://test.com", "user", None)  # type: ignore[arg-type]

    @pytest.mark.asyncio
    async def test_delete_request_handles_http_error(self):
        """Test that DELETE request handles HTTP errors properly."""
        client = SpiraClient("https://test.com", "user", "key")
        client._http_client = MagicMock()
        client._http_client.delete.side_effect = httpx.HTTPStatusError(
            "403 Forbidden",
            request=MagicMock(),
            response=MagicMock(),
        )
        with pytest.raises(
            Exception,
            match="Error returned when calling the Spira REST API",
        ):
            await client.make_spira_api_delete_request("tasks/40")


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
        """Test get_client raises ValueError when credentials are missing."""
        with (
            patch.dict(os.environ, {}, clear=True),
            pytest.raises(ValueError, match="INFLECTRA_SPIRA_BASE_URL"),
        ):
            get_client()
