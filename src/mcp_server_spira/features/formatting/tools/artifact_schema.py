"""Artifact schema tool — derives field schema from ArtifactConfig.field_metadata.

Single source of truth: ArtifactConfig holds field names, types, and descriptions.
No separate hardcoded dict to drift out of sync.
"""

import json

from mcp_server_spira.features.artifact_configs import ARTIFACT_CONFIG

# Types exposed by the get_artifact_schema tool.
# Subset of ARTIFACT_CONFIG keys — excludes "build" and "document" which
# don't have field_metadata (they aren't searchable/gettable by the LLM).
VALID_ARTIFACT_TYPES: tuple[str, ...] = (
    "task",
    "incident",
    "requirement",
    "test_case",
    "release",
    "risk",
    "test_set",
    "test_run",
    "automation_host",
    "capability",
    "milestone",
)


def _get_artifact_schema_impl(artifact_type: str) -> str:
    """Return the field schema for the given artifact type as a JSON string.

    Args:
        artifact_type: One of the values in VALID_ARTIFACT_TYPES.

    Returns:
        JSON string with {"artifact_type": ..., "fields": [...]} on success,
        or {"error": ..., "valid_types": [...]} for an unrecognised type.
        For creatable types, also includes "writable_fields" and
        "required_fields" derived from ArtifactConfig.

    Spec:
        - ALWAYS returns a valid JSON string — never raises
        - Pure function — no API calls, no side effects, no async needed
        - On success: response has "artifact_type" (str) and "fields"
          (list of dicts with name/type/description) — callers parse
          with json.loads without try/except
        - For creatable types (those with create_endpoint set in
          ArtifactConfig), response additionally includes
          "writable_fields" (list[str]) and "required_fields" (list[str])
          derived dynamically from the config
        - On failure (unknown type): response has "error" (str) and
          "valid_types" (sorted list) — callers distinguish success from
          error by checking for "error" key
        - The valid_types list in error response is always sorted
          alphabetically for consistent LLM presentation
        - Schema data is derived from ArtifactConfig.field_metadata —
          single source of truth, validated at import time
    """
    if artifact_type not in VALID_ARTIFACT_TYPES:
        return json.dumps(
            {
                "error": (
                    f"Unknown artifact type '{artifact_type}'. "
                    f"Valid types are: {', '.join(sorted(VALID_ARTIFACT_TYPES))}"
                ),
                "valid_types": sorted(VALID_ARTIFACT_TYPES),
            }
        )

    config = ARTIFACT_CONFIG[artifact_type]

    # Build fields list from config's field_metadata
    # Include all_fields + excluded_fields (same as the previous hardcoded schema)
    all_field_names = config.all_fields + config.excluded_fields
    fields_list = []
    for fname in all_field_names:
        meta = config.field_metadata.get(fname)
        if meta:
            fields_list.append({"name": fname, "type": meta.type, "description": meta.description})
        else:
            # Fallback for fields without metadata (shouldn't happen with validation)
            fields_list.append({"name": fname, "type": "str", "description": ""})

    schema: dict = {
        "artifact_type": artifact_type,
        "fields": fields_list,
    }

    # For creatable types, add writable_fields and required_fields
    if config.create_endpoint:
        schema["writable_fields"] = config.writable_fields
        schema["required_fields"] = config.required_fields

    # Add custom_properties_hint for all artifact types with config
    hint_parts = [
        "'custom_properties' is a virtual field on search/get tools. "
        "Include it in the 'fields' parameter to get a resolved {name: value} dict."
    ]
    if config.create_endpoint:
        hint_parts.append(
            "For creation: pass 'custom_properties' as a {name: value} dict "
            "in the fields object on product_create_artifact."
        )
    if config.update_endpoint:
        hint_parts.append(
            "For updates: pass 'custom_properties' as a {name: value} dict "
            "in the fields object on product_update_artifact. "
            "To clear a property value, set it to null."
        )
    hint_parts.append(
        "You can also filter by custom property names in the 'filters' parameter "
        "using the property display name as the field value."
    )
    schema["custom_properties_hint"] = " ".join(hint_parts)

    return json.dumps(schema, indent=2)


def register_tools(mcp) -> None:
    """Register the get_artifact_schema tool with the MCP server."""

    @mcp.tool(
        name="get_artifact_schema",
        description=(
            "Returns the field schema for a Spira artifact type as JSON.\n"
            "\n"
            "artifact_type: task, incident, requirement, test_case, release, risk, "
            "test_set, test_run, automation_host, capability, milestone\n"
            "Returns: {artifact_type, fields: [{name, type, description}]} or {error, valid_types}."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": False,
        },
    )
    async def get_artifact_schema(artifact_type: str) -> str:
        """Returns the field schema for a Spira artifact type."""
        try:
            return _get_artifact_schema_impl(artifact_type)
        except Exception as e:
            return json.dumps({"error": str(e)})
