---
inclusion: manual
---

# Spira MCP Server: Tool Implementation Patterns

## Overview

This document provides copy-paste patterns for implementing common tool types in the Spira MCP server. Use these as templates when creating new tools.

---

## Pattern 1: Simple GET Tool (Retrieve Single Item)

**Use Case:** Get a single artifact by ID (task, incident, requirement, etc.)

```python
# File: src/mcp_server_spira/features/tasks/tools/read.py

import json
from mcp_server_spira.features.common import get_spira_client

def _get_task_by_id_impl(spira_client, product_id: int, task_id: int) -> str:
    """
    Implementation of retrieving a single task by ID.

    Args:
        spira_client: The Spira API client instance
        product_id: The numeric ID of the product
        task_id: The numeric ID of the task

    Returns:
        JSON string containing the task object
    """
    try:
        task = spira_client.make_spira_api_get_request(
            f"projects/{product_id}/tasks/{task_id}"
        )
        return json.dumps(task, indent=2)

    except Exception as e:
        return json.dumps({
            "error": "Failed to retrieve task",
            "task_id": task_id,
            "product_id": product_id,
            "details": str(e)
        })

def register_tools(mcp) -> None:
    """Register task read tools with the MCP server."""

    @mcp.tool()
    def get_task_by_id(product_id: int, task_id: int) -> str:
        """
        Retrieves a single task by its ID.

        Args:
            product_id: The numeric ID of the product (e.g., 55 for PR:55)
            task_id: The numeric ID of the task (e.g., 40 for TK:40)

        Returns:
            JSON object with complete task details including:
            - TaskId, Name, Description
            - TaskStatusName, TaskTypeName, TaskPriorityName
            - EstimatedEffort, ActualEffort, RemainingEffort
            - StartDate, EndDate, CompletionPercent

        Example Response:
            {
              "TaskId": 40,
              "Name": "Fix login bug",
              "TaskStatusName": "In Progress",
              "EstimatedEffort": 120,
              "ActualEffort": 60,
              "RemainingEffort": 60,
              "CompletionPercent": 50
            }
        """
        # Validate inputs
        if product_id <= 0:
            return json.dumps({
                "error": "Invalid product_id",
                "value": product_id,
                "requirement": "product_id must be positive"
            })

        if task_id <= 0:
            return json.dumps({
                "error": "Invalid task_id",
                "value": task_id,
                "requirement": "task_id must be positive"
            })

        try:
            spira_client = get_spira_client()
            return _get_task_by_id_impl(spira_client, product_id, task_id)
        except Exception as e:
            return json.dumps({"error": str(e)})
```

---

## Pattern 2: List Tool with Pagination

**Use Case:** Get a list of artifacts with pagination support

