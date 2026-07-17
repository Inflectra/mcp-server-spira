"""Common utilities for MCP tools."""

from mcp_server_spira.utils.spira_client import (
    SpiraApiError,
    SpiraAuthError,
    SpiraClient,
    SpiraNotFoundError,
    SpiraRateLimitError,
    SpiraValidationError,
    _sanitize_error,
    get_client,
)

from .pagination import paginate_client_side, paginate_server_side
from .responses import ErrorCodes, format_error_response, format_success_response
from .validation import ParameterValidator


def get_spira_client() -> SpiraClient:
    """
    Get the Spira API client.

    Returns:
        SpiraClient instance
    """
    return get_client()


__all__ = [
    "ErrorCodes",
    "ParameterValidator",
    "SpiraApiError",
    "SpiraAuthError",
    "SpiraNotFoundError",
    "SpiraRateLimitError",
    "SpiraValidationError",
    "_sanitize_error",
    "format_error_response",
    "format_success_response",
    "get_spira_client",
    "paginate_client_side",
    "paginate_server_side",
]
