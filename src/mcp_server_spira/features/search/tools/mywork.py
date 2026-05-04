"""mywork_search_artifacts unified tool.

Replaces 5 separate my_get_* tools.
"""

import asyncio
import json
from typing import Annotated, Any

from pydantic import WithJsonSchema

from mcp_server_spira.features.artifact_configs import ARTIFACT_CONFIG
from mcp_server_spira.features.search.tools._shared import (
    apply_contains_filter,
    apply_field_projection,
    derive_display_name_field,
)
from mcp_server_spira.utils.common import get_spira_client
from mcp_server_spira.utils.common.pagination import paginate_client_side
from mcp_server_spira.utils.common.responses import (
    ErrorCodes,
    format_error_response,
    format_search_response,
)
from mcp_server_spira.utils.common.validation import ParameterValidator

# Re-export so existing imports (e.g. ``from ...mywork import apply_contains_filter``)
# continue to work.
__all__ = [
    "apply_contains_filter",
    "apply_field_projection",
    "derive_display_name_field",
    "MYWORK_ARTIFACT_TYPES",
    "MyworkArtifactType",
    "_mywork_search_impl",
    "register_tools",
]

# Derived from ArtifactConfig — NOT hardcoded.
# Qualifies as mywork if config has a non-None mywork_endpoint.
MYWORK_ARTIFACT_TYPES: tuple[str, ...] = tuple(
    name for name, cfg in ARTIFACT_CONFIG.items() if cfg.mywork_endpoint is not None
)

# Type hint for the tool signature — advertises valid values in the JSON
# schema (so the LLM sees them in tools/list) but accepts any string at
# Pydantic validation time.  Actual validation happens in _impl.
MyworkArtifactType = Annotated[
    list[str],
    WithJsonSchema(
        {
            "type": "array",
            "items": {
                "type": "string",
                "enum": list(MYWORK_ARTIFACT_TYPES),
            },
        }
    ),
]


async def _single_artifact_search(
    spira_client,
    artifact_type: str,
    fields: list[str] | None,
    status: str | None,
    priority: str | None,
    limit: int,
    offset: int,
) -> dict:
    """Execute the search pipeline for a single artifact type.

    Returns a result dict (NOT a JSON string) with keys:
    ``artifact_type``, ``data``, ``fields_returned``, ``fields_available``,
    ``pagination``, ``warnings``.

    Order of operations: fetch → filter status → filter priority → paginate → project.
    """
    config = ARTIFACT_CONFIG[artifact_type]
    warnings: list[str] = []

    # 1. Fetch
    raw = await spira_client.make_spira_api_get_request(config.mywork_endpoint)
    data: list[dict] = raw if raw else []

    # 2. Filter status
    data, status_warnings = apply_contains_filter(
        data,
        config.status_field,
        status,
        config.all_fields,
        "status",
    )
    warnings.extend(status_warnings)

    # 3. Filter priority
    data, priority_warnings = apply_contains_filter(
        data,
        config.priority_field,
        priority,
        config.all_fields,
        "priority",
    )
    warnings.extend(priority_warnings)

    # 4. Paginate
    page_result = paginate_client_side(data, limit, offset)

    # 5. Project fields
    projected, fields_returned, fields_available, proj_warnings = apply_field_projection(
        page_result["data"],
        fields,
        config.summary_fields,
        config.all_fields,
    )
    warnings.extend(proj_warnings)

    return {
        "artifact_type": artifact_type,
        "data": projected,
        "fields_returned": fields_returned,
        "fields_available": fields_available,
        "pagination": page_result["pagination"],
        "warnings": warnings,
    }


