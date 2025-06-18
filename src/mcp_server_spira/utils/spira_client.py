"""
Inflectra Spira client utilities.

This module provides helper functions for connecting to Inflectra Spira.
"""
import os
import httpx
from typing import Optional, Tuple, Any

# Constants
USER_AGENT = "mcp-server/1.0"
API_ENDPOINT_URL = "/Services/v7_0/RestService.svc"

def get_base_url() -> Optional[str]:
    """
    Gets the Inflectra Spira base URL from environment variables
    
    Returns:
        String containing the base URL for your instance of Inflectra Spira
    """    
    base_url = os.environ.get("INFLECTRA_SPIRA_BASE_URL")
    return base_url

def get_credentials() -> Tuple[Optional[str], Optional[str]]:
    """
    Get Inflectra Spira credentials from environment variables.
    
    Returns:
        Tuple containing (username, api_key)
    """
    username = os.environ.get("INFLECTRA_SPIRA_USERNAME")
    api_key = os.environ.get("INFLECTRA_SPIRA_API_KEY")
    return username, api_key
        
class SpiraClient:
    def __init__(self, base_url, username, api_key):
        self.base_url = base_url
        self.username = username
        self.api_key = api_key

    def make_spira_api_get_request(self, url: str) -> dict[str, Any] | list[Any] | None:
        """
        Makes an HTTP GET request to the Spira REST API with proper error handling.

        Args:
            url: The Relative URL for the specific REST resouce being called
                    
        Returns:
            List or Dictionary containing the JSON returned from the API
        """

        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "username": self.username,
            "api-key": self.api_key
        }

        # Check that we have the appropriate settings populated
        if self.base_url is None:
            raise ValueError("INFLECTRA_SPIRA_BASE_URL needs to be populated as an environment variable!")
        if self.username is None:
            raise ValueError("INFLECTRA_SPIRA_USERNAME needs to be populated as an environment variable!")
        if self.api_key is None:
            raise ValueError("INFLECTRA_SPIRA_API_KEY needs to be populated as an environment variable!")        

        full_url = self.base_url + API_ENDPOINT_URL + '/' + url
        
        with httpx.Client() as client:
            try:
                response = client.get(full_url, headers=headers, timeout=30.0)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                raise Exception(f"Error returned when calling the Spira REST API. The error message was: {e}")

def get_client() -> SpiraClient:

    # Get the base url, login and api key
    base_url = get_base_url()
    username, api_key = get_credentials()

    # Create the Spira client
    spira_client = SpiraClient(base_url, username, api_key)
    return spira_client
