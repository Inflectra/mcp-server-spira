"""Batch creation logic — sequential POST with partial-failure semantics.

Owns the batch loop, partial-failure detection, and result accumulation.
Callers prepare items and an endpoint, then delegate the actual creation
loop to this module.

The interface is intentionally small: one async function, one result
dataclass. All partial-failure semantics are concentrated here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from mcp_server_spira.utils.spira_client import SpiraApiError

if TYPE_CHECKING:
    from mcp_server_spira.utils.spira_client import SpiraClient


@dataclass(frozen=True)
class BatchResult:
    """Outcome of a batch creation loop.

    Spec:
        - Frozen dataclass — immutable after construction
        - created: list of formatted ID strings (e.g. ["IN:42", "IN:43"])
        - failed_at_index: index of the first failed item, or None if all
          succeeded
        - error: human-readable error message for the failure, or None if
          all succeeded
        - error_code: machine-readable error code from the failure source
          (e.g. "API_ERROR", "INVALID_PARAMETER"), or None if all succeeded
        - is_partial_failure: True when some items succeeded before the
          failure (created is non-empty AND failed_at_index is not None)
        - is_complete_failure: True when the first item failed (created is
          empty AND failed_at_index is not None)
        - is_success: True when all items succeeded (failed_at_index is None)
    """

    created: list[str] = field(default_factory=list)
    failed_at_index: int | None = None
    error: str | None = None
    error_code: str | None = None

    @property
    def is_partial_failure(self) -> bool:
        """Some items succeeded, then one failed."""
        return self.failed_at_index is not None and len(self.created) > 0

    @property
    def is_complete_failure(self) -> bool:
        """The first item (or an early item with no prior success) failed."""
        return self.failed_at_index is not None and len(self.created) == 0

    @property
    def is_success(self) -> bool:
        """All items were created successfully."""
        return self.failed_at_index is None


@dataclass(frozen=True)
class ItemValidator:
    """Per-item validation rule applied inside the batch loop.

    Spec:
        - check: callable that takes (item, index) and returns an error
          message string if validation fails, or None if it passes
        - Validators run before the POST request for each item
        - A failed validation stops the batch (same as a POST failure)
    """

    check: Any  # Callable[[dict, int], str | None]


async def create_batch(
    spira_client: SpiraClient,
    endpoint: str,
    items: list[dict[str, Any]],
    *,
    id_field: str,
    id_prefix: str,
    item_validators: list[ItemValidator] | None = None,
    pre_post_transform: Any | None = None,
) -> BatchResult:
    """Execute a sequential batch creation loop with partial-failure semantics.

    Posts items one at a time to the given endpoint. On first failure,
    stops the batch and returns what was created so far.

    Args:
        spira_client: Async Spira API client.
        endpoint: The POST endpoint URL (already formatted with product_id etc.).
        items: List of item dicts to POST sequentially.
        id_field: The response field containing the created artifact's ID
            (e.g. "IncidentId").
        id_prefix: The prefix for formatted IDs (e.g. "IN").
        item_validators: Optional per-item validators run before each POST.
            If any validator returns an error string, the batch stops.
        pre_post_transform: Optional callable (item, index) → item that
            transforms the item dict just before POSTing. Used for
            type-specific transformations (e.g. build Revisions field).
            Must be synchronous.

    Returns:
        BatchResult with created IDs and optional failure info.

    Spec:
        - ALWAYS returns a BatchResult — never raises to the caller
        - Items are POSTed sequentially; first failure stops the batch
        - Failure modes detected:
          1. item_validator returns error string → batch stops
          2. SpiraApiError from POST → batch stops
          3. Empty/falsy response from POST → batch stops
          4. Response missing id_field → batch stops
        - On any failure: BatchResult has failed_at_index and error set
        - On success: BatchResult has all created IDs, no failure info
        - pre_post_transform is called after validators but before POST
        - All API calls use await (async def)
    """
    created: list[str] = []

    for i, item in enumerate(items):
        # Run per-item validators
        if item_validators:
            for validator in item_validators:
                error_msg = validator.check(item, i)
                if error_msg is not None:
                    return BatchResult(
                        created=created,
                        failed_at_index=i,
                        error=error_msg,
                        error_code="INVALID_PARAMETER",
                    )

        # Apply pre-POST transformation
        if pre_post_transform is not None:
            item = pre_post_transform(item, i)

        # POST the item
        try:
            response = await spira_client.make_spira_api_post_request(endpoint, item)
        except SpiraApiError as e:
            return BatchResult(
                created=created,
                failed_at_index=i,
                error=str(e),
                error_code=e.error_code,
            )

        # Validate response is non-empty
        if not response:
            return BatchResult(
                created=created,
                failed_at_index=i,
                error="API returned empty response",
                error_code="API_ERROR",
            )

        # Extract ID from response
        artifact_id = response.get(id_field) if isinstance(response, dict) else None
        if artifact_id is None:
            return BatchResult(
                created=created,
                failed_at_index=i,
                error=f"Response missing expected field '{id_field}'",
                error_code="API_ERROR",
            )

        created.append(f"{id_prefix}:{artifact_id}")

    return BatchResult(created=created)
