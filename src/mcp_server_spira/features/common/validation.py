"""Shared validation helpers for create/update tools.

Extracts the common validation steps (product_id, artifact_type, parent_id)
that are identical between create and update validation pipelines.

All functions are synchronous, side-effect-free, and return either
None (valid) or a JSON error string (invalid).
"""

import json

from mcp_server_spira.features.sub_artifact_configs import (
    SUB_ARTIFACT_TYPES,
)
from mcp_server_spira.utils.common.responses import (
    ErrorCodes,
    format_error_response,
)
from mcp_server_spira.utils.common.validation import ParameterValidator


def validate_common_params(
    product_id: int,
    artifact_type: str,
    valid_types: tuple[str, ...],
    parent_id: int | None = None,
) -> str | None:
    """Validate the common parameters shared by create and update requests.

    Steps:
        1. product_id must be positive integer (>= 1)
        2. artifact_type must be in valid_types
        3. parent_id required for sub-artifact types (positive integer)

    Returns None if valid, or a JSON error string if invalid.

    Spec:
        - ALWAYS returns str | None — never raises
        - Returns None when all three validation steps pass
        - Returns a JSON error envelope on the first failing step
        - Validation order short-circuits on first failure
        - Step 3 only applies when artifact_type is in SUB_ARTIFACT_TYPES
        - Pure function — no I/O, no side effects, no mutations
    """
    # 1. Validate product_id
    validation_error = ParameterValidator.validate_positive_integer(product_id, "product_id")
    if validation_error is not None:
        return json.dumps(validation_error, indent=2)

    # 2. Validate artifact_type
    type_error = ParameterValidator.validate_type_param(artifact_type, valid_types, "artifact_type")
    if type_error is not None:
        return format_error_response(**type_error)

    # 3. Validate parent_id for sub-artifacts
    is_sub_artifact = artifact_type in SUB_ARTIFACT_TYPES
    if is_sub_artifact and parent_id is None:
        return format_error_response(
            error=f"parent_id is required for {artifact_type}",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "parameter": "parent_id",
                "artifact_type": artifact_type,
            },
            suggestion=f"Provide parent_id when working with {artifact_type}.",
        )
    if is_sub_artifact and parent_id is not None:
        validation_error = ParameterValidator.validate_positive_integer(parent_id, "parent_id")
        if validation_error is not None:
            return json.dumps(validation_error, indent=2)

    return None
