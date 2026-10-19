"""Pure helpers that merge provenance tags into an artifact's ``Tags`` field.

Synchronous by design (no I/O), a deliberate exception to the project's
"async everywhere" rule: the async create/update ``_impl`` functions call
these directly, without ``await``.
"""

from mcp_server_spira.models import ArtifactConfig


def merge_tags(existing: str | None, injected: str) -> str:
    """Append-if-absent merge of two comma-delimited tag strings.

    Spec:
        - Split both on ",", trim each token, drop empties
        - Normalize existing tokens by keeping the first token for each
          case-insensitive key; first existing occurrence and casing win
        - Append injected tokens not already present (case-insensitive match)
        - Dedup is case-insensitive; normalized existing casing always wins
        - Dedup injected-against-injected too: keep first occurrence in
          injected order, drop later case-insensitive duplicates
        - Re-join on ", "
        - Pure, synchronous, no I/O; idempotent when injected ⊆ existing
    """
    seen_keys: set[str] = set()
    result: list[str] = []

    # Existing tokens: first occurrence/casing wins per case-insensitive key.
    for token in (existing or "").split(","):
        token = token.strip()
        if not token:
            continue
        key = token.casefold()
        if key in seen_keys:
            continue
        seen_keys.add(key)
        result.append(token)

    # Append injected tokens not already seen (dedup is case-insensitive).
    for token in injected.split(","):
        token = token.strip()
        if not token:
            continue
        key = token.casefold()
        if key in seen_keys:
            continue
        seen_keys.add(key)
        result.append(token)

    return ", ".join(result)


def inject_tags(item: dict, config, injected: str | None) -> None:
    """Merge `injected` into item["Tags"] in place, if the gate passes.

    Spec:
        - No-op when injected is None (caller passed a disabled env value)
        - No-op unless isinstance(config, ArtifactConfig) and
          "Tags" in config.writable_fields
        - This positive ArtifactConfig gate excludes all SubArtifactConfig
          types, including test_step, mitigation, and requirement_step; the
          test_step config may carry writable "Tags" but MUST NOT be tagged
        - No-op for any other config-like object, even if it has writable
          "Tags"
        - Otherwise sets item["Tags"] = merge_tags(item.get("Tags"), injected)
        - Mutates item in place; adds no key other than "Tags"; returns None
        - Pure gate + single mutation; no I/O, raises nothing
    """
    if injected is None:
        return
    if not (isinstance(config, ArtifactConfig) and "Tags" in config.writable_fields):
        return
    item["Tags"] = merge_tags(item.get("Tags"), injected)
