"""
Provides operations for working with the Spira product tasks

This module provides MCP tools for retrieving and updating product tasks
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _get_tasks_impl(
    spira_client,
    product_id: int,
    starting_row: int = 1,
    number_of_rows: int = 100,
    sort_field: str = "",
    sort_direction: str = "ASC",
) -> str:
    """
    Implementation of retrieving the list of tasks in the specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product.
            If the ID is PR:45, just use 45.
        starting_row: The starting row number for pagination (1-based index)
        number_of_rows: The number of rows to return
        sort_field: The field to sort by (optional)
        sort_direction: The sort direction - "ASC" or "DESC"

    Returns:
        JSON string containing the list of tasks with data structure
    """
    try:
        # Build the search endpoint URL with query parameters
        tasks_url = (
            f"projects/{product_id}/tasks/search?"
            f"starting_row={starting_row}&number_of_rows={number_of_rows}"
        )

        # Add optional sort parameters if provided
        if sort_field:
            tasks_url += f"&sort_field={sort_field}&sort_direction={sort_direction}"

        # Make POST request with empty filter array (no filtering for now)
        tasks = spira_client.make_spira_api_post_request(tasks_url, [])

        # Return JSON response with data structure
        return format_success_response(data=tasks)

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve tasks",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e), "product_id": product_id},
            suggestion=("Check API connectivity, authentication, and that the product_id is valid"),
        )


def register_tools(mcp) -> None:
    """
    Register product tasks tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_tasks(
        product_id: int,
        starting_row: int = 1,
        number_of_rows: int = 100,
        sort_field: str = "",
        sort_direction: str = "ASC",
    ) -> str:
        """
        Retrieves a list of the tasks in the specified product

        Maps to Spira API: POST /projects/{product_id}/tasks/search

        This tool returns tasks from the specified product using
        server-side pagination. Use this for retrieving product-level
        task lists with filtering and sorting capabilities.

        **API Endpoint**: POST /projects/{product_id}/tasks/search
        **Query Parameters**: starting_row, number_of_rows, sort_field,
            sort_direction
        **Request Body**: [] (empty RemoteFilter array - no filtering
            for now)

        **Note**: This endpoint uses server-side pagination. The API
        returns only the requested page of results. A dedicated filter
        tool will be added in a future milestone.

        Args:
            product_id: The numeric ID of the product.
                If the ID is PR:45, just use 45.
            starting_row: The starting row number for pagination
                (default: 1, 1-based index)
            number_of_rows: The number of rows to return (default: 100)
            sort_field: The field to sort by (optional, e.g., "TaskId",
                "Name", "TaskStatusName")
            sort_direction: The sort direction - "ASC" or "DESC"
                (default: "ASC")

        Returns:
            JSON string with structure:
            {
                "data": [
                    {
                        "TaskId": 123,
                        "Name": "Fix login bug",
                        "Description": "Users cannot log in with
                            special characters",
                        "TaskStatusId": 2,
                        "TaskStatusName": "In Progress",
                        "TaskTypeId": 1,
                        "TaskTypeName": "Development",
                        "TaskPriorityId": 1,
                        "TaskPriorityName": "Critical",
                        "OwnerId": 5,
                        "OwnerName": "John Doe",
                        "CreatorId": 4,
                        "RequirementId": 45,
                        "RequirementName": "User Authentication",
                        "ReleaseId": 10,
                        "ReleaseVersionNumber": "1.5.0",
                        "ComponentId": 3,
                        "EstimatedEffort": 120,
                        "ActualEffort": 60,
                        "RemainingEffort": 60,
                        "ProjectedEffort": 120,
                        "CompletionPercent": 50,
                        "StartDate": "2024-01-15T09:00:00Z",
                        "EndDate": "2024-01-16T17:00:00Z",
                        "CreationDate": "2024-01-10T08:00:00Z",
                        "LastUpdateDate": "2024-01-15T14:30:00Z",
                        "ProjectId": 55,
                        "ProjectName": "Web Application",
                        "TaskFolderId": null,
                        "CustomProperties": [],
                        "Tags": "bug,security",
                        "IsAttachments": false,
                        "Guid": "abc-123-def-456"
                    }
                ]
            }

        Key Fields:
            - TaskId: Unique identifier for the task
            - Name: The name of the task
            - Description: The detailed description of the task
            - TaskStatusId/TaskStatusName: Current status of the task
            - TaskTypeId/TaskTypeName: Type of task (null for default)
            - TaskPriorityId/TaskPriorityName: Priority level of the task
            - OwnerId/OwnerName: User the task is assigned to
            - CreatorId: User who created the task
            - RequirementId/RequirementName: Parent requirement link
            - ReleaseId/ReleaseVersionNumber: Sprint/iteration assignment
            - ComponentId: Component the task belongs to (null if none)
            - EstimatedEffort: Original estimate in minutes
                (set at task creation)
            - ActualEffort: Time logged so far in minutes
                (increases as work progresses)
            - RemainingEffort: Developer's estimate of time remaining
                (updated manually)
            - ProjectedEffort: Calculated as ActualEffort + RemainingEffort
            - CompletionPercent: Calculated as
                (ActualEffort / ProjectedEffort) * 100
            - StartDate: Scheduled start date for the task
            - EndDate: Scheduled end date for the task
            - CreationDate: When the task was originally created
            - LastUpdateDate: When the task was last modified
            - ProjectId/ProjectName: Project the task belongs to
            - TaskFolderId: Folder the task is stored in (null for root)
            - CustomProperties: List of custom fields for this task
            - Tags: Meta-tags associated with the task
            - IsAttachments: Whether the task has attachments
            - Guid: Unique global identifier for the task

        When to Use:
            - Getting task list for a specific product
            - Retrieving tasks with server-side pagination
            - Sorting tasks by specific fields
            - Analyzing product-level task data

        Related Tools:
            - get_my_tasks: Get tasks assigned to current user
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
            # Get first 100 tasks from product 55
            tasks_json = get_tasks(product_id=55)
            tasks = json.loads(tasks_json)

            # Get next page of tasks
            tasks_json = get_tasks(
                product_id=55, starting_row=101, number_of_rows=100
            )

            # Get tasks sorted by priority
            tasks_json = get_tasks(
                product_id=55,
                sort_field="TaskPriorityId",
                sort_direction="ASC"
            )

            # Process and filter results
            tasks = json.loads(tasks_json)
            critical_tasks = [
                t for t in tasks["data"]
                if t["TaskPriorityName"] == "Critical"
            ]
        """
        try:
            # Validate product_id
            validation_error = ParameterValidator.validate_positive_integer(
                product_id, "product_id", min_value=1
            )
            if validation_error:
                return format_error_response(**validation_error)

            # Validate starting_row
            validation_error = ParameterValidator.validate_positive_integer(
                starting_row, "starting_row", min_value=1
            )
            if validation_error:
                return format_error_response(**validation_error)

            # Validate number_of_rows
            validation_error = ParameterValidator.validate_positive_integer(
                number_of_rows, "number_of_rows", min_value=1
            )
            if validation_error:
                return format_error_response(**validation_error)

            # Get Spira client and retrieve tasks
            spira_client = get_spira_client()
            return _get_tasks_impl(
                spira_client,
                product_id,
                starting_row,
                number_of_rows,
                sort_field,
                sort_direction,
            )
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve tasks",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
