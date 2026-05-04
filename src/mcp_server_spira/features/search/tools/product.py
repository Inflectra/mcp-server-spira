"""product_search_artifacts and product_get_artifact unified tools.

Replaces 11 separate per-artifact product read tools with 2 config-driven
tools supporting client-side filtering, field projection, and multi-product
fan-out.
"""

import asyncio
import json
from typing import Annotated, Any

from pydantic import WithJsonSchema

from mcp_server_spira.config import resolve_product_id
from mcp_server_spira.features.artifact_configs import ARTIFACT_CONFIG
from mcp_server_spira.features.search.sub_artifact_configs import SUB_ARTIFACT_CONFIG
from mcp_server_spira.features.search.tools._include import (
    MAX_INCLUDE_RESULTS,
    enrich_with_includes,
    resolve_includes,
)
from mcp_server_spira.features.search.tools._shared import (
    apply_contains_filter,
    apply_field_projection,
)
from mcp_server_spira.utils.common import get_spira_client
from mcp_server_spira.utils.common.responses import (
    ErrorCodes,
    format_error_response,
    format_multi_product_response,
    format_search_response,
    format_success_response,
)
from mcp_server_spira.utils.common.validation import ParameterValidator

# Derived from ArtifactConfig — product-scoped types only.
PRODUCT_ARTIFACT_TYPES: tuple[str, ...] = tuple(
    name for name, cfg in ARTIFACT_CONFIG.items() if cfg.workspace_type == "product"
)

# Type hint for the tool signature — advertises valid values in the JSON
# schema (so the LLM sees them in tools/list) but accepts any string at
# Pydantic validation time.  Actual validation happens in _impl functions
# via ParameterValidator, which returns our standard error envelope.
ProductArtifactType = Annotated[
    str,
    WithJsonSchema(
        {
            "type": "string",
            "enum": list(PRODUCT_ARTIFACT_TYPES),
        }
    ),
]


def _coerce_product_ids(product_ids: Any) -> list[int] | str:
    """Silently coerce product_ids to a list of ints.

    Returns a ``list[int]`` on success, or an error-response JSON string
    on failure.

    Coercion rules:
    - ``None`` → resolve from env default; error if unavailable.
    - bare ``int`` → ``[int]``
    - string parseable as int → ``[int]``
    - ``list[int]`` → pass through
    - anything else → ``INVALID_PARAMETER`` error string
    """
    if product_ids is None:
        resolved = resolve_product_id(None)
        if resolved is None:
            return format_error_response(
                error="product_ids is required",
                error_code=ErrorCodes.INVALID_PARAMETER,
                details={"parameter": "product_ids"},
                suggestion=(
                    "Pass product_ids explicitly or set SPIRA_PROJECT_ID in your environment."
                ),
            )
        return [resolved]

    if isinstance(product_ids, int):
        return [product_ids]

    if isinstance(product_ids, str):
        try:
            return [int(product_ids)]
        except ValueError:
            return format_error_response(
                error="Invalid product_ids parameter",
                error_code=ErrorCodes.INVALID_PARAMETER,
                details={"parameter": "product_ids", "value": product_ids},
                suggestion="product_ids must be an integer or list of integers.",
            )

    if isinstance(product_ids, list):
        return product_ids

    return format_error_response(
        error="Invalid product_ids parameter",
        error_code=ErrorCodes.INVALID_PARAMETER,
        details={"parameter": "product_ids", "value": str(product_ids)},
        suggestion="product_ids must be an integer or list of integers.",
    )


