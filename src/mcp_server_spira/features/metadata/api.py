"""Public API for the metadata feature.

Exposes metadata fetching and filtering to other features (e.g. search's
NameResolver) without requiring them to import internal configs or helpers.

This module is the seam between the metadata feature and its consumers.
Internal implementation details (config dicts, filter logic, endpoint
patterns) stay private to the metadata package.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from mcp_server_spira.features.metadata.configs import (
    PRIORITY_FIELD_CONFIGS,
    SEVERITY_FIELD_CONFIGS,
    STATUS_FIELD_CONFIGS,
    TYPE_FIELD_CONFIGS,
)
from mcp_server_spira.features.metadata.helpers import _filter_metadata_items
from mcp_server_spira.models import TemplateMetadataFieldConfig

if TYPE_CHECKING:
    from mcp_server_spira.utils.spira_client import SpiraClient

logger = logging.getLogger(__name__)

# Section name → config dict mapping (internal detail exposed via this API).
_SECTION_CONFIG_MAP: dict[str, dict[str, TemplateMetadataFieldConfig]] = {
    "statuses": STATUS_FIELD_CONFIGS,
    "priorities": PRIORITY_FIELD_CONFIGS,
    "types": TYPE_FIELD_CONFIGS,
    "severities": SEVERITY_FIELD_CONFIGS,
}


async def fetch_active_metadata_items(
    spira_client: SpiraClient,
    template_id: int,
    section: str,
    artifact_kind: str,
) -> tuple[list[dict], str | None]:
    """Fetch active metadata items for a given section and artifact kind.

    This is the public API for metadata resolution. Consumers (e.g.
    NameResolver) call this instead of importing internal configs and
    helpers directly.

    Spec:
        - Returns (list[dict], None) on success — filtered and projected
          metadata items with only Name, id_field, and include_fields
        - Returns ([], warning_string) on any failure — never raises
        - Unknown section → ([], warning mentioning "Unknown metadata section")
        - Unknown artifact_kind for the section → ([], warning suggesting
          Tier 2 integer IDs)
        - API failure → ([], warning suggesting integer ID fallback)
        - Empty/None API response → ([], warning mentioning "No metadata found")
        - Only active items are returned (filtered by the config's
          active_field) — inactive items are excluded
        - All caching is the caller's responsibility — this function
          always makes an API call
        - Pure async function — no mutation of shared state

    Args:
        spira_client: Async Spira API client.
        template_id: Product template numeric ID.
        section: One of "statuses", "priorities", "types".
        artifact_kind: Template metadata artifact kind string
            (e.g. "Incident", "Test Case", "Requirement").

    Returns:
        (items, warning) — filtered metadata items and an optional warning.
    """
    config_dict = _SECTION_CONFIG_MAP.get(section)
    if config_dict is None:
        return [], f"Unknown metadata section '{section}'."

    config = config_dict.get(artifact_kind)
    if config is None:
        return [], (
            f"Name resolution is not supported for {artifact_kind} "
            f"{section}. Use Tier 2 filtering with integer IDs."
        )

    url = config.endpoint.format(template_id=template_id)
    try:
        raw_items = await spira_client.make_spira_api_get_request(url)
    except Exception:
        logger.exception(
            "Failed to fetch %s metadata for %s (template %d)",
            section,
            artifact_kind,
            template_id,
        )
        return [], (
            f"Failed to fetch {section} metadata for "
            f"{artifact_kind}. Try using an integer ID instead."
        )

    if not raw_items or not isinstance(raw_items, list):
        return [], f"No {section} metadata found for {artifact_kind}."

    filtered = _filter_metadata_items(raw_items, config)
    return filtered, None


def get_id_field(section: str, artifact_kind: str) -> str | None:
    """Return the ID field name for a given section and artifact kind.

    Used by NameResolver to know which field contains the resolved integer
    ID in the metadata items returned by fetch_active_metadata_items.

    Spec:
        - Returns the id_field string on success (e.g. "IncidentStatusId")
        - Returns None if section or artifact_kind is unknown
        - Pure function — no I/O, no side effects
        - Never raises

    Args:
        section: One of "statuses", "priorities", "types".
        artifact_kind: Template metadata artifact kind string.

    Returns:
        The id_field name or None.
    """
    config_dict = _SECTION_CONFIG_MAP.get(section)
    if config_dict is None:
        return None
    config = config_dict.get(artifact_kind)
    if config is None:
        return None
    return config.id_field
