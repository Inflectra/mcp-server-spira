"""
Provides operations for recording the results of CI/CD builds into Spira

This module provides MCP tools for recording the results of continuous integration / continuous deployment
pipeline builds against a matching release in Spira
"""

from mcp_server_spira.config import resolve_product_id
from mcp_server_spira.utils.common import get_spira_client
from mcp_server_spira.utils.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.utils.common.validation import ParameterValidator


async def _create_build_url_impl(
    spira_client,
    product_id: int,
    release_id: int,
    build_status_id: int,
    name: str,
    description: str,
    commits: list[str],
) -> str:
    """
    Creates a new CI/CD pipeline build entry in Spira

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45.
        release_id: The ID of the release/sprint/phase in Spira that the build is for, without the RL prefix (e.g. RL:12 would be 12)
        build_status_id: The status of the build (1=Failed, 2=Passed)
        name: The name of the build (usually containing the project name and the date/time of the build)
        description: The detailed description of the build (optional), what was included and why
        commits: An optional array/list of the Git hashes of the commits included in the build

    Returns:
        JSON string with structure:
        {
            "build_id": "BL:123",
            "message": "Build created successfully"
        }
    """
    # Validate product_id
    validation_error = ParameterValidator.validate_positive_integer(product_id, "product_id")
    if validation_error:
        return format_error_response(
            error=validation_error["error"],
            error_code=ErrorCodes.INVALID_PARAMETER,
            details=validation_error.get("details", {}),
        )

    # Validate release_id
    validation_error = ParameterValidator.validate_positive_integer(release_id, "release_id")
    if validation_error:
        return format_error_response(
            error=validation_error["error"],
            error_code=ErrorCodes.INVALID_PARAMETER,
            details=validation_error.get("details", {}),
        )

    # Validate build_status_id (must be 1 or 2)
    if build_status_id not in [1, 2]:
        return format_error_response(
            error="build_status_id must be 1 (Failed) or 2 (Passed)",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={
                "parameter": "build_status_id",
                "value": build_status_id,
                "expected": "1 or 2 (1=Failed, 2=Passed)",
            },
            suggestion="Use build_status_id of 1 or 2",
        )

    # Validate required string parameters
    if not name or not name.strip():
        return format_error_response(
            error="name is required and cannot be empty",
            error_code=ErrorCodes.INVALID_PARAMETER,
            details={"parameter": "name"},
            suggestion="Provide a non-empty build name",
        )

    try:
        # Populate the revisions object from the commits
        revisions = []
        if commits:
            for commit in commits:
                revision = {"RevisionKey": commit}
                revisions.append(revision)

        # The body we are sending
        body = {
            "ProjectId": product_id,
            "BuildStatusId": build_status_id,
            "ReleaseId": release_id,
            "Name": name,
            "Description": description,
            "Revisions": revisions,
        }

        # Record the build using the API method
        create_build_url = f"projects/{product_id}/releases/{release_id}/builds"
        build = await spira_client.make_spira_api_post_request(create_build_url, body)

        if not build:
            return format_error_response(
                error="Build was not created successfully",
                error_code=ErrorCodes.API_ERROR,
                details={"product_id": product_id, "release_id": release_id},
                suggestion="Verify product_id and release_id are valid",
            )

        # Extract the new build ID
        build_id = build.get("BuildId")
        if not build_id:
            return format_error_response(
                error="Build created but ID not returned",
                error_code=ErrorCodes.API_ERROR,
                details={"response": build},
            )

        return format_success_response(
            {
                "build_id": f"BL:{build_id}",
                "message": "Build created successfully",
            }
        )
    except Exception as e:
        return format_error_response(
            error=f"Failed to create build: {str(e)}",
            error_code=ErrorCodes.API_ERROR,
            details={
                "product_id": product_id,
                "release_id": release_id,
                "exception": str(e),
            },
        )


def register_tools(mcp) -> None:
    """
    Register tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool(
        name="product_create_build",
        annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": True},
    )
    async def create_build(
        release_id: int,
        build_status_id: int,
        name: str,
        description: str,
        commits: list[str],
        product_id: int | None = None,
    ) -> str:
        """
        Creates a new CI/CD pipeline build entry in Spira.

        Maps to Spira API: POST /projects/{product_id}/releases/{release_id}/builds

        Use this to record CI/CD build results and associate commits with releases.

        Args:
            product_id: The numeric ID of the product (e.g., 55 for PR:55). If omitted, uses SPIRA_PROJECT_ID from environment.
            release_id: Release/sprint ID without RL prefix (e.g., 12 for RL:12)
            build_status_id: Build status (1=Failed, 2=Passed)
            name: Build name (typically project name + date/time)
            description: Detailed build description (what was included and why)
            commits: Array of Git commit hashes included in the build

        Returns:
            JSON: {"build_id": "BL:123", "message": "Build created successfully"}

        Error Responses:
            Returns structured JSON with error, error_code, details, and suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            result = create_build(
                product_id=55, release_id=10, build_status_id=2,
                name="Build 2024-02-13 v1.5.0", description="Production build",
                commits=["abc123", "def456"]
            )
        """
        try:
            # Resolve product_id from explicit arg or SPIRA_PROJECT_ID env var
            resolved_id = resolve_product_id(product_id)
            if resolved_id is None:
                return format_error_response(
                    error="product_id is required",
                    error_code=ErrorCodes.INVALID_PARAMETER,
                    details={"parameter": "product_id"},
                    suggestion="Pass product_id explicitly or set SPIRA_PROJECT_ID in your environment",
                )
            product_id = resolved_id
            spira_client = get_spira_client()
            return await _create_build_url_impl(
                spira_client, product_id, release_id, build_status_id, name, description, commits
            )
        except Exception as e:
            return format_error_response(
                error=f"Unexpected error: {str(e)}",
                error_code=ErrorCodes.API_ERROR,
                details={"exception": str(e)},
            )
