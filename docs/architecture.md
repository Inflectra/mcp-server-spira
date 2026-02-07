# Spira MCP Server - Architecture Documentation

**Version:** 1.0
**Last Updated:** 2026-02-05
**Status:** Active Development

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Directory Structure](#directory-structure)
4. [Feature-Based Organization](#feature-based-organization)
5. [Tool Registration Pattern](#tool-registration-pattern)
6. [SpiraClient Usage](#spiraclient-usage)
7. [Design Principles](#design-principles)
8. [Extension Guide](#extension-guide)
9. [References](#references)

---

## Overview

The Spira MCP Server is a Model Context Protocol (MCP) server that provides AI assistants with access to the Inflectra Spira API. It enables AI-driven workflows for project management, test management, and requirements management.

**Key Technologies:**
- **Language:** Python 3.13+
- **Framework:** FastMCP (MCP Python SDK)
- **API:** Spira REST API v7.0
- **HTTP Client:** httpx

**Current Version:** 0.5 (evolving toward production-ready v2.0)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│   LLM Client    │ ◄─────► │   MCP Server    │ ◄─────► │   Spira API     │
│   (e.g. Kiro)   │   MCP   │   (Python)      │  HTTPS  │   (REST v7.0)   │
│                 │ Protocol│                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
        │                           │                           │
        │                           │                           │
        v                           v                           v
  Tool Discovery            Feature Modules            API Endpoints
  Tool Invocation           Tool Registration          Authentication
  Prompt Access             Error Handling             Data Operations
```


### Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         MCP Server (server.py)                   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              FastMCP Instance ("inflectra-spira")          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│              ┌───────────────┴───────────────┐                  │
│              │                               │                  │
│              v                               v                  │
│  ┌──────────────────────┐       ┌──────────────────────┐       │
│  │  Feature Registration │       │  Prompt Registration │       │
│  │  (register_all)       │       │  (register_all_prompts)│     │
│  └──────────────────────┘       └──────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              v
┌─────────────────────────────────────────────────────────────────┐
│                        Features Package                          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   mywork     │  │ workspaces   │  │ automation   │         │
│  │              │  │              │  │              │         │
│  │ - mytasks    │  │ - products   │  │ - testruns   │         │
│  │ - myincidents│  │ - programs   │  │ - builds     │         │
│  │ - myrequire..│  │ - templates  │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │productartif..│  │programartif..│  │specifications│         │
│  │              │  │              │  │              │         │
│  │ - tasks      │  │ - capabilities│  │ - requirements│        │
│  │ - incidents  │  │ - milestones │  │ - design     │         │
│  │ - requirements│  │              │  │ - tasks      │         │
│  │ - testcases  │  │              │  │ - testcases  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │templateconf..│  │   common     │                            │
│  │              │  │              │                            │
│  │ - artifacttypes│ │ - formatting │                           │
│  │ - customprops│  │ - utilities  │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              v
┌─────────────────────────────────────────────────────────────────┐
│                         Utils Package                            │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │  SpiraClient     │  │  Prompts         │                    │
│  │                  │  │                  │                    │
│  │ - GET requests   │  │ - conventions    │                    │
│  │ - POST requests  │  │ - workflows      │                    │
│  │ - PUT requests   │  │                  │                    │
│  │ - DELETE requests│  │                  │                    │
│  │ - Authentication │  │                  │                    │
│  │ - Error handling │  │                  │                    │
│  └──────────────────┘  └──────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```


---

## Directory Structure

```
spira-mcp-server/
├── .kiro/                          # Kiro-specific configuration
│   ├── specs/                      # Feature specifications
│   │   ├── milestone-0-foundation/ # Foundation milestone
│   │   └── openapi-tracker/        # API coverage tracker
│   └── steering/                   # Development guidelines
│
├── docs/                           # Documentation
│   ├── architecture.md             # This file
│   └── development_setup.md        # Developer onboarding
│
├── src/                            # Source code
│   └── mcp_server_spira/           # Main package
│       ├── __init__.py
│       ├── __main__.py             # CLI entry point
│       ├── server.py               # MCP server initialization
│       │
│       ├── features/               # Feature modules
│       │   ├── __init__.py         # Feature registration
│       │   ├── common.py           # Shared utilities
│       │   ├── formatting.py       # Output formatting
│       │   │
│       │   ├── mywork/             # User-centric operations
│       │   │   ├── __init__.py
│       │   │   └── tools/
│       │   │       ├── mytasks.py
│       │   │       ├── myincidents.py
│       │   │       ├── myrequirements.py
│       │   │       ├── mytestcases.py
│       │   │       └── mytestsets.py
│       │   │
│       │   ├── workspaces/         # Workspace management
│       │   │   ├── __init__.py
│       │   │   └── tools/
│       │   │       ├── products.py
│       │   │       ├── programs.py
│       │   │       └── product_templates.py
│       │   │
│       │   ├── productartifacts/   # Product-level artifacts
│       │   │   ├── __init__.py
│       │   │   └── tools/
│       │   │       ├── tasks.py
│       │   │       ├── incidents.py
│       │   │       ├── requirements.py
│       │   │       ├── testcases.py
│       │   │       ├── testsets.py
│       │   │       ├── testruns.py
│       │   │       ├── releases.py
│       │   │       ├── automationhosts.py
│       │   │       └── risks.py
│       │   │
│       │   ├── programartifacts/   # Program-level artifacts
│       │   │   ├── __init__.py
│       │   │   └── tools/
│       │   │       ├── capabilities.py
│       │   │       └── milestones.py
│       │   │
│       │   ├── templateconfiguration/ # Template metadata
│       │   │   ├── __init__.py
│       │   │   └── tools/
│       │   │       ├── artifacttypes.py
│       │   │       └── customproperties.py
│       │   │
│       │   ├── automation/         # Automation features
│       │   │   ├── __init__.py
│       │   │   └── tools/
│       │   │       ├── automatedtestruns.py
│       │   │       └── builds.py
│       │   │
│       │   └── specifications/     # Kiro integration
│       │       ├── __init__.py
│       │       └── tools/
│       │           └── productspecification.py
│       │
│       └── utils/                  # Utility modules
│           ├── __init__.py
│           ├── spira_client.py     # API client
│           ├── conventions_prompt.py # Prompt templates
│           └── general.py          # General utilities
│
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── test_server.py              # Server tests
│   └── features/                   # Feature tests
│       └── mywork/
│           └── test_mytasks.py
│
├── .python-version                 # Python version specification
├── .pre-commit-config.yaml         # Pre-commit hooks
├── pyproject.toml                  # Project configuration
├── requirements-dev.txt            # Development dependencies
├── SpiraRestAPI-v7.0-OpenAPI.json  # API specification
└── README.md                       # Project overview
```


---

## Feature-Based Organization

The codebase is organized around **feature domains** rather than technical layers. Each feature represents a logical grouping of related functionality.

### Feature Structure

Each feature follows a consistent structure:

```
feature_name/
├── __init__.py          # Feature registration
└── tools/               # Tool implementations
    ├── tool1.py
    ├── tool2.py
    └── tool3.py
```

### Current Features

#### 1. mywork
**Purpose:** User-centric operations that don't require a product_id

**Tools:**
- `get_my_tasks()` - Retrieve tasks assigned to current user
- `get_my_incidents()` - Retrieve incidents assigned to current user
- `get_my_requirements()` - Retrieve requirements assigned to current user
- `get_my_test_cases()` - Retrieve test cases assigned to current user
- `get_my_test_sets()` - Retrieve test sets assigned to current user

**API Endpoints:**
- `GET /tasks` - My tasks
- `GET /incidents` - My incidents
- `GET /requirements` - My requirements
- `GET /test-cases` - My test cases
- `GET /test-sets` - My test sets

#### 2. workspaces
**Purpose:** Workspace and project management

**Tools:**
- `get_products()` - List all products
- `get_programs()` - List all programs
- `get_product_templates()` - List all product templates

**API Endpoints:**
- `GET /projects` - All products
- `GET /programs` - All programs
- `GET /project-templates` - All templates

#### 3. productartifacts
**Purpose:** Product-level artifact operations (requires product_id)

**Tools:**
- `get_product_tasks()` - List tasks in a product
- `get_product_incidents()` - List incidents in a product
- `get_product_requirements()` - List requirements in a product
- `get_product_test_cases()` - List test cases in a product
- `get_product_test_sets()` - List test sets in a product
- `get_product_test_runs()` - List test runs in a product
- `get_product_releases()` - List releases in a product
- `get_product_automation_hosts()` - List automation hosts
- `get_product_risks()` - List risks in a product

**API Endpoints:**
- `GET /projects/{id}/tasks`
- `GET /projects/{id}/incidents`
- `GET /projects/{id}/requirements`
- `GET /projects/{id}/test-cases`
- `GET /projects/{id}/test-sets`
- `GET /projects/{id}/test-runs`
- `GET /projects/{id}/releases`
- `GET /projects/{id}/automation-hosts`
- `GET /projects/{id}/risks`

#### 4. programartifacts
**Purpose:** Program-level artifact operations

**Tools:**
- `get_program_capabilities()` - List capabilities in a program
- `get_program_milestones()` - List milestones in a program

**API Endpoints:**
- `GET /programs/{id}/capabilities`
- `GET /programs/{id}/milestones`

#### 5. templateconfiguration
**Purpose:** Template metadata and configuration

**Tools:**
- `get_artifact_types()` - Get artifact type definitions
- `get_custom_properties()` - Get custom property definitions

**API Endpoints:**
- `GET /project-templates/{id}/artifact-types`
- `GET /project-templates/{id}/custom-properties`

#### 6. automation
**Purpose:** Test automation features

**Tools:**
- `get_automated_test_runs()` - List automated test runs
- `get_builds()` - List builds

**API Endpoints:**
- `GET /projects/{id}/automated-test-runs`
- `GET /projects/{id}/builds`

#### 7. specifications
**Purpose:** Kiro integration for spec-driven development

**Tools:**
- `get_product_specification()` - Generate specification from Spira data

**API Endpoints:**
- Multiple endpoints composed together

### Feature Registration

Features are registered in `features/__init__.py`:

```python
def register_all(mcp):
    """Register all features with the MCP server."""
    mywork.register(mcp)
    productartifacts.register(mcp)
    programartifacts.register(mcp)
    templateconfiguration.register(mcp)
    workspaces.register(mcp)
    automation.register(mcp)
    specifications.register(mcp)
```

Each feature module has its own `register()` function that registers its tools.


---

## Tool Registration Pattern

The project follows a consistent pattern for registering MCP tools. This pattern separates concerns and makes testing easier.

### Pattern Overview

```python
# In features/mywork/tools/mytasks.py

# 1. Implementation function (testable, no MCP dependencies)
def _get_my_tasks_impl(spira_client) -> str:
    """
    Implementation of retrieving my assigned Spira tasks.

    Args:
        spira_client: The Inflectra Spira API client instance

    Returns:
        Formatted string containing the list of assigned tasks
    """
    try:
        tasks = spira_client.make_spira_api_get_request("tasks")

        if not tasks:
            return "The current user does not have any tasks."

        # Format and return results
        formatted_results = []
        for task in tasks[:25]:
            task_info = format_task(task)
            formatted_results.append(task_info)

        return "\n\n".join(formatted_results)
    except Exception as e:
        return f"There was a problem using this tool: {e}"


# 2. Registration function (called by feature __init__.py)
def register_tools(mcp) -> None:
    """
    Register my work tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    # 3. Tool decorator (MCP-specific)
    @mcp.tool()
    def get_my_tasks() -> str:
        """
        Retrieves a list of the open tasks that are assigned to me.

        Use this tool when you need to:
        - View the complete details of a specific task
        - Examine the current state, assigned user, and other properties
        - Get information about multiple tasks at once

        Returns:
            Formatted string containing comprehensive information for the
            requested list of tasks
        """
        try:
            spira_client = get_spira_client()
            return _get_my_tasks_impl(spira_client)
        except Exception as e:
            return f"Error: {str(e)}"
```

### Pattern Benefits

1. **Testability:** Implementation functions can be tested without MCP framework
2. **Separation of Concerns:** Business logic separate from MCP registration
3. **Reusability:** Implementation functions can be called from multiple tools
4. **Consistency:** All tools follow the same pattern
5. **Error Handling:** Centralized error handling at both levels

### Registration Flow

```
server.py
    │
    └─> features/__init__.py::register_all(mcp)
            │
            ├─> mywork.register(mcp)
            │       │
            │       └─> mywork/__init__.py::register(mcp)
            │               │
            │               └─> mytasks.register_tools(mcp)
            │                       │
            │                       └─> @mcp.tool() decorators
            │
            ├─> workspaces.register(mcp)
            │       └─> ... (same pattern)
            │
            └─> ... (other features)
```

### Feature Registration Example

```python
# In features/mywork/__init__.py

from mcp_server_spira.features.mywork.tools import (
    myincidents,
    myrequirements,
    mytasks,
    mytestcases,
    mytestsets,
)


def register(mcp):
    """
    Register all mywork tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    mytasks.register_tools(mcp)
    myincidents.register_tools(mcp)
    myrequirements.register_tools(mcp)
    mytestcases.register_tools(mcp)
    mytestsets.register_tools(mcp)
```

### Tool Naming Conventions

Tools follow a consistent naming pattern:

**Pattern:** `{verb}_{scope}_{artifact}_{qualifier}`

**Examples:**
- `get_my_tasks()` - Get tasks for current user
- `get_product_tasks()` - Get tasks for a product
- `get_program_capabilities()` - Get capabilities for a program
- `get_artifact_types()` - Get artifact type definitions

**Verbs:**
- `get` - Retrieve data (read-only)
- `create` - Create new item (future)
- `update` - Update existing item (future)
- `delete` - Delete item (future)
- `search` - Advanced search (future)


---

## SpiraClient Usage

The `SpiraClient` class provides a clean interface to the Spira REST API with authentication, error handling, and HTTP method support.

### Client Initialization

```python
from mcp_server_spira.features.common import get_spira_client

# Get configured client instance
spira_client = get_spira_client()
```

The client is configured via environment variables:
- `INFLECTRA_SPIRA_BASE_URL` - Base URL (e.g., https://mycompany.spiraservice.net)
- `INFLECTRA_SPIRA_USERNAME` - Username for authentication
- `INFLECTRA_SPIRA_API_KEY` - API key (RSS Token)

### HTTP Methods

#### GET Requests

```python
# Retrieve data from API
data = spira_client.make_spira_api_get_request("tasks")

# With path parameters
task = spira_client.make_spira_api_get_request("projects/55/tasks/40")

# Returns: dict or list (parsed JSON)
```

#### POST Requests

```python
# Create new resource or search
new_task = {
    "Name": "Fix login bug",
    "Description": "Users cannot log in",
    "TaskStatusId": 1
}

result = spira_client.make_spira_api_post_request(
    "projects/55/tasks",
    new_task
)

# Search with filters
filters = [
    {"PropertyName": "TaskStatusId", "IntValue": 2}
]

results = spira_client.make_spira_api_post_request(
    "projects/55/tasks/search",
    filters
)
```

#### PUT Requests

```python
# Update existing resource
updated_task = {
    "TaskId": 40,
    "Name": "Fix login bug - UPDATED",
    "TaskStatusId": 3
}

result = spira_client.make_spira_api_put_request(
    "projects/55/tasks",
    updated_task
)
```

#### DELETE Requests

```python
# Delete resource
result = spira_client.make_spira_api_delete_request(
    "projects/55/tasks/40"
)
```

### URL Construction

The client automatically constructs full URLs:

```python
# Input: "tasks"
# Output: https://mycompany.spiraservice.net/Services/v7_0/RestService.svc/tasks

# Input: "projects/55/tasks/40"
# Output: https://mycompany.spiraservice.net/Services/v7_0/RestService.svc/projects/55/tasks/40
```

**Components:**
- Base URL: From `INFLECTRA_SPIRA_BASE_URL` environment variable
- API Endpoint: `/Services/v7_0/RestService.svc`
- Resource Path: Provided by caller

### Authentication

Authentication is handled automatically via HTTP headers:

```python
headers = {
    "User-Agent": "mcp-server/1.0",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "username": self.username,      # From environment
    "api-key": self.api_key         # From environment
}
```

### Error Handling

The client raises exceptions for various error conditions:

```python
try:
    data = spira_client.make_spira_api_get_request("tasks")
except ValueError as e:
    # Missing environment variables
    print(f"Configuration error: {e}")
except Exception as e:
    # API errors (404, 403, 500, timeout, etc.)
    print(f"API error: {e}")
```

**Common Errors:**
- `ValueError` - Missing required environment variables
- `httpx.HTTPStatusError` - HTTP error responses (404, 403, 500, etc.)
- `httpx.TimeoutException` - Request timeout (30 seconds)
- `Exception` - Other unexpected errors

### Best Practices

1. **Always use relative paths:**
   ```python
   # ✅ GOOD
   spira_client.make_spira_api_get_request("tasks")

   # ❌ BAD
   spira_client.make_spira_api_get_request("https://...")
   ```

2. **Handle errors appropriately:**
   ```python
   try:
       data = spira_client.make_spira_api_get_request("tasks")
       return json.dumps(data, indent=2)
   except Exception as e:
       return json.dumps({"error": str(e)})
   ```

3. **Use proper HTTP methods:**
   - GET for retrieval
   - POST for creation and search
   - PUT for updates
   - DELETE for deletion

4. **Validate inputs before API calls:**
   ```python
   if product_id <= 0:
       return json.dumps({"error": "product_id must be positive"})

   data = spira_client.make_spira_api_get_request(
       f"projects/{product_id}/tasks"
   )
   ```

### Client Implementation Details

**Location:** `src/mcp_server_spira/utils/spira_client.py`

**Key Features:**
- Environment variable configuration
- Automatic header management
- JSON request/response handling
- 30-second timeout on all requests
- Context manager for HTTP client (automatic cleanup)
- Consistent error messages

**Future Enhancements:**
- Connection pooling for performance
- Response caching for metadata
- Retry logic for transient failures
- Rate limiting support
- Async/await support


---

## Design Principles

The Spira MCP Server follows key design principles that guide development and ensure consistency.

### 1. One Tool = One API Endpoint

Each MCP tool maps directly to ONE Spira REST API endpoint. Complex workflows requiring multiple API calls should use multiple composable tools.

**Rationale:**
- Clear, predictable behavior for LLMs
- Easy to understand and maintain
- Composable for complex workflows
- Matches API documentation

**Example:**
```python
# ✅ GOOD - One tool, one endpoint
@mcp.tool()
def get_task_by_id(product_id: int, task_id: int) -> str:
    """GET /projects/{product_id}/tasks/{task_id}"""
    return spira_client.make_spira_api_get_request(
        f"projects/{product_id}/tasks/{task_id}"
    )

# ✅ GOOD - Separate tools for separate endpoints
@mcp.tool()
def list_tasks(product_id: int) -> str:
    """GET /projects/{product_id}/tasks"""

@mcp.tool()
def get_task_comments(product_id: int, task_id: int) -> str:
    """GET /projects/{product_id}/tasks/{task_id}/comments"""
```

### 2. JSON-First Architecture (Future Direction)

**Current State:** Tools return markdown-formatted strings
**Target State:** Tools return structured JSON

**Rationale:**
- Enables LLM to filter, sort, and aggregate data
- Preserves type information
- Easier to compose with other tools
- Optional formatting tools for human display

**Migration Path:**
```python
# Phase 1: Current (markdown output)
def get_my_tasks() -> str:
    tasks = spira_client.make_spira_api_get_request("tasks")
    return format_tasks_as_markdown(tasks)

# Phase 2: Target (JSON output)
def get_my_tasks() -> str:
    tasks = spira_client.make_spira_api_get_request("tasks")
    return json.dumps(tasks, indent=2)

# Phase 2: Optional formatting tool
def format_tasks_as_markdown(tasks_json: str) -> str:
    tasks = json.loads(tasks_json)
    return format_tasks_as_markdown(tasks)
```

### 3. Explicit Over Implicit

All parameters and behaviors should be explicit, not hidden.

**Pagination:**
```python
# ❌ BAD - Silent truncation
def get_my_tasks() -> str:
    tasks = spira_client.make_spira_api_get_request("tasks")
    return format_tasks(tasks[:25])  # Hidden limit!

# ✅ GOOD - Explicit pagination
def get_my_tasks(limit: int = 25, offset: int = 0) -> str:
    """
    Args:
        limit: Maximum number of tasks (1-100). Default: 25
        offset: Number of tasks to skip. Default: 0
    """
    tasks = spira_client.make_spira_api_get_request("tasks")
    return format_tasks(tasks[offset:offset + limit])
```

**Error Messages:**
```python
# ❌ BAD - Generic error
return f"There was a problem: {e}"

# ✅ GOOD - Specific error
return json.dumps({
    "error": "Task not found",
    "task_id": task_id,
    "product_id": product_id,
    "suggestion": "Verify the task exists and you have permission"
})
```

### 4. Modular & Composable

Features are organized by domain and can be composed for complex workflows.

**Feature Isolation:**
- Each feature is self-contained
- Features don't depend on each other
- Shared utilities in `common.py` and `utils/`

**Tool Composition:**
```python
# Get tasks
tasks = get_my_tasks(status_filter="In Progress")

# Extract IDs
task_ids = [t["TaskId"] for t in json.loads(tasks)]

# Update each
for task_id in task_ids:
    update_task_status(product_id, task_id, new_status_id=3)
```

### 5. Fail Fast with Clear Errors

Validate inputs early and provide actionable error messages.

**Input Validation:**
```python
def get_task_by_id(product_id: int, task_id: int) -> str:
    # Validate before API call
    if product_id <= 0:
        return json.dumps({"error": "product_id must be positive"})

    if task_id <= 0:
        return json.dumps({"error": "task_id must be positive"})

    # Make API call
    try:
        task = spira_client.make_spira_api_get_request(...)
        return json.dumps(task, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})
```

### 6. Document Everything

Every tool must have comprehensive documentation.

**Required Documentation:**
- Clear description of what the tool does
- Parameter descriptions with types and defaults
- Return value structure with examples
- Usage examples
- Error conditions

**Example:**
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

    Errors:
        - Returns error object if task not found
        - Returns error object if permission denied
    """
```

### 7. Test-Driven Development

Write tests for all new functionality.

**Testing Strategy:**
- Unit tests for implementation functions
- Mock API responses to avoid hitting real servers
- Test error cases and edge cases
- Aim for 80%+ code coverage

**Example:**
```python
def test_get_my_tasks_impl():
    # Mock the API client
    mock_client = Mock()
    mock_client.make_spira_api_get_request.return_value = [
        {"TaskId": 40, "Name": "Test task"}
    ]

    # Call implementation
    result = _get_my_tasks_impl(mock_client)

    # Assert
    assert "TK:40" in result
    assert "Test task" in result
```


---

## Extension Guide

This section provides guidance for extending the MCP server with new features and tools.

### Adding a New Feature

**Step 1: Create Feature Directory**

```bash
mkdir -p src/mcp_server_spira/features/newfeature/tools
touch src/mcp_server_spira/features/newfeature/__init__.py
```

**Step 2: Create Tool Module**

```python
# src/mcp_server_spira/features/newfeature/tools/newtool.py

from mcp_server_spira.features.common import get_spira_client
import json


def _get_new_data_impl(spira_client, param1: int) -> str:
    """
    Implementation of new data retrieval.

    Args:
        spira_client: The Spira API client
        param1: Description of parameter

    Returns:
        JSON string with data
    """
    try:
        data = spira_client.make_spira_api_get_request(
            f"endpoint/{param1}"
        )
        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def register_tools(mcp) -> None:
    """Register new feature tools."""

    @mcp.tool()
    def get_new_data(param1: int) -> str:
        """
        Tool description.

        Args:
            param1: Parameter description

        Returns:
            JSON with data
        """
        try:
            spira_client = get_spira_client()
            return _get_new_data_impl(spira_client, param1)
        except Exception as e:
            return json.dumps({"error": str(e)})
```

**Step 3: Create Feature Registration**

```python
# src/mcp_server_spira/features/newfeature/__init__.py

from mcp_server_spira.features.newfeature.tools import newtool


def register(mcp):
    """Register all newfeature tools."""
    newtool.register_tools(mcp)
```

**Step 4: Register Feature in Main Package**

```python
# src/mcp_server_spira/features/__init__.py

from mcp_server_spira.features import (
    # ... existing features ...
    newfeature,  # Add this
)


def register_all(mcp):
    """Register all features."""
    # ... existing registrations ...
    newfeature.register(mcp)  # Add this
```

**Step 5: Write Tests**

```python
# tests/features/newfeature/test_newtool.py

from unittest.mock import Mock
from mcp_server_spira.features.newfeature.tools.newtool import (
    _get_new_data_impl
)


def test_get_new_data_impl():
    # Mock client
    mock_client = Mock()
    mock_client.make_spira_api_get_request.return_value = {
        "id": 1,
        "name": "Test"
    }

    # Call implementation
    result = _get_new_data_impl(mock_client, 1)

    # Assert
    assert '"id": 1' in result
    assert '"name": "Test"' in result
```

### Adding a New Tool to Existing Feature

**Step 1: Create Tool Function in Existing Module**

```python
# src/mcp_server_spira/features/mywork/tools/mytasks.py

# Add new implementation function
def _update_my_task_impl(spira_client, task_id: int, status_id: int) -> str:
    """Implementation of task update."""
    # ... implementation ...


# Add to register_tools function
def register_tools(mcp) -> None:
    # ... existing tools ...

    @mcp.tool()
    def update_my_task(task_id: int, status_id: int) -> str:
        """Update task status."""
        try:
            spira_client = get_spira_client()
            return _update_my_task_impl(spira_client, task_id, status_id)
        except Exception as e:
            return json.dumps({"error": str(e)})
```

### Adding a New Prompt

**Step 1: Create Prompt Module**

```python
# src/mcp_server_spira/utils/new_prompt.py

def get_new_prompt() -> str:
    """
    Generate a new prompt for specific workflow.

    Returns:
        Prompt text
    """
    return """
    # Workflow Title

    ## Context
    ...

    ## Steps
    1. ...
    2. ...
    """
```

**Step 2: Register Prompt**

```python
# src/mcp_server_spira/utils/__init__.py

from mcp_server_spira.utils.new_prompt import get_new_prompt


def register_all_prompts(mcp):
    """Register all prompts."""

    @mcp.prompt(name="new_workflow")
    def new_workflow_prompt() -> str:
        """Description of workflow."""
        return get_new_prompt()
```

### Best Practices for Extensions

1. **Follow Existing Patterns:** Use the same structure as existing features
2. **Separate Implementation:** Keep business logic separate from MCP decorators
3. **Write Tests First:** TDD approach ensures quality
4. **Document Thoroughly:** Clear docstrings for all functions
5. **Validate Inputs:** Check parameters before API calls
6. **Handle Errors:** Provide specific, actionable error messages
7. **Use Type Hints:** Help with IDE support and documentation
8. **Keep It Simple:** One tool = one endpoint

### Common Pitfalls to Avoid

1. **Don't mix concerns:** Keep MCP registration separate from implementation
2. **Don't skip validation:** Always validate inputs
3. **Don't return raw exceptions:** Format errors as JSON
4. **Don't hardcode limits:** Make pagination explicit
5. **Don't skip tests:** Every tool needs tests
6. **Don't forget documentation:** Docstrings are required


---

## References

### Project Documentation

- **[Master Plan](../SPIRA_MCP_ENHANCEMENT_MASTER_PLAN.md)** - Overall project roadmap and milestones
- **[Analysis & Recommendations](../MCP_SERVER_ANALYSIS_AND_RECOMMENDATIONS.md)** - Detailed analysis of current state and improvement recommendations
- **[Development Setup](./development_setup.md)** - Developer onboarding guide
- **[Milestone 0 Requirements](../.kiro/specs/milestone-0-foundation/requirements.md)** - Foundation milestone requirements
- **[Milestone 0 Design](../.kiro/specs/milestone-0-foundation/design.md)** - Foundation milestone design
- **[Milestone 0 Tasks](../.kiro/specs/milestone-0-foundation/tasks.md)** - Foundation milestone implementation tasks

### External Documentation

- **[Spira REST API v7.0 OpenAPI Spec](../SpiraRestAPI-v7.0-OpenAPI.json)** - Complete API specification
- **[FastMCP Documentation](https://github.com/jlowin/fastmcp)** - MCP Python SDK
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - MCP specification
- **[Inflectra Spira Documentation](https://www.inflectra.com/SpiraTest/Documentation.aspx)** - Official Spira docs

### Development Resources

- **[Python 3.13 Documentation](https://docs.python.org/3.13/)** - Python language reference
- **[httpx Documentation](https://www.python-httpx.org/)** - HTTP client library
- **[pytest Documentation](https://docs.pytest.org/)** - Testing framework
- **[Ruff Documentation](https://docs.astral.sh/ruff/)** - Linter and formatter

### Key Concepts

- **MCP (Model Context Protocol):** A protocol for connecting AI assistants to external tools and data sources
- **FastMCP:** A Python SDK for building MCP servers quickly
- **Spira:** Inflectra's project management and test management platform
- **REST API:** Representational State Transfer API for programmatic access to Spira
- **Tool:** An MCP-exposed function that an AI assistant can call
- **Prompt:** An MCP-exposed template that provides context to an AI assistant
- **Feature:** A logical grouping of related tools in the codebase

---

## Appendix: Architecture Diagrams

### Data Flow Diagram

```
┌─────────────┐
│   AI/LLM    │
│   (Kiro)    │
└──────┬──────┘
       │ MCP Protocol
       │ (Tool Discovery, Tool Invocation)
       │
       v
┌─────────────────────────────────────────┐
│         MCP Server (FastMCP)            │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   Tool Registry                 │   │
│  │   - get_my_tasks()              │   │
│  │   - get_product_tasks()         │   │
│  │   - get_my_incidents()          │   │
│  │   - ...                         │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   Feature Modules               │   │
│  │   - mywork                      │   │
│  │   - productartifacts            │   │
│  │   - workspaces                  │   │
│  │   - ...                         │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   SpiraClient                   │   │
│  │   - Authentication              │   │
│  │   - HTTP Methods                │   │
│  │   - Error Handling              │   │
│  └─────────────────────────────────┘   │
└──────────────┬──────────────────────────┘
               │ HTTPS
               │ (REST API v7.0)
               │
               v
┌─────────────────────────────────────────┐
│         Spira REST API                  │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   Endpoints                     │   │
│  │   - /tasks                      │   │
│  │   - /projects/{id}/tasks        │   │
│  │   - /incidents                  │   │
│  │   - /requirements               │   │
│  │   - ...                         │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   Authentication                │   │
│  │   - Username + API Key          │   │
│  │   - Header-based auth           │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Tool Invocation Flow

```
1. AI Assistant discovers tools
   └─> MCP Protocol: list_tools()
       └─> Server returns tool definitions

2. AI Assistant invokes tool
   └─> MCP Protocol: call_tool("get_my_tasks", {})
       └─> Server routes to registered tool function
           └─> Tool function calls get_spira_client()
               └─> SpiraClient makes HTTP request
                   └─> Spira API returns JSON
                       └─> Tool formats response
                           └─> Server returns to AI Assistant

3. AI Assistant processes result
   └─> Uses data for next action
```

---

**End of Architecture Documentation**
