"""Include enrichment — fetch nested sub-artifact data for parent artifacts.

Shared by ``product_search_artifacts`` and ``product_get_artifact``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mcp_server_spira.features.artifact_configs import ARTIFACT_CONFIG
from mcp_server_spira.features.search.sub_artifact_configs import SUB_ARTIFACT_CONFIG
from mcp_server_spira.utils.common.field_projection import apply_field_projection

if TYPE_CHECKING:
    from mcp_server_spira.utils.spira_client import SpiraClient

MAX_INCLUDE_RESULTS = 50


def resolve_includes(
    artifact_type: str,
    include: list[str] | None,
) -> tuple[list[str], list[str]]:
    """Resolve include names to valid sub_artifact_type strings.

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
                    f"Unknown include '{name}' for artifact type '{artifact_type}'. "
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
    fields: list[str] | None = None,
    *,
    embedded_data: dict[str, list[dict[str, Any]]] | None = None,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    """Enrich artifact dicts with nested sub-artifact data.

    For each artifact and each include type, fetches the sub-artifact
    endpoint, applies field projection, and attaches the result under
    the ``sub_artifact_type`` key on the artifact dict.

    Parameters
    ----------
    spira_client:
        Async Spira API client.
    product_id:
        Product ID for endpoint construction.
    artifacts:
        Parent artifact dicts to enrich (mutated in place).
    include_types:
        Resolved ``sub_artifact_type`` strings to process.
    fields:
        Optional field projection for sub-artifacts (``None`` = summary).
    embedded_data:
        Pre-fetched raw sub-artifact data keyed by include type.
        When provided for an include type, skips the API call and
        projects from this data instead.  Used by ``product_get_artifact``
        to avoid redundant API calls when the parent GET response
        already embeds the sub-artifact data.

    Returns
    -------
    tuple
        ``(enriched_artifacts, includes_fetched, warnings)``
    """
    warnings: list[str] = []
    includes_fetched: list[str] = []

    for include_type in include_types:
        sub_config = SUB_ARTIFACT_CONFIG.get(include_type)
        if sub_config is None:
            warnings.append(f"No sub-artifact config found for '{include_type}'.")
            continue

        includes_fetched.append(include_type)

        for artifact in artifacts:
            # Check for pre-fetched embedded data first
            if embedded_data and include_type in embedded_data:
                raw_list = embedded_data[include_type]
                if not raw_list:
                    artifact[include_type] = []
                    continue
                projected, _, _, _ = apply_field_projection(
                    raw_list,
                    fields,
                    sub_config.summary_fields,
                    sub_config.all_fields,
                )
                artifact[include_type] = projected
                continue

            parent_id = artifact.get(sub_config.parent_id_field)
            if parent_id is None:
                warnings.append(
                    f"Artifact missing '{sub_config.parent_id_field}' field; "
                    f"skipping {include_type} enrichment."
                )
                artifact[include_type] = []
                continue

            endpoint = sub_config.endpoint_template.format(
                product_id=product_id,
                artifact_id=parent_id,
            )

            try:
                raw = await spira_client.make_spira_api_get_request(endpoint)
            except Exception as exc:
                artifact[include_type] = []
                warnings.append(
                    f"Failed to fetch {include_type} for "
                    f"{sub_config.parent_id_field}={parent_id}: {exc}"
                )
                continue

            if not raw:
                artifact[include_type] = []
                continue

            data = raw if isinstance(raw, list) else [raw]
            projected, _, _, _ = apply_field_projection(
                data,
                fields,
                sub_config.summary_fields,
                sub_config.all_fields,
            )
            artifact[include_type] = projected

    return artifacts, includes_fetched, warnings
