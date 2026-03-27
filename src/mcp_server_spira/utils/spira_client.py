"""
Inflectra Spira client utilities.

This module provides helper functions for connecting to Inflectra Spira.
"""

import os
from typing import Any

import httpx

# Constants
USER_AGENT = "mcp-server/1.0"
API_ENDPOINT_URL = "/Services/v7_0/RestService.svc"


def get_base_url() -> str | None:
    """Gets the Inflectra Spira base URL from environment variables."""
    return os.environ.get("INFLECTRA_SPIRA_BASE_URL")


def get_credentials() -> tuple[str | None, str | None]:
    """Get Inflectra Spira credentials from environment variables."""
    username = os.environ.get("INFLECTRA_SPIRA_USERNAME")
    api_key = os.environ.get("INFLECTRA_SPIRA_API_KEY")
    return username, api_key


class SpiraClient:
    """
    Async HTTP client for the Inflectra Spira REST API.

    Uses httpx.AsyncClient so all tool functions can be async,
    keeping the FastMCP event loop unblocked when multiple tools
    are called in sequence.
    """

    def __init__(self, base_url: str, username: str, api_key: str):
        if base_url is None:
            raise ValueError(
                "INFLECTRA_SPIRA_BASE_URL needs to be populated as an environment variable!"
            )
        if username is None:
            raise ValueError(
                "INFLECTRA_SPIRA_USERNAME needs to be populated as an environment variable!"
            )
        if api_key is None:
            raise ValueError(
                "INFLECTRA_SPIRA_API_KEY needs to be populated as an environment variable!"
            )

        self.base_url = base_url
        self.username = username
        self.api_key = api_key
        self._headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "username": self.username,
            "api-key": self.api_key,
        }
        self._http_client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the underlying HTTP client and release resources."""
        await self._http_client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    def _full_url(self, url: str) -> str:
        return self.base_url + API_ENDPOINT_URL + "/" + url

    async def make_spira_api_get_request(self, url: str) -> Any:
        """Makes an async HTTP GET request to the Spira REST API."""
        try:
            response = await self._http_client.get(self._full_url(url), headers=self._headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(
                f"Error returned when calling the Spira REST API. The error message was: {e}"
            ) from e

    async def make_spira_api_post_request(self, url: str, json: dict[str, Any] | list[Any]) -> Any:
        """Makes an async HTTP POST request to the Spira REST API."""
        try:
            response = await self._http_client.post(
                url=self._full_url(url), json=json, headers=self._headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(
                f"Error returned when calling the Spira REST API. The error message was: {e}"
            ) from e

    async def make_spira_api_put_request(self, url: str, json: dict[str, Any] | list[Any]) -> Any:
        """Makes an async HTTP PUT request to the Spira REST API."""
        try:
            response = await self._http_client.put(
                url=self._full_url(url), json=json, headers=self._headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(
                f"Error returned when calling the Spira REST API. The error message was: {e}"
            ) from e

    async def make_spira_api_delete_request(self, url: str) -> Any:
        """Makes an async HTTP DELETE request to the Spira REST API."""
        try:
            response = await self._http_client.delete(
                url=self._full_url(url), headers=self._headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(
                f"Error returned when calling the Spira REST API. The error message was: {e}"
            ) from e


_client_instance: SpiraClient | None = None


def get_client() -> SpiraClient:
    """
    Returns a singleton SpiraClient instance, creating it on first call.

    Reusing a single client (and its underlying httpx.AsyncClient connection
    pool) avoids the overhead of creating a new HTTP client on every tool call.
    """
    global _client_instance
    if _client_instance is None:
        base_url = get_base_url()
        username, api_key = get_credentials()
        _client_instance = SpiraClient(base_url, username, api_key)  # type: ignore[arg-type]
    return _client_instance


def reset_client() -> None:
    """Reset the singleton client (useful for testing or credential changes)."""
    global _client_instance
    _client_instance = None
