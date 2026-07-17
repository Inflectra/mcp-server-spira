"""Product-scoped artifact creation tool.

Implements `product_create_artifact` — a config-driven tool that creates
any supported artifact type via a single interface, following the same
pattern as `product_search_artifacts`.
"""

from typing import Annotated, Any

from pydantic import WithJsonSchema

from mcp_server_spira.config import resolve_product_id
from mcp_server_spira.features.artifact_configs import ARTIFACT_CONFIG
from mcp_server_spira.features.create.batch import (
    BatchResult,
    ItemValidator,
    create_batch,
)
from mcp_server_spira.features.create.field_resolver import resolve_fields_for_create
from mcp_server_spira.features.create.validation import (
    CREATABLE_ARTIFACT_TYPES,
    SUB_ARTIFACT_TYPE_TO_CONFIG_KEY,
    SUB_ARTIFACT_TYPES,
    validate_create_request,
)
from mcp_server_spira.features.custom_properties import (
    CustomPropertyResolver,
    serialize_custom_properties,
)
from mcp_server_spira.features.search.template_context import TemplateContext
from mcp_server_spira.features.sub_artifact_configs import SUB_ARTIFACT_CONFIG
from mcp_server_spira.models import ArtifactConfig, SubArtifactConfig
from mcp_server_spira.utils.common import _sanitize_error, get_spira_client
from mcp_server_spira.utils.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)


