"""create_comment tool — posts a comment to a Spira artifact.

Follows the register_tools(mcp) + _impl separation pattern (ADR-0004).
"""

from typing import Annotated

from pydantic import WithJsonSchema

from mcp_server_spira.config import resolve_product_id
from mcp_server_spira.features.artifact_configs import ARTIFACT_CONFIG
from mcp_server_spira.utils.common import (
    SpiraApiError,
    _sanitize_error,
    get_spira_client,
)
from mcp_server_spira.utils.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.utils.common.validation import ParameterValidator
from mcp_server_spira.utils.spira_client import SpiraClient

__all__ = [
    "COMMENTABLE_ARTIFACT_TYPES",
    "CommentableArtifactType",
    "_create_comment_impl",
    "register_tools",
]

# Derived from ArtifactConfig — types with a non-None comments_endpoint.
COMMENTABLE_ARTIFACT_TYPES: tuple[str, ...] = tuple(
    name for name, cfg in ARTIFACT_CONFIG.items() if cfg.comments_endpoint is not None
)

# Type hint for the tool signature — advertises valid values in the JSON
# schema (so the LLM sees them in tools/list) but accepts any string at
# Pydantic validation time. Actual validation happens in _impl.
CommentableArtifactType = Annotated[
    str,
    WithJsonSchema({"type": "string", "enum": list(COMMENTABLE_ARTIFACT_TYPES)}),
]


async def _create_comment_impl(
    spira_client: SpiraClient,
    artifact_type: str,
    artifact_id: int,
    text: str,
    product_id: int,
) -> str:
    """Core implementation for create_comment.

    Takes *spira_client* as first arg so callers (and tests) can inject a
    mock without touching MCP registration.

    Spec:
        - ALWAYS returns a JSON string (never raises to the MCP layer)
        - On success: success envelope with data containing comment_id,
          artifact_type, artifact_id, message
        - On validation failure: error envelope with INVALID_PARAMETER
        - On API failure: error envelope with API_ERROR
        - Validation order (short-circuits on first failure):
          1. artifact_type in COMMENTABLE_ARTIFACT_TYPES
          2. artifact_id is a positive integer
          3. text is a non-empty string
        - POST body is [{"Text": text, "ArtifactId": artifact_id}] for incidents
          (array), or {"Text": text, "ArtifactId": artifact_id} for all other
          types (single object), determined by
          ARTIFACT_CONFIG[artifact_type].comments_body_is_array
        - ArtifactId is always included because some types (requirement,
          release) require it and it is harmless for others
        - Endpoint resolved from ARTIFACT_CONFIG[artifact_type].comments_endpoint
          formatted with product_id and artifact_id
    """
    # 1. Validate artifact_type
    type_error = ParameterValidator.validate_type_param(
        artifact_type, COMMENTABLE_ARTIFACT_TYPES, "artifact_type"
    )
    if type_error is not None:
        return format_error_response(**type_error)

    # 2. Validate artifact_id
    id_error = ParameterValidator.validate_positive_integer(artifact_id, "artifact_id")
    if id_error is not None:
        return format_error_response(**id_error)

    # 3. Validate text
    if not isinstance(text, str) or not text.strip():
        return format_error_response(
            error="Invalid text parameter",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "parameter": "text",
                "value": text if isinstance(text, str) else type(text).__name__,
            },
            suggestion="text must be a non-empty string.",
        )

    # 4. Resolve endpoint
    config = ARTIFACT_CONFIG[artifact_type]
    assert config.comments_endpoint is not None  # guaranteed by COMMENTABLE_ARTIFACT_TYPES filter
    endpoint = config.comments_endpoint.format(product_id=product_id, artifact_id=artifact_id)

    # 5. POST comment
    # Incident API expects an array of RemoteComment objects;
    # all other artifact types expect a single RemoteComment object.
    # ArtifactId is required in the body for some types (requirement, release)
    # and harmless for others, so always include it.
    comment_obj: dict[str, str | int] = {"Text": text, "ArtifactId": artifact_id}
    body: list[dict[str, str | int]] | dict[str, str | int] = (
        [comment_obj] if config.comments_body_is_array else comment_obj
    )
    try:
        response = await spira_client.make_spira_api_post_request(endpoint, body)
    except SpiraApiError as e:
        return format_error_response(
            error=f"Failed to create comment: {_sanitize_error(e)}",
            error_code=e.error_code,
            suggestion="Check that the artifact exists and you have permission to comment.",
        )

    # 6. Return success envelope
    # API returns an array of created comments; extract CommentId from first element
    if isinstance(response, list) and response:
        comment_id = response[0].get("CommentId") if isinstance(response[0], dict) else None
    elif isinstance(response, dict):
        comment_id = response.get("CommentId")
    else:
        comment_id = None
    return format_success_response(
        data={
            "comment_id": comment_id,
            "artifact_type": artifact_type,
            "artifact_id": artifact_id,
            "message": "Comment created successfully",
        }
    )


def register_tools(mcp) -> None:
    """Register the create_comment tool with the MCP server."""

    @mcp.tool(
        name="create_comment",
        description=(
            "Add a comment to an artifact.\n"
            "\n"
            'Use product_get_artifact with include=["comments"] to read existing comments.'
        ),
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )
    async def create_comment(
        artifact_type: CommentableArtifactType,
        artifact_id: int,
        text: str,
        product_id: int | None = None,
    ) -> str:
        """Add a comment to an artifact."""
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
            return await _create_comment_impl(
                spira_client, artifact_type, artifact_id, text, resolved_id
            )
        except Exception as e:
            return format_error_response(
                error=f"Unexpected error: {_sanitize_error(e)}",
                error_code=getattr(e, "error_code", ErrorCodes.API_ERROR),
                details={"exception": _sanitize_error(e)},
            )