```python
# File: src/mcp_server_spira/features/tasks/tools/list.py

import json
from mcp_server_spira.features.common import get_spira_client

def _list_tasks_impl(
    spira_client,
    product_id: int,
    limit: int = 50,
    offset: int = 0
) -> str:
    """
    Implementation of listing tasks in a product.

    Args:
        spira_client: The Spira API client instance
        product_id: The numeric ID of the product
        limit: Maximum number of tasks to return
        offset: Number of tasks to skip

    Returns:
        JSON string containing array of task objects
    """
    try:
        # Get all tasks (API doesn't support pagination directly)
        all_tasks = spira_client.make_spira_api_get_request(
            f"projects/{product_id}/tasks"
        )

        # Apply pagination
        paginated_tasks = all_tasks[offset:offset + limit]

        # Return with metadata
        result = {
            "items": paginated_tasks,
            "total": len(all_tasks),
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < len(all_tasks)
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "error": "Failed to list tasks",
            "product_id": product_id,
            "details": str(e)
        })

def register_tools(mcp) -> None:
    """Register task list tools with the MCP server."""

    @mcp.tool()
    def list_tasks(
        product_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> str:
        """
        Retrieves a list of tasks in the specified product.

        Args:
            product_id: The numeric ID of the product (e.g., 55 for PR:55)
            limit: Maximum number of tasks to return (1-100). Default: 50
            offset: Number of tasks to skip for pagination. Default: 0

        Returns:
            JSON object with structure:
            {
              "items": [...],      // Array of task objects
              "total": 150,        // Total number of tasks
              "limit": 50,         // Requested limit
              "offset": 0,         // Requested offset
              "has_more": true     // Whether more results exist
            }

        Examples:
            - First page: list_tasks(product_id=55, limit=50, offset=0)
            - Second page: list_tasks(product_id=55, limit=50, offset=50)
            - Get all: list_tasks(product_id=55, limit=100, offset=0)
        """
        # Validate inputs
        if product_id <= 0:
            return json.dumps({"error": "product_id must be positive"})

        if limit < 1 or limit > 100:
            return json.dumps({"error": "limit must be between 1 and 100"})

        if offset < 0:
            return json.dumps({"error": "offset must be non-negative"})

        try:
            spira_client = get_spira_client()
            return _list_tasks_impl(spira_client, product_id, limit, offset)
        except Exception as e:
            return json.dumps({"error": str(e)})
```

---

## Pattern 3: Search Tool with Filters

**Use Case:** Search artifacts with multiple filter criteria

```python
# File: src/mcp_server_spira/features/tasks/tools/search.py

import json
from mcp_server_spira.features.common import get_spira_client

def _search_tasks_impl(
    spira_client,
    product_id: int,
    status_ids: list[int] | None = None,
    owner_id: int | None = None,
    priority_ids: list[int] | None = None,
    limit: int = 50,
    offset: int = 0
) -> str:
    """
    Implementation of searching tasks with filters.

    Args:
        spira_client: The Spira API client instance
        product_id: The numeric ID of the product
        status_ids: List of status IDs to filter by
        owner_id: Owner user ID to filter by
        priority_ids: List of priority IDs to filter by
        limit: Maximum number of results
        offset: Number of results to skip

    Returns:
        JSON string containing filtered task objects
    """
    try:
        # Build filter array
        filters = []

        if status_ids:
            filters.append({
                "PropertyName": "TaskStatusId",
                "MultiValue": {"Values": status_ids}
            })

        if owner_id:
            filters.append({
                "PropertyName": "OwnerId",
                "IntValue": owner_id
            })

        if priority_ids:
            filters.append({
                "PropertyName": "TaskPriorityId",
                "MultiValue": {"Values": priority_ids}
            })

        # Make search request
        url = f"projects/{product_id}/tasks/search?starting_row={offset}&number_of_rows={limit}"
        tasks = spira_client.make_spira_api_post_request(url, filters)

        return json.dumps(tasks, indent=2)

    except Exception as e:
        return json.dumps({
            "error": "Failed to search tasks",
            "product_id": product_id,
            "details": str(e)
        })

def register_tools(mcp) -> None:
    """Register task search tools with the MCP server."""

    @mcp.tool()
    def search_tasks(
        product_id: int,
        status_ids: list[int] | None = None,
        owner_id: int | None = None,
        priority_ids: list[int] | None = None,
        limit: int = 50,
        offset: int = 0
    ) -> str:
        """
        Searches for tasks matching the specified criteria.

        All filters are combined with AND logic. If no filters are provided,
        returns all tasks (subject to pagination).

        Args:
            product_id: The numeric ID of the product
            status_ids: Optional list of status IDs to filter by
            owner_id: Optional owner user ID to filter by
            priority_ids: Optional list of priority IDs to filter by
            limit: Maximum number of results (1-100). Default: 50
            offset: Number of results to skip. Default: 0

        Returns:
            JSON array of task objects matching the criteria

        Examples:
            - In-progress tasks: search_tasks(55, status_ids=[2])
            - My high-priority tasks: search_tasks(55, owner_id=10, priority_ids=[1])
            - All tasks: search_tasks(55)
        """
        # Validate inputs
        if product_id <= 0:
            return json.dumps({"error": "product_id must be positive"})

        if limit < 1 or limit > 100:
            return json.dumps({"error": "limit must be between 1 and 100"})

        if offset < 0:
            return json.dumps({"error": "offset must be non-negative"})

        try:
            spira_client = get_spira_client()
            return _search_tasks_impl(
                spira_client,
                product_id,
                status_ids,
                owner_id,
                priority_ids,
                limit,
                offset
            )
        except Exception as e:
            return json.dumps({"error": str(e)})
```