async def _create_artifact_impl(
    spira_client,
    artifact_type: str,
    product_id: int,
    fields: list[dict[str, Any]],
    release_id: int | None = None,
    parent_id: int | None = None,
) -> str:
    """Core creation logic for product_create_artifact.

    Takes *spira_client* as first arg so callers (and tests) can inject a
    mock without touching MCP registration.

    Returns a JSON string — either a success envelope with created IDs or
    an error envelope.

    Spec:
        Return type:
            - ALWAYS returns a JSON string (never raises to the MCP layer)
            - On success: response has "data" key with "created" list,
              "artifact_type", optional "parent_id", and "message"
            - On validation failure: error envelope with error_code
            - On partial batch failure: response has "data" key with
              "created", "failed_at_index", "error", and "message"

        Validation order (short-circuits on first failure):
            1. product_id must be positive integer (>= 1)
            2. artifact_type must be in CREATABLE_ARTIFACT_TYPES
            3. parent_id required for sub-artifact types
            4. url_params validation (e.g. release_id for builds)
            5. fields must be a non-empty list of dicts
            6. required_fields presence check for each item
            7. Name non-blank check for top-level types
            7a. Description non-blank check for sub-artifacts (per-item,
                inside batch loop — supports partial failure reporting)
            8. Build-specific BuildStatusId validation
            9a. Field name correction + string-to-ID resolution
                (top-level artifacts only, via resolve_fields_for_create;
                renames mismatched field names, resolves string values for
                priority/status/type to integer IDs; warnings collected,
                never errors)
            9. Inject defaults from config constants

        Batch semantics:
            - Items are POSTed sequentially; first failure stops the batch
            - Partial success returns created IDs + failed_at_index + error
            - Per-item validation (7a) also triggers partial failure when
              preceding items were already created successfully

        All functions are async def, all API calls use await.
    """
    try:
        # --- Validation Pipeline (pure, extracted to validation.py) ---
        validation_error = validate_create_request(
            artifact_type=artifact_type,
            product_id=product_id,
            fields=fields,
            release_id=release_id,
            parent_id=parent_id,
        )
        if validation_error is not None:
            return validation_error

        # --- Post-validation setup ---
        is_sub_artifact = artifact_type in SUB_ARTIFACT_TYPES

        # Look up config
        config: ArtifactConfig | SubArtifactConfig
        if is_sub_artifact:
            config_key = SUB_ARTIFACT_TYPE_TO_CONFIG_KEY[artifact_type]
            config = SUB_ARTIFACT_CONFIG[config_key]
        else:
            config = ARTIFACT_CONFIG[artifact_type]

        # 9a. Field alias + string-to-ID resolution.
        # Resolves friendly names like "Priority": "high" → "PriorityId": 2
        # and renames aliases like "Status" → "IncidentStatusId".
        # For sub-artifacts, only field name correction applies (no ID resolution).
        # Runs BEFORE inject_defaults so LLM intent takes precedence over defaults.
        create_warnings: list[str] = []
        template_context = TemplateContext(spira_client)
        field_warnings = await resolve_fields_for_create(
            spira_client,
            template_context,
            config,
            artifact_type,
            product_id,
            fields,
        )
        create_warnings.extend(field_warnings)

        # 9. Inject defaults from config constants
        if not is_sub_artifact and hasattr(config, "inject_defaults"):
            for item in fields:
                for key, value in config.inject_defaults.items():
                    if key not in item:
                        item[key] = value

        # Build-specific: inject ProjectId and ReleaseId into POST body.
        # The Spira API requires these fields in the body AND in the URL for builds.
        # Only inject if user didn't explicitly provide them.
        if artifact_type == "build":
            for item in fields:
                if "ProjectId" not in item:
                    item["ProjectId"] = product_id
                if "ReleaseId" not in item:
                    item["ReleaseId"] = release_id

        # 9b. Handle custom_properties serialization
        custom_property_resolver = CustomPropertyResolver(spira_client, template_context)
        for item in fields:
            cp_friendly = item.pop("custom_properties", None)

            if cp_friendly is not None:
                # Sub-artifacts: custom_properties not supported via this tool
                if is_sub_artifact:
                    create_warnings.append(
                        f"custom_properties is not supported for sub-artifact "
                        f"type '{artifact_type}'. Ignoring."
                    )
                    continue

                # If both formats present, use friendly and warn
                if "CustomProperties" in item:
                    item.pop("CustomProperties")
                    create_warnings.append(
                        "Both 'custom_properties' and 'CustomProperties' "
                        "provided. Using 'custom_properties' (friendly "
                        "format)."
                    )

                if not isinstance(cp_friendly, dict):
                    create_warnings.append(
                        f"custom_properties must be a dict, got "
                        f"{type(cp_friendly).__name__}. "
                        f"Skipping custom property serialization."
                    )
                else:
                    definitions = await custom_property_resolver.get_definitions(
                        product_id, artifact_type
                    )
                    wire_array, ser_warnings = serialize_custom_properties(cp_friendly, definitions)
                    create_warnings.extend(ser_warnings)
                    if wire_array:
                        item["CustomProperties"] = wire_array

        # --- Build endpoint URL ---
        # create_endpoint is guaranteed non-None for creatable types (validated at import time)
        if config.create_endpoint is None:
            return format_error_response(
                error=f"{artifact_type} does not support creation",
                error_code=ErrorCodes.INVALID_PARAMETER,
                details={"artifact_type": artifact_type},
                suggestion="This artifact type has no create_endpoint configured.",
            )
        if is_sub_artifact:
            # Resolve creator_id if the endpoint template requires it
            format_kwargs: dict[str, Any] = {
                "product_id": product_id,
                "parent_id": parent_id,
            }
            if "{creator_id}" in config.create_endpoint:
                user_response = await spira_client.make_spira_api_get_request("users")
                creator_id = (
                    user_response.get("UserId") if isinstance(user_response, dict) else None
                )
                if creator_id is None:
                    return format_error_response(
                        error="Could not resolve current user ID for sub-artifact creation",
                        error_code=ErrorCodes.API_ERROR,
                        details={"artifact_type": artifact_type},
                        suggestion="Check Spira credentials are valid.",
                    )
                format_kwargs["creator_id"] = creator_id

            endpoint = config.create_endpoint.format(**format_kwargs)

            # Inject parent ID into body for sub-artifacts that require it.
            # Same pattern as build's ProjectId/ReleaseId injection.
            if hasattr(config, "parent_id_field") and config.parent_id_field:
                for item in fields:
                    if config.parent_id_field not in item:
                        item[config.parent_id_field] = parent_id
        else:
            endpoint = config.create_endpoint.format(
                product_id=product_id,
                release_id=release_id,
            )

        # --- Batch creation loop (delegated to create_batch) ---
        id_field = config.id_field
        id_prefix = config.id_prefix

        # id_field and id_prefix are guaranteed non-None when create_endpoint
        # is set (validated at import time by ArtifactConfig.validate / SubArtifactConfig.validate)
        assert id_field is not None  # noqa: S101
        assert id_prefix is not None  # noqa: S101

        # Build per-item validators
        item_validators: list[ItemValidator] = []
        if is_sub_artifact:
            # 7a. Per-item Description non-blank check for sub-artifacts.
            # Validated inside the loop so partial success is reported for
            # items already created before the failing one.
            def _check_description(item: dict, _index: int) -> str | None:
                desc = item.get("Description")
                if isinstance(desc, str) and not desc.strip():
                    return "Description must contain non-whitespace characters"
                return None

            item_validators.append(ItemValidator(check=_check_description))

        # Build pre-POST transform for type-specific field transformations
        def _pre_post_transform(item: dict, _index: int) -> dict:
            # Build-specific Revisions field transformation
            if (
                artifact_type == "build"
                and "Revisions" in item
                and isinstance(item["Revisions"], list)
            ):
                item["Revisions"] = [{"RevisionKey": h} for h in item["Revisions"]]
            return item

        batch_result: BatchResult = await create_batch(
            spira_client,
            endpoint,
            fields,
            id_field=id_field,
            id_prefix=id_prefix,
            item_validators=item_validators or None,
            pre_post_transform=_pre_post_transform,
        )

        # --- Format response from BatchResult ---
        return _format_batch_response(
            batch_result,
            artifact_type=artifact_type,
            total_items=len(fields),
            product_id=product_id,
            release_id=release_id,
            parent_id=parent_id,
            is_sub_artifact=is_sub_artifact,
            create_warnings=create_warnings,
        )

    except Exception as e:
        return format_error_response(
            error=f"Unexpected error creating {artifact_type}: {_sanitize_error(e)}",
            error_code=getattr(e, "error_code", ErrorCodes.API_ERROR),
            details={
                "product_id": product_id,
                "artifact_type": artifact_type,
            },
            suggestion="Check Spira connection and try again.",
        )


