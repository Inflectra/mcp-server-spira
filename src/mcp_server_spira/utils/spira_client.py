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


def _sanitize_error(exc: BaseException) -> str:
    """Return a safe, non-leaking error description for *exc*.

    httpx exceptions can embed the full request URL (including path
    parameters that may contain product IDs or other internal details).
    This function maps each exception type to a short, safe string that
    is suitable for inclusion in LLM-visible error messages.

    Spec:
        - ALWAYS returns a str — never raises, never returns None
        - Never includes the original exception message or URL — only
          the exception type or HTTP status code
        - HTTPStatusError → "HTTP {status_code}" (numeric only)
        - TimeoutException → "request timed out"
        - ConnectError → "connection error"
        - Other RequestError → "request error"
        - SpiraApiError → str(exc) (message is already sanitized)
        - Any other BaseException → type(exc).__name__ only (no .args,
          no str(exc)) — prevents leaking internal details to the LLM
    """
    if isinstance(exc, httpx.HTTPStatusError):
        return f"HTTP {exc.response.status_code}"
    if isinstance(exc, httpx.TimeoutException):
        return "request timed out"
    if isinstance(exc, httpx.ConnectError):
        return "connection error"
    if isinstance(exc, httpx.RequestError):
        return "request error"
    # SpiraApiError carries a pre-sanitized message — return it directly.
    if isinstance(exc, SpiraApiError):
        return str(exc)
    # Fallback for any other exception — use the type name only, not the
    # message, to avoid leaking internal details.
    return type(exc).__name__


def _extract_error_detail(response: httpx.Response) -> str:
    """Extract actionable error detail from an HTTP error response body.

    Spira returns validation errors as XML (ValidationFaultMessage) or
    JSON. This function extracts the human-readable message without
    exposing internal URLs or stack traces.

    Spec:
        - ALWAYS returns a str (may be empty) — never raises
        - For XML responses containing ValidationFaultMessage: extracts
          FieldName and Message from each ValidationFaultMessageItem,
          returns them as a semicolon-separated string
        - For XML responses containing a single <Message> element:
          extracts the text content
        - For JSON responses with a "Message" key: returns that value
        - For unrecognised formats: returns the first 200 chars of the
          response body (truncated) as a fallback
        - Empty response body → empty string
        - Never includes URLs, stack traces, or internal identifiers
    """
    try:
        text: str = response.text
        if not text or not text.strip():
            return ""

        # Try XML validation fault (most common Spira error format)
        if "<ValidationFaultMessage" in text:
            return _parse_validation_fault_xml(text)

        # Try XML with a single <Message> element
        if "<Message>" in text:
            import re

            match = re.search(r"<Message>(.*?)</Message>", text, re.DOTALL)
            if match:
                return match.group(1).strip()

        # Try JSON
        content_type = response.headers.get("content-type", "")
        if "json" in content_type:
            import json

            try:
                data = json.loads(text)
                if isinstance(data, dict) and "Message" in data:
                    return str(data["Message"])
            except (json.JSONDecodeError, ValueError):
                pass

        # Fallback: first 200 chars
        return text[:200].strip()
    except Exception:
        return ""


def _parse_validation_fault_xml(text: str) -> str:
    """Parse Spira's ValidationFaultMessage XML into a readable string.

    Example input:
        <ValidationFaultMessage ...>
          <Messages>
            <ValidationFaultMessageItem>
              <FieldName>Custom_07</FieldName>
              <Message>The field 'Difficulty' requires a value.</Message>
            </ValidationFaultMessageItem>
          </Messages>
          <Summary>Validation Fault</Summary>
        </ValidationFaultMessage>

    Returns: "Custom_07: The field 'Difficulty' requires a value."

    Spec:
        - ALWAYS returns a str — never raises
        - Extracts all ValidationFaultMessageItem entries
        - Each item formatted as "FieldName: Message"
        - Multiple items joined with "; "
        - If no items found, returns the Summary text if present
        - If parsing fails entirely, returns empty string
    """
    import re

    try:
        items = re.findall(
            r"<ValidationFaultMessageItem>\s*"
            r"<FieldName>(.*?)</FieldName>\s*"
            r"<Message>(.*?)</Message>\s*"
            r"</ValidationFaultMessageItem>",
            text,
            re.DOTALL,
        )
        if items:
            parts = [f"{field.strip()}: {msg.strip()}" for field, msg in items]
            return "; ".join(parts)

        # Fallback to Summary
        summary_match = re.search(r"<Summary>(.*?)</Summary>", text, re.DOTALL)
        if summary_match:
            return summary_match.group(1).strip()

        return ""
    except Exception:
        return ""