---

## Pattern 4: Create Tool (POST)

**Use Case:** Create a new artifact

```python
# File: src/mcp_server_spira/features/tasks/tools/create.py

import json
from mcp_server_spira.features.common import get_spira_client

def _create_task_impl(
    spira_client,
    product_id: int,
    name: str,
    description: str | None = None,
    owner_id: int | None = None,
    task_type_id: int | None = None,
    task_priority_id: int | None = None,
    estimated_effort: int | None = None
) -> str:
    """
    Implementation of creating a new task.

    Args:
        spira_client: The Spira API client instance
        product_id: The numeric ID of the product
        name: Task name (required)
        description: Task description (optional)
        owner_id: User ID to assign task to (optional)
        task_type_id: Task type ID (optional, uses default if not provided)
        task_priority_id: Priority ID (optional, uses default if not provided)
        estimated_effort: Estimated effort in minutes (optional)

    Returns:
        JSON string containing the created task with its new TaskId
    """
    try:
        # Build task object
        task_data = {
            "Name": name,
            "Description": description,
            "OwnerId": owner_id,
            "TaskTypeId": task_type_id,
            "TaskPriorityId": task_priority_id,
            "EstimatedEffort": estimated_effort
        }

        # Remove None values
        task_data = {k: v for k, v in task_data.items() if v is not None}

        # Create task
        created_task = spira_client.make_spira_api_post_request(
            f"projects/{product_id}/tasks",
            task_data
        )

        return json.dumps(created_task, indent=2)

    except Exception as e:
        return json.dumps({
            "error": "Failed to create task",
            "product_id": product_id,
            "details": str(e)
        })

def register_tools(mcp) -> None:
    """Register task create tools with the MCP server."""

    @mcp.tool()
    def create_task(
        product_id: int,
        name: str,
        description: str | None = None,
        owner_id: int | None = None,
        task_type_id: int | None = None,
        task_priority_id: int | None = None,
        estimated_effort: int | None = None
    ) -> str:
        """
        Creates a new task in the specified product.

        Args:
            product_id: The numeric ID of the product
            name: Task name (required, max 255 characters)
            description: Task description (optional, supports HTML)
            owner_id: User ID to assign task to (optional)
            task_type_id: Task type ID (optional, uses default if omitted)
            task_priority_id: Priority ID (optional, uses default if omitted)
            estimated_effort: Estimated effort in minutes (optional)

        Returns:
            JSON object with the created task including its new TaskId

        Example:
            create_task(
                product_id=55,
                name="Fix login bug",
                description="Users cannot login with special characters",
                owner_id=10,
                estimated_effort=120
            )
        """
        # Validate required inputs
        if product_id <= 0:
            return json.dumps({"error": "product_id must be positive"})

        if not name or not name.strip():
            return json.dumps({"error": "name is required and cannot be empty"})

        if len(name) > 255:
            return json.dumps({"error": "name cannot exceed 255 characters"})

        # Validate optional inputs
        if owner_id is not None and owner_id <= 0:
            return json.dumps({"error": "owner_id must be positive if provided"})

        if estimated_effort is not None and estimated_effort < 0:
            return json.dumps({"error": "estimated_effort cannot be negative"})

        try:
            spira_client = get_spira_client()
            return _create_task_impl(
                spira_client,
                product_id,
                name,
                description,
                owner_id,
                task_type_id,
                task_priority_id,
                estimated_effort
            )
        except Exception as e:
            return json.dumps({"error": str(e)})
```

