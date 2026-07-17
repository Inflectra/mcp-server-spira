"""mywork_search_artifacts unified tool.

Replaces 5 separate my_get_* tools.
"""

import asyncio
import json
from typing import Annotated, Any

from pydantic import WithJsonSchema

from mcp_server_spira.features.artifact_configs import ARTIFACT_CONFIG
from mcp_server_spira.features.custom_properties.resolver import (
    CustomPropertyResolver,
)
from mcp_server_spira.features.search.template_context import TemplateContext
from mcp_server_spira.features.search.tools._shared import (
    apply_contains_filter,
)
from mcp_server_spira.utils.common import SpiraApiError, _sanitize_error, get_spira_client
from mcp_server_spira.utils.common.pagination import paginate_client_side
from mcp_server_spira.utils.common.responses import (
    ErrorCodes,
    format_error_response,
    format_search_response,
)
from mcp_server_spira.utils.common.validation import ParameterValidator

__all__ = [
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
    custom_property_resolver: CustomPropertyResolver | None = None,
) -> dict:
    """Execute the search pipeline for a single artifact type.

    Returns a result dict (NOT a JSON string) with keys:
    ``artifact_type``, ``data``, ``fields_returned``, ``fields_available``,
    ``pagination``, ``warnings``.

    Order of operations: fetch → filter status → filter priority → paginate → project.

    Spec:
        - ALWAYS returns a dict with keys: artifact_type, data, fields_returned,
          fields_available, pagination, warnings — callers destructure without
          key-existence checks
        - warnings is always a list (never None) — accumulated from status
          filter, priority filter, and field projection steps
        - Unsupported filters (config field is None) produce a warning and the
          search proceeds without that filter — never an error/exception
        - Zero-match filters return all data unfiltered with a warning (via
          apply_contains_filter contract) — callers never see empty data due
          solely to a bad filter value
        - Pipeline order is fetch → filter status → filter priority →
          paginate → project — filtering reduces total_count BEFORE
          pagination, so pagination.total_count reflects filtered count
        - pagination dict comes from paginate_client_side — has keys: limit,
          offset, returned_count, total_count, has_more, pagination_type
        - May raise on API errors (GET failure) — caller (_mywork_search_impl)
          is responsible for catching and converting to error envelope
        - Field projection applies after pagination — data objects contain
          only the requested (or summary default) fields
        - fields=None → summary_fields used; fields_available shows the delta
        - artifact_type in the response matches the input artifact_type string
        - When custom_property_resolver is provided and "custom_properties" is
          in fields, resolves custom properties per-artifact using each
          artifact's ProjectId for template resolution
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
    paginated_data: list[dict] = page_result["data"]

    # 5. Project fields, resolve CPs, inject — via shared pipeline
    from mcp_server_spira.features.search.tools._projection import project_and_enrich

    projection = await project_and_enrich(
        paginated_data,
        fields,
        config,
        cp_resolver=custom_property_resolver,
        product_id=None,  # mywork: cross-product, uses per-artifact ProjectId
        pagination=page_result["pagination"],
    )
    warnings.extend(projection.warnings)

    result: dict = {
        "data": projection.data,
        "artifact_type": artifact_type,
        "fields_returned": projection.fields_returned,
        "fields_available": projection.fields_available,
        "pagination": page_result["pagination"],
        "warnings": warnings,
    }
    if projection.custom_properties_resolved:
        result["custom_properties_resolved"] = True

    return result


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

    Spec:
        Return type:
            - ALWAYS returns a JSON string (never raises, never returns None)
            - On success (single type): search envelope via format_search_response
              with keys: data, artifact_type, fields_returned, fields_available,
              pagination, warnings
            - On success (multi-type): grouped envelope with key "groups"
              containing one entry per requested type
            - On validation failure: error envelope with error_code

        Validation order (short-circuits on first failure):
            1. Pagination params (limit in [1,500], offset >= 0)
            2. artifact_type is not None
            3. Bare string silently coerced to single-element list (fault-tolerant)
            4. Routing: len != 1 → multi-artifact path; len == 1 → single path
            5. Single path: artifact_type value in MYWORK_ARTIFACT_TYPES
            6. Single path: config.mywork_endpoint is not None

        Routing invariants:
            - len(artifact_type) == 1 → single-type path → search envelope
            - len(artifact_type) == 0 or > 1 → multi-type path → grouped envelope
            - Bare string coerced to ["string"] → routes to single-type path

        Error handling:
            - API exceptions caught and converted to error envelope with
              error_code=API_ERROR — never raises to the MCP layer
            - Validation errors return error envelope with
              error_code=INVALID_PARAMETER — no API call made

        Warnings accumulation:
            - Single-type: warnings from _single_artifact_search passed through
              in the search envelope
            - Multi-type: per-group warnings preserved in each group entry
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

    # 5b. Instantiate CustomPropertyResolver (shared across artifacts in batch)
    # NOTE: mywork uses GET (not POST with filters), so custom property
    # filters cannot be applied server-side. The tool intentionally does
    # not accept a `filters` parameter — CP filters are blocked at the
    # tool interface level. See Requirement 11.13.
    template_context = TemplateContext(spira_client)
    custom_property_resolver = CustomPropertyResolver(spira_client, template_context)

    # 6. Execute single-artifact pipeline
    try:
        result = await _single_artifact_search(
            spira_client,
            single_type,
            fields,
            status,
            priority,
            limit,
            offset,
            custom_property_resolver=custom_property_resolver,
        )
    except SpiraApiError as e:
        return format_error_response(
            error=f"Failed to retrieve {single_type} data: {e}",
            error_code=e.error_code,
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
        custom_properties_resolved=result.get("custom_properties_resolved", False),
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

    Spec:
        - ALWAYS returns a JSON string (never raises) — caller can return
          it directly to the MCP layer
        - Response has a top-level "groups" key containing a list
        - len(groups) ALWAYS equals len(artifact_types) — no type is ever
          silently dropped, even on failure
        - Failed types get an entry with "artifact_type", "error", and
          non-empty "warnings" keys — no "data", "fields_returned",
          "fields_available", or "pagination" keys present
        - Successful types get the full dict from _single_artifact_search
          (artifact_type, data, fields_returned, fields_available,
          pagination, warnings)
        - Uses asyncio.gather with return_exceptions=True — one type's
          failure never prevents other types from returning results
        - Validation of all types happens BEFORE any API calls — if any
          type is invalid, returns error envelope immediately with no
          API calls made
        - Empty list input (len == 0) returns {"groups": []} — valid
          grouped response with no API calls
        - Order of groups matches order of input artifact_types list
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

    # Fan out one coroutine per type — shared resolver for template caching
    template_context = TemplateContext(spira_client)
    custom_property_resolver = CustomPropertyResolver(spira_client, template_context)
    coros = [
        _single_artifact_search(
            spira_client,
            t,
            fields,
            status,
            priority,
            limit,
            offset,
            custom_property_resolver=custom_property_resolver,
        )
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
                    "error": f"Failed to retrieve {artifact_type_name}: {_sanitize_error(result)}",
                    "warnings": [
                        f"API call failed for {artifact_type_name}: {_sanitize_error(result)}"
                    ],
                }
            )
        else:
            groups.append(result)

    return json.dumps({"groups": groups}, indent=2, default=str)


def _build_docstring() -> str:
    """Build the dynamic docstring for mywork_search_artifacts at registration time."""
    type_names = ", ".join(MYWORK_ARTIFACT_TYPES)
    return f"Retrieve the current user's assigned artifacts.\n\nartifact_type: [{type_names}]"


def register_tools(mcp) -> None:
    """Register the mywork_search_artifacts unified tool."""
    docstring = _build_docstring()

    @mcp.tool(
        name="mywork_search_artifacts",
        description=docstring,
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
        """Retrieve the current user's assigned artifacts."""
        spira_client = get_spira_client()
        return await _mywork_search_impl(
            spira_client, artifact_type, fields, status, priority, limit, offset
        )