def _format_batch_response(
    batch_result: BatchResult,
    *,
    artifact_type: str,
    total_items: int,
    product_id: int,
    release_id: int | None,
    parent_id: int | None,
    is_sub_artifact: bool,
    create_warnings: list[str],
) -> str:
    """Format a BatchResult into the appropriate JSON response envelope.

    Spec:
        - ALWAYS returns a JSON string — never raises
        - On success (batch_result.is_success): returns format_success_response
          with created list, artifact_type, message, optional parent_id and warnings
        - On partial failure (batch_result.is_partial_failure): returns
          format_success_response with created, failed_at_index, error, message
        - On complete failure (batch_result.is_complete_failure): returns
          format_error_response with error details and suggestion
        - Response shapes match the original _create_artifact_impl contract
          exactly — existing tests pass without modification
    """
    if batch_result.is_success:
        result: dict[str, Any] = {
            "created": batch_result.created,
            "artifact_type": artifact_type,
            "message": f"{len(batch_result.created)} {artifact_type}(s) created successfully",
        }
        if is_sub_artifact:
            result["parent_id"] = parent_id
        if create_warnings:
            result["warnings"] = create_warnings
        return format_success_response(result)

    if batch_result.is_partial_failure:
        result = {
            "created": batch_result.created,
            "failed_at_index": batch_result.failed_at_index,
            "error": batch_result.error,
            "artifact_type": artifact_type,
            **({"parent_id": parent_id} if is_sub_artifact else {}),
            "message": (
                f"{len(batch_result.created)} of {total_items} "
                f"{artifact_type}(s) created. "
                f"Failed at index {batch_result.failed_at_index}"
                + (f": {batch_result.error}" if batch_result.error else ".")
            ),
        }
        return format_success_response(result)

    # Complete failure — first item failed
    error_msg = batch_result.error or f"Failed to create {artifact_type}"
    error_code = batch_result.error_code or ErrorCodes.API_ERROR

    # Validation errors (from item_validator) get INVALID_PARAMETER with
    # field-specific details. API/response errors get API_ERROR with
    # connection-level details.
    if error_code == ErrorCodes.INVALID_PARAMETER:
        # Derive the parameter name from the error message when possible.
        # Current validators produce messages like "X must contain ..."
        # where X is the field name.
        parameter = error_msg.split(" ")[0] if error_msg else "unknown"
        return format_error_response(
            error=error_msg,
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "parameter": parameter,
                "index": batch_result.failed_at_index,
                "artifact_type": artifact_type,
            },
            suggestion=f"Provide a valid {parameter} for each sub-artifact.",
        )

    # Distinguish error subtypes by the error message pattern:
    # - "API returned empty response" → "{artifact_type} was not created successfully"
    # - "Response missing expected field '...'" → pass through as-is
    # - Anything else (SpiraApiError message) → "Failed to create {artifact_type}: {msg}"
    if error_msg == "API returned empty response":
        formatted_error = f"{artifact_type} was not created successfully"
        details: dict[str, Any] = {
            "product_id": product_id,
            "artifact_type": artifact_type,
        }
        suggestion = "Check Spira connection and try again."
    elif error_msg.startswith("Response missing"):
        formatted_error = error_msg
        details = {
            "id_field": error_msg.split("'")[1] if "'" in error_msg else "",
            "artifact_type": artifact_type,
        }
        suggestion = "Unexpected API response format."
    else:
        formatted_error = f"Failed to create {artifact_type}: {error_msg}"
        details = {
            "product_id": product_id,
            "artifact_type": artifact_type,
            **({"release_id": release_id} if release_id else {}),
            **({"parent_id": parent_id} if parent_id else {}),
        }
        suggestion = "Check Spira connection and try again."

    return format_error_response(
        error=formatted_error,
        error_code=error_code,
        details=details,
        suggestion=suggestion,
    )


