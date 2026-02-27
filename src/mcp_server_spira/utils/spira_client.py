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
    """
    Gets the Inflectra Spira base URL from environment variables

    Returns:
        String containing the base URL for your instance of Inflectra Spira
    """
    base_url = os.environ.get("INFLECTRA_SPIRA_BASE_URL")
    return base_url


def get_credentials() -> tuple[str | None, str | None]:
    """
    Get Inflectra Spira credentials from environment variables.

    Returns:
        Tuple containing (username, api_key)
    """
    username = os.environ.get("INFLECTRA_SPIRA_USERNAME")
    api_key = os.environ.get("INFLECTRA_SPIRA_API_KEY")
    return username, api_key


class SpiraClient:
    def __init__(self, base_url: str, username: str, api_key: str):
        # Validate credentials at construction time
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
        self._http_client = httpx.Client(timeout=30.0)

    def close(self):
        """Close the underlying HTTP client and release resources."""
        self._http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _full_url(self, url: str) -> str:
        return self.base_url + API_ENDPOINT_URL + "/" + url

    def make_spira_api_get_request(self, url: str) -> Any:
        """
        Makes an HTTP GET request to the Spira REST API with proper error handling.

        Args:
            url: The Relative URL for the specific REST resouce being called

        Returns:
            List or Dictionary containing the JSON returned from the API
        """
        try:
            response = self._http_client.get(self._full_url(url), headers=self._headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(
                f"Error returned when calling the Spira REST API. The error message was: {e}"
            ) from e

    def make_spira_api_post_request(self, url: str, json: dict[str, Any] | list[Any]) -> Any:
        """
        Makes an HTTP POST request to the Spira REST API with proper error handling.

        Args:
            url: The Relative URL for the specific REST resouce being called
            json: The JSON body of the POST request being sent to the REST resource

        Returns:
            List or Dictionary containing the JSON returned from the API
        """
        try:
            response = self._http_client.post(
                url=self._full_url(url), json=json, headers=self._headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(
                f"Error returned when calling the Spira REST API. The error message was: {e}"
            ) from e

    def make_spira_api_put_request(self, url: str, json: dict[str, Any] | list[Any]) -> Any:
        """
        Makes an HTTP PUT request to the Spira REST API with proper error handling.

        Args:
            url: The Relative URL for the specific REST resouce being called
            json: The JSON body of the POST request being sent to the REST resource

        Returns:
            List or Dictionary containing the JSON returned from the API
        """
        try:
            response = self._http_client.put(
                url=self._full_url(url), json=json, headers=self._headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(
                f"Error returned when calling the Spira REST API. The error message was: {e}"
            ) from e

    def make_spira_api_delete_request(self, url: str) -> Any:
        """
        Makes an HTTP DELETE request to the Spira REST API with proper error handling.

        Args:
            url: The Relative URL for the specific REST resouce being called

        Returns:
            List or Dictionary containing the JSON returned from the API
        """
        try:
            response = self._http_client.delete(url=self._full_url(url), headers=self._headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(
                f"Error returned when calling the Spira REST API. The error message was: {e}"
            ) from e


def get_client() -> SpiraClient:
    # Get the base url, login and api key
    base_url = get_base_url()
    username, api_key = get_credentials()

    # Create the Spira client (constructor validates None values and raises ValueError)
    spira_client = SpiraClient(base_url, username, api_key)  # type: ignore[arg-type]
    return spira_client
