---
inclusion: manual
---

# Phase 1: Core Improvements - Implementation Guide

## Phase Overview

**Goal:** Fix fundamental issues in existing tools to establish a solid foundation.

**Duration:** 2 weeks

**Focus Areas:**
1. Convert markdown output to JSON
2. Add proper pagination
3. Improve error handling
4. Add input validation
5. Fix tool descriptions
6. Clean up specification outputs

## Success Criteria

- ✅ All tools return structured JSON (not markdown)
- ✅ All list operations support `limit` and `offset` parameters
- ✅ All tools have specific error messages
- ✅ All tools validate inputs before API calls
- ✅ All tool docstrings accurately describe functionality
- ✅ No HTML tags in specification outputs

## Task Breakdown

### Task 1: Convert Tools to Return JSON

**Affected Files:**
- `src/mcp_server_spira/features/mywork/tools/*.py`
- `src/mcp_server_spira/features/productartifacts/tools/*.py`
- `src/mcp_server_spira/features/workspaces/tools/*.py`

**Pattern to Follow:**

**BEFORE (Markdown):**
```python
def _get_my_tasks_impl(spira_client) -> str:
    tasks = spira_client.make_spira_api_get_request("tasks")
    formatted_results = []
    for task in tasks[:25]:
        task_info = format_task(task)  # Returns markdown
        formatted_results.append(task_info)
    return "\n\n".join(formatted_results)
```

**AFTER (JSON):**
```python
def _get_my_tasks_impl(spira_client, limit: int = 25, offset: int = 0) -> str:
    tasks = spira_client.make_spira_api_get_request("tasks")

    # Apply pagination
    paginated_tasks = tasks[offset:offset + limit]

    # Return as JSON
    return json.dumps(paginated_tasks, indent=2)
```

**Steps:**
1. Remove calls to `format_*()` functions
2. Remove markdown string concatenation
3. Add `import json` at top of file
4. Return `json.dumps(data, indent=2)`
5. Update docstring to reflect JSON return type

### Task 2: Add Pagination Parameters

**Pattern to Follow:**

```python
@mcp.tool()
def get_my_tasks(
    status_filter: str | None = None,
    limit: int = 25,
    offset: int = 0
) -> str:
    """
    Retrieves tasks assigned to the current user.

    Args:
        status_filter: Optional status name to filter by
        limit: Maximum number of tasks to return (1-100). Default: 25
        offset: Number of tasks to skip for pagination. Default: 0

    Returns:
        JSON array of task objects

    Examples:
        - First page: get_my_tasks(limit=25, offset=0)
        - Second page: get_my_tasks(limit=25, offset=25)
        - All in-progress: get_my_tasks(status_filter="In Progress", limit=100)
    """
    # Validate pagination params
    if limit < 1 or limit > 100:
        return json.dumps({"error": "limit must be between 1 and 100"})
    if offset < 0:
        return json.dumps({"error": "offset must be non-negative"})

    try:
        spira_client = get_spira_client()
        return _get_my_tasks_impl(spira_client, status_filter, limit, offset)
    except Exception as e:
        return json.dumps({"error": str(e)})
```

**Steps:**
1. Add `limit` and `offset` parameters to tool function
2. Add validation for these parameters
3. Pass parameters to implementation function
4. Update implementation to use parameters
5. Update docstring with pagination examples

### Task 3: Improve Error Handling

**Pattern to Follow:**

```python
def _get_task_by_id_impl(spira_client, product_id: int, task_id: int) -> str:
    try:
        task = spira_client.make_spira_api_get_request(
            f"projects/{product_id}/tasks/{task_id}"
        )
        return json.dumps(task, indent=2)

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return json.dumps({
                "error": "Task not found",
                "task_id": task_id,
                "product_id": product_id,
                "suggestion": "Verify the task ID and product ID are correct"
            })
        elif e.response.status_code == 403:
            return json.dumps({
                "error": "Permission denied",
                "task_id": task_id,
                "product_id": product_id,
                "suggestion": "You may not have permission to view this task"
            })
        else:
            return json.dumps({
                "error": f"API error: {e.response.status_code}",
                "details": str(e)
            })

    except Exception as e:
        return json.dumps({
            "error": "Unexpected error",
            "details": str(e)
        })
```

**Steps:**
1. Replace generic `except Exception` with specific exceptions
2. Return structured JSON error objects
3. Include relevant context (IDs, parameters)
4. Add helpful suggestions when possible
5. Distinguish between different error types (404, 403, 500, etc.)

### Task 4: Add Input Validation

**Pattern to Follow:**

```python
@mcp.tool()
def get_task_by_id(product_id: int, task_id: int) -> str:
    """Get a specific task by ID."""

    # Validate product_id
    if product_id <= 0:
        return json.dumps({
            "error": "Invalid product_id",
            "value": product_id,
            "requirement": "product_id must be a positive integer"
        })

    # Validate task_id
    if task_id <= 0:
        return json.dumps({
            "error": "Invalid task_id",
            "value": task_id,
            "requirement": "task_id must be a positive integer"
        })

    try:
        spira_client = get_spira_client()
        return _get_task_by_id_impl(spira_client, product_id, task_id)
    except Exception as e:
        return json.dumps({"error": str(e)})
```

**Common Validations:**
- IDs must be positive integers
- Strings must not be empty
- Dates must be valid ISO format
- Enums must be valid values
- Lists must not be empty when required

### Task 5: Fix Tool Descriptions

