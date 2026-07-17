"""Custom property resolution and serialization.

Provides:
- CustomPropertyResolver: async class that resolves wire-format custom
  property arrays to friendly {name: value} dicts (GET path) and caches
  definitions per (template_id, artifact_type).
- serialize_custom_properties: pure function that transforms friendly-format
  dicts back into wire-format arrays (POST path).
- resolve_custom_property_filters: async function that separates Tier 2
  filters into standard and CP filters, resolving CP filters to RemoteFilter
  format.
"""

from mcp_server_spira.features.custom_properties.filter_resolver import (
    resolve_custom_property_filters,
)
from mcp_server_spira.features.custom_properties.resolver import (
    CustomPropertyResolver,
    CustomPropertyResult,
)
from mcp_server_spira.features.custom_properties.serializer import serialize_custom_properties

__all__ = [
    "CustomPropertyResolver",
    "CustomPropertyResult",
    "resolve_custom_property_filters",
    "serialize_custom_properties",
]
