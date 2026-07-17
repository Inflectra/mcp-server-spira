"""Include enrichment — fetch nested includable data for parent artifacts.

Shared by ``product_search_artifacts`` and ``product_get_artifact``.

Two-tier dispatch:
  Tier 1 (IncludableEntry): flat-array types processed via a uniform
    fetch → post_filter → field projection → attach pipeline. Resolved
    via INCLUDABLE_REGISTRY + resolve_includable_entry. Today: sub-artifacts
    and comments. Adding a new flat-array type = one registry entry, zero
    changes to this module.
  Tier 2 (ENRICHMENT_STRATEGIES): custom fetch strategies for types with
    fundamentally different fetch patterns (e.g. associations, coverage).
    Each strategy is an async function that owns its own fetch-and-attach
    logic. Today: empty dict (placeholder for spec 20).
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from mcp_server_spira.features.artifact_configs import ARTIFACT_CONFIG
from mcp_server_spira.features.includable_registry import resolve_includable_entry
from mcp_server_spira.models import IncludableEntry
from mcp_server_spira.utils.common.field_projection import apply_field_projection

if TYPE_CHECKING:
    from mcp_server_spira.utils.spira_client import SpiraClient

MAX_INCLUDE_RESULTS = 50

# Type alias for Tier 2 enrichment strategy functions.
# Signature: (spira_client, product_id, artifacts, artifact_type, warnings) -> None
# Strategies mutate artifacts in place and append to warnings.
EnrichmentStrategy = Callable[
    ["SpiraClient", int, list[dict[str, Any]], str, list[str]],
    Awaitable[None],
]

# Tier 2: Custom enrichment strategies for types that don't fit the
# flat-array pipeline. Populated by spec 20 (associations, coverage).
ENRICHMENT_STRATEGIES: dict[str, EnrichmentStrategy] = {}


def resolve_includes(
    artifact_type: str,
    include: list[str] | None,
) -> tuple[list[str], list[str]]:
    """Resolve include names to valid sub_artifact_type strings.

    Spec:
        - None or empty include → ([], []) — no warnings, no work
        - Every name in include is checked against config.includes for the
          artifact type
        - Valid names appear in the first return list in the same order as
          the input
        - Invalid names produce exactly one warning each, listing valid
          options for the artifact type
        - Artifact types with no includes defined → every name produces a
          "does not support include" warning
        - warnings is always a list (never None)
        - Never raises — unknown artifact_type produces empty valid_options
          and all names generate warnings

    Returns ``(valid_types, warnings)`` where *warnings* lists any
    unrecognised names with the valid options for the artifact type.
    """
    if not include:
        return [], []

    config = ARTIFACT_CONFIG.get(artifact_type)
    valid_options = config.includes if config else []

    valid_types: list[str] = []
    warnings: list[str] = []

    for name in include:
        if name in valid_options:
            valid_types.append(name)
        else:
            if valid_options:
                opts = ", ".join(valid_options)
                warnings.append(
                    f"Unknown include '{name}' for artifact type "
                    f"'{artifact_type}'. "
                    f"Valid options: {opts}"
                )
            else:
                warnings.append(f"Artifact type '{artifact_type}' does not support include.")

    return valid_types, warnings


async def enrich_with_includes(
    spira_client: SpiraClient,
    product_id: int,
    artifacts: list[dict[str, Any]],
    include_types: list[str],
    artifact_type: str,
    fields: list[str] | None = None,
    *,
    embedded_data: dict[str, list[dict[str, Any]]] | None = None,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    """Enrich artifact dicts with nested includable data.

    Two-tier dispatch:
      Tier 1: Resolved via resolve_includable_entry → uniform pipeline
        (fetch → post_filter → field projection → attach array).
      Tier 2: Resolved via ENRICHMENT_STRATEGIES → custom async function
        that owns its own fetch-and-attach logic.

    Spec:
        - ALWAYS returns a 3-tuple (enriched_artifacts, includes_fetched,
          warnings) — never raises to the caller
        - enriched_artifacts is the SAME list object as input artifacts
          (mutated in place) — callers rely on identity
        - Config resolution: resolve_includable_entry handles sub-artifacts
          and comments; ENRICHMENT_STRATEGIES handles custom types;
          unresolved types emit a warning
        - Every include_type that resolves to a valid entry or strategy
          appears in includes_fetched, regardless of whether individual
          artifacts succeeded or failed
        - Tier 2 strategy exceptions are caught — the include_type still
          appears in includes_fetched, and a warning is emitted
        - After fetch, call config.post_filter(data) if non-None before
          field projection
        - API failure for one artifact does NOT block enrichment of other
          artifacts — each gets its own try/except
        - Empty/None API response → empty list attached, no warning
        - When embedded_data contains the include_type, API call is
          skipped entirely — data is projected from embedded_data instead
        - Field projection uses config.summary_fields as default when
          fields=None
        - warnings is always a list (never None)
        - All spira_client calls use await (async contract)

    Parameters
    ----------
    spira_client:
        Async Spira API client.
    product_id:
        Product ID for endpoint construction.
    artifacts:
        Parent artifact dicts to enrich (mutated in place).
    include_types:
        Resolved include type strings to process.
    artifact_type:
        Parent artifact type string — needed to resolve
        comments_endpoint and id_field from ARTIFACT_CONFIG.
    fields:
        Optional field projection (``None`` = summary).
    embedded_data:
        Pre-fetched raw sub-artifact data keyed by include type.
        When provided for an include type, skips the API call and
        projects from this data instead.  Used by
        ``product_get_artifact`` to avoid redundant API calls when
        the parent GET response already embeds the sub-artifact data.

    Returns
    -------
    tuple
        ``(enriched_artifacts, includes_fetched, warnings)``
    """
    warnings: list[str] = []
    includes_fetched: list[str] = []

    for include_type in include_types:
        # --- Tier 1: Registry-based (flat-array pipeline) ---
        entry = resolve_includable_entry(include_type, artifact_type)
        if entry is not None:
            includes_fetched.append(include_type)
            await _enrich_tier1(
                spira_client,
                product_id,
                artifacts,
                include_type,
                entry,
                fields,
                embedded_data,
                warnings,
            )
            continue

        # --- Tier 2: Strategy-based (custom fetch + transform) ---
        strategy = ENRICHMENT_STRATEGIES.get(include_type)
        if strategy is not None:
            try:
                await strategy(spira_client, product_id, artifacts, artifact_type, warnings)
            except Exception as exc:
                warnings.append(f"Enrichment strategy '{include_type}' failed: {exc}")
            includes_fetched.append(include_type)
            continue

        # --- Unknown include type ---
        # Provide a specific message for known include types that aren't
        # supported for this artifact type (e.g. comments on build)
        if include_type == "comments":
            warnings.append(f"Artifact type '{artifact_type}' does not support comments include.")
        else:
            warnings.append(f"No includable config found for '{include_type}'.")

    return artifacts, includes_fetched, warnings


async def _enrich_tier1(
    spira_client: SpiraClient,
    product_id: int,
    artifacts: list[dict[str, Any]],
    include_type: str,
    entry: IncludableEntry,
    fields: list[str] | None,
    embedded_data: dict[str, list[dict[str, Any]]] | None,
    warnings: list[str],
) -> None:
    """Tier 1 enrichment: fetch → post_filter → project → attach.

    Uniform pipeline for all flat-array includable types (sub-artifacts,
    comments). The entry carries all config needed — this function has
    zero knowledge of what kind of includable it's processing.

    Spec:
        - Mutates artifacts in place (attaches include_type key)
        - Appends to warnings list on failures
        - Never raises — all exceptions caught per-artifact
        - When embedded_data contains the include_type, skips API call
        - Empty/None API response → empty list attached, no warning
        - post_filter called before field projection when non-None
    """
    config = entry.config

    for artifact in artifacts:
        # Check for pre-fetched embedded data first
        if embedded_data and include_type in embedded_data:
            raw_list = embedded_data[include_type]
            if not raw_list:
                artifact[include_type] = []
                continue
            data = list(raw_list)
            if config.post_filter is not None:
                data = config.post_filter(data)
            projected, _, _, _ = apply_field_projection(
                data,
                fields,
                config.summary_fields,
                config.all_fields,
            )
            artifact[include_type] = projected
            continue

        artifact_id = artifact.get(entry.id_field)
        if artifact_id is None:
            warnings.append(
                f"Artifact missing '{entry.id_field}' field; skipping {include_type} enrichment."
            )
            artifact[include_type] = []
            continue

        endpoint = entry.endpoint_template.format(
            product_id=product_id,
            artifact_id=artifact_id,
        )

        try:
            raw = await spira_client.make_spira_api_get_request(endpoint)
        except Exception as exc:
            artifact[include_type] = []
            warnings.append(
                f"Failed to fetch {include_type} for {entry.id_field}={artifact_id}: {exc}"
            )
            continue

        if not raw:
            artifact[include_type] = []
            continue

        data = raw if isinstance(raw, list) else [raw]

        # Post-filter (e.g. remove deleted comments)
        if config.post_filter is not None:
            data = config.post_filter(data)

        projected, _, _, _ = apply_field_projection(
            data,
            fields,
            config.summary_fields,
            config.all_fields,
        )
        artifact[include_type] = projected
