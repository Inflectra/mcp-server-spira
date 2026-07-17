"""TemplateContext — shared per-invocation context for template-dependent resolution.

Owns the template_id cache and the canonical artifact-type name mappings.
Passed to both NameResolver and CustomPropertyResolver at construction so
they share a single cache — eliminating redundant API calls in multi-resolver
pipelines.

Instance lifetime matches a single tool invocation (no global state).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_server_spira.utils.spira_client import SpiraClient

logger = logging.getLogger(__name__)

# Canonical mapping: tool-facing artifact_type → template metadata kind string.
# Used by NameResolver for status/priority/type resolution.
# Format: space-separated words (e.g. "Test Case", "Automation Host").
_METADATA_ARTIFACT_KIND_MAP: dict[str, str] = {
    "incident": "Incident",
    "task": "Task",
    "requirement": "Requirement",
    "test_case": "Test Case",
    "risk": "Risk",
    "release": "Release",
    "test_set": "Test Set",
    "test_run": "Test Run",
    "document": "Document",
    "build": "Build",
    "automation_host": "Automation Host",
}

# Canonical mapping: tool-facing artifact_type → custom property API type name.
# Used by CustomPropertyResolver for definitions lookup.
# Format: PascalCase (e.g. "TestCase", "AutomationHost").
_CUSTOM_PROPERTY_API_NAME_MAP: dict[str, str] = {
    "incident": "Incident",
    "task": "Task",
    "requirement": "Requirement",
    "test_case": "TestCase",
    "risk": "Risk",
    "release": "Release",
    "test_set": "TestSet",
    "test_run": "TestRun",
    "automation_host": "AutomationHost",
    "document": "Document",
}


class TemplateContext:
    """Shared per-invocation context for template-dependent resolution.

    Owns the template_id cache and the canonical artifact-type name mapping.
    Passed to both NameResolver and CustomPropertyResolver at construction.

    Spec:
        - Instance-scoped (one per tool invocation) — no global state
        - get_template_id returns int | None, never raises
        - Single API call per product_id, shared across all consumers
        - get_metadata_artifact_kind and get_custom_property_api_name are
          pure lookups — no I/O, no side effects
        - Both mapping methods return None for unknown artifact types
          (callers decide how to handle)
    """

    def __init__(self, spira_client: SpiraClient) -> None:
        self._client = spira_client
        # Cache: product_id → template_id
        self._template_cache: dict[int, int] = {}

    async def get_template_id(self, product_id: int) -> int | None:
        """Resolve and cache ProjectTemplateId for a product.

        Single API call per product_id, shared across all consumers.

        Spec:
            - Returns int on success, None on failure — never raises
            - Caches per product_id — second call makes zero API calls
            - Calls GET projects/{product_id}, extracts ProjectTemplateId
            - Non-dict response → None (graceful degradation)
            - Missing ProjectTemplateId key → None
            - Non-int ProjectTemplateId value → None
            - API exception → None (logged, not propagated)
        """
        if product_id in self._template_cache:
            return self._template_cache[product_id]

        try:
            data = await self._client.make_spira_api_get_request(f"projects/{product_id}")
            if isinstance(data, dict):
                raw_id = data.get("ProjectTemplateId")
                if isinstance(raw_id, int):
                    self._template_cache[product_id] = raw_id
                    return raw_id
            logger.warning("No ProjectTemplateId in response for product %d", product_id)
            return None
        except Exception:
            logger.exception("Failed to fetch template ID for product %d", product_id)
            return None

    def get_metadata_artifact_kind(self, artifact_type: str) -> str | None:
        """Canonical mapping: tool-facing name → template metadata kind.

        Returns "Incident", "Test Case", "Requirement", etc.
        Used by NameResolver for status/priority/type resolution.

        Spec:
            - Pure lookup — no I/O, no side effects
            - Returns None for unknown artifact types
        """
        return _METADATA_ARTIFACT_KIND_MAP.get(artifact_type)

    def get_custom_property_api_name(self, artifact_type: str) -> str | None:
        """Canonical mapping: tool-facing name → custom property API name.

        Returns "Incident", "TestCase", "Requirement", etc.
        Used by CustomPropertyResolver for definitions lookup.

        Spec:
            - Pure lookup — no I/O, no side effects
            - Returns None for unknown artifact types
        """
        return _CUSTOM_PROPERTY_API_NAME_MAP.get(artifact_type)
