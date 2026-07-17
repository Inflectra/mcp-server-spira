"""create_association tool — links two artifacts via association or coverage.

Follows the register_tools(mcp) + _impl separation pattern (ADR-0004).
"""

from mcp_server_spira.config import resolve_product_id
from mcp_server_spira.constants import (
    ARTIFACT_LINK_TYPE_IDS,
    SPIRA_ARTIFACT_TYPE_IDS,
    VALID_ASSOCIATION_PAIRS,
)
from mcp_server_spira.features.associations.tools import (
    VALID_ASSOCIATION_TYPES,
    VALID_COVERAGE_PAIRS,
    DestArtifactType,
    SourceArtifactType,
)
from mcp_server_spira.utils.common import (
    _sanitize_error,
    get_spira_client,
)
from mcp_server_spira.utils.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.utils.spira_client import SpiraClient

__all__ = [
    "_create_association_impl",
    "register_tools",
]


async def _create_association_impl(
    spira_client: SpiraClient,
    source_artifact_type: str,
    source_artifact_id: int,
    dest_artifact_type: str,
    dest_artifact_id: int,
    association_type: str,
    comment: str | None,
    product_id: int,
) -> str:
    """Create an association or coverage mapping between two artifacts.

    Spec:
        - ALWAYS returns a JSON string (never raises to the MCP layer)
        - Validates all parameters before making any API call
        - For related-to/depends-on: validates source->dest pair against
          VALID_ASSOCIATION_PAIRS before POSTing RemoteAssociation
        - For coverage: dispatches to the appropriate coverage endpoint
          based on source/dest types, reversing direction if needed
        - Returns format_success_response on success,
          format_error_response on failure
    """
    # --- Common validation ---
    if association_type not in VALID_ASSOCIATION_TYPES:
        return format_error_response(
            error=(f"Invalid association_type '{association_type}'."),
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "parameter": "association_type",
                "valid_values": list(VALID_ASSOCIATION_TYPES),
            },
        )

    if source_artifact_id <= 0:
        return format_error_response(
            error="source_artifact_id must be a positive integer.",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "parameter": "source_artifact_id",
                "value": source_artifact_id,
            },
        )

    if dest_artifact_id <= 0:
        return format_error_response(
            error="dest_artifact_id must be a positive integer.",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "parameter": "dest_artifact_id",
                "value": dest_artifact_id,
            },
        )

    # --- Dispatch by association_type ---
    if association_type in ("related-to", "depends-on"):
        return await _create_general_association(
            spira_client,
            source_artifact_type,
            source_artifact_id,
            dest_artifact_type,
            dest_artifact_id,
            association_type,
            comment,
            product_id,
        )

    # association_type == "coverage"
    return await _create_coverage(
        spira_client,
        source_artifact_type,
        source_artifact_id,
        dest_artifact_type,
        dest_artifact_id,
        product_id,
    )


