---
inclusion: always
---

# Spira MCP Server Development Guide

## Project Overview

You are working on the **Spira MCP Server** - a Model Context Protocol server that provides AI assistants with access to the Inflectra Spira API. This server enables AI-driven workflows for project management, test management, and requirements management.

## Current State

- **Version:** 0.5 (starter/demo quality)
- **Language:** Python 3.10+
- **Framework:** FastMCP (MCP Python SDK)
- **API:** Spira REST API v7.0
- **Target:** Production-ready, comprehensive API wrapper

## Core Architecture

```
┌─────────┐         ┌─────────────┐         ┌──────────────┐
│   LLM   │ ◄─────► │ MCP Server  │ ◄─────► │  Spira API   │
│ (Kiro)  │   MCP   │  (Python)   │  HTTP   │ (REST/Auth)  │
└─────────┘         └─────────────┘         └──────────────┘
```

## Key Files

- `src/mcp_server_spira/server.py` - Main server entry point
- `src/mcp_server_spira/utils/spira_client.py` - API client
- `src/mcp_server_spira/features/` - Feature modules (tools organized by domain)
- `SpiraRestAPI-v7.0-OpenAPI.json` - Complete API specification
- `MCP_SERVER_ANALYSIS_AND_RECOMMENDATIONS.md` - Detailed analysis and roadmap

## Critical Design Principles

### 1. JSON-First for Data Processing
**Always return JSON for tools that provide data for AI processing.**

```python
# ✅ GOOD - Returns structured JSON
@mcp.tool()
async def get_my_tasks() -> str:
    tasks = await spira_client.make_spira_api_get_request("tasks")
    return json.dumps(tasks, indent=2)

# ❌ BAD - Returns markdown
@mcp.tool()
async def get_my_tasks() -> str:
    tasks = await spira_client.make_spira_api_get_request("tasks")
    return format_as_markdown(tasks)
```

### 2. Explicit Pagination
**Never truncate results silently. Always provide pagination parameters.**

```python
# ✅ GOOD
async def get_my_tasks(limit: int = 25, offset: int = 0) -> str:
    """Returns up to 'limit' tasks starting at 'offset'."""

# ❌ BAD
async def get_my_tasks() -> str:
    return tasks[:25]  # Silent truncation!
```

### 3. Specific Error Messages
**Return structured error information, not generic messages.**

```python
# ✅ GOOD
return json.dumps({
    "error": "Task not found",
    "task_id": task_id,
    "product_id": product_id
})

# ❌ BAD
return f"There was a problem: {e}"
```

### 4. Input Validation
**Validate all inputs before making API calls.**

```python
# ✅ GOOD
if product_id <= 0:
    return json.dumps({"error": "product_id must be positive"})

# ❌ BAD
# No validation, let API fail
```

### 5. Comprehensive Documentation
**Every tool must have clear docstrings with examples.**

```python
@mcp.tool()
def get_task_by_id(product_id: int, task_id: int) -> str:
    """
    Retrieves a single task by its ID.

    Args:
        product_id: The numeric ID of the product (e.g., 55 for PR:55)
        task_id: The numeric ID of the task (e.g., 40 for TK:40)

    Returns:
        JSON object with task details including:
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
          "ActualEffort": 60
        }
    """
```

## Development Phases

The project is organized into 6 phases:

1. **Phase 1:** Core Improvements (JSON output, pagination, error handling)
2. **Phase 2:** Write Operations (create, update, delete)
3. **Phase 3:** Advanced Search & Filtering
4. **Phase 4:** Utility & Helper Tools
5. **Phase 5:** Enhanced Prompts & Workflows
6. **Phase 6:** Testing & Documentation

**Current Focus:** Phase 1

## Common Patterns

### Tool Registration Pattern

**All tools and impl functions MUST be `async def`.** `SpiraClient` uses `httpx.AsyncClient`
internally — calling it from a sync function blocks the FastMCP event loop and causes hangs
when multiple tools are chained together.

```python
# In features/tasks/tools/read.py
def register_tools(mcp) -> None:
    @mcp.tool()
    async def get_task_by_id(product_id: int, task_id: int) -> str:
        """Tool implementation"""
        try:
            spira_client = get_spira_client()
            return await _get_task_by_id_impl(spira_client, product_id, task_id)
        except Exception as e:
            return json.dumps({"error": str(e)})

async def _get_task_by_id_impl(spira_client, product_id: int, task_id: int) -> str:
    """Separated implementation for testing"""
    task = await spira_client.make_spira_api_get_request(
        f"projects/{product_id}/tasks/{task_id}"
    )
    return json.dumps(task, indent=2)
```

### API Client Usage

`SpiraClient` is a singleton (`get_spira_client()` always returns the same instance).
All request methods are async — always `await` them.

```python
from mcp_server_spira.features.common import get_spira_client

spira_client = get_spira_client()

# GET request
data = await spira_client.make_spira_api_get_request("tasks")

# POST request (create or search)
data = await spira_client.make_spira_api_post_request("projects/55/tasks", task_data)

# PUT request (update)
data = await spira_client.make_spira_api_put_request("projects/55/tasks", task_data)

# DELETE request
data = await spira_client.make_spira_api_delete_request("projects/55/tasks/40")
```

### Adding New Tools Checklist

- [ ] `_impl` function is `async def`
- [ ] Registered tool function is `async def`
- [ ] Every `spira_client.make_spira_api_*` call has `await`
- [ ] Every call to another `_impl` or private helper has `await`
- [ ] Run `scripts/make_tools_async.py` if unsure — it's idempotent

## Testing Requirements

- Write unit tests for all new tools
- Use mocks to avoid hitting real API during tests
- Test error cases and edge cases
- Aim for 80%+ code coverage

## Reference Documents

- **Full Analysis:** `MCP_SERVER_ANALYSIS_AND_RECOMMENDATIONS.md`
- **API Spec:** `SpiraRestAPI-v7.0-OpenAPI.json`
- **Current Code:** `src/mcp_server_spira/`

## Questions or Clarifications

If you're unsure about:
- **API endpoints:** Check `SpiraRestAPI-v7.0-OpenAPI.json`
- **Design decisions:** Check `MCP_SERVER_ANALYSIS_AND_RECOMMENDATIONS.md`
- **Existing patterns:** Look at `src/mcp_server_spira/features/mywork/tools/mytasks.py`

When in doubt, ask the user for clarification rather than making assumptions.