**Pattern to Follow:**

**BEFORE (Inaccurate):**
```python
@mcp.tool()
def get_my_tasks() -> str:
    """
    Retrieves a list of the open tasks that are assigned to me

    Use this tool when you need to:
    - View the complete details of a specific task  # ← No task_id param!
    - Examine the current state, assigned user, and other properties
    - Get information about multiple tasks at once
    """
```

**AFTER (Accurate):**
```python
@mcp.tool()
def get_my_tasks(
    status_filter: str | None = None,
    limit: int = 25,
    offset: int = 0
) -> str:
    """
    Retrieves tasks assigned to the current authenticated user.

    This tool returns YOUR assigned tasks from Spira as JSON.
    Tasks are sorted by due date (earliest first).

    Args:
        status_filter: Optional status to filter by (e.g., "In Progress", "Not Started")
        limit: Maximum number of tasks to return (1-100). Default: 25
        offset: Number of tasks to skip for pagination. Default: 0

    Returns:
        JSON array of task objects with fields:
        - TaskId (int): Unique task identifier
        - Name (string): Task name
        - TaskStatusName (string): Current status
        - EstimatedEffort (int): Estimated minutes
        - ActualEffort (int): Actual minutes spent
        - EndDate (string): Due date in ISO format

    Examples:
        - Get first 25 tasks: get_my_tasks()
        - Get in-progress tasks: get_my_tasks(status_filter="In Progress")
        - Get next page: get_my_tasks(limit=25, offset=25)
    """
```

**Steps:**
1. Remove generic "Use this tool when" bullets
2. Describe exactly what the tool does
3. Document all parameters with types and defaults
4. Document return value structure
5. Provide concrete usage examples

### Task 6: Clean Up Specification Outputs

**Problem:** Specification tools return HTML mixed with markdown.

**File:** `src/mcp_server_spira/features/specifications/tools/productspecification.py`

**Pattern to Follow:**

```python
def _clean_html_from_text(text: str) -> str:
    """
    Remove HTML tags and convert to clean markdown.

    Args:
        text: Text that may contain HTML

    Returns:
        Clean markdown text
    """
    if not text:
        return ""

    # Remove HTML tags
    import re
    text = re.sub(r'<[^>]+>', '', text)

    # Decode HTML entities
    import html
    text = html.unescape(text)

    return text.strip()

def _add_requirement_scenarios(spira_client, product_id: int, requirement_id: int, formatted_specification: list[str]):
    """Gets scenarios and adds them to output."""
    scenarios_url = f"projects/{product_id}/requirements/{requirement_id}/steps"
    scenarios = spira_client.make_spira_api_get_request(scenarios_url)

    if scenarios:
        formatted_specification.append('#### Acceptance Criteria\n\n')
        for scenario in scenarios:
            position = scenario['Position']
            # Clean HTML from description
            description = _clean_html_from_text(scenario['Description'])
            text = f"{position}. {description}\n"
            formatted_specification.append(text)
        formatted_specification.append('\n')
```

**Steps:**
1. Create `_clean_html_from_text()` helper function
2. Apply to all description fields in specifications
3. Remove inline styles and color tags
4. Convert to clean markdown formatting
5. Test with sample specification data

## Testing Checklist

For each modified tool:

- [ ] Returns valid JSON (test with `json.loads()`)
- [ ] Pagination works correctly (test with different limit/offset values)
- [ ] Error cases return structured JSON errors
- [ ] Input validation catches invalid inputs
- [ ] Docstring accurately describes functionality
- [ ] Examples in docstring work as documented

## Common Pitfalls to Avoid

1. **Don't break existing functionality** - Ensure tools still work after changes
2. **Don't forget imports** - Add `import json` where needed
3. **Don't skip validation** - Always validate inputs
4. **Don't use generic errors** - Be specific about what went wrong
5. **Don't leave TODO comments** - Complete all changes before committing

## Files to Modify (Priority Order)

### High Priority (Core Tools)
1. `src/mcp_server_spira/features/mywork/tools/mytasks.py`
2. `src/mcp_server_spira/features/mywork/tools/myincidents.py`
3. `src/mcp_server_spira/features/productartifacts/tools/tasks.py`
4. `src/mcp_server_spira/features/productartifacts/tools/incidents.py`
5. `src/mcp_server_spira/features/workspaces/tools/products.py`

### Medium Priority (Supporting Tools)
6. `src/mcp_server_spira/features/mywork/tools/myrequirements.py`
7. `src/mcp_server_spira/features/mywork/tools/mytestcases.py`
8. `src/mcp_server_spira/features/productartifacts/tools/requirements.py`
9. `src/mcp_server_spira/features/productartifacts/tools/testcases.py`

### Lower Priority (Specification Tools)
10. `src/mcp_server_spira/features/specifications/tools/productspecification.py`

## Completion Criteria

Phase 1 is complete when:

1. ✅ All tools in `features/mywork/` return JSON
2. ✅ All tools in `features/productartifacts/` return JSON
3. ✅ All tools in `features/workspaces/` return JSON
4. ✅ All list operations support pagination
5. ✅ All tools have input validation
6. ✅ All tools have specific error handling
7. ✅ All docstrings are accurate and complete
8. ✅ Specification outputs are clean markdown
9. ✅ All existing tests pass
10. ✅ New tests added for modified functionality

## Next Phase

After Phase 1 completion, proceed to **Phase 2: Write Operations** which adds create, update, and delete capabilities.