async def _create_general_association(
    spira_client: SpiraClient,
    source_artifact_type: str,
    source_artifact_id: int,
    dest_artifact_type: str,
    dest_artifact_id: int,
    association_type: str,
    comment: str | None,
    product_id: int,
) -> str:
    """Create a related-to or depends-on association.

    Spec:
        - Validates source_artifact_type is a key in VALID_ASSOCIATION_PAIRS;
          returns INVALID_PARAMETER listing valid source types if not
        - Validates dest_artifact_type is in the source's frozenset of valid
          dests; returns INVALID_PARAMETER listing valid dests if not
        - Constructs RemoteAssociation POST body with type IDs from
          SPIRA_ARTIFACT_TYPE_IDS and link type from ARTIFACT_LINK_TYPE_IDS
        - POSTs to projects/{product_id}/associations
        - Returns format_success_response on success with source/dest info
        - Returns format_error_response with API_ERROR on POST failure
        - Never raises — all exceptions caught and returned as error envelope
    """
    valid_dests = VALID_ASSOCIATION_PAIRS.get(source_artifact_type)
    if valid_dests is None:
        return format_error_response(
            error=(f"Source type '{source_artifact_type}' does not support association creation."),
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "parameter": "source_artifact_type",
                "valid_source_types": sorted(VALID_ASSOCIATION_PAIRS.keys()),
            },
        )

    if dest_artifact_type not in valid_dests:
        return format_error_response(
            error=(
                f"Cannot create association from "
                f"'{source_artifact_type}' to "
                f"'{dest_artifact_type}'."
            ),
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "parameter": "dest_artifact_type",
                "valid_dest_types": sorted(valid_dests),
            },
        )

    body = {
        "SourceArtifactId": source_artifact_id,
        "SourceArtifactTypeId": SPIRA_ARTIFACT_TYPE_IDS[source_artifact_type],
        "DestArtifactId": dest_artifact_id,
        "DestArtifactTypeId": SPIRA_ARTIFACT_TYPE_IDS[dest_artifact_type],
        "ArtifactLinkTypeId": ARTIFACT_LINK_TYPE_IDS[association_type],
        "Comment": comment or "",
    }

    try:
        await spira_client.make_spira_api_post_request(f"projects/{product_id}/associations", body)
    except Exception as exc:
        return format_error_response(
            error=(f"Failed to create association: {_sanitize_error(exc)}"),
            error_code=ErrorCodes.API_ERROR,
            details={"exception": _sanitize_error(exc)},
        )

    return format_success_response(
        data={
            "source_artifact_type": source_artifact_type,
            "source_artifact_id": source_artifact_id,
            "dest_artifact_type": dest_artifact_type,
            "dest_artifact_id": dest_artifact_id,
            "association_type": association_type,
            "message": "Association created successfully",
        }
    )


async def _create_coverage(
    spira_client: SpiraClient,
    source_artifact_type: str,
    source_artifact_id: int,
    dest_artifact_type: str,
    dest_artifact_id: int,
    product_id: int,
) -> str:
    """Create a coverage mapping between two artifacts.

    Spec:
        - Validates (source_type, dest_type) pair against VALID_COVERAGE_PAIRS;
          returns INVALID_PARAMETER with valid pairs listed if not found
        - Dispatches to correct endpoint by dispatch_key:
          req_tc → POST {RequirementId, TestCaseId} to /requirements/test-cases
          req_ts → POST {RequirementId, TestStepId} to /requirements/test-steps
          rel_tc → POST [test_case_id] to /releases/{id}/test-cases
          tc_req → reverses IDs, POSTs as requirement→test_case internally
        - Returns format_success_response on success with source/dest info
        - Returns format_error_response with API_ERROR on POST failure
        - Returns format_error_response if dispatch_key is unhandled (defensive)
        - Never raises — all exceptions caught and returned as error envelope
    """
    pair = (source_artifact_type, dest_artifact_type)
    dispatch_key = VALID_COVERAGE_PAIRS.get(pair)

    if dispatch_key is None:
        return format_error_response(
            error=(f"Invalid coverage pair: {source_artifact_type} -> {dest_artifact_type}."),
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "parameter": "source/dest artifact types",
                "valid_pairs": [f"{s} -> {d}" for s, d in VALID_COVERAGE_PAIRS],
            },
            suggestion=(
                "Valid coverage pairs: "
                "requirement->test_case, "
                "requirement->test_step, "
                "release->test_case, "
                "test_case->requirement"
            ),
        )

    # Dispatch to the correct endpoint based on the pair
    try:
        if dispatch_key == "req_tc":
            body = {
                "RequirementId": source_artifact_id,
                "TestCaseId": dest_artifact_id,
            }
            endpoint = f"projects/{product_id}/requirements/test-cases"
            await spira_client.make_spira_api_post_request(endpoint, body)

        elif dispatch_key == "req_ts":
            body = {
                "RequirementId": source_artifact_id,
                "TestStepId": dest_artifact_id,
            }
            endpoint = f"projects/{product_id}/requirements/test-steps"
            await spira_client.make_spira_api_post_request(endpoint, body)

        elif dispatch_key == "rel_tc":
            endpoint = f"projects/{product_id}/releases/{source_artifact_id}/test-cases"
            await spira_client.make_spira_api_post_request(endpoint, [dest_artifact_id])

        elif dispatch_key == "tc_req":
            # Reverse: test_case->requirement becomes
            # requirement->test_case internally
            body = {
                "RequirementId": dest_artifact_id,
                "TestCaseId": source_artifact_id,
            }
            endpoint = f"projects/{product_id}/requirements/test-cases"
            await spira_client.make_spira_api_post_request(endpoint, body)

        else:
            return format_error_response(
                error=f"Unhandled coverage dispatch key: {dispatch_key}",
                error_code=ErrorCodes.API_ERROR,
                details={"dispatch_key": dispatch_key},
            )

    except Exception as exc:
        return format_error_response(
            error=(f"Failed to create coverage: {_sanitize_error(exc)}"),
            error_code=ErrorCodes.API_ERROR,
            details={"exception": _sanitize_error(exc)},
        )

    return format_success_response(
        data={
            "source_artifact_type": source_artifact_type,
            "source_artifact_id": source_artifact_id,
            "dest_artifact_type": dest_artifact_type,
            "dest_artifact_id": dest_artifact_id,
            "association_type": "coverage",
            "message": "Association created successfully",
        }
    )


