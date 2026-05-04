"""Unified template metadata tool.

Replaces 2 separate template configuration tools
(system_get_artifact_types, template_get_custom_properties)
with a single template_get_metadata tool.
"""

import asyncio
import json
from typing import Annotated, Any

from pydantic import WithJsonSchema

from mcp_server_spira.features.metadata.helpers import (
    VALID_CUSTOM_PROPERTIES_ARTIFACT_KINDS,
    VALID_IMPACTS_ARTIFACT_KINDS,
    VALID_IMPORTANCES_ARTIFACT_KINDS,
    VALID_PRIORITIES_ARTIFACT_KINDS,
    VALID_PROBABILITIES_ARTIFACT_KINDS,
    VALID_SEVERITIES_ARTIFACT_KINDS,
    VALID_STATUSES_ARTIFACT_KINDS,
    VALID_TYPES_ARTIFACT_KINDS,
    _get_artifact_types_impl,
    _get_custom_properties_impl,
    _get_impacts_impl,
    _get_importances_impl,
    _get_priorities_impl,
    _get_probabilities_impl,
    _get_severities_impl,
    _get_statuses_impl,
)
from mcp_server_spira.utils.common import get_spira_client
from mcp_server_spira.utils.common.responses import (
    ErrorCodes,
    format_error_response,
)
from mcp_server_spira.utils.common.validation import ParameterValidator

VALID_METADATA_TYPES: tuple[str, ...] = (
    "types",
    "custom_properties",
    "statuses",
    "priorities",
    "severities",
    "importances",
    "probabilities",
    "impacts",
)

# Type hint for the tool signature — advertises valid values in the JSON
# schema (so the LLM sees them in tools/list) but accepts any string at
# Pydantic validation time.  Actual validation happens in _impl.
TemplateMetadataType = Annotated[
    list[str],
    WithJsonSchema(
        {
            "type": "array",
            "items": {
                "type": "string",
                "enum": list(VALID_METADATA_TYPES),
            },
        }
    ),
]

_SECTION_FETCHERS: dict[str, Any] = {
    "types": _get_artifact_types_impl,
    "custom_properties": _get_custom_properties_impl,
    "statuses": _get_statuses_impl,
    "priorities": _get_priorities_impl,
    "severities": _get_severities_impl,
    "importances": _get_importances_impl,
    "probabilities": _get_probabilities_impl,
    "impacts": _get_impacts_impl,
}

_SECTION_VALID_ARTIFACT_KINDS: dict[str, tuple[str, ...]] = {
    "types": VALID_TYPES_ARTIFACT_KINDS,
    "custom_properties": VALID_CUSTOM_PROPERTIES_ARTIFACT_KINDS,
    "statuses": VALID_STATUSES_ARTIFACT_KINDS,
    "priorities": VALID_PRIORITIES_ARTIFACT_KINDS,
    "severities": VALID_SEVERITIES_ARTIFACT_KINDS,
    "importances": VALID_IMPORTANCES_ARTIFACT_KINDS,
    "probabilities": VALID_PROBABILITIES_ARTIFACT_KINDS,
    "impacts": VALID_IMPACTS_ARTIFACT_KINDS,
}


