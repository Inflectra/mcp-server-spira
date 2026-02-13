"""
Provides operations for recording the results of CI/CD builds into Spira

This module provides MCP tools for recording the results of continuous integration / continuous deployment
pipeline builds against a matching release in Spira
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _create_build_url_impl(
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
        build = spira_client.make_spira_api_post_request(create_build_url, body)

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

    @mcp.tool()
    def create_build(
        product_id: int,
        release_id: int,
        build_status_id: int,
        name: str,
        description: str,
        commits: list[str],
    ) -> str:
        """
        Creates a new CI/CD pipeline build entry in Spira

        Maps to Spira API: POST /projects/{product_id}/releases/{release_id}/builds

        Use this tool when you need to:
        - Push the results of an automated software build into Spira
        - Record CI/CD pipeline build results
        - Track build history and associate commits with releases

        Args:
            product_id: The numeric ID of the product. If the ID is PR:45, just use 45.
            release_id: The ID of the release/sprint/phase in Spira that the build is for, without the RL prefix (e.g. RL:12 would be 12)
            build_status_id: The status of the build:
                - 1 = Failed
                - 2 = Passed
            name: The name of the build (usually containing the project name and the date/time of the build)
            description: The detailed description of the build (optional), what was included and why
            commits: An optional array/list of the Git hashes of the commits included in the build

        Returns:
            JSON string with structure:
            {
                "build_id": "BL:123",
                "message": "Build created successfully"
            }

        Error Responses:
            {
                "error": "product_id must be a positive integer",
                "error_code": "INVALID_PARAMETER",
                "details": {
                    "parameter": "product_id",
                    "value": -1,
                    "expected": ">= 1"
                },
                "suggestion": "Use product_id >= 1"
            }

        Example Usage:
            # Record a successful build
            result = create_build(
                product_id=55,
                release_id=10,
                build_status_id=2,
                name="Build 2024-02-13 v1.5.0",
                description="Production build with bug fixes",
                commits=["abc123def", "456ghi789"]
            )
            # Returns: {"build_id": "BL:456", "message": "Build created successfully"}

            # Record a failed build
            result = create_build(
                product_id=55,
                release_id=10,
                build_status_id=1,
                name="Build 2024-02-13 v1.5.0",
                description="Build failed due to compilation errors",
                commits=[]
            )
        """
        try:
            spira_client = get_spira_client()
            return _create_build_url_impl(
                spira_client, product_id, release_id, build_status_id, name, description, commits
            )
        except Exception as e:
            return format_error_response(
                error=f"Unexpected error: {str(e)}",
                error_code=ErrorCodes.API_ERROR,
                details={"exception": str(e)},
            )