---

## Pattern 5: Update Tool (PUT)

**Use Case:** Update an existing artifact

```python
# File: src/mcp_server_spira/features/tasks/tools/update.py

import json
from mcp_server_spira.features.common import get_spira_client

def _update_task_impl(
    spira_client,
    product_id: int,
    task_id: int,
    name: str | None = None,
    description: str | None = None,
    task_status_id: int | None = None,
    owner_id: int | None = None
) -> str:
    """
    Implementation of updating a task.

    Args:
        spira_client: The Spira API client instance
        product_id: The numeric ID of the product
        task_id: The numeric ID of the task to update
        name: New task name (optional)
        description: New description (optional)
        task_status_id: New status ID (optional)
        owner_id: New owner ID (optional)

    Returns:
        JSON string containing the updated task
    """
    try:
        # First, get the existing task
        existing_task = spira_client.make_spira_api_get_request(
            f"projects/{product_id}/tasks/{task_id}"
        )

        # Update only provided fields
        if name is not None:
            existing_task['Name'] = name
        if description is not None:
            existing_task['Description'] = description
        if task_status_id is not None:
            existing_task['TaskStatusId'] = task_status_id
        if owner_id is not None:
            existing_task['OwnerId'] = owner_id

        # Update the task
        updated_task = spira_client.make_spira_api_put_request(
            f"projects/{product_id}/tasks",
            existing_task
        )

        return json.dumps(updated_task, indent=2)

    except Exception as e:
        return json.dumps({
            "error": "Failed to update task",
            "task_id": task_id,
            "product_id": product_id,
            "details": str(e)
        })

def register_tools(mcp) -> None:
    """Register task update tools with the MCP server."""

    @mcp.tool()
    def update_task(
        product_id: int,
        task_id: int,
        name: str | None = None,
        description: str | None = None,
        task_status_id: int | None = None,
        owner_id: int | None = None
    ) -> str:
        """
        Updates an existing task. Only provided fields are updated.

        Args:
            product_id: The numeric ID of the product
            task_id: The numeric ID of the task to update
            name: New task name (optional)
            description: New description (optional)
            task_status_id: New status ID (optional)
            owner_id: New owner user ID (optional)

        Returns:
            JSON object with the updated task

        Example:
            update_task(
                product_id=55,
                task_id=40,
                task_status_id=3,  # Mark as completed
                description="Fixed by updating authentication logic"
            )
        """
        # Validate required inputs
        if product_id <= 0:
            return json.dumps({"error": "product_id must be positive"})

        if task_id <= 0:
            return json.dumps({"error": "task_id must be positive"})

        # Ensure at least one field is being updated
        if all(v is None for v in [name, description, task_status_id, owner_id]):
            return json.dumps({
                "error": "At least one field must be provided for update"
            })

        try:
            spira_client = get_spira_client()
            return _update_task_impl(
                spira_client,
                product_id,
                task_id,
                name,
                description,
                task_status_id,
                owner_id
            )
        except Exception as e:
            return json.dumps({"error": str(e)})
```

---

## Pattern 6: Delete Tool (DELETE)

**Use Case:** Delete an artifact

