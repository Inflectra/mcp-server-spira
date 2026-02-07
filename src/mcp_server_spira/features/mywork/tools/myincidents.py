"""
Provides operations for working with the Spira incidents I have been assigned

This module provides MCP tools for retrieving and updating my assigned
incidents.
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.pagination import paginate_client_side
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _get_my_incidents_impl(spira_client, limit: int, offset: int) -> str:
    """
    Implementation of retrieving my assigned Spira incidents.

    Args:
        spira_client: The Inflectra Spira API client instance
        limit: Maximum number of incidents to return
        offset: Number of incidents to skip

    Returns:
        JSON string with paginated incident data
    """
    try:
        # Get the list of open incidents for the current user
        incidents_url = "incidents"
        all_incidents = spira_client.make_spira_api_get_request(incidents_url)

        # Handle empty results
        if not all_incidents:
            all_incidents = []

        # Apply client-side pagination
        result = paginate_client_side(all_incidents, limit, offset)

        # Return formatted JSON response
        return format_success_response(data=result["data"], pagination=dict(result["pagination"]))

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve incidents",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e)},
            suggestion="Check API connectivity and authentication",
        )


def register_tools(mcp) -> None:
    """
    Register my work tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_my_incidents(limit: int = 25, offset: int = 0) -> str:
        """
        Retrieves incidents assigned to the current user.

        Maps to Spira API: GET /incidents

        This tool returns incidents where the current user is the Owner
        (assigned to). Use this for personal incident lists, bug tracking,
        or issue management.

        **Pagination:** This endpoint uses CLIENT-SIDE pagination. The API
        returns all incidents, and we slice the results in Python. This is
        acceptable for "my work" queries which typically return < 500 items.
        For large result sets, consider using project-level queries with
        server-side pagination (available in Milestone 2+).

        **For Display:** Modern LLMs can format JSON naturally for simple
        display. For complex workflows where you've filtered or processed
        the data, use format_artifacts_as_markdown() to ensure consistent
        formatting.

        Args:
            limit: Maximum number of incidents to return (1-500, default: 25)
                Controls result set size for pagination.
            offset: Number of incidents to skip (>= 0, default: 0)
                Used for retrieving subsequent pages of results.

        Returns:
            JSON string with structure:
            {
                "data": [
                    {
                        "IncidentId": 456,
                        "Name": "Login page crashes on mobile",
                        "Description": "The login page crashes when accessed
                            from mobile devices",
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
                ],
                "pagination": {
                    "limit": 25,
                    "offset": 0,
                    "returned_count": 25,
                    "total_count": 87,
                    "has_more": true,
                    "pagination_type": "client-side"
                }
            }

        Key Fields:
            - IncidentId: Unique identifier for the incident
            - Name: The name/title of the incident
            - Description: The detailed description of the incident
            - IncidentStatusId/IncidentStatusName: Current status of the
                incident
            - IncidentStatusOpenStatus: Whether the incident is in an open
                status (true) or closed (false)
            - IncidentTypeId/IncidentTypeName: Type of incident (Bug,
                Enhancement, Issue, etc.)
            - PriorityId/PriorityName: Priority level (1-Critical to
                5-Low)
            - SeverityId/SeverityName: Severity level (1-Critical to
                4-Low)
            - OwnerId/OwnerName/OwnerGuid: User the incident is assigned to
            - OpenerId/OpenerName/OpenerGuid: User who detected/reported
                the incident
            - EstimatedEffort: Original estimate in minutes to resolve the
                incident
            - ActualEffort: Time logged so far in minutes (increases as
                work progresses)
            - RemainingEffort: Developer's estimate of time remaining
                (updated manually)
            - ProjectedEffort: Calculated as ActualEffort + RemainingEffort
            - CompletionPercent: Calculated as (ActualEffort /
                ProjectedEffort) * 100
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
            - Getting personal incident list for current user
            - Tracking bugs and issues assigned to you
            - Analyzing incident workload
            - Finding incidents by status, priority, or severity (filter
                the JSON)

        Related Tools:
            - format_artifacts_as_markdown: Format filtered/processed
                results for display
            - get_incident_by_id: Get single incident with full details
                (future)
            - search_incidents: Advanced filtering across all incidents
                (future)

        Error Responses:
            {
                "error": "Invalid pagination parameters",
                "error_code": "INVALID_PARAMETER",
                "details": {
                    "parameter": "limit",
                    "value": 1000,
                    "expected": "1-500"
                },
                "suggestion": "Use limit between 1 and 500"
            }

        Example Usage:
            # Simple display - LLM formats naturally
            incidents_json = get_my_incidents()
            # LLM can format this JSON for display without additional tools

            # Pagination - Get next page
            incidents_json = get_my_incidents(limit=25, offset=25)

            # Complex workflow - Use formatting tool for filtered results
            incidents_json = get_my_incidents(limit=100)
            incidents = json.loads(incidents_json)
            critical = [i for i in incidents["data"]
                        if i["PriorityName"] == "1 - Critical"]
            critical_json = json.dumps({"data": critical})
            readable = format_artifacts_as_markdown(critical_json,
                                                     "incident")
        """
        try:
            # Validate pagination parameters
            validation_error = ParameterValidator.validate_pagination_params(limit, offset)
            if validation_error:
                return format_error_response(**validation_error)

            # Get Spira client
            spira_client = get_spira_client()

            # Retrieve and paginate incidents
            return _get_my_incidents_impl(spira_client, limit, offset)

        except Exception as e:
            return format_error_response(
                error="Failed to retrieve incidents",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