async def _single_product_search(
    spira_client,
    artifact_type: str,
    product_id: int,
    fields: list[str] | None,
    status: str | None,
    release_id: int | None,
    priority: str | None,
    starting_row: int,
    number_of_rows: int,
    requirement_id: int | None = None,
    include_types: list[str] | None = None,
) -> dict:
    """Execute the search pipeline for one product.

    Returns a result dict (NOT a JSON string) with keys:
    ``product_id``, ``data``, ``fields_returned``, ``fields_available``,
    ``pagination``, ``warnings``, and optionally ``includes_fetched``.

    Order: fetch → filter status → filter priority → filter requirement_id
    → project → include enrichment.
    """
    config = ARTIFACT_CONFIG[artifact_type]
    warnings: list[str] = []

    # 0. Cap number_of_rows when include is active
    effective_rows = number_of_rows
    if include_types:
        effective_rows = min(number_of_rows, MAX_INCLUDE_RESULTS)
        if number_of_rows > MAX_INCLUDE_RESULTS:
            warnings.append(
                f"Results capped at {MAX_INCLUDE_RESULTS} due to include parameter. "
                "There may be additional artifacts."
            )

    # 1. Build endpoint URL with config-driven query parameter names
    endpoint = config.search_endpoint.format(
        product_id=product_id,
        release_id=release_id,
    )
    qp = config.search_query_params
    # Build query string with ALL config params in the URL.
    # Spira WCF routing needs every param present for route matching.
    query_parts = []
    for role, api_name in qp.items():
        if role == "row_start":
            query_parts.append(f"{api_name}={starting_row}")
        elif role == "row_count":
            query_parts.append(f"{api_name}={effective_rows}")
        elif role in ("sort_field", "sort_by"):
            default = config.default_sort_field or ""
            query_parts.append(f"{api_name}={default}")
        elif role == "sort_direction":
            query_parts.append(f"{api_name}={config.default_sort_direction}")
        elif role == "release_id" and release_id is not None:
            query_parts.append(f"{api_name}={release_id}")
        elif role == "release_id":
            # Skip release_id when not provided
            pass
    url = f"{endpoint}?{'&'.join(query_parts)}"

    # 2. POST with empty body (no server-side filters)
    raw = await spira_client.make_spira_api_post_request(url, [])
    data: list[dict] = raw if raw else []

    # 3. Filter status
    data, status_warnings = apply_contains_filter(
        data,
        config.status_field,
        status,
        config.all_fields,
        "status",
    )
    warnings.extend(status_warnings)

    # 4. Filter priority
    data, priority_warnings = apply_contains_filter(
        data,
        config.priority_field,
        priority,
        config.all_fields,
        "priority",
    )
    warnings.extend(priority_warnings)

    # 5. Filter requirement_id (client-side, tasks only)
    if requirement_id is not None:
        if artifact_type == "task":
            data = [d for d in data if d.get("RequirementId") == requirement_id]
        else:
            warnings.append("requirement_id filtering is only supported for tasks. Filter ignored.")

    # 6. Project fields
    projected, fields_returned, fields_available, proj_warnings = apply_field_projection(
        data,
        fields,
        config.summary_fields,
        config.all_fields,
    )
    warnings.extend(proj_warnings)

    # 7. Include enrichment
    includes_fetched: list[str] | None = None
    if include_types:
        projected, includes_fetched, include_warnings = await enrich_with_includes(
            spira_client,
            product_id,
            projected,
            include_types,
        )
        warnings.extend(include_warnings)

    result: dict = {
        "product_id": product_id,
        "data": projected,
        "fields_returned": fields_returned,
        "fields_available": fields_available,
        "pagination": {
            "starting_row": starting_row,
            "number_of_rows": effective_rows,
            "total_returned": len(projected),
        },
        "warnings": warnings,
    }
    if includes_fetched is not None:
        result["includes_fetched"] = includes_fetched
    return result


