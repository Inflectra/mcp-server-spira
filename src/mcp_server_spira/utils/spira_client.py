"""
Inflectra Spira client utilities.

This module provides helper functions for connecting to Inflectra Spira.
"""
import os
import httpx
from typing import Optional, Tuple, Any

# Constants
USER_AGENT = "mcp-server/1.0"

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

def make_spira_api_get_request(url: str) -> dict[str, Any] | None:
    """Make a request to the Spira REST API with proper error handling."""
    base_url = get_base_url()
    username, api_key = get_credentials()

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "username": username,
        "api-key": api_key
    }
    
    with httpx.Client() as client:
        try:
            response = client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None