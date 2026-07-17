"""Pagination utilities for MCP tools."""

from typing import Any, TypedDict


class PaginationMetadata(TypedDict):
    """Pagination information for list responses."""

    limit: int
    offset: int
    returned_count: int
    total_count: int
    has_more: bool
    pagination_type: str


class PaginationResult(TypedDict):
    """Result of pagination operation."""

    data: list[Any]
    pagination: PaginationMetadata


def paginate_client_side(all_items: list[Any], limit: int, offset: int) -> PaginationResult:
    """
    Implements client-side pagination by slicing a list.

    This is used for API endpoints that don't support server-side pagination.
    The API returns all results, and we slice them in Python.

    Args:
        all_items: Complete list of items from API
        limit: Maximum number of items to return
        offset: Number of items to skip

    Returns:
        Dictionary with paginated data and metadata

    Spec:
        - ALWAYS returns a PaginationResult dict with "data" and
          "pagination" keys — never raises
        - data = all_items[offset : offset + limit] — standard Python
          slice semantics (no IndexError on out-of-bounds)
        - pagination.returned_count == len(data) — always matches actual
          slice length
        - pagination.total_count == len(all_items) — reflects full input
          regardless of offset/limit
        - pagination.has_more is True iff (offset + returned_count) <
          total_count — callers use this to decide whether to request
          another page
        - pagination.pagination_type == "client-side" — callers use this
          to distinguish from server-side pagination
        - Does NOT validate limit/offset (caller must validate first via
          ParameterValidator) — accepts any int without error
        - Does NOT mutate all_items — returns a slice (new list)

    Example:
        >>> items = [1, 2, 3, 4, 5]
        >>> result = paginate_client_side(items, limit=2, offset=1)
        >>> result["data"]
        [2, 3]
        >>> result["pagination"]["has_more"]
        True
    """
    total_count = len(all_items)
    paginated_items = all_items[offset : offset + limit]
    returned_count = len(paginated_items)
    has_more = (offset + returned_count) < total_count

    return {
        "data": paginated_items,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "returned_count": returned_count,
            "total_count": total_count,
            "has_more": has_more,
            "pagination_type": "client-side",
        },
    }


def paginate_server_side(
    items: list[Any], limit: int, offset: int, total_count: int
) -> PaginationResult:
    """
    Wraps server-side paginated results with metadata.

    This is used for API endpoints that support server-side pagination
    (start_row, number_rows parameters). The API returns only the requested
    page, and we add pagination metadata.

    Args:
        items: Items returned from API (already paginated)
        limit: Requested limit
        offset: Requested offset
        total_count: Total items available (from API response header or metadata)

    Returns:
        Dictionary with data and pagination metadata

    Spec:
        - ALWAYS returns a PaginationResult dict with "data" and
          "pagination" keys — never raises
        - data is the items list as-is (no slicing — server already
          paginated)
        - pagination.returned_count == len(items) — always matches actual
          items length, not the requested limit
        - pagination.total_count == total_count arg — passed through from
          caller (server-reported total)
        - pagination.has_more is True iff (offset + returned_count) <
          total_count — same formula as client-side for consistency
        - pagination.pagination_type == "server-side" — callers use this
          to distinguish from client-side pagination
        - Does NOT validate inputs — caller must ensure limit/offset are
          valid before calling
    """
    returned_count = len(items)
    has_more = (offset + returned_count) < total_count

    return {
        "data": items,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "returned_count": returned_count,
            "total_count": total_count,
            "has_more": has_more,
            "pagination_type": "server-side",
        },
    }
