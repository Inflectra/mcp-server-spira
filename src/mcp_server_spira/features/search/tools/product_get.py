"""product_get_artifact tool — single-artifact retrieval with include enrichment.

Separated from product.py to concentrate GET-specific logic (embedded
extraction, unconditional CP resolution, field projection) in one
focused module. The search pipeline lives in product.py.
"""

from __future__ import annotations

import json
from typing import Any

from mcp_server_spira.config import resolve_product_id
from mcp_server_spira.features.artifact_configs import ARTIFACT_CONFIG
from mcp_server_spira.features.custom_properties.resolver import CustomPropertyResolver
from mcp_server_spira.features.search.template_context import TemplateContext
from mcp_server_spira.features.search.tools._include import (
    enrich_with_includes,
    resolve_includes,
)
from mcp_server_spira.features.search.tools.product import (
    PRODUCT_ARTIFACT_TYPES,
    ProductArtifactType,
)
from mcp_server_spira.features.sub_artifact_configs import SUB_ARTIFACT_CONFIG
from mcp_server_spira.utils.common import SpiraApiError, get_spira_client
from mcp_server_spira.utils.common.field_projection import apply_field_projection
from mcp_server_spira.utils.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.utils.common.validation import ParameterValidator


async def _product_get_impl(
    spira_client,
    artifact_type: Any,
    artifact_id: int,
    product_id: int | None,
    release_id: int | None = None,
    *,
    include: list[str] | None = None,
) -> str:
    """Single-item retrieval with field projection.

    Takes *spira_client* as first arg so callers (and tests) can inject a
    mock without touching MCP registration.

    Returns a JSON string via ``format_success_response``.

    Spec:
        - ALWAYS returns a JSON string (never raises to the MCP layer)
        - On success: response has "data" key containing the full artifact
          object (all LLM-visible fields, excluded fields stripped)
        - fields_available is NOT present in the response — design doc says
          "Always returns full object. fields_available omitted."
        - custom_properties key is ALWAYS present when the artifact type
          supports custom properties (has CustomProperties in excluded_fields),
          even if all values are null → empty dict. Absent only when the
          artifact type has no CP support.
        - Validation failures (bad artifact_type, missing product_id, missing
          release_id for builds) short-circuit before any API call and return
          error envelope with error_code
        - API exceptions caught and converted to error envelope with
          error_code=API_ERROR
        - Not-found (None/empty API response) returns error envelope with
          error_code=NOT_FOUND
        - When include is provided, sub-artifact or comment data is enriched
          onto the artifact object; warnings from include resolution are
          included in the response
        - product_id=None resolves from SPIRA_PROJECT_ID env — error envelope
          if both are unset
    """
    # 1. Validate artifact_type
    type_error = ParameterValidator.validate_type_param(
        artifact_type, PRODUCT_ARTIFACT_TYPES, "artifact_type"
    )
    if type_error is not None:
        return format_error_response(**type_error)

    # 2. Resolve product_id
    resolved_product_id = resolve_product_id(product_id)
    if resolved_product_id is None:
        return format_error_response(
            error="product_id is required",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={"parameter": "product_id"},
            suggestion=("Pass product_id explicitly or set SPIRA_PROJECT_ID in your environment."),
        )

    # 3. Build requires release_id
    if artifact_type == "build" and release_id is None:
        return format_error_response(
            error="release_id is required for build artifact retrieval",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={"parameter": "release_id", "artifact_type": "build"},
            suggestion="Builds are scoped to a release. Pass release_id to retrieve a build.",
        )

    # 4. Build endpoint URL
    config = ARTIFACT_CONFIG[artifact_type]
    endpoint = config.single_endpoint.format(
        product_id=resolved_product_id,
        artifact_id=artifact_id,
        release_id=release_id,
    )

    # 5. GET the artifact
    try:
        raw_data = await spira_client.make_spira_api_get_request(endpoint)
    except SpiraApiError as e:
        return format_error_response(
            error=f"Failed to retrieve {artifact_type}: {e}",
            error_code=e.error_code,
            details={"product_id": resolved_product_id, "artifact_id": artifact_id},
            suggestion="Check your Spira connection and try again.",
        )

    # 5a. Handle None/empty response (artifact not found)
    if not raw_data:
        return format_error_response(
            error=f"{artifact_type} with ID {artifact_id} not found in product {resolved_product_id}.",
            error_code=ErrorCodes.NOT_FOUND,
            details={
                "product_id": resolved_product_id,
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
            },
            suggestion="Verify the artifact_id and product_id are correct.",
        )

    # 5b. Resolve includes once — reused for embedded extraction and enrichment
    include_types: list[str] = []
    include_warnings: list[str] = []
    if include:
        include_types, include_warnings = resolve_includes(artifact_type, include)

    # 5c. Extract embedded sub-artifact data before projection strips it
    embedded_data: dict[str, list[dict]] = {}
    for inc_type in include_types:
        sub_config = SUB_ARTIFACT_CONFIG.get(inc_type)
        if sub_config and sub_config.embedded_field:
            raw_embedded = raw_data.get(sub_config.embedded_field)
            if raw_embedded and isinstance(raw_embedded, list):
                embedded_data[inc_type] = raw_embedded

    # 5d. Extract raw CustomProperties before projection strips them
    raw_cp = raw_data.get("CustomProperties")

    # 5e. Project fields — strip excluded fields (Guids, ConcurrencyDate, etc.)
    projected, _, _, _ = apply_field_projection(
        [raw_data],
        list(config.all_fields),  # all LLM-visible fields, strips excluded
        config.summary_fields,
        config.all_fields,
    )
    data = projected[0]

    # 5f. Resolve custom properties unconditionally
    warnings: list[str] = include_warnings
    custom_property_resolver = CustomPropertyResolver(spira_client, TemplateContext(spira_client))
    if raw_cp is not None and isinstance(raw_cp, list):
        friendly, cp_warnings = await custom_property_resolver.resolve(
            raw_cp, resolved_product_id, artifact_type
        )
        warnings.extend(cp_warnings)
        data["custom_properties"] = friendly
    elif "CustomProperties" in config.excluded_fields:
        # Artifact type supports CPs but this instance has none set (null/absent).
        # Always include the key so consumers can distinguish "no values set"
        # from "endpoint doesn't support custom properties".
        data["custom_properties"] = {}

    # 6. Include enrichment (no cap for single artifact)
    if include_types:
        enriched, _fetched, enrich_warnings = await enrich_with_includes(
            spira_client,
            resolved_product_id,
            [data],
            include_types,
            artifact_type,
            embedded_data=embedded_data,
        )
        data = enriched[0]
        warnings.extend(enrich_warnings)

    if warnings:
        response = json.loads(format_success_response(data=data))
        response["warnings"] = warnings
        return json.dumps(response, indent=2, default=str)

    return format_success_response(data=data)


def _build_get_docstring() -> str:
    """Build the dynamic docstring for product_get_artifact."""
    type_names = "|".join(PRODUCT_ARTIFACT_TYPES)
    return (
        "Retrieve a single artifact by ID from a Spira product.\n"
        "\n"
        f"artifact_type: {type_names}\n"
        "release_id: required when artifact_type='build'\n"
        "include: test_steps (test_case), mitigations (risk), steps (requirement), "
        "comments (most types), associations (most types), coverage (requirement, test_case, release)"
    )


def register_tools(mcp) -> None:
    """Register product_get_artifact with the MCP server."""
    get_docstring = _build_get_docstring()

    @mcp.tool(
        name="product_get_artifact",
        description=get_docstring,
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )
    async def product_get_artifact(
        artifact_type: ProductArtifactType,
        artifact_id: int,
        product_id: int | None = None,
        release_id: int | None = None,
        include: list[str] | None = None,
    ) -> str:
        """Retrieve a single artifact by ID from a Spira product."""
        spira_client = get_spira_client()
        return await _product_get_impl(
            spira_client,
            artifact_type,
            artifact_id,
            product_id,
            release_id,
            include=include,
        )
