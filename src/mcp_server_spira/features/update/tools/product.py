"""Product-scoped artifact update tool.

Implements `product_update_artifact` — a config-driven tool that updates
any supported artifact type via GET-merge-PUT, following the same
pattern as `product_create_artifact`.
"""

from typing import Annotated, Any

from pydantic import WithJsonSchema

from mcp_server_spira.config import resolve_product_id
from mcp_server_spira.features.artifact_configs import ARTIFACT_CONFIG
from mcp_server_spira.features.create.field_resolver import resolve_fields_for_create
from mcp_server_spira.features.custom_properties import (
    CustomPropertyResolver,
    serialize_custom_properties,
)
from mcp_server_spira.features.search.template_context import TemplateContext
from mcp_server_spira.features.sub_artifact_configs import SUB_ARTIFACT_CONFIG
from mcp_server_spira.features.update.validation import (
    SUB_ARTIFACT_TYPE_TO_CONFIG_KEY,
    SUB_ARTIFACT_TYPES,
    UPDATABLE_ARTIFACT_TYPES,
    validate_field_keys,
    validate_update_request,
)
from mcp_server_spira.models import ArtifactConfig, SubArtifactConfig
from mcp_server_spira.utils.common import _sanitize_error, get_spira_client
from mcp_server_spira.utils.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.utils.spira_client import SpiraApiError, SpiraClient


