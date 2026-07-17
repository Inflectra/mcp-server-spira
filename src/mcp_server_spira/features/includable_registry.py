"""Includable registry — maps include-type names to IncludableEntry objects.

Built at import time from SUB_ARTIFACT_CONFIG. Comments are resolved
dynamically via _resolve_includable_entry because their endpoint varies
by artifact type (lives on ArtifactConfig.comments_endpoint).

The enrichment loop uses _resolve_includable_entry for all Tier 1
(flat-array) includable types. Tier 2 (custom fetch strategies like
associations and coverage) are handled separately via
ENRICHMENT_STRATEGIES.
"""

from __future__ import annotations

from mcp_server_spira.features.artifact_configs import ARTIFACT_CONFIG
from mcp_server_spira.features.comment_config import COMMENT_CONFIG
from mcp_server_spira.features.sub_artifact_configs import SUB_ARTIFACT_CONFIG
from mcp_server_spira.models import IncludableEntry

# --- Tier 1 registry: flat-array includable types ---
# Built from SUB_ARTIFACT_CONFIG at import time.
INCLUDABLE_REGISTRY: dict[str, IncludableEntry] = {}

for _name, _sub_config in SUB_ARTIFACT_CONFIG.items():
    INCLUDABLE_REGISTRY[_name] = IncludableEntry(
        config=_sub_config,
        endpoint_template=_sub_config.endpoint_template,
        id_field=_sub_config.parent_id_field,
        embedded_field=_sub_config.embedded_field or None,
    )


def resolve_includable_entry(
    include_type: str,
    artifact_type: str,
) -> IncludableEntry | None:
    """Resolve an include type to its registry entry.

    Spec:
        - Sub-artifacts: direct lookup by include_type in INCLUDABLE_REGISTRY
        - Comments: shared COMMENT_CONFIG, endpoint from
          ArtifactConfig.comments_endpoint (varies by artifact type)
        - Returns None if the include_type is not a Tier 1 includable
          (caller should check Tier 2 strategies or emit a warning)
        - Never raises — unknown include_type or missing endpoint → None
        - Pure function (no I/O, no side effects)
    """
    # Direct lookup (sub-artifacts)
    entry = INCLUDABLE_REGISTRY.get(include_type)
    if entry is not None:
        return entry

    # Comments: config is shared, endpoint varies by artifact type
    if include_type == "comments":
        art_config = ARTIFACT_CONFIG.get(artifact_type)
        if art_config and art_config.comments_endpoint and art_config.id_field:
            return IncludableEntry(
                config=COMMENT_CONFIG,
                endpoint_template=art_config.comments_endpoint,
                id_field=art_config.id_field,
            )

    return None