async def _mywork_search_impl(
    spira_client,
    artifact_type: Any,
    fields: list[str] | None,
    status: str | None,
    priority: str | None,
    limit: int,
    offset: int,
) -> str:
    """Core implementation for mywork_search_artifacts.

    Takes *spira_client* as first arg so callers (and tests) can inject a
    mock without touching MCP registration.

    Returns a JSON string — either a search response envelope (single type)
    or a grouped response envelope (multi-type, handled by task 5).
    """
    # 1. Validate pagination
    pagination_error = ParameterValidator.validate_pagination_params(limit, offset)
    if pagination_error is not None:
        return json.dumps(pagination_error, indent=2)

    # 1b. Handle None (omitted parameter)
    if artifact_type is None:
        return format_error_response(
            error="artifact_type is required",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "parameter": "artifact_type",
                "valid_values": list(MYWORK_ARTIFACT_TYPES),
            },
            suggestion="Provide at least one artifact type: " + ", ".join(MYWORK_ARTIFACT_TYPES),
        )

    # 2. Silently coerce bare strings to a single-element list.
    # This makes the tool fault-tolerant while the docstring only advertises
    # the list form.  Must happen before any validation so the rest of the
    # pipeline always sees a list.
    if isinstance(artifact_type, str):
        artifact_type = [artifact_type]

    # 3. Route based on list length
    if len(artifact_type) != 1:
        # Zero elements or two or more → multi-artifact path (validates internally)
        return await _multi_artifact_search(
            spira_client, artifact_type, fields, status, priority, limit, offset
        )

    # Single-element list — unwrap and validate
    single_type = artifact_type[0]

    # 4. Validate artifact_type value
    if single_type not in MYWORK_ARTIFACT_TYPES:
        return format_error_response(
            error="Invalid artifact_type parameter",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "parameter": "artifact_type",
                "value": single_type,
                "valid_values": list(MYWORK_ARTIFACT_TYPES),
            },
            suggestion="Use one of the valid artifact types.",
        )

    # 5. Validate mywork_endpoint exists
    config = ARTIFACT_CONFIG[single_type]
    if config.mywork_endpoint is None:
        return format_error_response(
            error="Artifact type does not support mywork queries",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "parameter": "artifact_type",
                "value": single_type,
            },
            suggestion="This artifact type does not have a mywork endpoint.",
        )

    # 6. Execute single-artifact pipeline
    try:
        result = await _single_artifact_search(
            spira_client, single_type, fields, status, priority, limit, offset
        )
    except Exception as e:
        return format_error_response(
            error=f"Failed to retrieve {single_type} data: {e}",
            error_code=ErrorCodes.API_ERROR,
            suggestion="Check your Spira connection and try again.",
        )

    # 7. Format response envelope
    return format_search_response(
        data=result["data"],
        artifact_type=result["artifact_type"],
        fields_returned=result["fields_returned"],
        pagination=result["pagination"],
        fields_available=result["fields_available"],
        warnings=result["warnings"],
    )


async def _multi_artifact_search(
    spira_client,
    artifact_types: list[str],
    fields: list[str] | None,
    status: str | None,
    priority: str | None,
    limit: int,
    offset: int,
) -> str:
    """Execute search across multiple artifact types concurrently.

    Validates all requested types, fans out via ``asyncio.gather`` with
    ``return_exceptions=True`` so one type's failure doesn't block others,
    and returns a grouped JSON response.
    """
    # Validate all types up front
    invalid = [t for t in artifact_types if t not in MYWORK_ARTIFACT_TYPES]
    if invalid:
        return format_error_response(
            error="Invalid artifact_type value(s) in list",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "parameter": "artifact_type",
                "invalid_values": invalid,
                "valid_values": list(MYWORK_ARTIFACT_TYPES),
            },
            suggestion="Use only valid artifact types in the list.",
        )

    # Fan out one coroutine per type
    coros = [
        _single_artifact_search(spira_client, t, fields, status, priority, limit, offset)
        for t in artifact_types
    ]
    results = await asyncio.gather(*coros, return_exceptions=True)

    # Build grouped response
    groups: list[dict] = []
    for artifact_type_name, result in zip(artifact_types, results, strict=True):
        if isinstance(result, BaseException):
            groups.append(
                {
                    "artifact_type": artifact_type_name,
                    "error": f"Failed to retrieve {artifact_type_name}: {result}",
                    "warnings": [f"API call failed for {artifact_type_name}: {result}"],
                }
            )
        else:
            groups.append(result)

    return json.dumps({"groups": groups}, indent=2, default=str)


def _build_docstring() -> str:
    """Build the dynamic docstring for mywork_search_artifacts at registration time."""
    type_names = ", ".join(MYWORK_ARTIFACT_TYPES)
    first_type = MYWORK_ARTIFACT_TYPES[0]
    return (
        "Retrieves the current user's assigned artifacts from Spira.\n"
        "\n"
        "artifact_type (list[str], required): "
        f"[{type_names}].\n"
        f'Example: ["{first_type}"] for one type, '
        f"or pass multiple types to query in one call."
    )


def register_tools(mcp) -> None:
    """Register the mywork_search_artifacts unified tool."""
    docstring = _build_docstring()

    @mcp.tool(
        name="mywork_search_artifacts",
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )
    async def mywork_search_artifacts(
        artifact_type: MyworkArtifactType | None = None,
        fields: list[str] | None = None,
        status: str | None = None,
        priority: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> str:
        spira_client = get_spira_client()
        return await _mywork_search_impl(
            spira_client, artifact_type, fields, status, priority, limit, offset
        )

    mywork_search_artifacts.__doc__ = docstring
