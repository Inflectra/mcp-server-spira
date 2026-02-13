"""
Provides operations for working with the Spira product incidents

This module provides MCP tools for retrieving and updating product incidents
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _get_incidents_impl(
    spira_client,
    product_id: int,
    start_row: int = 1,
    number_rows: int = 100,
    sort_by: str = "",
) -> str:
    """
    Implementation of retrieving the list of incidents in the specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product.
            If the ID is PR:45, just use 45.
        start_row: The starting row number for pagination (1-based index)
        number_rows: The number of rows to return
        sort_by: The field to sort by (optional)

    Returns:
        JSON string containing the list of incidents with data structure
    """
    try:
        # Build the search endpoint URL with query parameters
        incidents_url = (
            f"projects/{product_id}/incidents/search?"
            f"start_row={start_row}&number_rows={number_rows}"
        )

        # Add optional sort parameter if provided
        if sort_by:
            incidents_url += f"&sort_by={sort_by}"

        # Make POST request with empty filter array (no filtering for now)
        incidents = spira_client.make_spira_api_post_request(incidents_url, [])

        # Return JSON response with data structure
        return format_success_response(data=incidents)

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve incidents",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e), "product_id": product_id},
            suggestion=("Check API connectivity, authentication, and that the product_id is valid"),
        )


def register_tools(mcp) -> None:
    """
    Register product incidents tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_incidents(
        product_id: int,
        start_row: int = 1,
        number_rows: int = 100,
        sort_by: str = "",
    ) -> str:
        """
        Retrieves a list of the incidents in the specified product

        Maps to Spira API: POST /projects/{product_id}/incidents/search

        This tool returns incidents from the specified product using
        server-side pagination. Use this for retrieving product-level
        incident lists with filtering and sorting capabilities.

        **API Endpoint**: POST /projects/{product_id}/incidents/search
        **Query Parameters**: start_row, number_rows, sort_by
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
            sort_by: The field to sort by (optional, e.g., "IncidentId",
                "Name", "IncidentStatusName")

        Returns:
            JSON string with structure:
            {
                "data": [
                    {
                        "IncidentId": 456,
                        "Name": "Login page crashes on mobile",
                        "Description": "The login page crashes when
                            accessed from mobile devices",
                        "IncidentStatusId": 1,
                        "IncidentStatusName": "New",
                        "IncidentStatusOpenStatus": true,
                        "IncidentTypeId": 1,
                        "IncidentTypeName": "Bug",
                        "PriorityId": 1,
                        "PriorityName": "1 - Critical",
                        "SeverityId": 1,
                        "SeverityName": "1 - Critical",
                        "OwnerId": 5,
                        "OwnerName": "John Doe",
                        "OwnerGuid": "abc-123",
                        "OpenerId": 4,
                        "OpenerName": "Jane Smith",
                        "OpenerGuid": "def-456",
                        "EstimatedEffort": 240,
                        "ActualEffort": 120,
                        "RemainingEffort": 120,
                        "ProjectedEffort": 240,
                        "CompletionPercent": 50,
                        "StartDate": "2024-01-15T09:00:00Z",
                        "EndDate": "2024-01-18T17:00:00Z",
                        "ClosedDate": null,
                        "CreationDate": "2024-01-14T10:00:00Z",
                        "LastUpdateDate": "2024-01-16T14:30:00Z",
                        "DetectedReleaseId": 8,
                        "DetectedReleaseVersionNumber": "1.4.0",
                        "DetectedReleaseGuid": "ghi-789",
                        "ResolvedReleaseId": 10,
                        "ResolvedReleaseVersionNumber": "1.5.0",
                        "ResolvedReleaseGuid": "jkl-012",
                        "VerifiedReleaseId": null,
                        "VerifiedReleaseVersionNumber": null,
                        "VerifiedReleaseGuid": null,
                        "DetectedBuildId": 15,
                        "DetectedBuildName": "Build 1.4.0.15",
                        "FixedBuildId": null,
                        "FixedBuildName": null,
                        "ComponentIds": [3, 7],
                        "TestRunStepIds": [101, 102],
                        "ProjectId": 55,
                        "ProjectName": "Web Application",
                        "ProjectGuid": "mno-345",
                        "ArtifactTypeId": 3,
                        "ConcurrencyDate": "2024-01-16T14:30:00Z",
                        "CustomProperties": [],
                        "Tags": "mobile,critical,login",
                        "IsAttachments": true,
                        "Guid": "pqr-678"
                    }
                ]
            }

        Key Fields:
            - IncidentId: Unique identifier for the incident
            - Name: The name/title of the incident
            - Description: The detailed description of the incident
            - IncidentStatusId/IncidentStatusName: Current status of
                the incident
            - IncidentStatusOpenStatus: Whether the incident is in an
                open status (true) or closed (false)
            - IncidentTypeId/IncidentTypeName: Type of incident (Bug,
                Enhancement, Issue, etc.)
            - PriorityId/PriorityName: Priority level (1-Critical to
                5-Low)
            - SeverityId/SeverityName: Severity level (1-Critical to
                4-Low)
            - OwnerId/OwnerName/OwnerGuid: User the incident is
                assigned to
            - OpenerId/OpenerName/OpenerGuid: User who detected/reported
                the incident
            - EstimatedEffort: Original estimate in minutes to resolve
                the incident
            - ActualEffort: Time logged so far in minutes
                (increases as work progresses)
            - RemainingEffort: Developer's estimate of time remaining
                (updated manually)
            - ProjectedEffort: Calculated as ActualEffort + RemainingEffort
            - CompletionPercent: Calculated as
                (ActualEffort / ProjectedEffort) * 100
            - StartDate: When work started on the incident
            - EndDate: Scheduled completion date for the incident
            - ClosedDate: When the incident was closed (null if still open)
            - CreationDate: When the incident was originally created
            - LastUpdateDate: When the incident was last modified
            - DetectedReleaseId/DetectedReleaseVersionNumber/
                DetectedReleaseGuid: Release where the incident was found
            - ResolvedReleaseId/ResolvedReleaseVersionNumber/
                ResolvedReleaseGuid: Release where the incident will be
                fixed
            - VerifiedReleaseId/VerifiedReleaseVersionNumber/
                VerifiedReleaseGuid: Release where the fix was verified
                (null if not yet verified)
            - DetectedBuildId/DetectedBuildName: Build where the incident
                was detected
            - FixedBuildId/FixedBuildName: Build where the incident was
                fixed (null if not yet fixed)
            - ComponentIds: List of component IDs this incident belongs to
            - TestRunStepIds: List of test run step IDs that relate to
                this incident
            - ProjectId/ProjectName/ProjectGuid: Project the incident
                belongs to
            - ArtifactTypeId: Type of artifact (3 for incidents)
            - ConcurrencyDate: Timestamp for optimistic concurrency control
            - CustomProperties: List of custom fields for this incident
            - Tags: Meta-tags associated with the incident
            - IsAttachments: Whether the incident has attachments
            - Guid: Unique global identifier for the incident

        When to Use:
            - Getting incident list for a specific product
            - Retrieving incidents with server-side pagination
            - Sorting incidents by specific fields
            - Analyzing product-level incident data
            - Tracking bugs and issues in a product

        Related Tools:
            - get_my_incidents: Get incidents assigned to current user
                (with client-side pagination)
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
            # Get first 100 incidents from product 55
            incidents_json = get_incidents(product_id=55)
            incidents = json.loads(incidents_json)

            # Get next page of incidents
            incidents_json = get_incidents(
                product_id=55, start_row=101, number_rows=100
            )

            # Get incidents sorted by priority
            incidents_json = get_incidents(
                product_id=55, sort_by="PriorityId"
            )

            # Process and filter results
            incidents = json.loads(incidents_json)
            critical_incidents = [
                i for i in incidents["data"]
                if i["PriorityName"] == "1 - Critical"
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

            # Get Spira client and retrieve incidents
            spira_client = get_spira_client()
            return _get_incidents_impl(
                spira_client,
                product_id,
                start_row,
                number_rows,
                sort_by,
            )
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve incidents",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