# Type hint for the tool signature — advertises valid values in the JSON
# schema (so the LLM sees them in tools/list) but accepts any string at
# Pydantic validation time.  Actual validation happens in _impl via
# ParameterValidator, which returns our standard error envelope.
CreatableArtifactType = Annotated[
    str,
    WithJsonSchema(
        {
            "type": "string",
            "enum": list(CREATABLE_ARTIFACT_TYPES),
        }
    ),
]


def register_tools(mcp) -> None:
    """Register product_create_artifact with the MCP server."""

    @mcp.tool(
        name="product_create_artifact",
        description=(
            "Create artifacts in a Spira product.\n"
            "\n"
            "Name and Description are required for most types. "
            "Sub-artifacts (test_step, mitigation, requirement_step) require parent_id. "
            "Builds require release_id. Use get_artifact_schema to discover optional writable fields."
        ),
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )
    # Spec:
    #   - Thin wrapper with product_id resolution — resolves product_id
    #     from env via resolve_product_id, then delegates to
    #     _create_artifact_impl
    #   - ALWAYS returns a JSON string (never raises to the MCP layer)
    #     — outer try/except catches any unexpected exception from
    #     resolve_product_id or get_spira_client and returns error envelope
    #   - product_id=None → resolved from SPIRA_PROJECT_ID env; if both
    #     are unset, returns INVALID_PARAMETER error envelope before
    #     calling _impl (no side effects)
    #   - All domain validation (artifact_type, fields, parent_id, etc.)
    #     lives in _create_artifact_impl — this wrapper only handles
    #     product_id resolution and the safety-net catch
    async def product_create_artifact(
        artifact_type: CreatableArtifactType,
        fields: list[dict[str, Any]],
        product_id: int | None = None,
        release_id: int | None = None,
        parent_id: int | None = None,
    ) -> str:
        """Create artifacts in a Spira product."""
        try:
            resolved_id = resolve_product_id(product_id)
            if resolved_id is None:
                return format_error_response(
                    error="product_id is required",
                    error_code=ErrorCodes.INVALID_PARAMETER,
                    details={"parameter": "product_id"},
                    suggestion=(
                        "Pass product_id explicitly or set SPIRA_PROJECT_ID in your environment"
                    ),
                )
            spira_client = get_spira_client()
            return await _create_artifact_impl(
                spira_client,
                artifact_type,
                resolved_id,
                fields,
                release_id=release_id,
                parent_id=parent_id,
            )
        except Exception as e:
            return format_error_response(
                error=f"Unexpected error: {_sanitize_error(e)}",
                error_code=getattr(e, "error_code", ErrorCodes.API_ERROR),
                details={"exception": _sanitize_error(e)},
            )