async def _multi_product_search(
    spira_client,
    artifact_type: str,
    product_ids: list[int],
    fields: list[str] | None,
    status: str | None,
    release_id: int | None,
    priority: str | None,
    starting_row: int,
    number_of_rows: int,
) -> str:
    """Fan out search across multiple products via asyncio.gather.

    Returns a Multi_Product_Envelope JSON string.  Every product in
    *product_ids* gets exactly one entry in the ``products`` array,
    regardless of success or failure.
    """
    tasks = [
        _single_product_search(
            spira_client,
            artifact_type,
            pid,
            fields,
            status,
            release_id,
            priority,
            starting_row,
            number_of_rows,
        )
        for pid in product_ids
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    products: list[dict] = []
    for pid, result in zip(product_ids, results, strict=True):
        if isinstance(result, BaseException):
            products.append(
                {
                    "product_id": pid,
                    "error": str(result),
                    "warnings": [f"API call failed for product {pid}: {result}"],
                }
            )
        else:
            # _single_product_search returns a dict with the right keys already
            products.append(result)

    return format_multi_product_response(
        artifact_type=artifact_type,
        products=products,
    )


async def _product_search_impl(
    spira_client,
    artifact_type: Any,
    product_ids: Any,
    fields: list[str] | None,
    status: str | None,
    release_id: int | None,
    priority: str | None,
    starting_row: int,
    number_of_rows: int,
    include: list[str] | None = None,
    requirement_id: int | None = None,
) -> str:
    """Core implementation for product_search_artifacts.

    Takes *spira_client* as first arg so callers (and tests) can inject a
    mock without touching MCP registration.

    Returns a JSON string — either a single-product search response envelope
    or a multi-product envelope (task 4).
    """
    # 1. Validate artifact_type
    type_error = ParameterValidator.validate_type_param(
        artifact_type, PRODUCT_ARTIFACT_TYPES, "artifact_type"
    )
    if type_error is not None:
        return format_error_response(**type_error)

    # 2. Validate pagination params
    validation_error = ParameterValidator.validate_positive_integer(
        starting_row, "starting_row", min_value=1
    )
    if validation_error is not None:
        return json.dumps(validation_error, indent=2)

    validation_error = ParameterValidator.validate_positive_integer(
        number_of_rows, "number_of_rows", min_value=1
    )
    if validation_error is not None:
        return json.dumps(validation_error, indent=2)

    # 3. Build special case: require release_id
    if artifact_type == "build" and release_id is None:
        return format_error_response(
            error="release_id is required for build searches",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={"parameter": "release_id", "artifact_type": "build"},
            suggestion=("Builds are scoped to a release. Pass release_id to search for builds."),
        )

    # 4. Coerce product_ids
    coerced = _coerce_product_ids(product_ids)
    if isinstance(coerced, str):
        # Error response string
        return coerced
    product_id_list: list[int] = coerced

    # 5. Resolve include types (shared by both paths for validation)
    include_types: list[str] = []
    include_warnings: list[str] = []
    if include:
        include_types, include_warnings = resolve_includes(artifact_type, include)

    # 6. Route: single vs multi-product
    if len(product_id_list) == 1:
        try:
            result = await _single_product_search(
                spira_client,
                artifact_type,
                product_id_list[0],
                fields,
                status,
                release_id,
                priority,
                starting_row,
                number_of_rows,
                requirement_id=requirement_id,
                include_types=include_types,
            )
        except Exception as e:
            return format_error_response(
                error=f"Failed to retrieve {artifact_type} data: {e}",
                error_code=ErrorCodes.API_ERROR,
                details={"product_id": product_id_list[0]},
                suggestion="Check your Spira connection and try again.",
            )

        all_warnings = include_warnings + result["warnings"]
        return format_search_response(
            data=result["data"],
            artifact_type=artifact_type,
            fields_returned=result["fields_returned"],
            pagination=result["pagination"],
            fields_available=result["fields_available"],
            warnings=all_warnings,
            includes_fetched=result.get("includes_fetched"),
        )

    # Multi-product path — include not supported
    multi_warnings: list[str] = []
    if include:
        multi_warnings.append(
            "include is not supported for multi-product fan-out. "
            "Results returned without include data."
        )

    result_str = await _multi_product_search(
        spira_client,
        artifact_type,
        product_id_list,
        fields,
        status,
        release_id,
        priority,
        starting_row,
        number_of_rows,
    )

    # Inject multi-product include warning into the response if needed
    if multi_warnings:
        parsed = json.loads(result_str)
        parsed["warnings"] = multi_warnings + parsed.get("warnings", [])
        return json.dumps(parsed, indent=2, default=str)

    return result_str


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
    except Exception as e:
        return format_error_response(
            error=f"Failed to retrieve {artifact_type}: {e}",
            error_code=ErrorCodes.API_ERROR,
            details={"product_id": resolved_product_id, "artifact_id": artifact_id},
            suggestion="Check your Spira connection and try again.",
        )

    # 5b. Extract embedded sub-artifact data before projection strips it
    embedded_data: dict[str, list[dict]] = {}
    if include:
        include_types, include_warnings = resolve_includes(artifact_type, include)
        for inc_type in include_types:
            sub_config = SUB_ARTIFACT_CONFIG.get(inc_type)
            if sub_config and sub_config.embedded_field:
                raw_embedded = raw_data.get(sub_config.embedded_field)
                if raw_embedded and isinstance(raw_embedded, list):
                    embedded_data[inc_type] = raw_embedded

    # 5c. Project fields — strip excluded fields (Guids, ConcurrencyDate, etc.)
    projected, _, _, _ = apply_field_projection(
        [raw_data],
        list(config.all_fields),  # all LLM-visible fields, strips excluded
        config.summary_fields,
        config.all_fields,
    )
    data = projected[0]

    # 6. Include enrichment (no cap for single artifact)
    warnings: list[str] = []
    if include:
        include_types, include_warnings = resolve_includes(artifact_type, include)
        warnings.extend(include_warnings)

        if include_types:
            enriched, _fetched, enrich_warnings = await enrich_with_includes(
                spira_client,
                resolved_product_id,
                [data],
                include_types,
                embedded_data=embedded_data,
            )
            data = enriched[0]
            warnings.extend(enrich_warnings)

    if warnings:
        response = json.loads(format_success_response(data=data))
        response["warnings"] = warnings
        return json.dumps(response, indent=2, default=str)

    return format_success_response(data=data)


def _build_search_docstring() -> str:
    """Build the dynamic docstring for product_search_artifacts.

    Injects valid ProductArtifactType values from ARTIFACT_CONFIG at
    registration time so the docstring always reflects the current config.
    """
    type_names = ", ".join(PRODUCT_ARTIFACT_TYPES)
    return (
        "Searches for artifacts in a Spira product.\n"
        "\n"
        f"Valid artifact types: {type_names}\n"
        "\n"
        "Args:\n"
        f"  artifact_type: One of [{type_names}].\n"
        "  product_ids: Product IDs to search. "
        "Defaults to SPIRA_PROJECT_ID env var. "
        "Pass 2+ IDs for cross-product fan-out.\n"
        "  fields: Fields to return per object. "
        "Defaults to summary fields. "
        "Use get_artifact_schema to "
        "discover valid field names.\n"
        "  status: Substring filter on status "
        "(case-insensitive).\n"
        "  priority: Substring filter on priority "
        "(case-insensitive).\n"
        "  release_id: Required when "
        "artifact_type='build'. Ignored otherwise.\n"
        "  starting_row: Pagination start "
        "(1-based, default 1).\n"
        "  number_of_rows: Page size (default 100). "
        "Capped to 50 when include is active.\n"
        "  include: Fetch nested sub-artifact data inline. "
        "Valid values depend on artifact_type: "
        "test_case supports ['test_steps'], "
        "risk supports ['mitigations'], "
        "requirement supports ['steps']. "
        "Not supported for multi-product fan-out.\n"
        "  requirement_id: Filter tasks by requirement ID "
        "(client-side). Only supported when "
        "artifact_type='task'.\n"
        "\n"
        "Call get_artifact_schema for full "
        "field discovery per artifact type."
    )


def _build_get_docstring() -> str:
    """Build the dynamic docstring for product_get_artifact.

    Injects valid ProductArtifactType values from ARTIFACT_CONFIG at
    registration time so the docstring always reflects the current config.
    """
    type_names = ", ".join(PRODUCT_ARTIFACT_TYPES)
    return (
        "Retrieves a single artifact by ID "
        "from a Spira product.\n"
        "\n"
        "Returns the full artifact object "
        "with all fields (no field projection).\n"
        "\n"
        f"Valid artifact types: {type_names}\n"
        "\n"
        "Args:\n"
        f"  artifact_type: One of [{type_names}].\n"
        "  artifact_id: Numeric ID of the artifact.\n"
        "  product_id: Product ID. "
        "Defaults to SPIRA_PROJECT_ID env var.\n"
        "  release_id: Required when "
        "artifact_type='build'. Ignored otherwise.\n"
        "  include: Fetch nested sub-artifact data inline. "
        "Valid values depend on artifact_type: "
        "test_case supports ['test_steps'], "
        "risk supports ['mitigations'], "
        "requirement supports ['steps']. "
        "No cap applied for single artifact retrieval.\n"
        "\n"
        "Call get_artifact_schema for "
        "full field discovery per artifact type."
    )


def register_tools(mcp) -> None:
    """Register product_search_artifacts and product_get_artifact."""
    search_docstring = _build_search_docstring()
    get_docstring = _build_get_docstring()

    @mcp.tool(
        name="product_search_artifacts",
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )
    async def product_search_artifacts(
        artifact_type: ProductArtifactType,
        product_ids: list[int] | None = None,
        fields: list[str] | None = None,
        status: str | None = None,
        release_id: int | None = None,
        priority: str | None = None,
        starting_row: int = 1,
        number_of_rows: int = 100,
        include: list[str] | None = None,
        requirement_id: int | None = None,
    ) -> str:
        spira_client = get_spira_client()
        return await _product_search_impl(
            spira_client,
            artifact_type,
            product_ids,
            fields,
            status,
            release_id,
            priority,
            starting_row,
            number_of_rows,
            include=include,
            requirement_id=requirement_id,
        )

    product_search_artifacts.__doc__ = search_docstring

    @mcp.tool(
        name="product_get_artifact",
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
        spira_client = get_spira_client()
        return await _product_get_impl(
            spira_client,
            artifact_type,
            artifact_id,
            product_id,
            release_id,
            include=include,
        )

    product_get_artifact.__doc__ = get_docstring