async def _template_get_metadata_impl(
    spira_client,
    template_id: int,
    metadata_type: Any,
    artifact_type: str | None = None,
) -> str:
    """Core implementation for template_get_metadata.

    Takes *spira_client* as first arg so callers (and tests) can inject a
    mock without touching MCP registration.

    Returns a JSON string — either a response envelope or an error response.
    """
    warnings: list[str] = []

    # 0. Handle None (omitted parameter)
    if metadata_type is None:
        return format_error_response(
            error="metadata_type is required",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "parameter": "metadata_type",
                "valid_values": list(VALID_METADATA_TYPES),
            },
            suggestion="Provide at least one metadata type: " + ", ".join(VALID_METADATA_TYPES),
        )

    # 1. Coerce bare string to single-element list
    if isinstance(metadata_type, str):
        metadata_type = [metadata_type]

    # 1b. Reject non-list types (int, float, bool, dict, etc.)
    if not isinstance(metadata_type, list):
        return format_error_response(
            error="Invalid metadata_type parameter",
            error_code=ErrorCodes.INVALID_TYPE,
            details={
                "parameter": "metadata_type",
                "value": str(metadata_type),
                "expected_type": "list[str]",
            },
            suggestion="metadata_type must be a list of strings: "
            '["types"], ["custom_properties"], or both',
        )

    # 2. Validate template_id
    validation_error = ParameterValidator.validate_positive_integer(template_id, "template_id")
    if validation_error:
        return format_error_response(**validation_error)

    # 3. Validate non-empty list
    if not metadata_type:
        return format_error_response(
            error="Invalid metadata_type parameter",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "parameter": "metadata_type",
                "value": metadata_type,
                "valid_values": list(VALID_METADATA_TYPES),
            },
            suggestion="Provide at least one metadata type: types, custom_properties",
        )

    # 4. Validate all values
    invalid = [v for v in metadata_type if v not in VALID_METADATA_TYPES]
    if invalid:
        return format_error_response(
            error="Invalid metadata_type value(s)",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "parameter": "metadata_type",
                "invalid_values": invalid,
                "valid_values": list(VALID_METADATA_TYPES),
            },
            suggestion="Use only valid metadata types: types, custom_properties",
        )

    # 5. Deduplicate with warning
    seen: set[str] = set()
    unique_types: list[str] = []
    for t in metadata_type:
        if t not in seen:
            seen.add(t)
            unique_types.append(t)
    if len(unique_types) < len(metadata_type):
        warnings.append(f"Duplicate metadata_type values were removed. Fetching: {unique_types}")
    metadata_type = unique_types

    # 6. Validate artifact_type against valid kinds per section
    #    Determine which sections are valid/invalid for the given artifact_type
    sections_to_fetch = list(metadata_type)
    if artifact_type is not None:
        valid_sections: list[str] = []
        invalid_sections: list[str] = []
        for section in metadata_type:
            valid_kinds = _SECTION_VALID_ARTIFACT_KINDS[section]
            if artifact_type in valid_kinds:
                valid_sections.append(section)
            else:
                invalid_sections.append(section)

        if not valid_sections:
            # Invalid for ALL requested sections → hard error
            details: dict[str, Any] = {
                "parameter": "artifact_type",
                "value": artifact_type,
            }
            for section in metadata_type:
                details[f"valid_artifact_kinds_for_{section}"] = list(
                    _SECTION_VALID_ARTIFACT_KINDS[section]
                )
            return format_error_response(
                error=f"Invalid artifact_type '{artifact_type}' for requested section(s)",
                error_code=ErrorCodes.INVALID_PARAMETER,
                details=details,
                suggestion="Provide an artifact_type that is valid for at least one "
                "requested metadata section, or omit it to fetch all artifact kinds",
            )

        # Some sections invalid → fetch valid ones, error entry for invalid
        sections_to_fetch = valid_sections
        for section in invalid_sections:
            warnings.append(
                f"artifact_type '{artifact_type}' is not valid for the "
                f"'{section}' section. Valid kinds: "
                f"{list(_SECTION_VALID_ARTIFACT_KINDS[section])}"
            )

    # 7. Fetch sections
    sections: dict[str, Any] = {}

    # Pre-populate error entries for sections invalid due to artifact_type
    if artifact_type is not None:
        for section in metadata_type:
            if section not in sections_to_fetch:
                sections[section] = {
                    "error": f"artifact_type '{artifact_type}' is not valid for "
                    f"the '{section}' section"
                }

    if len(sections_to_fetch) == 1:
        # Single section — call directly
        section_name = sections_to_fetch[0]
        fetcher = _SECTION_FETCHERS[section_name]
        try:
            sections[section_name] = await fetcher(
                spira_client, template_id, artifact_type=artifact_type
            )
        except Exception as e:
            sections[section_name] = {"error": f"Failed to retrieve {section_name} data: {e}"}
            warnings.append(f"Failed to retrieve {section_name} section: {e}")
    elif len(sections_to_fetch) > 1:
        # Multiple sections — concurrent fetch
        coros = [
            _SECTION_FETCHERS[name](spira_client, template_id, artifact_type=artifact_type)
            for name in sections_to_fetch
        ]
        results = await asyncio.gather(*coros, return_exceptions=True)

        for name, result in zip(sections_to_fetch, results, strict=True):
            if isinstance(result, BaseException):
                sections[name] = {"error": f"Failed to retrieve {name} data: {result}"}
                warnings.append(f"Failed to retrieve {name} section: {result}")
            else:
                sections[name] = result

    # 8. Build response envelope
    response = {
        "template_id": template_id,
        "sections": sections,
        "warnings": warnings,
    }
    return json.dumps(response, indent=2, default=str)


def register_tools(mcp) -> None:
    """Register the template_get_metadata unified tool."""

    @mcp.tool(
        name="template_get_metadata",
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )
    async def template_get_metadata(
        template_id: int,
        metadata_type: TemplateMetadataType | None = None,
        artifact_type: str | None = None,
    ) -> str:
        """Retrieves template metadata sections for a product template.

        metadata_type (list[str], required): Sections to fetch.
          - "types": Artifact type definitions per artifact kind
            (e.g. Requirement types: Use Case, User Story).
          - "custom_properties": Custom field definitions per artifact kind.
          - "statuses": Status definitions per artifact kind
            (Requirement, Incident, Task, Risk, Release, Test Case, Document).
          - "priorities": Priority definitions per artifact kind
            (Incident, Task, Test Case).
          - "severities": Severity definitions (Incident only).
          - "importances": Importance definitions (Requirement only).
          - "probabilities": Probability definitions (Risk only).
          - "impacts": Impact definitions (Risk only).
        template_id (int, required): Numeric ID of the product template
          (e.g. 45 for PT:45).
        artifact_type (str, optional): Filter to a single artifact kind
          (e.g. "Requirement"). When omitted, all artifact kinds are fetched.

        Returns JSON with template_id, sections dict, and warnings list.
        """
        spira_client = get_spira_client()
        return await _template_get_metadata_impl(
            spira_client, template_id, metadata_type, artifact_type=artifact_type
        )