async def _update_artifact_impl(
    spira_client: SpiraClient,
    artifact_type: str,
    artifact_id: int,
    product_id: int,
    fields: dict[str, Any],
    parent_id: int | None = None,
) -> str:
    """Core update logic for product_update_artifact.

    Takes *spira_client* as first arg so callers (and tests) can inject a
    mock without touching MCP registration.

    Returns a JSON string — either a success envelope or an error envelope.

    Spec:
        Return type:
            - ALWAYS returns a JSON string (never raises to the MCP layer)
            - On success: response has "data" key with "artifact_type",
              "artifact_id", "message", and optional "warnings"
            - On validation failure: error envelope with error_code
            - On API failure: error envelope with error_code from SpiraApiError

        Pipeline (9 steps):
            1. validate_update_request (steps 1-5 only)
            2. Config lookup (ArtifactConfig or SubArtifactConfig)
            3. Shallow copy fields, pop custom_properties — never mutate caller's dict
            3+. Strip ConcurrencyDate with warning (silently tolerated for
                LLM convenience; real value always comes from GET)
            3a. Field name resolution + value resolution (all artifact types;
                sub-artifacts get name correction only, top-level also gets
                string-to-ID resolution)
            3b. validate_field_keys on working_fields (after resolution)
            4. GET full artifact via single_endpoint
            5. Shallow merge working_fields into GET response, preserve ConcurrencyDate
            6. Serialize and merge custom properties into existing CustomProperties
               (top-level only; sub-artifacts produce a warning and skip)
            7. PUT to update_endpoint
            8. Return success envelope

        Error handling:
            - SpiraApiError caught for GET and PUT failures
            - Outer Exception safety net for unexpected errors
            - All functions are async def, all API calls use await
    """
    try:
        # --- Step 1: Validation (steps 1-5) ---
        validation_error = validate_update_request(
            artifact_type=artifact_type,
            product_id=product_id,
            artifact_id=artifact_id,
            fields=fields,
            parent_id=parent_id,
        )
        if validation_error is not None:
            return validation_error

        # --- Step 2: Config lookup ---
        is_sub_artifact = artifact_type in SUB_ARTIFACT_TYPES
        config: ArtifactConfig | SubArtifactConfig
        if is_sub_artifact:
            config_key = SUB_ARTIFACT_TYPE_TO_CONFIG_KEY[artifact_type]
            config = SUB_ARTIFACT_CONFIG[config_key]
        else:
            config = ARTIFACT_CONFIG[artifact_type]

        # --- Step 3: Shallow copy + extract custom_properties ---
        working_fields = dict(fields)
        cp_friendly = working_fields.pop("custom_properties", None)
        update_warnings: list[str] = []

        # Strip ConcurrencyDate — it's managed internally (always from GET).
        # LLM agents often copy-paste GET responses; rejecting this field
        # creates unnecessary friction.
        if "ConcurrencyDate" in working_fields:
            working_fields.pop("ConcurrencyDate")
            update_warnings.append(
                "ConcurrencyDate is managed internally and was ignored. "
                "The server uses the current value from the artifact."
            )

        # After stripping internal fields, ensure there's still something to update
        if not working_fields and cp_friendly is None:
            return format_error_response(
                error="No updatable fields provided after removing internal-only fields",
                error_code=ErrorCodes.INVALID_PARAMETER,
                details={"parameter": "fields", "stripped_fields": ["ConcurrencyDate"]},
                suggestion="Provide at least one writable field besides ConcurrencyDate.",
            )

        # --- Step 3a: Field name resolution + value resolution ---
        # For top-level artifacts: corrects misnamed keys AND resolves string values to IDs.
        # For sub-artifacts: corrects misnamed keys only (no priority/status/type fields).
        template_context = TemplateContext(spira_client)
        field_warnings = await resolve_fields_for_create(
            spira_client,
            template_context,
            config,
            artifact_type,
            product_id,
            [working_fields],  # wrap in list — resolver expects list[dict]
        )
        update_warnings.extend(field_warnings)

        # Validate custom_properties type (after extraction, before field key check)
        if cp_friendly is not None and not isinstance(cp_friendly, dict):
            update_warnings.append(
                f"custom_properties must be a dict, got {type(cp_friendly).__name__}. Skipping."
            )
            cp_friendly = None

        # Sub-artifacts: custom_properties not supported via this tool
        if cp_friendly is not None and is_sub_artifact:
            update_warnings.append(
                f"custom_properties is not supported for sub-artifact "
                f"type '{artifact_type}'. Ignoring."
            )
            cp_friendly = None

        # --- Step 3b: Validate field keys against writable_fields ---
        field_key_error = validate_field_keys(
            working_fields,
            config.writable_fields,
        )
        if field_key_error is not None:
            return field_key_error

        # --- Step 4: GET full artifact ---
        # single_endpoint is guaranteed non-None for updatable types
        # (validated at import time by config.validate())
        assert config.single_endpoint is not None  # noqa: S101
        if is_sub_artifact:
            get_endpoint = config.single_endpoint.format(
                product_id=product_id,
                parent_id=parent_id,
                artifact_id=artifact_id,
            )
        else:
            get_endpoint = config.single_endpoint.format(
                product_id=product_id,
                artifact_id=artifact_id,
            )

        try:
            raw_data = await spira_client.make_spira_api_get_request(get_endpoint)
        except SpiraApiError as e:
            return format_error_response(
                error=f"Failed to retrieve {artifact_type}: {e}",
                error_code=e.error_code,
                details={
                    "product_id": product_id,
                    "artifact_type": artifact_type,
                    "artifact_id": artifact_id,
                },
                suggestion="Check that the artifact exists and you have access.",
            )

        if not raw_data:
            return format_error_response(
                error=f"{artifact_type} with ID {artifact_id} not found",
                error_code=ErrorCodes.NOT_FOUND,
                details={
                    "product_id": product_id,
                    "artifact_type": artifact_type,
                    "artifact_id": artifact_id,
                },
                suggestion="Verify the artifact_id is correct.",
            )

        # --- Step 5: Shallow merge ---
        merged = dict(raw_data)
        for key, value in working_fields.items():
            merged[key] = value

        # Preserve ConcurrencyDate from GET (override any user-provided value)
        if "ConcurrencyDate" in raw_data:
            merged["ConcurrencyDate"] = raw_data["ConcurrencyDate"]

        # --- Step 6: Custom properties serialization + merge ---
        if cp_friendly is not None:
            custom_property_resolver = CustomPropertyResolver(spira_client, template_context)
            definitions = await custom_property_resolver.get_definitions(product_id, artifact_type)
            wire_array, ser_warnings = serialize_custom_properties(cp_friendly, definitions)
            update_warnings.extend(ser_warnings)

            # Merge: keep existing CPs not mentioned in user's dict
            existing_cps = raw_data.get("CustomProperties") or []
            if wire_array:
                # Build set of property numbers being updated
                updated_numbers = {entry["PropertyNumber"] for entry in wire_array}
                # Keep existing entries not being updated
                kept = [e for e in existing_cps if e.get("PropertyNumber") not in updated_numbers]
                merged["CustomProperties"] = kept + wire_array
            # If wire_array is empty (all skipped), keep existing CPs unchanged

        # --- Step 7: PUT ---
        # update_endpoint is guaranteed non-None for updatable types
        # (validated at import time by config.validate())
        assert config.update_endpoint is not None  # noqa: S101
        if is_sub_artifact:
            put_endpoint = config.update_endpoint.format(
                product_id=product_id,
                parent_id=parent_id,
            )
        else:
            put_endpoint = config.update_endpoint.format(
                product_id=product_id,
                artifact_id=artifact_id,
            )

        try:
            await spira_client.make_spira_api_put_request(put_endpoint, merged)
        except SpiraApiError as e:
            return format_error_response(
                error=f"Failed to update {artifact_type}: {e}",
                error_code=e.error_code,
                details={
                    "product_id": product_id,
                    "artifact_type": artifact_type,
                    "artifact_id": artifact_id,
                },
                suggestion="Check Spira connection and try again.",
            )

        # --- Step 8: Success response ---
        result: dict[str, Any] = {
            "artifact_type": artifact_type,
            "artifact_id": artifact_id,
            "message": f"{artifact_type} updated successfully",
        }
        if update_warnings:
            result["warnings"] = update_warnings
        return format_success_response(result)

    except Exception as e:
        return format_error_response(
            error=f"Unexpected error updating {artifact_type}: {_sanitize_error(e)}",
            error_code=getattr(e, "error_code", ErrorCodes.API_ERROR),
            details={
                "product_id": product_id,
                "artifact_type": artifact_type,
                "artifact_id": artifact_id,
            },
            suggestion="Check Spira connection and try again.",
        )


