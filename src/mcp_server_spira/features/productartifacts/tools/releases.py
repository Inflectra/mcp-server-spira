"""
Provides operations for working with the Spira product releases

This module provides MCP tools for retrieving and updating product releases
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _get_releases_impl(
    spira_client,
    product_id: int,
    start_row: int = 1,
    number_rows: int = 100,
) -> str:
    """
    Implementation of retrieving the list of releases in the specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product.
            If the ID is PR:45, just use 45.
        start_row: The starting row number for pagination (1-based index)
        number_rows: The number of rows to return

    Returns:
        JSON string containing the list of releases with data structure
    """
    try:
        # Build the search endpoint URL with query parameters
        releases_url = (
            f"projects/{product_id}/releases/search?start_row={start_row}&number_rows={number_rows}"
        )

        # Make POST request with empty filter array (no filtering for now)
        releases = spira_client.make_spira_api_post_request(releases_url, [])

        # Return JSON response with data structure
        return format_success_response(data=releases)

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve releases",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e), "product_id": product_id},
            suggestion=("Check API connectivity, authentication, and that the product_id is valid"),
        )


def _get_release_by_id_impl(spira_client, product_id: int, release_id: int) -> str:
    """
    Implementation of retrieving a single release in the specified
    product with the specified ID

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product.
            If the ID is PR:45, just use 45.
        release_id: The numeric ID of the release.
            If the ID is RL:12, just use 12.

    Returns:
        JSON string containing the details of the release
    """
    try:
        # Get the release in the product
        release_url = f"projects/{product_id}/releases/{release_id}"
        release = spira_client.make_spira_api_get_request(release_url)

        # Return JSON response with data structure (single item as array)
        return format_success_response(data=[release])

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve release",
            error_code=ErrorCodes.API_ERROR,
            details={
                "message": str(e),
                "product_id": product_id,
                "release_id": release_id,
            },
            suggestion=(
                "Check API connectivity, authentication, and that "
                "the product_id and release_id are valid"
            ),
        )


def register_tools(mcp) -> None:
    """
    Register product releases tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_releases(
        product_id: int,
        start_row: int = 1,
        number_rows: int = 100,
    ) -> str:
        """
        Retrieves a list of the releases in the specified product

        Maps to Spira API: POST /projects/{product_id}/releases/search

        This tool returns releases from the specified product using
        server-side pagination. Use this for retrieving product-level
        release lists with filtering and sorting capabilities.

        **API Endpoint**: POST /projects/{product_id}/releases/search
        **Query Parameters**: start_row, number_rows
        **Request Body**: [] (empty RemoteFilter array - no filtering
            for now)

        **Note**: This endpoint uses server-side pagination. The API
        returns only the requested page of results. A dedicated filter
        tool will be added in a future milestone.

        Args:
            product_id: The numeric ID of the product.
                If the ID is PR:45, just use 45.
            start_row: The starting row number for pagination
                (default: 1, 1-based index)
            number_rows: The number of rows to return (default: 100)

        Returns:
            JSON string with structure:
            {
                "data": [
                    {
                        "ReleaseId": 10,
                        "Name": "Release 1.5.0",
                        "Description": "Major feature release",
                        "VersionNumber": "1.5.0",
                        "ReleaseStatusId": 2,
                        "ReleaseStatusName": "In Progress",
                        "ReleaseTypeId": 1,
                        "ReleaseTypeName": "Major Release",
                        "Active": true,
                        "Summary": false,
                        "CreatorId": 4,
                        "CreatorName": "Jane Smith",
                        "CreatorGuid": "def-456",
                        "OwnerId": 5,
                        "OwnerName": "John Doe",
                        "OwnerGuid": "abc-123",
                        "IndentLevel": "1",
                        "StartDate": "2024-01-01T00:00:00Z",
                        "EndDate": "2024-03-31T00:00:00Z",
                        "CreationDate": "2023-12-01T10:00:00Z",
                        "LastUpdateDate": "2024-01-15T14:30:00Z",
                        "ResourceCount": 5,
                        "DaysNonWorking": 10,
                        "PlannedEffort": 2400,
                        "AvailableEffort": 1200,
                        "TaskEstimatedEffort": 1800,
                        "TaskActualEffort": 900,
                        "TaskCount": 25,
                        "FullName": "Release 1.5.0",
                        "CountBlocked": 2,
                        "CountCaution": 1,
                        "CountFailed": 3,
                        "CountNotApplicable": 0,
                        "CountNotRun": 5,
                        "CountPassed": 15,
                        "PercentComplete": 50,
                        "RequirementCount": 12,
                        "RequirementPoints": 34.5,
                        "ProjectId": 55,
                        "ProjectGuid": "mno-345",
                        "ArtifactTypeId": 4,
                        "ConcurrencyDate": "2024-01-15T14:30:00Z",
                        "CustomProperties": [],
                        "Tags": "major,feature",
                        "IsAttachments": true,
                        "Guid": "pqr-678"
                    }
                ]
            }

        Key Fields:
            - ReleaseId: Unique identifier for the release
            - Name: The name of the release
            - Description: The detailed description of the release
            - VersionNumber: The version number string (e.g., "1.5.0")
            - ReleaseStatusId/ReleaseStatusName: Current status of the
                release
            - ReleaseTypeId/ReleaseTypeName: Type of release
                (Major, Minor, etc.)
            - Active: Whether the release is active for the project
            - Summary: Whether this is a summary release with child
                releases
            - CreatorId/CreatorName/CreatorGuid: User who created the
                release
            - OwnerId/OwnerName/OwnerGuid: User the release is assigned to
            - IndentLevel: Indentation level for hierarchical display
            - StartDate: Scheduled start date for the release
            - EndDate: Scheduled end date for the release
            - CreationDate: When the release was originally created
            - LastUpdateDate: When the release was last modified
            - ResourceCount: Number of people working on the release
            - DaysNonWorking: Non-working days in the release period
            - PlannedEffort: Estimated planned effort in minutes
            - AvailableEffort: Remaining effort available for planning
            - TaskEstimatedEffort: Total estimated effort from all tasks
            - TaskActualEffort: Total actual effort from all tasks
            - TaskCount: Number of tasks scheduled for this release
            - FullName: Full name and version number combined
            - CountBlocked/CountCaution/CountFailed/CountNotApplicable/
                CountNotRun/CountPassed: Test case execution counts
            - PercentComplete: Percentage complete of the release
            - RequirementCount: Number of requirements in this release
            - RequirementPoints: Total story points from requirements
            - ProjectId/ProjectGuid: Project the release belongs to
            - ArtifactTypeId: Type of artifact (4 for releases)
            - ConcurrencyDate: Timestamp for optimistic concurrency control
            - CustomProperties: List of custom fields for this release
            - Tags: Meta-tags associated with the release
            - IsAttachments: Whether the release has attachments
            - Guid: Unique global identifier for the release

        When to Use:
            - Getting release list for a specific product
            - Retrieving releases with server-side pagination
            - Planning sprints and iterations
            - Analyzing release progress and metrics

        Related Tools:
            - get_release_by_id: Get single release with full details
            - format_artifacts_as_markdown: Format filtered/processed
                results for display

        Error Responses:
            {
                "error": "Invalid product_id parameter",
                "error_code": "INVALID_VALUE",
                "details": {
                    "parameter": "product_id",
                    "value": -1,
                    "expected": ">= 1"
                },
                "suggestion": "product_id must be >= 1"
            }

        Example Usage:
            # Get first 100 releases from product 55
            releases_json = get_releases(product_id=55)
            releases = json.loads(releases_json)

            # Get next page of releases
            releases_json = get_releases(
                product_id=55, start_row=101, number_rows=100
            )

            # Process and filter results
            releases = json.loads(releases_json)
            active_releases = [
                r for r in releases["data"]
                if r["Active"] and not r["Summary"]
            ]
        """
        try:
            # Validate product_id
            validation_error = ParameterValidator.validate_positive_integer(
                product_id, "product_id", min_value=1
            )
            if validation_error:
                return format_error_response(**validation_error)

            # Validate start_row
            validation_error = ParameterValidator.validate_positive_integer(
                start_row, "start_row", min_value=1
            )
            if validation_error:
                return format_error_response(**validation_error)

            # Validate number_rows
            validation_error = ParameterValidator.validate_positive_integer(
                number_rows, "number_rows", min_value=1
            )
            if validation_error:
                return format_error_response(**validation_error)

            # Get Spira client and retrieve releases
            spira_client = get_spira_client()
            return _get_releases_impl(
                spira_client,
                product_id,
                start_row,
                number_rows,
            )
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve releases",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )

    @mcp.tool()
    def get_release_by_id(product_id: int, release_id: int) -> str:
        """
        Retrieves the details of a single release in the specified product

        Maps to Spira API: GET /projects/{product_id}/releases/{release_id}

        Use this tool when you need to:
        - View the details of a single release in the specified product
        - Access the full description and selected fields of the release

        Args:
            product_id: The numeric ID of the product.
                If the ID is PR:45, just use 45.
            release_id: The numeric ID of the release.
                If the ID is RL:12, just use 12.

        Returns:
            JSON string with structure:
            {
                "data": [
                    {
                        "ReleaseId": 10,
                        "Name": "Release 1.5.0",
                        "Description": "Major feature release",
                        "VersionNumber": "1.5.0",
                        "ReleaseStatusId": 2,
                        "ReleaseStatusName": "In Progress",
                        ... (same fields as get_releases)
                    }
                ]
            }

        Key Fields:
            Same as get_releases - see that tool for field descriptions

        When to Use:
            - Getting details of a specific release by ID
            - Retrieving full release information including metrics
            - Checking release status and progress

        Related Tools:
            - get_releases: Get list of releases for a product
            - format_artifacts_as_markdown: Format for display

        Error Responses:
            {
                "error": "Failed to retrieve release",
                "error_code": "API_ERROR",
                "details": {
                    "message": "Release not found",
                    "product_id": 55,
                    "release_id": 999
                },
                "suggestion": "Check API connectivity, authentication, "
                    "and that the product_id and release_id are valid"
            }

        Example Usage:
            # Get specific release
            release_json = get_release_by_id(product_id=55, release_id=10)
            release = json.loads(release_json)
            release_data = release["data"][0]
            print(f"Release: {release_data['Name']}")
            print(f"Status: {release_data['ReleaseStatusName']}")
            print(f"Progress: {release_data['PercentComplete']}%")
        """
        try:
            # Validate product_id
            validation_error = ParameterValidator.validate_positive_integer(
                product_id, "product_id", min_value=1
            )
            if validation_error:
                return format_error_response(**validation_error)

            # Validate release_id
            validation_error = ParameterValidator.validate_positive_integer(
                release_id, "release_id", min_value=1
            )
            if validation_error:
                return format_error_response(**validation_error)

            # Get Spira client and retrieve release
            spira_client = get_spira_client()
            return _get_release_by_id_impl(spira_client, product_id, release_id)
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve release",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
