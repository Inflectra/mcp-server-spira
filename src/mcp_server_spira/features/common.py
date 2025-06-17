"""
Common utilities for Inflectra Spira features.

This module provides shared functionality used by both tools and resources.
"""
from mcp_server_spira.utils.spira_client import SpiraClient, get_client

def get_spira_client() -> SpiraClient:
    """
    Get the Spira API client.
    
    Returns:
        SpiraClient instance
        
    """
    # Get Spira client
    spira_client = get_client()        
    return spira_client
