"""product_search_artifacts unified tool.

Config-driven search tool supporting server-side filtering, field projection,
multi-product fan-out, and include enrichment.

The product_get_artifact tool lives in product_get.py.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
from dataclasses import dataclass
from typing import Annotated, Any, NotRequired, TypedDict

from pydantic import WithJsonSchema

from mcp_server_spira.config import resolve_product_id
from mcp_server_spira.features.artifact_configs import ARTIFACT_CONFIG
from mcp_server_spira.features.custom_properties.filter_resolver import (
    resolve_custom_property_filters,
)
from mcp_server_spira.features.custom_properties.resolver import (
    CustomPropertyResolver,
)
from mcp_server_spira.features.search.filter_builder import (
    build_remote_filters,
    merge_date_range_filters,
)
from mcp_server_spira.features.search.name_resolver import NameResolver
from mcp_server_spira.features.search.template_context import TemplateContext
from mcp_server_spira.features.search.tools._include import (
    MAX_INCLUDE_RESULTS,
    resolve_includes,
)
from mcp_server_spira.models import ArtifactConfig
from mcp_server_spira.utils.common import SpiraApiError, _sanitize_error, get_spira_client
from mcp_server_spira.utils.common.responses import (
    ErrorCodes,
    format_error_response,
    format_multi_product_response,
    format_search_response,
)
from mcp_server_spira.utils.common.validation import ParameterValidator

# Derived from ArtifactConfig — product-scoped types only.
PRODUCT_ARTIFACT_TYPES: tuple[str, ...] = tuple(
    name for name, cfg in ARTIFACT_CONFIG.items() if cfg.workspace_type == "product"
)

# Type hint for the tool signature — advertises valid values in the JSON
# schema (so the LLM sees them in tools/list) but accepts any string at
# Pydantic validation time.  Actual validation happens in _impl functions
# via ParameterValidator, which returns our standard error envelope.
ProductArtifactType = Annotated[
    str,
    WithJsonSchema(
        {
            "type": "string",
            "enum": list(PRODUCT_ARTIFACT_TYPES),
        }
    ),
]


def _coerce_product_ids(product_ids: Any) -> list[int] | str:
    """Silently coerce product_ids to a list of ints.

    Returns a ``list[int]`` on success, or an error-response JSON string
    on failure.

    Coercion rules:
    - ``None`` → resolve from env default; error if unavailable.
    - bare ``int`` → ``[int]``
    - string parseable as int → ``[int]``
    - ``list[int]`` → pass through
    - anything else → ``INVALID_PARAMETER`` error string

    Spec:
        - ALWAYS returns either list[int] or a JSON error string — never raises
        - None input resolves from SPIRA_PROJECT_ID env; returns error string
          (not exception) when env is also unset
        - Bare int and int-parseable string both coerce to single-element list,
          enabling callers to route to single-product path without type-checking
        - list input is passed through without element validation (caller is
          responsible for element types); empty list returns error string
        - Error string is a valid JSON object with error_code=INVALID_PARAMETER
          — callers return it directly without further wrapping
    """
    if product_ids is None:
        resolved = resolve_product_id(None)
        if resolved is None:
            return format_error_response(
                error="product_ids is required",
                error_code=ErrorCodes.INVALID_PARAMETER,
                details={"parameter": "product_ids"},
                suggestion=(
                    "Pass product_ids explicitly or set SPIRA_PROJECT_ID in your environment."
                ),
            )
        return [resolved]

    if isinstance(product_ids, int):
        return [product_ids]

    if isinstance(product_ids, str):
        try:
            return [int(product_ids)]
        except ValueError:
            return format_error_response(
                error="Invalid product_ids parameter",
                error_code=ErrorCodes.INVALID_PARAMETER,
                details={"parameter": "product_ids", "value": product_ids},
                suggestion="product_ids must be an integer or list of integers.",
            )

    if isinstance(product_ids, list):
        if not product_ids:
            return format_error_response(
                error="product_ids must not be empty",
                error_code=ErrorCodes.INVALID_PARAMETER,
                details={"parameter": "product_ids", "value": "[]"},
                suggestion="Pass at least one product ID.",
            )
        return product_ids

    return format_error_response(
        error="Invalid product_ids parameter",
        error_code=ErrorCodes.INVALID_PARAMETER,
        details={"parameter": "product_ids", "value": str(product_ids)},
        suggestion="product_ids must be an integer or list of integers.",
    )


def _build_search_url(
    config: ArtifactConfig,
    product_id: int,
    release_id: int | str | None,
    starting_row: int,
    effective_rows: int,
) -> str:
    """Build the full search endpoint URL with config-driven query parameters.

    Thin wrapper around ``config.build_search_url()`` — kept for backward
    compatibility with existing test imports.

    Spec:
        - Pure function — delegates entirely to ArtifactConfig.build_search_url
        - Returns a URL string with query parameters appended
        - All config.search_query_params roles are represented in the URL
        - release_id query param is only included when release_id is not None
        - Never raises for any valid config
    """
    return config.build_search_url(
        starting_row=starting_row,
        number_of_rows=effective_rows,
        release_id=release_id,
        product_id=product_id,
    )


# ---------------------------------------------------------------------------
# Request / Response dataclasses for the search pipeline
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProductSearchRequest:
    """Parameters for a single-product search invocation.

    Constructed once per product in the search pipeline. Immutable —
    the pipeline reads from it but never mutates it.

    Spec:
        - Frozen dataclass — constructed once, never mutated. Enables safe
          sharing across async tasks and makes data flow explicit.
        - One request per product in multi-product fan-out. Each product gets
          its own ProductSearchRequest with identical filter params but a
          different product_id.
        - release_id stays as int | str | None on the request. Resolution of
          version strings happens inside the pipeline (step 0b), not before
          construction. Rationale: resolution needs resolver + product_id +
          config, which are only available inside the pipeline.
        - include_types carries already-resolved include type
          strings (sub-artifacts or comments). Resolution happens in
          _product_search_impl before request construction. Named to
          eliminate confusion with artifact_type_filter.
        - filters (Tier 2) is passed through as-is — a list of dicts with
          field/operator/value keys. Validation happens in build_remote_filters.
        - All Tier 1 filter params are explicit fields (not a dict) for type
          safety and discoverability. The cost is a few extra None fields;
          the benefit is uniform handling in the resolver.
    """

    # --- Required ---
    artifact_type: str  # e.g. "incident", "task" — selects ArtifactConfig
    product_id: int  # Spira ProjectId — scopes the search

    # --- Field projection ---
    fields: list[str] | None = None  # Which fields to return; None → summary defaults

    # --- Tier 1 filters (generic — apply to most artifact types) ---
    status: str | None = None  # Display name or ID; resolved via template metadata
    priority: str | None = None  # Display name or ID; "importance" for requirements
    release_id: int | str | None = None  # Int ID or version string like "1.0.0"
    owner_id: int | None = None  # User ID to filter by owner
    current_user: bool = False  # If True, resolve authenticated user → owner filter
    component: str | None = None  # Component name or ID
    artifact_type_filter: str | None = None  # Sub-type like "Bug", "Use Case" (not artifact_type)

    # --- Tier 1 filters (specialized — apply to specific artifact types) ---
    requirement_id: int | None = None  # Filter tasks by parent requirement (task-only)

    # --- Tier 2 filters (escape hatch for any field) ---
    filters: list[dict] | None = None  # [{"field": ..., "operator": ..., "value": ...}]

    # --- Output shaping ---
    include_types: list[str] | None = None  # e.g. ["test_steps"] — resolved types

    # --- Custom property resolution (optional) ---
    custom_property_resolver: CustomPropertyResolver | None = None

    # --- Pagination ---
    starting_row: int = 1  # 1-indexed start position
    number_of_rows: int = 100  # Max results to return (capped when include active)


class ProductSearchResult(TypedDict):
    """Return type of _single_product_search.

    Spec:
        - TypedDict (not dataclass) because the result is built incrementally
          inside _single_product_search, not constructed all-at-once.
        - All keys except includes_fetched are always present — callers can
          destructure without key-existence checks.
        - warnings is always a list (never None) — accumulated from all
          resolution steps, filter building, projection, and include enrichment.
        - includes_fetched is NotRequired — only present when include_types
          was active and includes were fetched.
        - pagination is a dict with starting_row, number_of_rows, total_returned.
          total_returned always equals len(data).
    """

    product_id: int  # Echo of request.product_id for multi-product correlation
    data: list[dict]  # Projected artifact objects
    fields_returned: list[str]  # Fields present in each data object
    fields_available: list[str]  # Additional fields available on request (delta)
    pagination: dict  # {starting_row, number_of_rows, total_returned}
    warnings: list[str]  # Accumulated warnings from all pipeline steps
    includes_fetched: NotRequired[list[str]]  # Sub-artifact types that were enriched
    custom_properties_resolved: NotRequired[bool]  # True when at least one artifact resolved


async def _single_product_search(
    spira_client,
    request: ProductSearchRequest,
    resolver: NameResolver,
) -> ProductSearchResult:
    """Execute the search pipeline for one product.

    Returns a ProductSearchResult dict (NOT a JSON string) with keys:
    ``product_id``, ``data``, ``fields_returned``, ``fields_available``,
    ``pagination``, ``warnings``, and optionally ``includes_fetched``.

    Order: resolve template → resolve release → cap rows → build URL →
    resolve filters → POST → resolve CPs → project → enrich includes.

    Spec:
        - ALWAYS returns a dict with keys: product_id, data, fields_returned,
          fields_available, pagination, warnings — callers destructure without
          key-existence checks
        - warnings is always a list (never None) — accumulated from all
          resolution steps, filter building, projection, and include enrichment
        - Unsupported filters (config field is None) produce a warning and the
          search proceeds without that filter — never an error/exception
        - Name resolution failure (no template_id, or name not found) produces
          a warning and the search proceeds — partial filters are still applied
        - When include_types is active, number_of_rows is capped at
          MAX_INCLUDE_RESULTS with a warning — callers see the cap in
          pagination.number_of_rows
        - pagination.total_returned always equals len(data) — callers use it
          for consistency checks
        - May raise on API errors (POST failure) — caller (_product_search_impl
          or _multi_product_search) is responsible for catching and converting
          to error envelope
        - Field projection applies after API call — data objects contain only
          the requested (or summary default) fields
        - Every Tier 1 filter that resolves successfully becomes a RemoteFilter
          in the POST body; Tier 2 filters merge after Tier 1
        - resolver is always provided (never None) — Tier 1 resolution is
          always delegated to NameResolver.resolve_all_tier1 which handles
          both name-based resolution (when template_id is available) and
          integer passthrough (when template_id is None)
    """
    ctx = _SearchPipelineContext(request, resolver, spira_client)

    await ctx.resolve_template()
    await ctx.resolve_release_id()
    ctx.cap_rows_for_includes()
    ctx.build_endpoint_url()
    await ctx.resolve_filters()
    await ctx.execute_search()
    await ctx.project_and_enrich_stage()

    return ctx.to_result()


class _SearchPipelineContext:
    """Mutable pipeline state for a single-product search invocation.

    Accumulates warnings, resolved filters, and intermediate data as it
    flows through the named pipeline stages. Lives in the same file as
    ``_single_product_search`` (per ADR-0011: depth belongs in orchestration).

    Spec:
        - One instance per product per search invocation — never shared
          across products in a fan-out
        - Mutable — each stage method mutates self in place
        - warnings is always a list (never None) — stages append to it
        - Stages must be called in the order defined by
          _single_product_search — no reordering
        - Not exported — private to this module (underscore prefix)
    """

    __slots__ = (
        "_config",
        "_request",
        "_resolver",
        "_spira_client",
        "data",
        "effective_rows",
        "fields_available",
        "fields_returned",
        "custom_properties_resolved",
        "includes_fetched",
        "projected",
        "release_id",
        "remote_filters",
        "template_id",
        "url",
        "warnings",
    )

    def __init__(
        self,
        request: ProductSearchRequest,
        resolver: NameResolver,
        spira_client: Any,
    ) -> None:
        self._request = request
        self._resolver = resolver
        self._spira_client = spira_client
        self._config: ArtifactConfig = ARTIFACT_CONFIG[request.artifact_type]
        self.warnings: list[str] = []

        # Intermediate state — set by stages
        self.template_id: int | None = None
        self.release_id: int | str | None = request.release_id
        self.effective_rows: int = request.number_of_rows
        self.url: str = ""
        self.remote_filters: list[dict] = []
        self.data: list[dict] = []
        self.projected: list[dict] = []
        self.fields_returned: list[str] = []
        self.fields_available: list[str] = []
        self.custom_properties_resolved: bool = False
        self.includes_fetched: list[str] | None = None

    # ------------------------------------------------------------------
    # Stage: resolve_template
    # ------------------------------------------------------------------

    async def resolve_template(self) -> None:
        """Resolve template_id for name-based filter resolution.

        Sets self.template_id. Appends warning if resolution fails.
        """
        self.template_id = await self._resolver.get_template_id(self._request.product_id)
        if self.template_id is None:
            self.warnings.append(
                f"Could not resolve template ID for product {self._request.product_id}. "
                "Name-based filters (status, priority, type) will be skipped."
            )

    # ------------------------------------------------------------------
    # Stage: resolve_release_id
    # ------------------------------------------------------------------

    async def resolve_release_id(self) -> None:
        """Resolve version-string release_id to integer for URL query params.

        Only runs when release_id is a string AND the artifact type uses
        release_id as a URL query param (test_case, test_set).
        """
        if isinstance(self.release_id, str) and "release_id" in self._config.search_query_params:
            resolved_rid, warning = await self._resolver.resolve_release(
                self._request.product_id, self.release_id, self._request.artifact_type
            )
            if warning:
                self.warnings.append(warning)
            self.release_id = resolved_rid if resolved_rid is not None else None

    # ------------------------------------------------------------------
    # Stage: cap_rows_for_includes
    # ------------------------------------------------------------------

    def cap_rows_for_includes(self) -> None:
        """Cap number_of_rows when include is active.

        Sets self.effective_rows. Appends warning if capped.
        """
        if self._request.include_types:
            self.effective_rows = min(self._request.number_of_rows, MAX_INCLUDE_RESULTS)
            if self._request.number_of_rows > MAX_INCLUDE_RESULTS:
                self.warnings.append(
                    f"Results capped at {MAX_INCLUDE_RESULTS} due to include parameter. "
                    "There may be additional artifacts."
                )

    # ------------------------------------------------------------------
    # Stage: build_endpoint_url
    # ------------------------------------------------------------------

    def build_endpoint_url(self) -> None:
        """Build the POST endpoint URL with pagination and query params."""
        self.url = _build_search_url(
            self._config,
            self._request.product_id,
            self.release_id,
            self._request.starting_row,
            self.effective_rows,
        )

    # ------------------------------------------------------------------
    # Stage: resolve_filters
    # ------------------------------------------------------------------

    async def resolve_filters(self) -> None:
        """Resolve Tier 1 names, Tier 2 custom property filters, and build RemoteFilter array.

        Combines stages 2, 2b, 3, 3b, 3c from the original pipeline into
        one logical stage: "turn all filter inputs into a RemoteFilter array."

        Spec:
            - Sets self.remote_filters to the final RemoteFilter array for POST
            - Tier 1 resolution always runs (via resolve_all_tier1) — failures
              produce warnings, never exceptions
            - Tier 2 CP filter resolution only runs when both filters and
              custom_property_resolver are present on the request
            - After resolution, effective_tier2 excludes any filters that were
              consumed by the CP resolver — remaining go to build_remote_filters
            - Date range merge only runs when cp_remote_filters were produced
              (optimization: skip when no CP filters exist)
            - All warnings from sub-steps are appended to self.warnings
        """
        # Tier 1: resolve named parameters to filter tuples
        tier1_filters, resolve_warnings = await self._resolver.resolve_all_tier1(
            self._config,
            self._request.product_id,
            self.template_id,
            artifact_type=self._request.artifact_type,
            status=self._request.status,
            priority=self._request.priority,
            owner_id=self._request.owner_id,
            current_user=self._request.current_user,
            component=self._request.component,
            artifact_type_filter=self._request.artifact_type_filter,
            release_id=self.release_id,
            requirement_id=self._request.requirement_id,
        )
        self.warnings.extend(resolve_warnings)

        # Tier 2: separate custom property filters from standard filters
        effective_tier2 = self._request.filters
        cp_remote_filters: list[dict] = []
        if self._request.filters and self._request.custom_property_resolver:
            (
                effective_tier2,
                cp_remote_filters,
                cp_filter_warnings,
            ) = await resolve_custom_property_filters(
                self._request.filters,
                self._config.all_fields,
                self._request.custom_property_resolver,
                self._request.product_id,
                self._request.artifact_type,
            )
            self.warnings.extend(cp_filter_warnings)

        # Build RemoteFilter array from Tier 1 + remaining Tier 2
        self.remote_filters, filter_warnings = build_remote_filters(
            tier1_filters, effective_tier2, self._config.all_fields
        )
        self.warnings.extend(filter_warnings)

        # Append resolved CP filters (already in RemoteFilter format)
        self.remote_filters.extend(cp_remote_filters)

        # Merge duplicate DateRangeValue filters on the same field
        if cp_remote_filters:
            self.remote_filters, merge_warnings = merge_date_range_filters(self.remote_filters)
            self.warnings.extend(merge_warnings)

    # ------------------------------------------------------------------
    # Stage: execute_search
    # ------------------------------------------------------------------

    async def execute_search(self) -> None:
        """POST the search request with server-side filters.

        Sets self.data. May raise SpiraApiError — caller handles.
        """
        raw = await self._spira_client.make_spira_api_post_request(self.url, self.remote_filters)
        self.data = raw if raw else []

    # ------------------------------------------------------------------
    # Stage: project_and_enrich (delegates to _projection.py pipeline)
    # ------------------------------------------------------------------

    async def project_and_enrich_stage(self) -> None:
        """Resolve CPs, project fields, inject CPs, and enrich includes.

        Delegates to the shared projection pipeline. Sets self.projected,
        self.fields_returned, self.fields_available, self.custom_properties_resolved,
        self.includes_fetched, and extends self.warnings with pipeline warnings.
        """
        from mcp_server_spira.features.search.tools._projection import project_and_enrich

        result = await project_and_enrich(
            self.data,
            self._request.fields,
            self._config,
            cp_resolver=self._request.custom_property_resolver,
            product_id=self._request.product_id,
            pagination={
                "starting_row": self._request.starting_row,
                "number_of_rows": self.effective_rows,
                "total_returned": len(self.data),
            },
            spira_client=self._spira_client,
            include_types=self._request.include_types,
            artifact_type=self._request.artifact_type,
        )

        self.projected = result.data
        self.fields_returned = result.fields_returned
        self.fields_available = result.fields_available
        self.custom_properties_resolved = result.custom_properties_resolved
        self.includes_fetched = result.includes_fetched
        self.warnings.extend(result.warnings)

    # ------------------------------------------------------------------
    # Result assembly
    # ------------------------------------------------------------------

    def to_result(self) -> ProductSearchResult:
        """Assemble the final ProductSearchResult from accumulated state."""
        result: ProductSearchResult = {
            "product_id": self._request.product_id,
            "data": self.projected,
            "fields_returned": self.fields_returned,
            "fields_available": self.fields_available,
            "pagination": {
                "starting_row": self._request.starting_row,
                "number_of_rows": self.effective_rows,
                "total_returned": len(self.projected),
            },
            "warnings": self.warnings,
        }
        if self.includes_fetched is not None:
            result["includes_fetched"] = self.includes_fetched
        if self.custom_properties_resolved:
            result["custom_properties_resolved"] = True
        return result


async def _multi_product_search(
    spira_client,
    requests: list[ProductSearchRequest],
    resolver: NameResolver,
) -> str:
    """Fan out search across multiple products via asyncio.gather.

    Returns a Multi_Product_Envelope JSON string.  Every product in
    *requests* gets exactly one entry in the ``products`` array,
    regardless of success or failure.

    Spec:
        - ALWAYS returns a JSON string (never raises) — caller can return
          it directly to the MCP layer
        - len(products) in the response ALWAYS equals len(requests) —
          no product is ever silently dropped
        - Failed products get an entry with "error" and non-empty "warnings"
          keys — callers iterate products without checking for missing IDs
        - Successful products get the full dict from _single_product_search
          (product_id, data, fields_returned, fields_available, pagination,
          warnings)
        - Uses asyncio.gather with return_exceptions=True — one product's
          failure never prevents other products from returning results
        - Top-level warnings is always a list (via format_multi_product_response)
        - artifact_type in the response matches requests[0].artifact_type
        - All requests must share the same artifact_type (caller guarantees)
    """
    tasks = [_single_product_search(spira_client, req, resolver) for req in requests]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    products: list[dict[str, Any]] = []
    for req, result in zip(requests, results, strict=True):
        if isinstance(result, BaseException):
            products.append(
                {
                    "product_id": req.product_id,
                    "error": f"API call failed: {_sanitize_error(result)}",
                    "warnings": [
                        f"API call failed for product {req.product_id}: {_sanitize_error(result)}"
                    ],
                }
            )
        else:
            # _single_product_search returns a ProductSearchResult (TypedDict)
            products.append(dict(result))

    return format_multi_product_response(
        artifact_type=requests[0].artifact_type,
        products=products,
    )


async def _product_search_impl(
    spira_client,
    artifact_type: Any,
    product_ids: Any,
    fields: list[str] | None,
    status: str | None,
    release_id: int | str | None,
    priority: str | None,
    starting_row: int,
    number_of_rows: int,
    include: list[str] | None = None,
    requirement_id: int | None = None,
    owner_id: int | None = None,
    current_user: bool = False,
    component: str | None = None,
    artifact_type_filter: str | None = None,
    filters: list[dict] | None = None,
) -> str:
    """Core implementation for product_search_artifacts.

    Takes *spira_client* as first arg so callers (and tests) can inject a
    mock without touching MCP registration.

    Returns a JSON string — either a single-product search response envelope
    or a multi-product envelope (task 4).

    Spec:
        Return type:
            - ALWAYS returns a JSON string (never raises, never returns None)
            - On success: search envelope or multi-product envelope
            - On validation failure: error envelope with error_code

        Validation order (short-circuits on first failure):
            1. artifact_type must be in PRODUCT_ARTIFACT_TYPES
            2. starting_row must be >= 1
            3. number_of_rows must be >= 1
            4. If artifact_type == "build": release_id required and must be int
            5. product_ids must coerce to list[int] (or resolve from env)

        Routing invariants:
            - len(product_ids) == 1 → single-product path → search envelope
            - len(product_ids) > 1  → multi-product path → multi-product envelope

        Include behavior:
            - Single-product: include types resolved and passed to search
            - Multi-product: include silently ignored with warning injected

        Error handling:
            - API exceptions caught and converted to error envelope
            - Per-product failures in multi-product: error entry in products array
              (never drops a product from results)

        Warnings accumulation:
            - Warnings from include resolution + search warnings merged
            - Multi-product include warning prepended when include provided
    """
    # 1. Validate artifact_type
    type_error = ParameterValidator.validate_type_param(
        artifact_type, PRODUCT_ARTIFACT_TYPES, "artifact_type"
    )
    if type_error is not None:
        return format_error_response(**type_error)

    # 2. Validate pagination params
    validation_error = ParameterValidator.validate_positive_integer(
        starting_row, "starting_row", min_value=1
    )
    if validation_error is not None:
        return json.dumps(validation_error, indent=2)

    validation_error = ParameterValidator.validate_positive_integer(
        number_of_rows, "number_of_rows", min_value=1
    )
    if validation_error is not None:
        return json.dumps(validation_error, indent=2)

    # 3. Parse release_id: int-string → int, otherwise keep as str
    if release_id is not None:
        if isinstance(release_id, int):
            pass  # already int
        elif isinstance(release_id, str):
            with contextlib.suppress(ValueError):
                release_id = int(release_id)

    # 3b. Build special case: require release_id and must be numeric
    if artifact_type == "build" and release_id is None:
        return format_error_response(
            error="release_id is required for build searches",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={"parameter": "release_id", "artifact_type": "build"},
            suggestion=("Builds are scoped to a release. Pass release_id to search for builds."),
        )
    if artifact_type == "build" and release_id is not None and not isinstance(release_id, int):
        return format_error_response(
            error="builds require numeric release IDs",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={"parameter": "release_id", "value": release_id, "artifact_type": "build"},
            suggestion=(
                "Pass release_id as an integer for builds. "
                "Version number strings are only supported for non-build artifact types."
            ),
        )

    # 4. Coerce product_ids
    coerced = _coerce_product_ids(product_ids)
    if isinstance(coerced, str):
        # Error response string
        return coerced
    product_id_list: list[int] = coerced

    # 4b. Search guard: strip unsupported include types (only supported on GET)
    search_unsupported_includes = {"comments", "associations", "coverage"}
    include_warnings_pre: list[str] = []
    if include:
        unsupported_found = search_unsupported_includes & set(include)
        for unsupported_type in sorted(unsupported_found):
            include_warnings_pre.append(
                f"include='{unsupported_type}' is only supported on product_get_artifact "
                "(single-artifact retrieval), not on search."
            )
        if unsupported_found:
            include = [i for i in include if i not in search_unsupported_includes]

    # 5. Resolve include types (shared by both paths for validation)
    include_types: list[str] = []
    include_warnings: list[str] = include_warnings_pre
    if include:
        _resolved, _warnings = resolve_includes(artifact_type, include)
        include_types = _resolved
        include_warnings.extend(_warnings)

    # 5b. Create NameResolver once, shared across multi-product fan-out
    template_context = TemplateContext(spira_client)
    resolver = NameResolver(spira_client, template_context)
    custom_property_resolver = CustomPropertyResolver(spira_client, template_context)

    # 6. Route: single vs multi-product
    if len(product_id_list) == 1:
        try:
            request = ProductSearchRequest(
                artifact_type=artifact_type,
                product_id=product_id_list[0],
                fields=fields,
                status=status,
                priority=priority,
                release_id=release_id,
                owner_id=owner_id,
                current_user=current_user,
                component=component,
                artifact_type_filter=artifact_type_filter,
                requirement_id=requirement_id,
                filters=filters,
                include_types=include_types or None,
                custom_property_resolver=custom_property_resolver,
                starting_row=starting_row,
                number_of_rows=number_of_rows,
            )
            result = await _single_product_search(
                spira_client,
                request,
                resolver,
            )
        except SpiraApiError as e:
            return format_error_response(
                error=f"Failed to retrieve {artifact_type} data: {e}",
                error_code=e.error_code,
                details={"product_id": product_id_list[0]},
                suggestion="Check your Spira connection and try again.",
            )

        all_warnings = include_warnings + result["warnings"]
        return format_search_response(
            data=result["data"],
            artifact_type=artifact_type,
            fields_returned=result["fields_returned"],
            pagination=result["pagination"],
            fields_available=result["fields_available"],
            warnings=all_warnings,
            includes_fetched=result.get("includes_fetched"),
            custom_properties_resolved=result.get("custom_properties_resolved", False),
        )

    # Multi-product path — include not supported
    multi_warnings: list[str] = []
    if include:
        multi_warnings.append(
            "include is not supported for multi-product fan-out. "
            "Results returned without include data."
        )

    requests = [
        ProductSearchRequest(
            artifact_type=artifact_type,
            product_id=pid,
            fields=fields,
            status=status,
            priority=priority,
            release_id=release_id,
            owner_id=owner_id,
            current_user=current_user,
            component=component,
            artifact_type_filter=artifact_type_filter,
            requirement_id=requirement_id,
            filters=filters,
            custom_property_resolver=custom_property_resolver,
            starting_row=starting_row,
            number_of_rows=number_of_rows,
        )
        for pid in product_id_list
    ]

    result_str = await _multi_product_search(
        spira_client,
        requests,
        resolver,
    )

    # Inject multi-product include warning into the response if needed
    if multi_warnings:
        parsed = json.loads(result_str)
        parsed["warnings"] = multi_warnings + parsed.get("warnings", [])
        return json.dumps(parsed, indent=2, default=str)

    return result_str


def _build_search_docstring() -> str:
    """Build the dynamic docstring for product_search_artifacts."""
    return (
        "Search artifacts in a Spira product.\n"
        "\n"
        'filters: [{{"field": "Name", "operator": "contains", "value": "login"}}]'
        " — use get_artifact_schema for fields.\n"
        "release_id: required for builds."
    )


def register_tools(mcp) -> None:
    """Register product_search_artifacts."""
    search_docstring = _build_search_docstring()

    @mcp.tool(
        name="product_search_artifacts",
        description=search_docstring,
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )
    async def product_search_artifacts(
        artifact_type: ProductArtifactType,
        product_ids: list[int] | None = None,
        fields: list[str] | None = None,
        status: str | None = None,
        release_id: str | None = None,
        priority: str | None = None,
        starting_row: int = 1,
        number_of_rows: int = 100,
        include: list[str] | None = None,
        requirement_id: int | None = None,
        owner_id: int | None = None,
        current_user: bool = False,
        component: str | None = None,
        artifact_type_filter: str | None = None,
        filters: list[dict] | None = None,
    ) -> str:
        """Search artifacts in a Spira product."""
        spira_client = get_spira_client()
        return await _product_search_impl(
            spira_client,
            artifact_type,
            product_ids,
            fields,
            status,
            release_id,
            priority,
            starting_row,
            number_of_rows,
            include=include,
            requirement_id=requirement_id,
            owner_id=owner_id,
            current_user=current_user,
            component=component,
            artifact_type_filter=artifact_type_filter,
            filters=filters,
        )
