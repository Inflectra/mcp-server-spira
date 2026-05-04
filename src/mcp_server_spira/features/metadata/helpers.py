"""
Shared helpers for template configuration features.

Contains implementation functions used by both the unified template metadata
tool (Spec I) and dynamic custom property resolution (Spec E).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from mcp_server_spira.features.metadata.configs import (
    IMPACT_FIELD_CONFIGS,
    IMPORTANCE_FIELD_CONFIGS,
    PRIORITY_FIELD_CONFIGS,
    PROBABILITY_FIELD_CONFIGS,
    SEVERITY_FIELD_CONFIGS,
    STATUS_FIELD_CONFIGS,
    TYPE_FIELD_CONFIGS,
)

if TYPE_CHECKING:
    from mcp_server_spira.models import TemplateMetadataFieldConfig

logger = logging.getLogger(__name__)

# Valid artifact kinds for the "types" section (6 kinds)
VALID_TYPES_ARTIFACT_KINDS: tuple[str, ...] = (
    "Requirement",
    "Test Case",
    "Task",
    "Risk",
    "Incident",
    "Document",
)

# Valid artifact kinds for the "custom_properties" section (11 kinds)
VALID_CUSTOM_PROPERTIES_ARTIFACT_KINDS: tuple[str, ...] = (
    "Requirement",
    "Release",
    "TestCase",
    "Task",
    "Risk",
    "Incident",
    "TestSet",
    "TestStep",
    "TestRun",
    "AutomationHost",
    "Document",
)

# Valid artifact kinds for the "statuses" section (7 kinds)
VALID_STATUSES_ARTIFACT_KINDS: tuple[str, ...] = (
    "Requirement",
    "Incident",
    "Task",
    "Risk",
    "Release",
    "Test Case",
    "Document",
)

# Valid artifact kinds for the "priorities" section (4 kinds — includes Requirement via importances)
VALID_PRIORITIES_ARTIFACT_KINDS: tuple[str, ...] = (
    "Incident",
    "Task",
    "Test Case",
    "Requirement",
)

# Valid artifact kinds for the "severities" section (1 kind)
VALID_SEVERITIES_ARTIFACT_KINDS: tuple[str, ...] = ("Incident",)

# Valid artifact kinds for the "importances" section (1 kind)
VALID_IMPORTANCES_ARTIFACT_KINDS: tuple[str, ...] = ("Requirement",)

# Valid artifact kinds for the "probabilities" section (1 kind)
VALID_PROBABILITIES_ARTIFACT_KINDS: tuple[str, ...] = ("Risk",)

# Valid artifact kinds for the "impacts" section (1 kind)
VALID_IMPACTS_ARTIFACT_KINDS: tuple[str, ...] = ("Risk",)


def _filter_metadata_items(items: list[dict], config: TemplateMetadataFieldConfig) -> list[dict]:
    """Filter and project metadata items using a field config.

    Pure synchronous function — no API calls, easy to unit test.
    Reusable for any metadata section (types, priorities, statuses, etc.).

    1. Filters out items where ``config.active_field`` is False.
    2. For each remaining item, builds a new dict containing only
       ``config.id_field``, ``"Name"``, and ``config.include_fields``.

    Args:
        items: Raw metadata dicts from the Spira API.
        config: Field config controlling projection and active filtering.

    Returns:
        Filtered and projected list of dicts.
    """
    keep_fields = (config.id_field, "Name", *config.include_fields)
    return [
        {k: item[k] for k in keep_fields if k in item}
        for item in items
        if item.get(config.active_field) is not False
    ]


async def _get_custom_properties_for_artifact_type(
    spira_client, template_id: int, artifact_type_name: str
) -> list:
    """
    Retrieves custom properties for a specific artifact type.

    Args:
        spira_client: The Inflectra Spira API client instance
        template_id: The numeric ID of the product template
        artifact_type_name: The name of the artifact type
            (e.g., "Requirement", "TestCase")

    Returns:
        List of custom property dictionaries, or empty list if none found
    """
    try:
        custom_props_url = (
            "project-templates/" + str(template_id) + "/custom-properties/" + artifact_type_name
        )
        custom_props = await spira_client.make_spira_api_get_request(custom_props_url)

        return custom_props if custom_props else []

    except Exception:
        return []


# Mapping from artifact kind name to its types API endpoint URL pattern.
# The placeholder {template_id} is formatted at call time.
_TYPES_ENDPOINT_MAP: dict[str, str] = {
    "Requirement": "project-templates/{template_id}/requirements/types",
    "Test Case": "project-templates/{template_id}/test-cases/types",
    "Task": "project-templates/{template_id}/tasks/types",
    "Risk": "project-templates/{template_id}/risks/types",
    "Incident": "project-templates/{template_id}/incidents/types",
    "Document": "project-templates/{template_id}/document-types?active_only=true",
}


async def _get_artifact_types_impl(
    spira_client, template_id: int, artifact_type: str | None = None
) -> list[dict]:
    """
    Fetch type definitions for artifact kinds.

    When artifact_type is None, fetches all 6 kinds.
    When artifact_type is provided, fetches only that kind (single API call).

    Returns a list of dicts (not a JSON string) for composability.
    Raises on failure (caller handles error wrapping).

    Args:
        spira_client: The Inflectra Spira API client instance
        template_id: The numeric ID of the product template.
        artifact_type: Optional artifact kind to filter to (e.g. "Requirement").

    Returns:
        List of dicts, each with ArtifactTypeName and Types.
    """
    kinds_to_fetch = (
        {artifact_type: _TYPES_ENDPOINT_MAP[artifact_type]}
        if artifact_type is not None
        else _TYPES_ENDPOINT_MAP
    )

    artifact_types: list[dict] = []
    for kind_name, url_pattern in kinds_to_fetch.items():
        types_url = url_pattern.format(template_id=template_id)
        types_data = await spira_client.make_spira_api_get_request(types_url)
        if types_data:
            config = TYPE_FIELD_CONFIGS.get(kind_name)
            if config is not None:
                types_data = _filter_metadata_items(types_data, config)
            else:
                logger.warning(
                    "No TemplateMetadataFieldConfig for artifact kind %r — returning unfiltered",
                    kind_name,
                )
            artifact_types.append({"ArtifactTypeName": kind_name, "Types": types_data})

    return artifact_types


async def _get_section_metadata_impl(
    spira_client,
    template_id: int,
    field_configs: dict[str, TemplateMetadataFieldConfig],
    data_key: str,
    artifact_type: str | None = None,
) -> list[dict]:
    """Generic fetcher for config-driven metadata sections.

    Iterates over field_configs, calls config.endpoint for each kind,
    applies _filter_metadata_items, and wraps results with ArtifactTypeName
    and the section-specific data_key.

    Args:
        spira_client: Async API client.
        template_id: Product template numeric ID.
        field_configs: Dict mapping artifact kind name to its config.
        data_key: Response key name (e.g. "Statuses", "Priorities").
        artifact_type: Optional filter to a single artifact kind.

    Returns:
        List of dicts, each with ArtifactTypeName and data_key.
    """
    configs_to_fetch: dict[str, TemplateMetadataFieldConfig] = (
        {artifact_type: field_configs[artifact_type]}
        if artifact_type is not None
        else field_configs
    )

    results: list[dict] = []
    for kind_name, config in configs_to_fetch.items():
        url = config.endpoint.format(template_id=template_id)
        data = await spira_client.make_spira_api_get_request(url)
        if data:
            filtered = _filter_metadata_items(data, config)
            results.append({"ArtifactTypeName": kind_name, data_key: filtered})

    return results


async def _get_statuses_impl(
    spira_client, template_id: int, artifact_type: str | None = None
) -> list[dict]:
    """Fetch status definitions for artifact kinds."""
    return await _get_section_metadata_impl(
        spira_client, template_id, STATUS_FIELD_CONFIGS, "Statuses", artifact_type
    )


async def _get_priorities_impl(
    spira_client, template_id: int, artifact_type: str | None = None
) -> list[dict]:
    """Fetch priority definitions for artifact kinds."""
    return await _get_section_metadata_impl(
        spira_client, template_id, PRIORITY_FIELD_CONFIGS, "Priorities", artifact_type
    )


async def _get_severities_impl(
    spira_client, template_id: int, artifact_type: str | None = None
) -> list[dict]:
    """Fetch severity definitions for artifact kinds."""
    return await _get_section_metadata_impl(
        spira_client, template_id, SEVERITY_FIELD_CONFIGS, "Severities", artifact_type
    )


async def _get_importances_impl(
    spira_client, template_id: int, artifact_type: str | None = None
) -> list[dict]:
    """Fetch importance definitions for artifact kinds."""
    return await _get_section_metadata_impl(
        spira_client, template_id, IMPORTANCE_FIELD_CONFIGS, "Importances", artifact_type
    )


async def _get_probabilities_impl(
    spira_client, template_id: int, artifact_type: str | None = None
) -> list[dict]:
    """Fetch probability definitions for artifact kinds."""
    return await _get_section_metadata_impl(
        spira_client, template_id, PROBABILITY_FIELD_CONFIGS, "Probabilities", artifact_type
    )


async def _get_impacts_impl(
    spira_client, template_id: int, artifact_type: str | None = None
) -> list[dict]:
    """Fetch impact definitions for artifact kinds."""
    return await _get_section_metadata_impl(
        spira_client, template_id, IMPACT_FIELD_CONFIGS, "Impacts", artifact_type
    )


async def _get_custom_properties_impl(
    spira_client, template_id: int, artifact_type: str | None = None
) -> list[dict]:
    """
    Fetch custom property definitions for artifact kinds.

    When artifact_type is None, fetches all 11 kinds.
    When artifact_type is provided, fetches only that kind (single API call).

    Returns a list of dicts (not a JSON string) for composability.
    Raises on failure (caller handles error wrapping).

    Args:
        spira_client: The Inflectra Spira API client instance
        template_id: The numeric ID of the product template.
        artifact_type: Optional artifact kind to filter to (e.g. "Requirement").

    Returns:
        List of dicts, each with ArtifactTypeName and CustomProperties.
    """
    kinds_to_fetch = (
        (artifact_type,) if artifact_type is not None else VALID_CUSTOM_PROPERTIES_ARTIFACT_KINDS
    )

    artifact_custom_properties: list[dict] = []
    for artifact_type_name in kinds_to_fetch:
        custom_props = await _get_custom_properties_for_artifact_type(
            spira_client, template_id, artifact_type_name
        )

        if custom_props:
            artifact_custom_properties.append(
                {
                    "ArtifactTypeName": artifact_type_name,
                    "CustomProperties": custom_props,
                }
            )

    return artifact_custom_properties
