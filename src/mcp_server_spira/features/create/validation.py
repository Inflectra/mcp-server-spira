"""Pure validation for artifact creation requests.

Extracted from _create_artifact_impl to enable:
- Unit testing without async or mocks
- Reuse by future update/patch tools

All functions are synchronous, side-effect-free, and return either
None (valid) or a JSON error string (invalid).
"""

import json
from typing import Any

from mcp_server_spira.features.artifact_configs import ARTIFACT_CONFIG
from mcp_server_spira.features.common.validation import validate_common_params
from mcp_server_spira.features.sub_artifact_configs import (
    SUB_ARTIFACT_CONFIG,
    SUB_ARTIFACT_TYPE_TO_CONFIG_KEY,
    SUB_ARTIFACT_TYPES,
)
from mcp_server_spira.models import ArtifactConfig, SubArtifactConfig
from mcp_server_spira.utils.common.responses import (
    ErrorCodes,
    format_error_response,
)
from mcp_server_spira.utils.common.validation import ParameterValidator

# All artifact types supported by the create tool (top-level + sub-artifacts).
CREATABLE_ARTIFACT_TYPES: tuple[str, ...] = (
    "incident",
    "task",
    "requirement",
    "test_case",
    "risk",
    "release",
    "test_set",
    "build",
    "test_step",
    "mitigation",
    "requirement_step",
)


def validate_create_request(
    artifact_type: str,
    product_id: int,
    fields: list[dict[str, Any]],
    release_id: int | None = None,
    parent_id: int | None = None,
) -> str | None:
    """Validate a create-artifact request before any async/API work.

    Returns None if the request is valid, or a JSON error string if invalid.
    Pure function — no I/O, no side effects, no mutations to `fields`.

    Spec:
        - ALWAYS returns str | None — never raises
        - Returns None when all validation steps pass
        - Returns a JSON error envelope (same format as format_error_response)
          on the first failing validation step
        - Validation order (short-circuits on first failure):
            1. product_id must be positive integer (>= 1)
            2. artifact_type must be in CREATABLE_ARTIFACT_TYPES
            3. parent_id required for sub-artifact types, must be positive
            4. url_params validation (e.g. release_id required for builds)
            5. fields must be a non-empty list of dicts
            6. required_fields presence check for each item
            7. Name non-blank check for top-level types
            8. Build-specific BuildStatusId validation
        - Does NOT validate step 7a (per-item Description for sub-artifacts)
          because that requires partial-failure reporting from the batch loop
        - Does NOT mutate fields (inject_defaults, CP serialization stay in _impl)
    """
    # Steps 1-3: Validate product_id, artifact_type, parent_id (shared with update)
    common_error = validate_common_params(
        product_id=product_id,
        artifact_type=artifact_type,
        valid_types=CREATABLE_ARTIFACT_TYPES,
        parent_id=parent_id,
    )
    if common_error is not None:
        return common_error

    # Determine if this is a sub-artifact
    is_sub_artifact = artifact_type in SUB_ARTIFACT_TYPES

    # Look up config
    config: ArtifactConfig | SubArtifactConfig
    if is_sub_artifact:
        config_key = SUB_ARTIFACT_TYPE_TO_CONFIG_KEY[artifact_type]
        config = SUB_ARTIFACT_CONFIG[config_key]
    else:
        config = ARTIFACT_CONFIG[artifact_type]

    # 4. Validate url_params (e.g. release_id for builds)
    if not is_sub_artifact and hasattr(config, "url_params"):
        for param in config.url_params:
            if param == "release_id" and release_id is None:
                return format_error_response(
                    error=f"release_id is required for {artifact_type}",
                    error_code=ErrorCodes.INVALID_PARAMETER,
                    details={
                        "parameter": "release_id",
                        "artifact_type": artifact_type,
                    },
                    suggestion=f"release_id is required for {artifact_type}.",
                )
            if param == "release_id" and release_id is not None:
                validation_error = ParameterValidator.validate_positive_integer(
                    release_id, "release_id"
                )
                if validation_error is not None:
                    return json.dumps(validation_error, indent=2)

    # 5. Validate fields is a non-empty list of dicts
    if not isinstance(fields, list) or len(fields) == 0:
        return format_error_response(
            error="fields must be a non-empty list of dicts",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={"parameter": "fields"},
            suggestion="Provide fields as a list with at least one dict.",
        )
    for i, item in enumerate(fields):
        # Runtime guard: MCP framework may pass non-dict elements despite type hint
        if not isinstance(item, dict):  # pragma: no branch
            return format_error_response(  # type: ignore[unreachable]
                error=f"fields[{i}] must be a dict",
                error_code=ErrorCodes.INVALID_PARAMETER,
                details={"parameter": "fields", "index": i},
                suggestion="Each element in fields must be a dict.",
            )

    # 6. Validate required_fields presence for each item
    required = config.required_fields
    for i, item in enumerate(fields):
        missing = [f for f in required if f not in item or item[f] is None]
        if missing:
            return format_error_response(
                error=f"Missing required fields for {artifact_type}",
                error_code=ErrorCodes.INVALID_PARAMETER,
                details={
                    "missing_fields": missing,
                    "required_fields": required,
                    "artifact_type": artifact_type,
                    "index": i,
                },
                suggestion=f"Provide {' and '.join(required)}.",
            )

    # 7. Name non-blank check for top-level types
    if not is_sub_artifact:
        for i, item in enumerate(fields):
            if "Name" in item and isinstance(item["Name"], str) and not item["Name"].strip():
                return format_error_response(
                    error="Name must contain at least one non-whitespace character",
                    error_code=ErrorCodes.INVALID_PARAMETER,
                    details={
                        "parameter": "Name",
                        "index": i,
                        "artifact_type": artifact_type,
                    },
                    suggestion="Provide a non-blank Name.",
                )

    # 8. Build-specific BuildStatusId validation
    if artifact_type == "build":
        for i, item in enumerate(fields):
            build_status = item.get("BuildStatusId")
            if build_status not in (1, 2):
                return format_error_response(
                    error="BuildStatusId must be 1 (Failed) or 2 (Passed)",
                    error_code=ErrorCodes.INVALID_PARAMETER,
                    details={
                        "parameter": "BuildStatusId",
                        "value": build_status,
                        "valid_values": [1, 2],
                        "index": i,
                    },
                    suggestion="Use 1 (Failed) or 2 (Passed).",
                )

    return None