# Type hint for the tool signature — advertises valid values in the JSON
# schema (so the LLM sees them in tools/list) but accepts any string at
# Pydantic validation time.  Actual validation happens in _impl via
# ParameterValidator, which returns our standard error envelope.
UpdatableArtifactType = Annotated[
    str,
    WithJsonSchema(
        {
            "type": "string",
            "enum": list(UPDATABLE_ARTIFACT_TYPES),
        }
    ),
]


def register_tools(mcp) -> None:
    """Register product_update_artifact with the MCP server."""

    @mcp.tool(
        name="product_update_artifact",
        description=(
            "Update a single artifact by ID in a Spira product.\n"
            "\n"
            "Sub-artifacts (test_step, mitigation, requirement_step) require parent_id. "
            "Use get_artifact_schema to discover writable fields for each type.\n"
            "To clear a custom property, set its value to null."
        ),
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )
    async def product_update_artifact(
        artifact_type: UpdatableArtifactType,
        artifact_id: int,
        fields: dict[str, Any],
        product_id: int | None = None,
        parent_id: int | None = None,
    ) -> str:
        """Update a single artifact by ID in a Spira product."""
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
            return await _update_artifact_impl(
                spira_client,
                artifact_type,
                artifact_id,
                resolved_id,
                fields,
                parent_id=parent_id,
            )
        except Exception as e:
            return format_error_response(
                error=f"Unexpected error: {_sanitize_error(e)}",
                error_code=getattr(e, "error_code", ErrorCodes.API_ERROR),
                details={"exception": _sanitize_error(e)},
            )
