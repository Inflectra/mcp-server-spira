"""Pure validation for artifact update requests.

Extracted from _update_artifact_impl to enable:
- Unit testing without async or mocks
- Clear separation of validation phases (steps 1-5 vs step 6)

All functions are synchronous, side-effect-free, and return either
None (valid) or a JSON error string (invalid).
"""

import json
from typing import Any

from mcp_server_spira.features.common.validation import validate_common_params
from mcp_server_spira.features.sub_artifact_configs import (
    SUB_ARTIFACT_TYPE_TO_CONFIG_KEY,
    SUB_ARTIFACT_TYPES,
)
from mcp_server_spira.utils.common.responses import (
    ErrorCodes,
    format_error_response,
)
from mcp_server_spira.utils.common.validation import ParameterValidator

# Re-export for consumers that import from this module.
__all__ = [
    "SUB_ARTIFACT_TYPE_TO_CONFIG_KEY",
    "SUB_ARTIFACT_TYPES",
    "UPDATABLE_ARTIFACT_TYPES",
    "validate_field_keys",
    "validate_update_request",
]

# All artifact types supported by the update tool (top-level + sub-artifacts).
UPDATABLE_ARTIFACT_TYPES: tuple[str, ...] = (
    "incident",
    "task",
    "requirement",
    "test_case",
    "risk",
    "release",
    "test_set",
    "test_step",
    "mitigation",
    "requirement_step",
)


def validate_update_request(
    artifact_type: str,
    product_id: int,
    artifact_id: int,
    fields: dict[str, Any],
    parent_id: int | None = None,
) -> str | None:
    """Validate an update request (steps 1-5). Returns None if valid, JSON error string if invalid.

    Spec:
        - ALWAYS returns str | None — never raises
        - Returns None when all validation steps pass
        - Returns a JSON error envelope (same format as format_error_response)
          on the first failing validation step
        - Validation order (short-circuits on first failure):
            1-3. Common params (product_id, artifact_type, parent_id) via
                 validate_common_params
            4. artifact_id must be positive integer (>= 1)
            5. fields must be a non-empty dict
        - Does NOT validate field keys against writable_fields — that is
          handled by validate_field_keys after field resolution
        - Does NOT mutate fields
    """
    # Steps 1-3: Validate product_id, artifact_type, parent_id (shared with create)
    common_error = validate_common_params(
        product_id=product_id,
        artifact_type=artifact_type,
        valid_types=UPDATABLE_ARTIFACT_TYPES,
        parent_id=parent_id,
    )
    if common_error is not None:
        return common_error

    # 4. Validate artifact_id
    validation_error = ParameterValidator.validate_positive_integer(artifact_id, "artifact_id")
    if validation_error is not None:
        return json.dumps(validation_error, indent=2)

    # 5. Validate fields is a non-empty dict
    if not isinstance(fields, dict) or len(fields) == 0:
        return format_error_response(
            error="fields must be a non-empty dict",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={"parameter": "fields"},
            suggestion="Provide fields as a dict with at least one key.",
        )

    return None


def validate_field_keys(
    fields: dict[str, Any],
    writable_fields: list[str],
) -> str | None:
    """Validate field keys against writable_fields (step 6).

    Returns None if valid, JSON error string if invalid.

    Spec:
        - ALWAYS returns str | None — never raises
        - Step 6a: rejects ``CustomProperties`` key with INVALID_PARAMETER
          (wire format not allowed). This check runs BEFORE the writable_fields
          check since ``CustomProperties`` may appear in some configs'
          writable_fields list but is never allowed for updates.
        - Step 6b: validates remaining keys against writable_fields excluding
          the virtual ``custom_properties`` entry. Keys not in the filtered
          writable_fields list produce an INVALID_PARAMETER error listing
          invalid fields and valid writable fields.
        - Does NOT mutate fields or writable_fields
    """
    # 6a. Reject CustomProperties wire format key
    if "CustomProperties" in fields:
        return format_error_response(
            error="CustomProperties wire format is not allowed for updates",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "parameter": "fields",
                "invalid_key": "CustomProperties",
            },
            suggestion=(
                "Use 'custom_properties' as a {name: value} dict instead of "
                "the raw CustomProperties array."
            ),
        )

    # 6b. Validate remaining keys against writable_fields (excluding virtual custom_properties)
    allowed = {f for f in writable_fields if f != "custom_properties"}
    invalid_keys = [k for k in fields if k not in allowed]

    if invalid_keys:
        return format_error_response(
            error=f"Invalid field(s) for update: {', '.join(invalid_keys)}",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "invalid_fields": invalid_keys,
                "writable_fields": sorted(allowed),
            },
            suggestion="Use only fields from the writable_fields list.",
        )

    return None