```python
# File: src/mcp_server_spira/features/tasks/tools/delete.py

import json
from mcp_server_spira.features.common import get_spira_client

def _delete_task_impl(spira_client, product_id: int, task_id: int) -> str:
    """
    Implementation of deleting a task.

    Args:
        spira_client: The Spira API client instance
        product_id: The numeric ID of the product
        task_id: The numeric ID of the task to delete

    Returns:
        JSON string with success status
    """
    try:
        spira_client.make_spira_api_delete_request(
            f"projects/{product_id}/tasks/{task_id}"
        )

        return json.dumps({
            "success": True,
            "message": "Task deleted successfully",
            "task_id": task_id,
            "product_id": product_id
        })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": "Failed to delete task",
            "task_id": task_id,
            "product_id": product_id,
            "details": str(e)
        })

def register_tools(mcp) -> None:
    """Register task delete tools with the MCP server."""

    @mcp.tool()
    def delete_task(product_id: int, task_id: int) -> str:
        """
        Deletes a task from the specified product.

        WARNING: This operation cannot be undone.

        Args:
            product_id: The numeric ID of the product
            task_id: The numeric ID of the task to delete

        Returns:
            JSON object with success status:
            {
              "success": true,
              "message": "Task deleted successfully",
              "task_id": 40,
              "product_id": 55
            }

        Example:
            delete_task(product_id=55, task_id=40)
        """
        # Validate inputs
        if product_id <= 0:
            return json.dumps({"error": "product_id must be positive"})

        if task_id <= 0:
            return json.dumps({"error": "task_id must be positive"})

        try:
            spira_client = get_spira_client()
            return _delete_task_impl(spira_client, product_id, task_id)
        except Exception as e:
            return json.dumps({"error": str(e)})
```

---

## Quick Reference

| Operation | HTTP Method | Pattern | Example Endpoint |
|-----------|-------------|---------|------------------|
| Get single item | GET | Pattern 1 | `/projects/55/tasks/40` |
| List items | GET | Pattern 2 | `/projects/55/tasks` |
| Search/filter | POST | Pattern 3 | `/projects/55/tasks/search` |
| Create item | POST | Pattern 4 | `/projects/55/tasks` |
| Update item | PUT | Pattern 5 | `/projects/55/tasks` |
| Delete item | DELETE | Pattern 6 | `/projects/55/tasks/40` |

## Common Validation Rules

```python
# Positive integer IDs
if id_value <= 0:
    return json.dumps({"error": "id must be positive"})

# Non-empty strings
if not string_value or not string_value.strip():
    return json.dumps({"error": "value cannot be empty"})

# String length limits
if len(string_value) > max_length:
    return json.dumps({"error": f"value cannot exceed {max_length} characters"})

# Pagination limits
if limit < 1 or limit > 100:
    return json.dumps({"error": "limit must be between 1 and 100"})

if offset < 0:
    return json.dumps({"error": "offset must be non-negative"})

# List not empty
if required_list is not None and len(required_list) == 0:
    return json.dumps({"error": "list cannot be empty"})
```

## Testing Template

```python
# tests/features/tasks/test_read.py

import json
from unittest.mock import Mock, patch
from mcp_server_spira.features.tasks.tools.read import _get_task_by_id_impl

def test_get_task_by_id_success():
    """Test successful task retrieval."""
    # Mock client
    mock_client = Mock()
    mock_client.make_spira_api_get_request.return_value = {
        "TaskId": 40,
        "Name": "Test Task",
        "TaskStatusName": "In Progress"
    }

    # Call implementation
    result = _get_task_by_id_impl(mock_client, 55, 40)

    # Verify
    result_data = json.loads(result)
    assert result_data["TaskId"] == 40
    assert result_data["Name"] == "Test Task"
    mock_client.make_spira_api_get_request.assert_called_once_with(
        "projects/55/tasks/40"
    )

def test_get_task_by_id_not_found():
    """Test task not found error."""
    # Mock client to raise exception
    mock_client = Mock()
    mock_client.make_spira_api_get_request.side_effect = Exception("404 Not Found")

    # Call implementation
    result = _get_task_by_id_impl(mock_client, 55, 999)

    # Verify error response
    result_data = json.loads(result)
    assert "error" in result_data
    assert result_data["task_id"] == 999
```
