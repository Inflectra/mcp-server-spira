"""
Provides operations for working with the Spira tasks I have been assigned

This module provides MCP tools for retrieving and updating my assigned tasks.
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.pagination import paginate_client_side
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _get_my_tasks_impl(spira_client, limit: int, offset: int) -> str:
    """
    Implementation of retrieving my assigned Spira tasks.

    Args:
        spira_client: The Inflectra Spira API client instance
        limit: Maximum number of tasks to return
        offset: Number of tasks to skip

    Returns:
        JSON string with paginated task data
    """
    try:
        # Validate pagination parameters
        validation_error = ParameterValidator.validate_pagination_params(limit, offset)
        if validation_error:
            return format_error_response(**validation_error)

        # Get the list of open tasks for the current user
        tasks_url = "tasks"
        all_tasks = spira_client.make_spira_api_get_request(tasks_url)

        # Handle empty results
        if not all_tasks:
            all_tasks = []

        # Apply client-side pagination
        result = paginate_client_side(all_tasks, limit, offset)

        # Return formatted JSON response
        return format_success_response(data=result["data"], pagination=dict(result["pagination"]))

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve tasks",
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
    def get_my_tasks(limit: int = 25, offset: int = 0) -> str:
        """
        Retrieves tasks assigned to the current user.

        Maps to Spira API: GET /tasks

        This tool returns tasks where the current user is the Owner
        (assigned to). Use this for personal task lists, daily standup
        reports, or workload analysis.

        **Pagination:** This endpoint uses CLIENT-SIDE pagination. The API
        returns all tasks, and we slice the results in Python. This is
        acceptable for "my work" queries which typically return < 500 items.
        For large result sets, consider using project-level queries with
        server-side pagination (available in Milestone 2+).

        **For Display:** Modern LLMs can format JSON naturally for simple
        display. For complex workflows where you've filtered or processed
        the data, use format_artifacts_as_markdown() to ensure consistent
        formatting.

        Args:
            limit: Maximum number of tasks to return (1-500, default: 25)
                Controls result set size for pagination.
            offset: Number of tasks to skip (>= 0, default: 0)
                Used for retrieving subsequent pages of results.

        Returns:
            JSON string with structure:
            {
                "data": [
                    {
                        "TaskId": 123,
                        "Name": "Fix login bug",
                        "Description": "Users cannot log in with special
                            characters",
                        "TaskStatusId": 2,
                        "TaskStatusName": "In Progress",
                        "TaskTypeId": 1,
                        "TaskTypeName": "Development",
                        "TaskPriorityId": 1,
                        "TaskPriorityName": "Critical",
                        "OwnerId": 5,
                        "OwnerName": "John Doe",
                        "EstimatedEffort": 120,
                        "ActualEffort": 60,
                        "RemainingEffort": 60,
                        "ProjectedEffort": 120,
                        "CompletionPercent": 50,
                        "StartDate": "2024-01-15T09:00:00Z",
                        "EndDate": "2024-01-16T17:00:00Z",
                        "CreationDate": "2024-01-10T08:00:00Z",
                        "LastUpdateDate": "2024-01-15T14:30:00Z",
                        "ReleaseId": 10,
                        "ReleaseVersionNumber": "1.5.0",
                        "RequirementId": 45,
                        "RequirementName": "User Authentication",
                        "ProjectId": 55,
                        "ProjectName": "Web Application",
                        "ComponentId": 3,
                        "CreatorId": 4,
                        "TaskFolderId": null,
                        "CustomProperties": [],
                        "Tags": "bug,security",
                        "IsAttachments": false
                    }
                ],
                "pagination": {
                    "limit": 25,
                    "offset": 0,
                    "returned_count": 25,
                    "total_count": 150,
                    "has_more": true,
                    "pagination_type": "client-side"
                }
            }

        Key Fields:
            - TaskId: Unique identifier for the task
            - Name: The name of the task
            - Description: The detailed description of the task
            - TaskStatusId/TaskStatusName: Current status of the task
            - TaskTypeId/TaskTypeName: Type of task (null for default)
            - TaskPriorityId/TaskPriorityName: Priority level of the task
            - OwnerId/OwnerName: User the task is assigned to
            - EstimatedEffort: Original estimate in minutes (set at task
                creation)
            - ActualEffort: Time logged so far in minutes (increases as
                work progresses)
            - RemainingEffort: Developer's estimate of time remaining
                (updated manually)
            - ProjectedEffort: Calculated as ActualEffort + RemainingEffort
            - CompletionPercent: Calculated as (ActualEffort /
                ProjectedEffort) * 100
            - StartDate: Scheduled start date for the task
            - EndDate: Scheduled end date for the task
            - CreationDate: When the task was originally created
            - LastUpdateDate: When the task was last modified
            - ReleaseId/ReleaseVersionNumber: Sprint/iteration assignment
            - RequirementId/RequirementName: Parent requirement link
            - ProjectId/ProjectName: Project the task belongs to
            - ComponentId: Component the task belongs to (null if none)
            - CreatorId: User who created the task
            - TaskFolderId: Folder the task is stored in (null for root)
            - CustomProperties: List of custom fields for this task
            - Tags: Meta-tags associated with the task
            - IsAttachments: Whether the task has attachments

        When to Use:
            - Getting personal task list for current user
            - Generating daily standup reports
            - Analyzing personal workload
            - Finding tasks by status or priority (filter the JSON)

        Related Tools:
            - format_artifacts_as_markdown: Format filtered/processed
                results for display
            - get_task_by_id: Get single task with full details (future)
            - search_tasks: Advanced filtering across all tasks (future)

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
            tasks_json = get_my_tasks()
            # LLM can format this JSON for display without additional tools

            # Pagination - Get next page
            tasks_json = get_my_tasks(limit=25, offset=25)

            # Complex workflow - Use formatting tool for filtered results
            tasks_json = get_my_tasks(limit=100)
            tasks = json.loads(tasks_json)
            late_tasks = [t for t in tasks["data"]
                          if is_late(t["EndDate"])]
            late_json = json.dumps({"data": late_tasks})
            readable = format_artifacts_as_markdown(late_json, "task")
        """
        try:
            # Validate pagination parameters
            validation_error = ParameterValidator.validate_pagination_params(limit, offset)
            if validation_error:
                return format_error_response(**validation_error)

            # Get Spira client
            spira_client = get_spira_client()

            # Retrieve and paginate tasks
            return _get_my_tasks_impl(spira_client, limit, offset)

        except Exception as e:
            return format_error_response(
                error="Failed to retrieve tasks",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