def get_base_url() -> str | None:
    """Gets the Inflectra Spira base URL from environment variables."""
    return os.environ.get("INFLECTRA_SPIRA_BASE_URL")


def get_credentials() -> tuple[str | None, str | None]:
    """Get Inflectra Spira credentials from environment variables."""
    username = os.environ.get("INFLECTRA_SPIRA_USERNAME")
    api_key = os.environ.get("INFLECTRA_SPIRA_API_KEY")
    return username, api_key


class SpiraApiError(Exception):
    """Domain-aware exception raised by SpiraClient on API failures.

    Carries a pre-sanitized message (safe for LLM output) and an error
    code from ``ErrorCodes`` that callers can use directly in
    ``format_error_response`` without guessing.

    Spec:
        - message is always a safe, non-leaking string — never contains
          raw URLs, request bodies, or internal identifiers
        - error_code is one of the ErrorCodes constants (API_ERROR,
          NOT_FOUND, AUTHENTICATION_ERROR, INVALID_PARAMETER, etc.)
        - status_code is the HTTP status code (int) when available,
          None for non-HTTP errors (timeout, connection)
        - str(error) returns the message — callers can use it directly
          in format_error_response without calling _sanitize_error
        - Subclasses (SpiraAuthError, SpiraNotFoundError,
          SpiraRateLimitError, SpiraValidationError) allow type-based
          dispatch at catch sites — existing ``except SpiraApiError``
          catches still work (backward compatible)
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: str = "API_ERROR",
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.status_code = status_code


class SpiraAuthError(SpiraApiError):
    """Raised on 401/403 — authentication or permission failure.

    Spec:
        - error_code is always "AUTHENTICATION_ERROR"
        - status_code is 401 or 403
        - Caught by ``except SpiraApiError`` (backward compatible)
        - Enables future re-auth flows without string comparison
    """

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message, error_code="AUTHENTICATION_ERROR", status_code=status_code)


class SpiraNotFoundError(SpiraApiError):
    """Raised on 404 — requested resource does not exist.

    Spec:
        - error_code is always "NOT_FOUND"
        - status_code is 404
        - Caught by ``except SpiraApiError`` (backward compatible)
    """

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message, error_code="NOT_FOUND", status_code=status_code)


class SpiraRateLimitError(SpiraApiError):
    """Raised on 429 — rate limit exceeded.

    Spec:
        - error_code is always "RATE_LIMIT_EXCEEDED"
        - status_code is 429
        - Caught by ``except SpiraApiError`` (backward compatible)
        - Enables future retry-with-backoff without string comparison
    """

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message, error_code="RATE_LIMIT_EXCEEDED", status_code=status_code)


class SpiraValidationError(SpiraApiError):
    """Raised on 4xx with validation fault detail.

    Spec:
        - error_code is always "INVALID_PARAMETER"
        - status_code is the original 4xx code
        - Caught by ``except SpiraApiError`` (backward compatible)
        - Enables callers to distinguish "bad input" from "server down"
    """

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message, error_code="INVALID_PARAMETER", status_code=status_code)


class SpiraClient:
    """
    Async HTTP client for the Inflectra Spira REST API.

    Uses httpx.AsyncClient so all tool functions can be async,
    keeping the FastMCP event loop unblocked when multiple tools
    are called in sequence.

    Spec:
        - All API methods (make_spira_api_*) are async def — callers
          MUST await them; sync calls block the event loop
        - All API methods raise SpiraApiError on any HTTP or network
          error — callers catch SpiraApiError and use str(e) directly
          for safe messages; error_code attribute provides the
          classification
        - Raised exceptions never expose raw URLs or request bodies
        - Constructor raises ValueError if any of base_url, username,
          api_key is None — fails fast at startup, not at first API call
        - Singleton pattern via get_client() — one httpx.AsyncClient
          connection pool shared across all tool calls
        - close() must be awaited to release the connection pool;
          supports async context manager protocol
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

    async def _request(self, method: str, url: str, body: Any = None) -> Any:
        """Single internal dispatch for all HTTP methods.

        Concentrates URL construction, error handling, and response parsing
        in one place. Public methods delegate here.

        Spec:
            - Returns the parsed JSON response body on success (any JSON type)
            - Raises SpiraApiError with a classified error_code on any HTTP
              or network error — never exposes raw URLs or request bodies
            - error_code classification:
              - 401, 403 → AUTHENTICATION_ERROR
              - 404 → NOT_FOUND
              - 429 → RATE_LIMIT_EXCEEDED
              - 4xx with ValidationFault → INVALID_PARAMETER
              - Other 4xx/5xx → API_ERROR
              - Timeout → API_ERROR (message: "request timed out")
              - Connection error → API_ERROR (message: "connection error")
            - For backward compatibility, SpiraApiError is a subclass of
              Exception — existing `except Exception` blocks still catch it
            - method must be one of "GET", "POST", "PUT", "DELETE"
            - body is passed as the `json` kwarg for POST/PUT; ignored for GET/DELETE
            - Must be awaited — blocking call if used synchronously
        """
        full_url = self._full_url(url)
        try:
            if method == "GET":
                response = await self._http_client.get(full_url, headers=self._headers)
            elif method == "POST":
                response = await self._http_client.post(
                    url=full_url, json=body, headers=self._headers
                )
            elif method == "PUT":
                response = await self._http_client.put(
                    url=full_url, json=body, headers=self._headers
                )
            elif method == "DELETE":
                response = await self._http_client.delete(full_url, headers=self._headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            detail = _extract_error_detail(e.response)
            message = f"HTTP {status} — {detail}" if detail else f"HTTP {status}"
            raise self._build_api_error(status, detail, message) from e
        except httpx.TimeoutException as e:
            raise SpiraApiError("request timed out", error_code="API_ERROR") from e
        except httpx.ConnectError as e:
            raise SpiraApiError("connection error", error_code="API_ERROR") from e
        except httpx.RequestError as e:
            raise SpiraApiError("request error", error_code="API_ERROR") from e
        except SpiraApiError:
            raise  # Don't re-wrap our own exceptions
        except Exception as e:
            raise SpiraApiError(_sanitize_error(e), error_code="API_ERROR") from e

    @staticmethod
    def _classify_http_error(status_code: int, detail: str) -> str:
        """Classify an HTTP status code into an error_code string.

        Spec:
            - 401, 403 → AUTHENTICATION_ERROR
            - 404 → NOT_FOUND
            - 429 → RATE_LIMIT_EXCEEDED
            - 4xx with "Validation" in detail → INVALID_PARAMETER
            - All other → API_ERROR
            - Pure function — no I/O, no side effects

        Note: Uses string literals matching ErrorCodes constants from
        responses.py to avoid circular imports (spira_client.py is
        imported by utils/common/__init__.py which re-exports ErrorCodes).
        """
        if status_code in (401, 403):
            return "AUTHENTICATION_ERROR"
        if status_code == 404:
            return "NOT_FOUND"
        if status_code == 429:
            return "RATE_LIMIT_EXCEEDED"
        if 400 <= status_code < 500 and "Validation" in detail:
            return "INVALID_PARAMETER"
        return "API_ERROR"

    @staticmethod
    def _build_api_error(status_code: int, detail: str, message: str) -> SpiraApiError:
        """Build the appropriate SpiraApiError subclass for an HTTP error.

        Spec:
            - Delegates classification to _classify_http_error (single source
              of truth for status-code → error_code mapping)
            - 401, 403 → SpiraAuthError
            - 404 → SpiraNotFoundError
            - 429 → SpiraRateLimitError
            - 4xx with "Validation" in detail → SpiraValidationError
            - All other → SpiraApiError (base class)
            - Pure function — no I/O, no side effects
            - Returned error always has correct error_code and status_code
        """
        error_code = SpiraClient._classify_http_error(status_code, detail)
        if error_code == "AUTHENTICATION_ERROR":
            return SpiraAuthError(message, status_code=status_code)
        if error_code == "NOT_FOUND":
            return SpiraNotFoundError(message, status_code=status_code)
        if error_code == "RATE_LIMIT_EXCEEDED":
            return SpiraRateLimitError(message, status_code=status_code)
        if error_code == "INVALID_PARAMETER":
            return SpiraValidationError(message, status_code=status_code)
        return SpiraApiError(message, error_code=error_code, status_code=status_code)

    async def make_spira_api_get_request(self, url: str) -> Any:
        """Makes an async HTTP GET request to the Spira REST API.

        Spec:
            - Returns the parsed JSON response body on success (any JSON
              type: list, dict, str, int, etc.)
            - Raises SpiraApiError with classified error_code on any HTTP
              error (4xx, 5xx) or network error — never exposes raw URLs
            - str(error) is a safe, pre-sanitized message
            - Must be awaited — blocking call if used synchronously
        """
        return await self._request("GET", url)

    async def make_spira_api_post_request(self, url: str, json: dict[str, Any] | list[Any]) -> Any:
        """Makes an async HTTP POST request to the Spira REST API.

        Spec:
            - Returns the parsed JSON response body on success
            - Raises SpiraApiError with classified error_code on any HTTP
              error or network error — never exposes raw URLs or request bodies
            - str(error) is a safe, pre-sanitized message
            - Must be awaited — blocking call if used synchronously
        """
        return await self._request("POST", url, body=json)

    async def make_spira_api_put_request(self, url: str, json: dict[str, Any] | list[Any]) -> Any:
        """Makes an async HTTP PUT request to the Spira REST API.

        Spec:
            - Returns the parsed JSON response body on success
            - Raises SpiraApiError with classified error_code on any HTTP
              error or network error — never exposes raw URLs or request bodies
            - str(error) is a safe, pre-sanitized message
            - Must be awaited — blocking call if used synchronously
        """
        return await self._request("PUT", url, body=json)

    async def make_spira_api_delete_request(self, url: str) -> Any:
        """Makes an async HTTP DELETE request to the Spira REST API.

        Spec:
            - Returns the parsed JSON response body on success
            - Raises SpiraApiError with classified error_code on any HTTP
              error or network error — never exposes raw URLs
            - str(error) is a safe, pre-sanitized message
            - Must be awaited — blocking call if used synchronously
        """
        return await self._request("DELETE", url)


_client_instance: SpiraClient | None = None


def get_client() -> SpiraClient:
    """
    Returns a singleton SpiraClient instance, creating it on first call.

    Reusing a single client (and its underlying httpx.AsyncClient connection
    pool) avoids the overhead of creating a new HTTP client on every tool call.

    Spec:
        - Returns the same SpiraClient instance on every call after the
          first — singleton pattern
        - First call reads INFLECTRA_SPIRA_BASE_URL, INFLECTRA_SPIRA_USERNAME,
          INFLECTRA_SPIRA_API_KEY from environment — raises ValueError
          (via SpiraClient.__init__) if any is missing
        - After reset_client(), the next call creates a fresh instance
          (re-reads env vars)
        - Thread-safety: not guaranteed — designed for single-threaded
          async event loop usage
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
