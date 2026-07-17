"""Field resolution for artifact creation.

Two concerns:
1. **Field name correction** — if the LLM uses a wrong field name, match
   it to the correct writable field using case-insensitive exact match,
   then substring fallback. Works for ALL writable fields.
2. **String-to-ID resolution** — if a known ID field has a string value,
   resolve it to an integer via NameResolver. Driven by
   ``config.resolvable_fields`` (field_name → metadata_section mapping).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from mcp_server_spira.features.search.name_resolver import NameResolver

if TYPE_CHECKING:
    from mcp_server_spira.features.search.template_context import TemplateContext
    from mcp_server_spira.models import ArtifactConfig, SubArtifactConfig
    from mcp_server_spira.utils.spira_client import SpiraClient

logger = logging.getLogger(__name__)


def _match_writable_field(key: str, writable_fields: list[str]) -> str | None:
    """Match an unrecognized key to a writable field.

    Uses the same matching strategy as NameResolver for values:
    1. Case-insensitive exact match
    2. Case-insensitive substring (key in field OR field in key),
       only if exactly one field matches

    Spec:
        - Pure function — no I/O, no side effects
        - Returns the matched field name, or None
        - Exact match (case-insensitive) takes priority over substring
        - Substring match only succeeds with exactly one match (no ambiguity)
        - Minimum key length of 4 to avoid false positives on substrings
    """
    key_lower = key.lower()

    # Exact match (case-insensitive)
    for field in writable_fields:
        if field.lower() == key_lower:
            return field

    # Substring match — only if key is long enough to be meaningful
    if len(key_lower) < 4:
        return None

    matches = [
        f
        for f in writable_fields
        if key_lower in f.lower() or f.lower().removesuffix("s") in key_lower
    ]
    if len(matches) == 1:
        return matches[0]
    return None


async def resolve_fields_for_create(
    spira_client: SpiraClient,
    template_context: TemplateContext,
    config: ArtifactConfig | SubArtifactConfig,
    artifact_type: str,
    product_id: int,
    fields: list[dict[str, Any]],
) -> list[str]:
    """Resolve field names and string values in field dicts for creation/update.

    Pass 1: For each key not in writable_fields, try to match it to a
    writable field (case-insensitive exact, then substring). Rename on match.

    Pass 2: For fields listed in ``config.resolvable_fields`` with string
    values, resolve via NameResolver. The mapping is field_name → metadata
    section (e.g. ``{"SeverityId": "severities"}``). SubArtifactConfig has
    no resolvable_fields so Pass 2 is a no-op for them.

    Spec:
        - ALWAYS returns a list of warning strings — never raises
        - Mutates items in fields in-place (renames keys, replaces values)
        - Field name matching works for ALL writable fields (both ArtifactConfig
          and SubArtifactConfig)
        - Value resolution driven by config.resolvable_fields dict;
          SubArtifactConfig has no such attribute so Pass 2 is a no-op
        - Resolution success → value replaced with integer ID
        - Resolution failure → field removed from dict to prevent raw string
          from reaching the API (which would cause HTTP 400), warning added
        - template_id fetch failure → skip value resolution, warn once
        - All operations are async-safe (NameResolver uses await)
    """
    warnings: list[str] = []
    writable_list = config.writable_fields or []
    writable_set = set(writable_list)
    # Pseudo-fields that shouldn't trigger unknown-field warnings
    writable_set.add("custom_properties")
    writable_set.add("CustomProperties")

    # Get resolvable_fields from config (ArtifactConfig has it, SubArtifactConfig doesn't)
    resolvable: dict[str, str] = getattr(config, "resolvable_fields", None) or {}

    # Resolve template_id once
    template_id = await template_context.get_template_id(product_id)
    if template_id is None:
        warnings.append(
            f"Could not resolve template for product {product_id}. "
            "String-to-ID resolution skipped; integer IDs required."
        )

    resolver = NameResolver(spira_client, template_context)

    for item_index, item in enumerate(fields):
        # --- Pass 1: Field name correction ---
        for key in list(item.keys()):
            if key in writable_set:
                continue  # Already correct

            matched = _match_writable_field(key, writable_list)
            if matched is not None and matched != key:
                if matched in item:
                    warnings.append(
                        f"Field '{key}' (item {item_index}): "
                        f"matched '{matched}' but it's already present. "
                        f"'{key}' dropped."
                    )
                    del item[key]
                else:
                    item[matched] = item.pop(key)
            elif matched is None:
                warnings.append(
                    f"Field '{key}' (item {item_index}): "
                    f"not recognized for '{artifact_type}'. "
                    f"It may be ignored by the API."
                )

        # --- Pass 2: String-to-ID resolution ---
        for field_name, section in resolvable.items():
            if field_name not in item:
                continue
            value = item[field_name]
            if not isinstance(value, str):
                continue

            resolved, w = await _resolve_value(resolver, section, template_id, artifact_type, value)
            if w:
                warnings.append(f"Field '{field_name}' (item {item_index}): {w}")
            if isinstance(resolved, int):
                item[field_name] = resolved
            else:
                # Resolution failed — remove the field to prevent sending
                # a raw string to the API (which would cause HTTP 400).
                del item[field_name]
                warnings.append(
                    f"Field '{field_name}' (item {item_index}): "
                    f"could not resolve '{value}' to a valid ID. "
                    f"Field removed from request."
                )

    return warnings


async def _resolve_value(
    resolver: NameResolver,
    section: str,
    template_id: int | None,
    artifact_type: str,
    value: str,
) -> tuple[Any, str | None]:
    """Resolve a string value to an integer ID.

    Returns (resolved_value, warning). If resolution fails, returns the
    original string value unchanged — the caller is responsible for
    detecting unresolved strings and removing them from the request.

    Spec:
        - Returns (int, None) on success
        - Returns (int, None) for integer-strings (e.g. "2") without API call
        - Returns (original_str, warning) on failure — never raises
        - Skips NameResolver when template_id is None (int bypass only)
    """
    # Integer-string bypass
    try:
        return int(value), None
    except (ValueError, TypeError):
        pass

    if template_id is None:
        return value, (
            f"value '{value}' is a string but template resolution "
            f"unavailable. Pass an integer ID instead."
        )

    resolved_id, warning = await resolver.resolve_by_section(
        section, template_id, artifact_type, value
    )
    if resolved_id is not None:
        return resolved_id, None
    return value, warning
