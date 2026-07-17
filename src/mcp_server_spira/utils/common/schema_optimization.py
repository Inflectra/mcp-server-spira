"""Post-process tool JSON schemas to reduce token cost in tools/list.

Removes Pydantic-generated noise (title fields, verbose anyOf nullable
patterns) that adds tokens without improving LLM understanding. The
underlying tool signatures and validation are unchanged — only the
serialized schema seen by the LLM is affected.

Spec:
    - Mutates tool.parameters dicts in-place for all registered tools
    - Strips all "title" keys recursively (they just repeat param names)
    - Collapses {"anyOf": [<type>, {"type": "null"}], "default": null}
      into {<type>, "default": null} — LLMs infer optionality from
      "default": null without needing the verbose union syntax
    - Never removes "type", "enum", "items", "default", "required",
      "properties", or "description" — these carry semantic meaning
    - Idempotent — safe to call multiple times
    - No effect on runtime validation (Pydantic still uses the original
      model, not the serialized schema)
"""

from __future__ import annotations

from typing import Any


def _strip_titles(obj: Any) -> None:
    """Recursively remove all 'title' keys from a JSON schema object."""
    if isinstance(obj, dict):
        obj.pop("title", None)
        for v in obj.values():
            _strip_titles(v)
    elif isinstance(obj, list):
        for v in obj:
            _strip_titles(v)


def _collapse_nullable(schema: dict[str, Any]) -> None:
    """Collapse verbose anyOf nullable patterns in properties.

    Transforms:
        {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null}
    Into:
        {"type": "string", "default": null}

    Only collapses 2-element anyOf where one element is {"type": "null"}.
    """
    if "properties" not in schema:
        return
    for prop in schema["properties"].values():
        if not isinstance(prop, dict):
            continue
        if "anyOf" in prop and len(prop["anyOf"]) == 2:
            types = prop["anyOf"]
            non_null = [t for t in types if t != {"type": "null"}]
            if len(non_null) == 1:
                del prop["anyOf"]
                prop.update(non_null[0])
        # Recurse into nested properties (e.g. items with properties)
        if "properties" in prop:
            _collapse_nullable(prop)


def optimize_tool_schemas(mcp) -> None:
    """Strip schema noise from all registered tools.

    Call after register_all(mcp) in server.py. Mutates each tool's
    parameters dict in-place.

    Spec:
        - Iterates all tools in mcp._tool_manager._tools
        - Applies _strip_titles then _collapse_nullable to each
          tool.parameters dict
        - Idempotent — repeated calls produce the same result
        - Does not modify tool.fn, tool.fn_metadata, or any runtime
          validation behavior
    """
    for tool in mcp._tool_manager._tools.values():
        schema = tool.parameters
        _strip_titles(schema)
        _collapse_nullable(schema)
