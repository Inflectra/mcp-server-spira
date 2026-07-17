"""Projection pipeline — shared tail for search tools.

Owns the "resolve CPs → project fields → inject CPs → enrich includes"
sequence used by both product_search and mywork_search. Eliminates the
duplicated 4-step tail that previously lived inline in each caller.

Consumers: _SearchPipelineContext (product.py), _single_artifact_search (mywork.py).
Not used by product_get (different CP resolution mode, no pagination).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from mcp_server_spira.features.custom_properties.resolver import (
    CustomPropertyResult,
)
from mcp_server_spira.features.search.tools._include import enrich_with_includes
from mcp_server_spira.features.search.tools._shared import finalize_search_results

if TYPE_CHECKING:
    from mcp_server_spira.features.custom_properties.resolver import CustomPropertyResolver
    from mcp_server_spira.models import ArtifactConfig
    from mcp_server_spira.utils.spira_client import SpiraClient


@dataclass(frozen=True)
class ProjectionResult:
    """Output of the projection pipeline.

    Spec:
        - Frozen dataclass — immutable after construction
        - data: projected artifact dicts (field-projected, CP-injected,
          optionally include-enriched)
        - fields_returned: fields present in each data object
        - fields_available: delta fields not returned (empty when all returned)
        - warnings: warnings produced BY THIS PIPELINE ONLY — caller merges
          with its own pre-pipeline warnings
        - custom_properties_resolved: True when at least one artifact had
          CPs resolved and injected
        - includes_fetched: list of include types that were processed,
          or None when includes weren't requested
    """

    data: list[dict] = field(default_factory=list)
    fields_returned: list[str] = field(default_factory=list)
    fields_available: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    custom_properties_resolved: bool = False
    includes_fetched: list[str] | None = None


async def project_and_enrich(
    data: list[dict],
    fields: list[str] | None,
    config: ArtifactConfig,
    *,
    cp_resolver: CustomPropertyResolver | None,
    product_id: int | None,
    pagination: Mapping[str, Any],
    spira_client: SpiraClient | None = None,
    include_types: list[str] | None = None,
    artifact_type: str | None = None,
) -> ProjectionResult:
    """Execute the shared projection tail: CP resolve → project → inject → enrich.

    Spec:
        - ALWAYS returns a ProjectionResult — never raises
        - warnings contains ONLY warnings produced by this pipeline
          (CP resolution, field projection, include enrichment)
        - When cp_resolver is None: skips CP resolution entirely, treats
          fields as-is for projection
        - When include_types is None or empty: skips enrichment, returns
          includes_fetched=None
        - When spira_client is None and include_types is provided: skips
          enrichment with a warning (defensive — shouldn't happen in practice)
        - custom_properties_resolved is True only when CP injection occurred
        - pagination is passed through to finalize_search_results (not owned
          by this pipeline — caller computes it)
        - All async calls use await (async contract)

    Args:
        data: Raw artifact dicts from the API (post-search, pre-projection).
        fields: Requested field projection (None → summary defaults).
        config: ArtifactConfig for the artifact type.
        cp_resolver: CustomPropertyResolver instance (None = skip CP resolution).
        product_id: Product ID for CP resolution. None for mywork cross-product.
        pagination: Pre-built pagination metadata dict (caller-owned).
        spira_client: Required when include_types is provided.
        include_types: Resolved include type strings, or None to skip enrichment.
        artifact_type: Artifact type string (needed for include enrichment).

    Returns:
        ProjectionResult with projected data, field lists, warnings, and
        include/CP metadata.
    """
    warnings: list[str] = []

    try:
        return await _project_and_enrich_impl(
            data,
            fields,
            config,
            warnings,
            cp_resolver=cp_resolver,
            product_id=product_id,
            pagination=pagination,
            spira_client=spira_client,
            include_types=include_types,
            artifact_type=artifact_type,
        )
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"Projection pipeline failed: {type(exc).__name__}")
        return ProjectionResult(warnings=warnings)


async def _project_and_enrich_impl(
    data: list[dict],
    fields: list[str] | None,
    config: ArtifactConfig,
    warnings: list[str],
    *,
    cp_resolver: CustomPropertyResolver | None,
    product_id: int | None,
    pagination: Mapping[str, Any],
    spira_client: SpiraClient | None = None,
    include_types: list[str] | None = None,
    artifact_type: str | None = None,
) -> ProjectionResult:
    """Inner implementation — may raise. Caller wraps in safety net."""
    # --- Step 1: Resolve custom properties (pre-projection) ---
    if cp_resolver is not None:
        cp_result = await cp_resolver.resolve_for_search_results(
            data, fields, config, product_id=product_id
        )
        warnings.extend(cp_result.warnings)
    else:
        cp_result = CustomPropertyResult(effective_fields=fields)

    # --- Step 2: Field projection via finalize_search_results ---
    # finalize_search_results appends projection warnings to the list we pass.
    # We pass a local list so we control what goes into our result.
    projection_warnings: list[str] = []
    result_dict = finalize_search_results(
        data,
        cp_result.effective_fields,
        config,
        pagination=pagination,
        warnings=projection_warnings,
    )
    warnings.extend(projection_warnings)

    # --- Step 3: Inject resolved custom properties ---
    cp_result.inject_into_search_results(result_dict, config)
    custom_properties_resolved = result_dict.get("custom_properties_resolved", False)

    projected_data: list[dict] = result_dict["data"]
    fields_returned: list[str] = result_dict["fields_returned"]
    fields_available: list[str] = result_dict["fields_available"]

    # --- Step 4: Include enrichment (optional) ---
    includes_fetched: list[str] | None = None
    if include_types:
        if spira_client is None:
            warnings.append("Include enrichment requested but no spira_client provided. Skipping.")
        elif artifact_type is None:
            warnings.append("Include enrichment requested but no artifact_type provided. Skipping.")
        elif product_id is None:
            warnings.append("Include enrichment requested but no product_id provided. Skipping.")
        else:
            projected_data, includes_fetched, include_warnings = await enrich_with_includes(
                spira_client,
                product_id,
                projected_data,
                include_types,
                artifact_type,
            )
            warnings.extend(include_warnings)

    return ProjectionResult(
        data=projected_data,
        fields_returned=fields_returned,
        fields_available=fields_available,
        warnings=warnings,
        custom_properties_resolved=custom_properties_resolved,
        includes_fetched=includes_fetched,
    )