def _build_docstring() -> str:
    """Build the dynamic docstring for create_association at registration time.

    Derives the valid pairs table from VALID_ASSOCIATION_PAIRS and
    VALID_COVERAGE_PAIRS so it stays in sync with constants.py.
    """
    # Build association pairs lines
    pair_lines: list[str] = []
    for src in sorted(VALID_ASSOCIATION_PAIRS.keys()):
        dests = ",".join(sorted(VALID_ASSOCIATION_PAIRS[src]))
        pair_lines.append(f"{src}->{dests}")

    # Build coverage summary
    # Group by source, note bidirectional pairs
    coverage_parts: list[str] = []
    seen: set[tuple[str, str]] = set()
    for src, dest in sorted(VALID_COVERAGE_PAIRS.keys()):
        if (src, dest) in seen:
            continue
        # Check if reverse pair exists
        if (dest, src) in VALID_COVERAGE_PAIRS:
            coverage_parts.append(f"{src}<->{dest}")
            seen.add((dest, src))
        else:
            coverage_parts.append(f"{src}->{dest}")
        seen.add((src, dest))

    pairs_block = ";\n".join(pair_lines) + "."
    coverage_block = ", ".join(coverage_parts)

    return (
        "Link two artifacts. association_type: related-to, depends-on, coverage.\n"
        "\n"
        f"Valid source->dest (related-to/depends-on):\n{pairs_block}\n"
        f"Coverage: {coverage_block}."
    )


def register_tools(mcp) -> None:
    """Register the create_association tool with the MCP server."""
    docstring = _build_docstring()

    @mcp.tool(
        name="create_association",
        description=docstring,
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )
    async def create_association(
        source_artifact_type: SourceArtifactType,
        source_artifact_id: int,
        dest_artifact_type: DestArtifactType,
        dest_artifact_id: int,
        association_type: str = "related-to",
        comment: str | None = None,
        product_id: int | None = None,
    ) -> str:
        """Link two artifacts."""
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
            return await _create_association_impl(
                spira_client,
                source_artifact_type,
                source_artifact_id,
                dest_artifact_type,
                dest_artifact_id,
                association_type,
                comment,
                resolved_id,
            )
        except Exception as e:
            return format_error_response(
                error=(f"Unexpected error: {_sanitize_error(e)}"),
                error_code=getattr(e, "error_code", ErrorCodes.API_ERROR),
                details={"exception": _sanitize_error(e)},
            )
