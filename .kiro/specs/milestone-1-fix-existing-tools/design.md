# Milestone 1: Fix Existing Tools - Design Document

**Feature Name:** milestone-1-fix-existing-tools
**Version:** 1.0
**Status:** Draft
**Created:** 2026-02-05
**Last Updated:** 2026-02-05

---

## Overview

This design document specifies the technical architecture for transforming the Spira MCP Server from markdown-based output to a JSON-first architecture. The design addresses all requirements from the requirements document while establishing patterns for future tool development.

**Key Design Principles:**
1. JSON-first for data processing
2. Explicit pagination with clear metadata
3. Comprehensive input validation
4. Rich, auto-generated documentation
5. Backward-compatible tool names
6. Consistent error handling

---

## Architecture Overview

### System Context

```
┌─────────────────┐
│   LLM Client    │
│   (Kiro/Claude) │
└────────┬────────┘
         │ MCP Protocol
         │ (JSON-RPC)
         ▼
┌─────────────────┐
│  MCP Server     │
│  ┌───────────┐  │
│  │   Tools   │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │Validation │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │Pagination │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │SpiraClient│  │
│  └─────┬─────┘  │
└────────┼────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│   Spira API     │
│   (REST v7.0)   │
└─────────────────┘
```


### Component Architecture

```
src/mcp_server_spira/
├── server.py                          # Main MCP server entry point
├── features/
│   ├── common/
│   │   ├── __init__.py
│   │   ├── validation.py              # NEW: Input validation utilities
│   │   ├── pagination.py              # NEW: Pagination utilities
│   │   ├── responses.py               # NEW: Response formatting
│   │   └── errors.py                  # NEW: Error classes
│   ├── mywork/
│   │   └── tools/
│   │       ├── mytasks.py             # MODIFIED: JSON + pagination
│   │       ├── myincidents.py         # MODIFIED: JSON + pagination
│   │       ├── myrequirements.py      # MODIFIED: JSON + pagination
│   │       ├── mytestcases.py         # MODIFIED: JSON + pagination
│   │       └── mytestsets.py          # MODIFIED: JSON + pagination
│   ├── workspace/
│   │   └── tools/
│   │       ├── products.py            # MODIFIED: JSON output
│   │       ├── programs.py            # MODIFIED: JSON output
│   │       └── product_templates.py   # MODIFIED: JSON output
│   └── formatting/
│       ├── __init__.py
│       ├── common.py                  # REFACTORED: Shared formatting logic
│       └── tools/
│           └── format_artifacts.py    # NEW: Generic markdown formatter
├── utils/
│   └── spira_client.py                # UNCHANGED: Existing API client
└── scripts/
    └── generate_tool_docs.py          # NEW: Documentation generator

tests/
├── features/
│   ├── common/
│   │   ├── test_validation.py         # NEW
│   │   ├── test_pagination.py         # NEW
│   │   └── test_responses.py          # NEW
│   ├── mywork/
│   │   └── tools/
│   │       ├── test_mytasks.py        # MODIFIED
│   │       ├── test_myincidents.py    # MODIFIED
│   │       ├── test_myrequirements.py # MODIFIED
│   │       ├── test_mytestcases.py    # MODIFIED
│   │       └── test_mytestsets.py     # MODIFIED
│   └── formatting/
│       └── test_format_artifacts.py   # NEW
└── scripts/
    └── test_generate_tool_docs.py     # NEW
```

---

## Core Components Design

### 1. Response Format

All data-retrieval tools return a standardized JSON structure:

```python
# Type definitions
from typing import TypedDict, List, Any, Literal

class PaginationMetadata(TypedDict):
    """Pagination information for list responses."""
    limit: int                    # Requested limit
    offset: int                   # Requested offset
    returned_count: int           # Number of items in this response
    total_count: int              # Total items available
    has_more: bool                # Whether more items exist
    pagination_type: Literal["client-side", "server-side"]

class SuccessResponse(TypedDict):
    """Standard success response structure."""
    data: List[Any]               # Array of artifacts
    pagination: PaginationMetadata

class ErrorResponse(TypedDict):
    """Standard error response structure."""
    error: str                    # Human-readable error message
    error_code: str               # Machine-readable error code
    details: dict                 # Additional error context
    suggestion: str               # Actionable suggestion for resolution
```

**Design Decisions:**
- Pagination metadata is embedded in response (not separate tool)
- `pagination_type` field distinguishes client-side vs server-side
- Error responses have consistent structure across all tools
- All responses are JSON strings (MCP requirement)



### 2. Validation Module

**File:** `src/mcp_server_spira/features/common/validation.py`

```python
"""Input validation utilities for MCP tools."""

from typing import Optional, Tuple
from .errors import ValidationError

class ParameterValidator:
    """Validates tool input parameters."""

    @staticmethod
    def validate_positive_integer(
        value: int,
        param_name: str,
        min_value: int = 1
    ) -> Optional[dict]:
        """
        Validates that a parameter is a positive integer.

        Args:
            value: The value to validate
            param_name: Name of the parameter (for error messages)
            min_value: Minimum allowed value (default: 1)

        Returns:
            None if valid, error dict if invalid
        """
        if not isinstance(value, int):
            return {
                "error": f"Invalid {param_name} parameter",
                "error_code": "INVALID_TYPE",
                "details": {
                    "parameter": param_name,
                    "value": value,
                    "expected_type": "integer"
                },
                "suggestion": f"{param_name} must be an integer"
            }

        if value < min_value:
            return {
                "error": f"Invalid {param_name} parameter",
                "error_code": "INVALID_VALUE",
                "details": {
                    "parameter": param_name,
                    "value": value,
                    "expected": f">= {min_value}"
                },
                "suggestion": f"{param_name} must be >= {min_value}"
            }

        return None

    @staticmethod
    def validate_pagination_params(
        limit: int,
        offset: int
    ) -> Optional[dict]:
        """
        Validates pagination parameters.

        Args:
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            None if valid, error dict if invalid
        """
        # Validate limit
        if not isinstance(limit, int) or not (1 <= limit <= 500):
            return {
                "error": "Invalid limit parameter",
                "error_code": "INVALID_PARAMETER",
                "details": {
                    "parameter": "limit",
                    "value": limit,
                    "expected": "1-500"
                },
                "suggestion": "Use limit between 1 and 500"
            }

        # Validate offset
        if not isinstance(offset, int) or offset < 0:
            return {
                "error": "Invalid offset parameter",
                "error_code": "INVALID_PARAMETER",
                "details": {
                    "parameter": "offset",
                    "value": offset,
                    "expected": ">= 0"
                },
                "suggestion": "Use offset >= 0"
            }

        return None
```

**Design Decisions:**
- Static methods for stateless validation
- Returns error dicts (not exceptions) for easy JSON serialization
- Consistent error structure across all validators
- Reusable across all tools



### 3. Pagination Module

**File:** `src/mcp_server_spira/features/common/pagination.py`

```python
"""Pagination utilities for MCP tools."""

from typing import List, Any, TypedDict

class PaginationResult(TypedDict):
    """Result of pagination operation."""
    data: List[Any]
    pagination: dict

def paginate_client_side(
    all_items: List[Any],
    limit: int,
    offset: int
) -> PaginationResult:
    """
    Implements client-side pagination by slicing a list.

    This is used for API endpoints that don't support server-side pagination.
    The API returns all results, and we slice them in Python.

    Args:
        all_items: Complete list of items from API
        limit: Maximum number of items to return
        offset: Number of items to skip

    Returns:
        Dictionary with paginated data and metadata

    Example:
        >>> items = [1, 2, 3, 4, 5]
        >>> result = paginate_client_side(items, limit=2, offset=1)
        >>> result["data"]
        [2, 3]
        >>> result["pagination"]["has_more"]
        True
    """
    total_count = len(all_items)
    paginated_items = all_items[offset:offset + limit]
    returned_count = len(paginated_items)
    has_more = (offset + returned_count) < total_count

    return {
        "data": paginated_items,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "returned_count": returned_count,
            "total_count": total_count,
            "has_more": has_more,
            "pagination_type": "client-side"
        }
    }

def paginate_server_side(
    items: List[Any],
    limit: int,
    offset: int,
    total_count: int
) -> PaginationResult:
    """
    Wraps server-side paginated results with metadata.

    This is used for API endpoints that support server-side pagination
    (start_row, number_rows parameters). The API returns only the requested
    page, and we add pagination metadata.

    Args:
        items: Items returned from API (already paginated)
        limit: Requested limit
        offset: Requested offset
        total_count: Total items available (from API response header or metadata)

    Returns:
        Dictionary with data and pagination metadata

    Note:
        This will be used in Milestone 2+ for project-level endpoints.
        Milestone 1 only uses client-side pagination.
    """
    returned_count = len(items)
    has_more = (offset + returned_count) < total_count

    return {
        "data": items,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "returned_count": returned_count,
            "total_count": total_count,
            "has_more": has_more,
            "pagination_type": "server-side"
        }
    }
```

**Design Decisions:**
- Separate functions for client-side vs server-side pagination
- `pagination_type` field makes implementation transparent
- Consistent metadata structure for both types
- Server-side function prepared for future milestones



### 4. Response Formatting Module

**File:** `src/mcp_server_spira/features/common/responses.py`

```python
"""Response formatting utilities for MCP tools."""

import json
from typing import Any, Dict, List

def format_success_response(data: Any, pagination: Dict = None) -> str:
    """
    Formats a successful response as JSON string.

    Args:
        data: The data to return (list or dict)
        pagination: Optional pagination metadata

    Returns:
        JSON string with proper formatting
    """
    response = {"data": data}
    if pagination:
        response["pagination"] = pagination

    return json.dumps(response, indent=2, default=str)

def format_error_response(
    error: str,
    error_code: str,
    details: Dict = None,
    suggestion: str = None
) -> str:
    """
    Formats an error response as JSON string.

    Args:
        error: Human-readable error message
        error_code: Machine-readable error code
        details: Additional error context
        suggestion: Actionable suggestion for resolution

    Returns:
        JSON string with error information
    """
    response = {
        "error": error,
        "error_code": error_code
    }

    if details:
        response["details"] = details
    if suggestion:
        response["suggestion"] = suggestion

    return json.dumps(response, indent=2)

# Standard error codes
class ErrorCodes:
    """Standard error codes used across all tools."""
    INVALID_PARAMETER = "INVALID_PARAMETER"
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    API_ERROR = "API_ERROR"
    NOT_FOUND = "NOT_FOUND"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
```

**Design Decisions:**
- Centralized response formatting ensures consistency
- `default=str` handles datetime and other non-JSON types
- Error codes are constants to prevent typos
- 2-space indentation for readability



### 5. Error Classes Module

**File:** `src/mcp_server_spira/features/common/errors.py`

```python
"""Custom exception classes for MCP tools."""

class SpiraMCPError(Exception):
    """Base exception for all Spira MCP errors."""

    def __init__(self, message: str, error_code: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> dict:
        """Convert exception to error response dict."""
        return {
            "error": self.message,
            "error_code": self.error_code,
            "details": self.details
        }

class ValidationError(SpiraMCPError):
    """Raised when input validation fails."""

    def __init__(self, message: str, parameter: str, value: Any, expected: str):
        super().__init__(
            message=message,
            error_code="INVALID_PARAMETER",
            details={
                "parameter": parameter,
                "value": value,
                "expected": expected
            }
        )

class APIError(SpiraMCPError):
    """Raised when Spira API call fails."""

    def __init__(self, message: str, endpoint: str, status_code: int = None):
        super().__init__(
            message=message,
            error_code="API_ERROR",
            details={
                "endpoint": endpoint,
                "status_code": status_code
            }
        )

class AuthenticationError(SpiraMCPError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR"
        )
```

**Design Decisions:**
- Exception hierarchy for different error types
- Exceptions can be converted to JSON error responses
- Consistent error structure across exception types
- Exceptions are optional (tools can return error dicts directly)

---

## Tool Implementation Patterns

### Pattern 1: MyWork Tools (Client-Side Pagination)

All "my work" tools follow this pattern:

```python
# File: src/mcp_server_spira/features/mywork/tools/mytasks.py

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.validation import ParameterValidator
from mcp_server_spira.features.common.pagination import paginate_client_side
from mcp_server_spira.features.common.responses import (
    format_success_response,
    format_error_response,
    ErrorCodes
)
import json

def register_tools(mcp) -> None:
    """Register MyWork tools with MCP server."""

    @mcp.tool()
    def get_my_tasks(limit: int = 25, offset: int = 0) -> str:
        """
        Retrieves tasks assigned to the current user.

        Maps to Spira API: GET /tasks

        This tool returns tasks where the current user is the Owner (assigned to).
        Use this for personal task lists, daily standup reports, or workload analysis.

        **Pagination:** This endpoint uses CLIENT-SIDE pagination. The API returns
        all tasks, and we slice the results in Python. This is acceptable for "my work"
        queries which typically return < 500 items. For large result sets, consider
        using project-level queries with server-side pagination (available in Milestone 2+).

        **For Display:** Modern LLMs can format JSON naturally for simple display.
        For complex workflows where you've filtered or processed the data, use
        format_artifacts_as_markdown() to ensure consistent formatting.

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
                        "Description": "Users cannot log in with special characters",
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
                        "ReleaseId": 10,
                        "ReleaseVersionNumber": "1.5.0",
                        "RequirementId": 45,
                        "RequirementName": "User Authentication",
                        "ProjectId": 55,
                        "ProjectName": "Web Application"
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
            - EstimatedEffort: Original estimate in minutes (set at task creation)
            - ActualEffort: Time logged so far in minutes (increases as work progresses)
            - RemainingEffort: Developer's estimate of time remaining (updated manually)
            - ProjectedEffort: Calculated as ActualEffort + RemainingEffort
            - CompletionPercent: Calculated as (ActualEffort / ProjectedEffort) * 100
            - ReleaseId/ReleaseVersionNumber: Sprint/iteration assignment
            - RequirementId/RequirementName: Parent requirement link

        When to Use:
            - Getting personal task list for current user
            - Generating daily standup reports
            - Analyzing personal workload
            - Finding tasks by status or priority (filter the JSON)

        Related Tools:
            - format_artifacts_as_markdown: Format filtered/processed results
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

            # Complex workflow - Use formatting tool for filtered results
            tasks_json = get_my_tasks(limit=100)
            tasks = json.loads(tasks_json)
            late_tasks = [t for t in tasks["data"] if is_late(t["EndDate"])]
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

            # Retrieve ALL tasks from API (no server-side pagination available)
            all_tasks = spira_client.make_spira_api_get_request("tasks")

            # Apply client-side pagination
            result = paginate_client_side(all_tasks, limit, offset)

            # Return formatted JSON response
            return format_success_response(
                data=result["data"],
                pagination=result["pagination"]
            )

        except Exception as e:
            return format_error_response(
                error="Failed to retrieve tasks",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication"
            )
```

**Pattern Summary:**
1. Validate inputs using `ParameterValidator`
2. Get Spira client
3. Retrieve all data from API
4. Apply client-side pagination
5. Return formatted JSON response
6. Handle errors with structured error responses



### Pattern 2: Workspace Tools (No Pagination)

Workspace tools return all items without pagination:

```python
# File: src/mcp_server_spira/features/workspace/tools/products.py

def register_tools(mcp) -> None:
    """Register workspace tools with MCP server."""

    @mcp.tool()
    def get_products() -> str:
        """
        Retrieves all products the current user has access to.

        Maps to Spira API: GET /projects

        Returns a list of all products (projects) that the current user can access.
        Use this to discover available products before querying product-specific data.

        Args:
            None

        Returns:
            JSON string with structure:
            {
                "data": [
                    {
                        "ProjectId": 55,
                        "Name": "Web Application",
                        "Description": "Main web application project",
                        "Active": true,
                        "CreationDate": "2023-01-15T10:00:00Z",
                        "ProjectGroupId": 10,
                        "ProjectGroupName": "Engineering"
                    }
                ]
            }

        Key Fields:
            - ProjectId: Unique identifier (use this in other tool calls)
            - Name: Display name of the product
            - Active: Whether the product is currently active
            - ProjectGroupId/ProjectGroupName: Organizational grouping

        When to Use:
            - Discovering available products
            - Listing products for user selection
            - Validating product IDs before other operations

        Related Tools:
            - get_programs: Get program-level groupings
            - get_product_templates: Get available templates

        Example Usage:
            products_json = get_products()
            products = json.loads(products_json)
            for product in products["data"]:
                print(f"Product {product['ProjectId']}: {product['Name']}")
        """
        try:
            spira_client = get_spira_client()
            products = spira_client.make_spira_api_get_request("projects")

            return format_success_response(data=products)

        except Exception as e:
            return format_error_response(
                error="Failed to retrieve products",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication"
            )
```

**Pattern Summary:**
1. No pagination parameters (workspace data is typically small)
2. Simple data retrieval and formatting
3. Consistent error handling



### Pattern 3: Formatting Tool

**File:** `src/mcp_server_spira/features/formatting/tools/format_artifacts.py`

```python
"""Generic artifact formatting tool."""

import json
from typing import Literal

def register_tools(mcp) -> None:
    """Register formatting tools with MCP server."""

    @mcp.tool()
    def format_artifacts_as_markdown(
        artifact_json: str,
        artifact_type: Literal["task", "incident", "requirement", "test_case", "test_set"]
    ) -> str:
        """
        Converts artifact JSON to human-readable markdown format.

        This tool is designed for complex workflows where you've filtered, sorted,
        or processed artifact data and need consistent markdown formatting. For simple
        display of unmodified results, modern LLMs can format JSON naturally.

        Args:
            artifact_json: JSON string containing artifact data
                Can be full response with pagination or just data array.
                Can be filtered/modified JSON from processing.
            artifact_type: Type of artifact to format
                One of: "task", "incident", "requirement", "test_case", "test_set"

        Returns:
            Markdown formatted string with artifact information, suitable for
            displaying to users.

        When to Use:
            - After filtering or processing JSON data
            - When you need consistent formatting across multiple operations
            - When combining multiple artifact types in one display
            - When LLM's natural formatting isn't sufficient

        When NOT to Use:
            - Simple "show me my tasks" requests (LLM can format naturally)
            - Direct display of unmodified API results
            - When LLM's natural formatting quality is acceptable

        Example Output (for tasks):
            ## Task [TK:123] - Fix login bug
            Users cannot log in with special characters
            - **Status:** In Progress
            - **Type:** Development
            - **Priority:** Critical
            - **Owner:** John Doe
            - **Effort:** 60/120 min (50% complete)
            - **Due Date:** 2024-01-16
            - **Release:** 1.5.0

            ## Task [TK:124] - Update documentation
            ...

        Example Usage:
            # Filter then format
            tasks_json = get_my_tasks(limit=100)
            tasks = json.loads(tasks_json)
            critical = [t for t in tasks["data"] if t["TaskPriorityName"] == "Critical"]
            critical_json = json.dumps({"data": critical})
            display = format_artifacts_as_markdown(critical_json, "task")

            # Combine multiple artifact types
            tasks = get_my_tasks()
            incidents = get_my_incidents()
            combined = format_artifacts_as_markdown(tasks, "task") + "\\n\\n" + \\
                       format_artifacts_as_markdown(incidents, "incident")
        """
        try:
            # Parse JSON input
            data = json.loads(artifact_json)

            # Handle both full response and data array
            artifacts = data.get("data", data) if isinstance(data, dict) else data

            if not artifacts:
                return "No artifacts to display."

            # Format based on artifact type
            if artifact_type == "task":
                return _format_tasks(artifacts)
            elif artifact_type == "incident":
                return _format_incidents(artifacts)
            elif artifact_type == "requirement":
                return _format_requirements(artifacts)
            elif artifact_type == "test_case":
                return _format_test_cases(artifacts)
            elif artifact_type == "test_set":
                return _format_test_sets(artifacts)
            else:
                return f"Error: Unknown artifact type '{artifact_type}'"

        except json.JSONDecodeError:
            return "Error: Invalid JSON input"
        except KeyError as e:
            return f"Error: Missing required field: {e}"
        except Exception as e:
            return f"Error: {str(e)}"

def _format_tasks(tasks: list) -> str:
    """Format tasks as markdown."""
    formatted = []
    for task in tasks:
        effort_info = ""
        if task.get("EstimatedEffort"):
            actual = task.get("ActualEffort", 0)
            estimated = task["EstimatedEffort"]
            percent = task.get("CompletionPercent", 0)
            effort_info = f"- **Effort:** {actual}/{estimated} min ({percent}% complete)\\n"

        formatted.append(f"""## Task [TK:{task['TaskId']}] - {task['Name']}
{task.get('Description', '')}
- **Status:** {task['TaskStatusName']}
- **Type:** {task['TaskTypeName']}
- **Priority:** {task['TaskPriorityName']}
- **Owner:** {task['OwnerName']}
{effort_info}- **Due Date:** {task.get('EndDate', 'Not set')}
- **Release:** {task.get('ReleaseVersionNumber', 'Unscheduled')}
""")

    return "\\n\\n".join(formatted)

def _format_incidents(incidents: list) -> str:
    """Format incidents as markdown."""
    formatted = []
    for incident in incidents:
        formatted.append(f"""## Incident [IN:{incident['IncidentId']}] - {incident['Name']}
{incident.get('Description', '')}
- **Status:** {incident['IncidentStatusName']}
- **Type:** {incident['IncidentTypeName']}
- **Priority:** {incident['PriorityName']}
- **Severity:** {incident.get('SeverityName', 'Not set')}
- **Owner:** {incident['OwnerName']}
- **Detected Date:** {incident.get('StartDate', 'Not set')}
- **Release:** {incident.get('DetectedReleaseVersionNumber', 'Unknown')}
""")

    return "\\n\\n".join(formatted)

def _format_requirements(requirements: list) -> str:
    """Format requirements as markdown."""
    formatted = []
    for req in requirements:
        formatted.append(f"""## Requirement [RQ:{req['RequirementId']}] - {req['Name']}
{req.get('Description', '')}
- **Status:** {req['StatusName']}
- **Type:** {req['RequirementTypeName']}
- **Importance:** {req['ImportanceName']}
- **Owner:** {req['OwnerName']}
- **Estimate:** {req.get('EstimatePoints', 'Not estimated')} points
- **Release:** {req.get('ReleaseVersionNumber', 'Unscheduled')}
""")

    return "\\n\\n".join(formatted)

def _format_test_cases(test_cases: list) -> str:
    """Format test cases as markdown."""
    formatted = []
    for tc in test_cases:
        formatted.append(f"""## Test Case [TC:{tc['TestCaseId']}] - {tc['Name']}
{tc.get('Description', '')}
- **Status:** {tc['ExecutionStatusName']}
- **Type:** {tc['TestCaseTypeName']}
- **Priority:** {tc['TestCasePriorityName']}
- **Owner:** {tc['OwnerName']}
- **Automation:** {tc.get('AutomationEngineName', 'Manual')}
- **Release:** {tc.get('ReleaseVersionNumber', 'Unscheduled')}
""")

    return "\\n\\n".join(formatted)

def _format_test_sets(test_sets: list) -> str:
    """Format test sets as markdown."""
    formatted = []
    for ts in test_sets:
        formatted.append(f"""## Test Set [TX:{ts['TestSetId']}] - {ts['Name']}
{ts.get('Description', '')}
- **Status:** {ts['TestSetStatusName']}
- **Owner:** {ts['OwnerName']}
- **Test Cases:** {ts.get('TestCaseCount', 0)}
- **Release:** {ts.get('ReleaseVersionNumber', 'Unscheduled')}
""")

    return "\\n\\n".join(formatted)
```

**Design Decisions:**
- Single generic formatter handles all artifact types
- Type parameter uses Literal for type safety
- Handles both full responses and data arrays
- Graceful error handling for missing fields
- Consistent markdown structure per artifact type



---

## Documentation Generation System

### OpenAPI Documentation Generator

**File:** `scripts/generate_tool_docs.py`

```python
"""
Generates tool documentation from OpenAPI specification.

This script automates the creation of tool docstrings by extracting
information from the Spira OpenAPI spec. It generates templates that
developers can review and enhance with workflow context.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

class OpenAPIDocGenerator:
    """Generates tool documentation from OpenAPI spec."""

    def __init__(self, openapi_spec_path: str):
        """
        Initialize generator with OpenAPI spec.

        Args:
            openapi_spec_path: Path to OpenAPI JSON file
        """
        with open(openapi_spec_path, 'r') as f:
            self.spec = json.load(f)

    def extract_endpoint_info(self, path: str, method: str) -> Dict:
        """
        Extract endpoint information from OpenAPI spec.

        Args:
            path: API path (e.g., "/tasks")
            method: HTTP method (e.g., "get")

        Returns:
            Dictionary with endpoint details:
            - operation_id: OpenAPI operation ID
            - summary: Brief description
            - description: Detailed description
            - parameters: List of parameter definitions
            - responses: Response schema information
        """
        endpoint = self.spec["paths"][path][method]

        return {
            "operation_id": endpoint.get("operationId"),
            "summary": endpoint.get("summary", ""),
            "description": endpoint.get("description", ""),
            "parameters": endpoint.get("parameters", []),
            "responses": endpoint.get("responses", {})
        }

    def extract_schema_info(self, schema_ref: str) -> Dict:
        """
        Extract schema information from OpenAPI spec.

        Args:
            schema_ref: Schema reference (e.g., "#/components/schemas/RemoteTask")

        Returns:
            Dictionary with schema details:
            - properties: Field definitions
            - required: List of required fields
            - description: Schema description
        """
        # Parse schema reference
        schema_name = schema_ref.split("/")[-1]
        schema = self.spec["components"]["schemas"][schema_name]

        return {
            "name": schema_name,
            "properties": schema.get("properties", {}),
            "required": schema.get("required", []),
            "description": schema.get("description", "")
        }

    def generate_docstring_template(
        self,
        tool_name: str,
        endpoint_path: str,
        method: str
    ) -> str:
        """
        Generate docstring template for a tool.

        Args:
            tool_name: Name of the MCP tool
            endpoint_path: API endpoint path
            method: HTTP method

        Returns:
            Formatted docstring template as string
        """
        endpoint_info = self.extract_endpoint_info(endpoint_path, method)

        # Extract response schema
        response_schema = None
        if "200" in endpoint_info["responses"]:
            response_ref = endpoint_info["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
            response_schema = self.extract_schema_info(response_ref)

        # Build docstring
        docstring = f'''"""
{endpoint_info["summary"]}

Maps to Spira API: {method.upper()} {endpoint_path}

{endpoint_info["description"]}

Args:
'''

        # Add parameters
        for param in endpoint_info["parameters"]:
            param_desc = param.get("description", "No description")
            required = "required" if param.get("required") else "optional"
            docstring += f'    {param["name"]}: {param_desc} ({required})\\n'

        # Add return value documentation
        docstring += '''
Returns:
    JSON string with structure:
    {
        "data": [
'''

        # Add key fields from schema
        if response_schema:
            for field_name, field_info in list(response_schema["properties"].items())[:10]:
                field_type = field_info.get("type", "unknown")
                field_desc = field_info.get("description", "")
                docstring += f'            "{field_name}": {field_type},  // {field_desc}\\n'

        docstring += '''        ],
        "pagination": {
            "limit": int,
            "offset": int,
            "returned_count": int,
            "total_count": int,
            "has_more": bool,
            "pagination_type": "client-side"
        }
    }

Key Fields:
'''

        # Add field descriptions
        if response_schema:
            for field_name, field_info in list(response_schema["properties"].items())[:5]:
                field_desc = field_info.get("description", "No description")
                docstring += f'    - {field_name}: {field_desc}\\n'

        docstring += '''
When to Use:
    [TO BE FILLED: Describe use cases and scenarios]

Related Tools:
    [TO BE FILLED: List related tools]

Example Usage:
    [TO BE FILLED: Provide example code]
"""'''

        return docstring

    def identify_clarifications_needed(
        self,
        endpoint_path: str,
        method: str
    ) -> List[str]:
        """
        Identify areas that need human clarification.

        Args:
            endpoint_path: API endpoint path
            method: HTTP method

        Returns:
            List of clarification questions
        """
        clarifications = []
        endpoint_info = self.extract_endpoint_info(endpoint_path, method)

        # Check for missing descriptions
        if not endpoint_info["description"]:
            clarifications.append(
                f"Missing endpoint description for {method.upper()} {endpoint_path}"
            )

        # Check for missing parameter descriptions
        for param in endpoint_info["parameters"]:
            if not param.get("description"):
                clarifications.append(
                    f"Missing description for parameter '{param['name']}'"
                )

        # Check response schema
        if "200" in endpoint_info["responses"]:
            response_ref = endpoint_info["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
            schema = self.extract_schema_info(response_ref)

            # Check for vague field descriptions
            for field_name, field_info in schema["properties"].items():
                desc = field_info.get("description", "")
                if not desc or desc.lower().startswith("the id"):
                    clarifications.append(
                        f"Vague or missing description for field '{field_name}': '{desc}'"
                    )

        return clarifications

    def generate_documentation_report(self, output_path: str) -> None:
        """
        Generate complete documentation report for all tools.

        Args:
            output_path: Path to save markdown report
        """
        report = "# Tool Documentation Generation Report\\n\\n"

        # Define tools to document
        tools = [
            ("get_my_tasks", "/tasks", "get"),
            ("get_my_incidents", "/incidents", "get"),
            ("get_my_requirements", "/requirements", "get"),
            ("get_my_test_cases", "/test-cases", "get"),
            ("get_my_test_sets", "/test-sets", "get"),
        ]

        for tool_name, path, method in tools:
            report += f"## {tool_name}\\n\\n"

            # Generate docstring
            docstring = self.generate_docstring_template(tool_name, path, method)
            report += f"### Generated Docstring\\n\\n```python\\n{docstring}\\n```\\n\\n"

            # Identify clarifications
            clarifications = self.identify_clarifications_needed(path, method)
            if clarifications:
                report += "### Clarifications Needed\\n\\n"
                for clarification in clarifications:
                    report += f"- {clarification}\\n"
                report += "\\n"

            report += "---\\n\\n"

        # Write report
        with open(output_path, 'w') as f:
            f.write(report)

        print(f"Documentation report generated: {output_path}")

# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate tool documentation from OpenAPI spec")
    parser.add_argument("--spec", required=True, help="Path to OpenAPI JSON file")
    parser.add_argument("--output", required=True, help="Path to output markdown file")

    args = parser.parse_args()

    generator = OpenAPIDocGenerator(args.spec)
    generator.generate_documentation_report(args.output)
```

**Usage:**
```bash
python scripts/generate_tool_docs.py \\
    --spec SpiraRestAPI-v7.0-OpenAPI.json \\
    --output docs/tool_documentation_report.md
```

**Design Decisions:**
- Extracts all available information from OpenAPI spec
- Generates templates with placeholders for human input
- Identifies areas needing clarification
- Outputs markdown report for review
- Reusable for future tool development



---

## Testing Strategy

### Unit Test Structure

All tools have comprehensive unit tests with mocked SpiraClient:

```python
# File: tests/features/mywork/tools/test_mytasks.py

import pytest
import json
from unittest.mock import Mock, patch
from mcp_server_spira.features.mywork.tools.mytasks import get_my_tasks

class TestGetMyTasks:
    """Test suite for get_my_tasks tool."""

    @pytest.fixture
    def mock_spira_client(self):
        """Create mock SpiraClient."""
        client = Mock()
        return client

    @pytest.fixture
    def sample_tasks(self):
        """Sample task data for testing."""
        return [
            {
                "TaskId": 1,
                "Name": "Task 1",
                "TaskStatusName": "In Progress",
                "TaskTypeName": "Development",
                "TaskPriorityName": "High",
                "OwnerName": "John Doe",
                "EstimatedEffort": 120,
                "ActualEffort": 60
            },
            {
                "TaskId": 2,
                "Name": "Task 2",
                "TaskStatusName": "Not Started",
                "TaskTypeName": "Testing",
                "TaskPriorityName": "Medium",
                "OwnerName": "Jane Smith",
                "EstimatedEffort": 60,
                "ActualEffort": 0
            }
        ]

    def test_get_my_tasks_success(self, mock_spira_client, sample_tasks):
        """Test successful task retrieval."""
        mock_spira_client.make_spira_api_get_request.return_value = sample_tasks

        with patch('mcp_server_spira.features.mywork.tools.mytasks.get_spira_client',
                   return_value=mock_spira_client):
            result = get_my_tasks(limit=10, offset=0)

        # Parse response
        response = json.loads(result)

        # Verify structure
        assert "data" in response
        assert "pagination" in response

        # Verify data
        assert len(response["data"]) == 2
        assert response["data"][0]["TaskId"] == 1

        # Verify pagination
        assert response["pagination"]["limit"] == 10
        assert response["pagination"]["offset"] == 0
        assert response["pagination"]["returned_count"] == 2
        assert response["pagination"]["total_count"] == 2
        assert response["pagination"]["has_more"] is False
        assert response["pagination"]["pagination_type"] == "client-side"

    def test_get_my_tasks_pagination_first_page(self, mock_spira_client):
        """Test pagination - first page."""
        # Create 50 tasks
        tasks = [{"TaskId": i, "Name": f"Task {i}"} for i in range(50)]
        mock_spira_client.make_spira_api_get_request.return_value = tasks

        with patch('mcp_server_spira.features.mywork.tools.mytasks.get_spira_client',
                   return_value=mock_spira_client):
            result = get_my_tasks(limit=25, offset=0)

        response = json.loads(result)

        assert len(response["data"]) == 25
        assert response["data"][0]["TaskId"] == 0
        assert response["data"][24]["TaskId"] == 24
        assert response["pagination"]["has_more"] is True

    def test_get_my_tasks_pagination_second_page(self, mock_spira_client):
        """Test pagination - second page."""
        tasks = [{"TaskId": i, "Name": f"Task {i}"} for i in range(50)]
        mock_spira_client.make_spira_api_get_request.return_value = tasks

        with patch('mcp_server_spira.features.mywork.tools.mytasks.get_spira_client',
                   return_value=mock_spira_client):
            result = get_my_tasks(limit=25, offset=25)

        response = json.loads(result)

        assert len(response["data"]) == 25
        assert response["data"][0]["TaskId"] == 25
        assert response["data"][24]["TaskId"] == 49
        assert response["pagination"]["has_more"] is False

    def test_get_my_tasks_pagination_partial_page(self, mock_spira_client):
        """Test pagination - partial last page."""
        tasks = [{"TaskId": i, "Name": f"Task {i}"} for i in range(30)]
        mock_spira_client.make_spira_api_get_request.return_value = tasks

        with patch('mcp_server_spira.features.mywork.tools.mytasks.get_spira_client',
                   return_value=mock_spira_client):
            result = get_my_tasks(limit=25, offset=25)

        response = json.loads(result)

        assert len(response["data"]) == 5
        assert response["pagination"]["returned_count"] == 5
        assert response["pagination"]["has_more"] is False

    def test_get_my_tasks_empty_results(self, mock_spira_client):
        """Test empty task list."""
        mock_spira_client.make_spira_api_get_request.return_value = []

        with patch('mcp_server_spira.features.mywork.tools.mytasks.get_spira_client',
                   return_value=mock_spira_client):
            result = get_my_tasks()

        response = json.loads(result)

        assert response["data"] == []
        assert response["pagination"]["total_count"] == 0
        assert response["pagination"]["has_more"] is False

    def test_get_my_tasks_invalid_limit_too_high(self):
        """Test validation - limit too high."""
        result = get_my_tasks(limit=1000, offset=0)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_PARAMETER"
        assert response["details"]["parameter"] == "limit"
        assert response["details"]["value"] == 1000

    def test_get_my_tasks_invalid_limit_too_low(self):
        """Test validation - limit too low."""
        result = get_my_tasks(limit=0, offset=0)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_PARAMETER"

    def test_get_my_tasks_invalid_offset_negative(self):
        """Test validation - negative offset."""
        result = get_my_tasks(limit=25, offset=-1)
        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "INVALID_PARAMETER"
        assert response["details"]["parameter"] == "offset"

    def test_get_my_tasks_api_error(self, mock_spira_client):
        """Test API error handling."""
        mock_spira_client.make_spira_api_get_request.side_effect = Exception("API connection failed")

        with patch('mcp_server_spira.features.mywork.tools.mytasks.get_spira_client',
                   return_value=mock_spira_client):
            result = get_my_tasks()

        response = json.loads(result)

        assert "error" in response
        assert response["error_code"] == "API_ERROR"
        assert "API connection failed" in response["details"]["message"]
```

**Test Coverage Requirements:**
- Successful data retrieval
- Pagination edge cases (first page, last page, partial page, empty)
- Input validation errors
- API errors
- JSON structure validation
- Pagination metadata accuracy



### Test Coverage for Formatting Tool

```python
# File: tests/features/formatting/test_format_artifacts.py

import pytest
import json
from mcp_server_spira.features.formatting.tools.format_artifacts import (
    format_artifacts_as_markdown
)

class TestFormatArtifactsAsMarkdown:
    """Test suite for format_artifacts_as_markdown tool."""

    @pytest.fixture
    def sample_tasks_response(self):
        """Sample tasks response with pagination."""
        return {
            "data": [
                {
                    "TaskId": 123,
                    "Name": "Fix login bug",
                    "Description": "Users cannot log in",
                    "TaskStatusName": "In Progress",
                    "TaskTypeName": "Development",
                    "TaskPriorityName": "Critical",
                    "OwnerName": "John Doe",
                    "EstimatedEffort": 120,
                    "ActualEffort": 60,
                    "CompletionPercent": 50,
                    "EndDate": "2024-01-16T17:00:00Z",
                    "ReleaseVersionNumber": "1.5.0"
                }
            ],
            "pagination": {
                "limit": 25,
                "offset": 0,
                "returned_count": 1,
                "total_count": 1,
                "has_more": False
            }
        }

    def test_format_tasks_full_response(self, sample_tasks_response):
        """Test formatting full response with pagination."""
        json_input = json.dumps(sample_tasks_response)
        result = format_artifacts_as_markdown(json_input, "task")

        assert "## Task [TK:123] - Fix login bug" in result
        assert "Users cannot log in" in result
        assert "**Status:** In Progress" in result
        assert "**Priority:** Critical" in result
        assert "60/120 min (50% complete)" in result

    def test_format_tasks_data_array_only(self):
        """Test formatting data array without pagination."""
        tasks = [
            {
                "TaskId": 1,
                "Name": "Task 1",
                "TaskStatusName": "Done",
                "TaskTypeName": "Development",
                "TaskPriorityName": "High",
                "OwnerName": "Jane Smith"
            }
        ]
        json_input = json.dumps(tasks)
        result = format_artifacts_as_markdown(json_input, "task")

        assert "## Task [TK:1] - Task 1" in result
        assert "**Status:** Done" in result

    def test_format_incidents(self):
        """Test formatting incidents."""
        incidents = {
            "data": [
                {
                    "IncidentId": 456,
                    "Name": "Login failure",
                    "Description": "Cannot authenticate",
                    "IncidentStatusName": "Open",
                    "IncidentTypeName": "Bug",
                    "PriorityName": "High",
                    "SeverityName": "Critical",
                    "OwnerName": "John Doe",
                    "StartDate": "2024-01-15T10:00:00Z",
                    "DetectedReleaseVersionNumber": "1.4.0"
                }
            ]
        }
        json_input = json.dumps(incidents)
        result = format_artifacts_as_markdown(json_input, "incident")

        assert "## Incident [IN:456] - Login failure" in result
        assert "**Severity:** Critical" in result

    def test_format_empty_list(self):
        """Test formatting empty artifact list."""
        json_input = json.dumps({"data": []})
        result = format_artifacts_as_markdown(json_input, "task")

        assert result == "No artifacts to display."

    def test_format_invalid_json(self):
        """Test error handling for invalid JSON."""
        result = format_artifacts_as_markdown("not valid json", "task")

        assert "Error: Invalid JSON input" in result

    def test_format_unknown_artifact_type(self):
        """Test error handling for unknown artifact type."""
        json_input = json.dumps({"data": [{"id": 1}]})
        result = format_artifacts_as_markdown(json_input, "unknown_type")

        assert "Error: Unknown artifact type" in result

    def test_format_missing_required_field(self):
        """Test error handling for missing required fields."""
        tasks = {"data": [{"Name": "Task without ID"}]}
        json_input = json.dumps(tasks)
        result = format_artifacts_as_markdown(json_input, "task")

        assert "Error: Missing required field" in result
```

---

## Data Flow Diagrams

### Tool Execution Flow

```
┌─────────────┐
│ LLM Request │
│ get_my_tasks│
│ (limit=25)  │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Validate Inputs  │
│ - Check limit    │
│ - Check offset   │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Get Spira Client │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ API Call         │
│ GET /tasks       │
│ (returns ALL)    │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Client-Side      │
│ Pagination       │
│ - Slice results  │
│ - Calculate meta │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Format Response  │
│ - JSON structure │
│ - 2-space indent │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Return to LLM    │
│ (JSON string)    │
└──────────────────┘
```

### Error Handling Flow

```
┌──────────────┐
│ Tool Called  │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌─────────────────┐
│ Validation   │────>│ Validation Error│
└──────┬───────┘     │ Return JSON     │
       │             └─────────────────┘
       ▼
┌──────────────┐     ┌─────────────────┐
│ API Call     │────>│ API Error       │
└──────┬───────┘     │ Return JSON     │
       │             └─────────────────┘
       ▼
┌──────────────┐     ┌─────────────────┐
│ Pagination   │────>│ Logic Error     │
└──────┬───────┘     │ Return JSON     │
       │             └─────────────────┘
       ▼
┌──────────────┐
│ Success      │
│ Return JSON  │
└──────────────┘
```



---

## Migration Strategy

### Breaking Changes

**Version Bump:** 0.5.x → 1.0.0

**Changes:**
1. Tool output format: Markdown → JSON
2. Return structure: String → `{"data": [...], "pagination": {...}}`
3. Silent truncation removed: Now explicit pagination
4. New pagination parameters: `limit`, `offset`

**What Stays the Same:**
- Tool names unchanged
- Tool discovery unchanged
- Authentication unchanged
- API endpoints unchanged

### Migration Guide for LLM Prompts

**Before (v0.5):**
```python
# LLM would receive markdown string
tasks = get_my_tasks()
# Output: "## Task [TK:123] - Fix bug\n..."
```

**After (v1.0):**
```python
# LLM receives JSON string
tasks_json = get_my_tasks()
# Output: '{"data": [{"TaskId": 123, ...}], "pagination": {...}}'

# LLM can parse and process
tasks = json.loads(tasks_json)
for task in tasks["data"]:
    if task["TaskPriorityName"] == "Critical":
        # Process critical tasks
        pass

# For display, LLM can format naturally or use formatting tool
display = format_artifacts_as_markdown(tasks_json, "task")
```

### Backward Compatibility Considerations

**Decision:** Clean break with version 1.0.0 (no compatibility mode)

**Rationale:**
- Modern LLMs adapt easily to JSON output
- Compatibility mode adds complexity to every tool
- Clear version bump signals breaking change
- Formatting tool provides fallback for complex workflows

**Migration Support:**
- Comprehensive documentation of changes
- Example prompts for common workflows
- Clear error messages if LLM uses old patterns

---

## Performance Considerations

### Client-Side Pagination Performance

**Scenario:** User has 500 tasks assigned

**Current Implementation (v0.5):**
- API call: Retrieve all 500 tasks
- Processing: Truncate to 25 silently
- Memory: Full 500 tasks in memory
- Network: ~250KB response

**New Implementation (v1.0):**
- API call: Retrieve all 500 tasks (same)
- Processing: Slice to requested limit
- Memory: Full 500 tasks in memory (same)
- Network: ~250KB response (same)
- Benefit: LLM can retrieve all data with pagination

**Performance Impact:**
- No change in API calls or network traffic
- Slightly more memory for pagination metadata (~100 bytes)
- Benefit: No hidden data, complete dataset access

**Large Dataset Handling:**
- If user has > 1000 items, API call may be slow
- Document this limitation in tool descriptions
- Recommend project-level queries for large datasets (Milestone 2+)

### JSON Serialization Performance

**Benchmark Estimates:**
- 100 tasks: ~50KB JSON, ~5ms serialization
- 500 tasks: ~250KB JSON, ~20ms serialization
- 1000 tasks: ~500KB JSON, ~40ms serialization

**Impact:** Negligible compared to network latency (100-500ms)

### Memory Usage

**Before (v0.5):**
- API response: 500 tasks in memory
- Markdown generation: Additional string allocation
- Total: ~2x task data size

**After (v1.0):**
- API response: 500 tasks in memory
- JSON serialization: Minimal additional allocation
- Pagination metadata: ~100 bytes
- Total: ~1.1x task data size

**Improvement:** Reduced memory usage by eliminating markdown generation

---

## Security Considerations

### Input Validation

**Threats Mitigated:**
- Integer overflow: Validate limit and offset ranges
- Negative values: Reject negative offsets
- Type confusion: Validate parameter types

**Validation Rules:**
- `limit`: 1-500 (prevents excessive memory usage)
- `offset`: >= 0 (prevents negative indexing)
- `product_id`: > 0 (prevents invalid API calls)

### Error Message Safety

**Principle:** Error messages should not leak sensitive information

**Safe Error Messages:**
```json
{
  "error": "Invalid product_id parameter",
  "error_code": "INVALID_PARAMETER",
  "details": {"parameter": "product_id", "value": -1, "expected": "> 0"},
  "suggestion": "Use a positive product ID"
}
```

**Unsafe Error Messages (Avoided):**
```json
{
  "error": "Database query failed: SELECT * FROM tasks WHERE user_id=123",
  "details": {"sql": "...", "connection_string": "..."}
}
```

**Guidelines:**
- Never include SQL queries or connection strings
- Never include authentication tokens or credentials
- Never include internal system paths
- Include only parameter names and expected formats

### API Error Handling

**Principle:** Wrap API errors to prevent information leakage

**Implementation:**
```python
try:
    data = spira_client.make_spira_api_get_request("tasks")
except Exception as e:
    # Don't expose raw API error
    return format_error_response(
        error="Failed to retrieve tasks",
        error_code=ErrorCodes.API_ERROR,
        details={"message": "API request failed"},  # Generic message
        suggestion="Check API connectivity and authentication"
    )
```

---

## Monitoring and Observability

### Logging Strategy

**Log Levels:**
- DEBUG: Parameter validation, pagination calculations
- INFO: Tool invocations, API calls
- WARNING: Validation failures, empty results
- ERROR: API errors, exceptions

**Log Format:**
```python
import logging

logger = logging.getLogger(__name__)

# Tool invocation
logger.info(f"get_my_tasks called: limit={limit}, offset={offset}")

# Validation failure
logger.warning(f"Validation failed: {error_dict}")

# API error
logger.error(f"API call failed: {endpoint}", exc_info=True)
```

### Metrics to Track

**Tool Usage:**
- Tool invocation count per tool
- Average response time per tool
- Error rate per tool

**Pagination:**
- Average limit value used
- Distribution of offset values
- Percentage of requests with has_more=true

**Errors:**
- Validation error count by parameter
- API error count by endpoint
- Error rate trend over time

### Health Checks

**Tool Health:**
- Can tools be registered successfully?
- Can validation utilities be imported?
- Can pagination utilities be imported?

**API Health:**
- Can SpiraClient connect to API?
- Are authentication credentials valid?
- Is API responding within acceptable time?



---

## Implementation Phases

### Phase 1: Infrastructure (Days 1-2)

**Deliverables:**
- `src/mcp_server_spira/features/common/validation.py`
- `src/mcp_server_spira/features/common/pagination.py`
- `src/mcp_server_spira/features/common/responses.py`
- `src/mcp_server_spira/features/common/errors.py`
- Unit tests for all utilities

**Acceptance Criteria:**
- All utility modules pass unit tests
- 100% test coverage for utility functions
- Documentation for each utility function

### Phase 2: Documentation Tooling (Days 3-4)

**Deliverables:**
- `scripts/generate_tool_docs.py`
- `docs/tool_documentation_report.md`
- `docs/tool_definition_guide.md`

**Acceptance Criteria:**
- Script can parse OpenAPI spec
- Script generates docstring templates
- Script identifies clarification needs
- Guide documents tool definition process

### Phase 3: MyWork Tools (Days 5-7)

**Deliverables:**
- Modified `get_my_tasks` with JSON output and pagination
- Modified `get_my_incidents` with JSON output and pagination
- Modified `get_my_requirements` with JSON output and pagination
- Modified `get_my_test_cases` with JSON output and pagination
- Modified `get_my_test_sets` with JSON output and pagination
- Comprehensive unit tests for all tools

**Acceptance Criteria:**
- All tools return valid JSON
- All tools support pagination
- All tools validate inputs
- All tools have 80%+ test coverage
- All tests pass

### Phase 4: Formatting Tool (Days 8-9)

**Deliverables:**
- `src/mcp_server_spira/features/formatting/tools/format_artifacts.py`
- Refactored formatting utilities
- Unit tests for formatting tool

**Acceptance Criteria:**
- Tool handles all 5 artifact types
- Tool handles both full responses and data arrays
- Tool has comprehensive error handling
- Tool has 80%+ test coverage

### Phase 5: Workspace Tools (Day 10)

**Deliverables:**
- Modified `get_products` with JSON output
- Modified `get_programs` with JSON output
- Modified `get_product_templates` with JSON output
- Unit tests for workspace tools

**Acceptance Criteria:**
- All tools return valid JSON
- All tools have consistent error handling
- All tools have 80%+ test coverage

### Phase 6: Documentation & Release (Days 11-12)

**Deliverables:**
- Updated README with examples
- CHANGELOG.md with breaking changes
- Migration guide for LLM prompts
- Version bump to 1.0.0
- Release notes

**Acceptance Criteria:**
- All documentation is complete
- All examples are tested
- Version is bumped correctly
- Release notes are comprehensive

---

## Design Decisions and Rationale

### Decision 1: Client-Side vs Server-Side Pagination

**Decision:** Implement client-side pagination for "my work" endpoints

**Options Considered:**
A. Client-side pagination (retrieve all, slice in Python)
B. No pagination (document limitation)
C. Wait for API update with server-side pagination

**Rationale:**
- "My work" endpoints don't support server-side pagination
- Typical result sets are < 500 items (manageable)
- Provides consistent interface across all tools
- Future milestones will add server-side pagination for project endpoints
- Better than silent truncation (current behavior)

**Trade-offs:**
- Pro: Consistent pagination interface
- Pro: No hidden data
- Pro: Simple implementation
- Con: Full API response retrieved even for small limits
- Con: May be slow for users with > 1000 items

### Decision 2: Single Generic Formatter vs Multiple Specific Formatters

**Decision:** Create one `format_artifacts_as_markdown` tool with type parameter

**Options Considered:**
A. Single generic formatter with type parameter
B. Five separate formatters (format_tasks_as_markdown, etc.)
C. No formatting tools (LLMs format naturally)

**Rationale:**
- Reduces tool count (1 vs 5)
- Simpler for LLMs to discover and use
- Easier to maintain (one implementation)
- Type parameter provides type safety
- Consistent formatting logic across artifact types

**Trade-offs:**
- Pro: Fewer tools to maintain
- Pro: Consistent interface
- Pro: Easier discovery
- Con: Slightly more complex parameter (type enum)
- Con: Single point of failure

### Decision 3: Embedded Pagination Metadata vs Separate Tool

**Decision:** Embed pagination metadata in response

**Options Considered:**
A. Embed in response: `{"data": [...], "pagination": {...}}`
B. Separate tool: `get_pagination_info()`
C. HTTP-style headers (not possible in MCP)

**Rationale:**
- Keeps data and metadata together
- Single tool call provides complete information
- Matches common API patterns (REST, GraphQL)
- Simpler for LLMs to use

**Trade-offs:**
- Pro: Single tool call
- Pro: Data and metadata together
- Pro: Standard pattern
- Con: Slightly larger response size (~100 bytes)

### Decision 4: Error Response Structure

**Decision:** Structured error responses with error_code, details, suggestion

**Options Considered:**
A. Structured errors (chosen)
B. Simple error strings
C. Exception-based errors (not possible in MCP)

**Rationale:**
- Enables programmatic error handling
- Provides actionable suggestions
- Consistent across all tools
- Helps LLMs self-correct

**Trade-offs:**
- Pro: Machine-readable error codes
- Pro: Actionable suggestions
- Pro: Consistent structure
- Con: More verbose than simple strings

### Decision 5: Version Bump Strategy

**Decision:** Clean break with version 1.0.0 (no compatibility mode)

**Options Considered:**
A. Clean break (0.5 → 1.0)
B. Add output_format parameter to all tools
C. Maintain v0.5 and v1.0 branches

**Rationale:**
- Simplest implementation
- Clear signal of breaking change
- Modern LLMs adapt easily to JSON
- Avoids complexity of compatibility mode

**Trade-offs:**
- Pro: Simple, clear
- Pro: No compatibility code
- Pro: Forces migration to better architecture
- Con: Requires users to update prompts

---

## Open Questions and Decisions

### Q1: Pagination Metadata Location

**Question:** Should pagination metadata be in response or separate tool?

**Decision:** Embed in response as `{"data": [...], "pagination": {...}}`

**Rationale:** Keeps data and metadata together, single tool call

### Q2: Client-Side Pagination for "My Work" Endpoints

**Question:** How to handle endpoints without server-side pagination?

**Decision:** Implement client-side pagination with clear documentation

**Rationale:** Provides consistent interface, acceptable for typical result sets

### Q3: Formatting Tool Input Format

**Question:** Should formatting tools accept JSON strings or Python objects?

**Decision:** JSON strings (consistent with MCP string-only interface)

**Rationale:** Maintains MCP consistency, works with tool output directly

### Q4: Error Message Detail Level

**Question:** How detailed should error messages be?

**Decision:** Detailed with error_code, details, and suggestions

**Rationale:** Helps LLMs self-correct, enables programmatic handling

### Q5: Compatibility Mode

**Question:** Should we maintain v0.5 compatibility?

**Decision:** No compatibility mode, clean break with version 1.0.0

**Rationale:** Simplest approach, clear migration path, modern LLMs adapt easily

---

## Dependencies and Prerequisites

### External Dependencies

**Required:**
- Python 3.13+
- FastMCP framework
- Existing SpiraClient implementation
- OpenAPI spec: `SpiraRestAPI-v7.0-OpenAPI.json`

**Development:**
- pytest for testing
- pytest-mock for mocking
- pytest-cov for coverage
- mypy for type checking
- ruff for linting

### Internal Dependencies

**Must be Complete:**
- Milestone 0: Development environment setup
- Milestone 0: Linting and testing infrastructure
- Milestone 0: CI/CD pipeline

**Provides Foundation For:**
- Milestone 2: Write operations (create, update, delete)
- Milestone 3: Metadata tools (status, priority, type lookups)
- Milestone 4: Advanced search and filtering
- All future tool development

---

## Success Criteria

### Functional Requirements

✅ All 8 existing tools return valid JSON
✅ All 5 "my work" tools support pagination
✅ All tools validate inputs before API calls
✅ All tools return structured error responses
✅ Formatting tool handles all 5 artifact types
✅ Documentation generator produces usable templates

### Non-Functional Requirements

✅ 80%+ test coverage for all modified code
✅ All tests pass in CI/CD pipeline
✅ JSON serialization adds < 10ms overhead
✅ Response size for 100 tasks < 500KB
✅ Tool documentation is clear and comprehensive
✅ Migration guide is complete and tested

### Quality Metrics

✅ 0 silent truncations in production
✅ < 5% of tool calls result in validation errors
✅ LLMs can successfully filter and aggregate data
✅ Developers can create new tools following patterns
✅ Human clarification requests are specific and actionable

---

## Risks and Mitigations

### Risk 1: OpenAPI Spec Incomplete or Inaccurate

**Likelihood:** Medium
**Impact:** High

**Mitigation:**
- Test all tools against real API
- Document discrepancies between spec and reality
- Create issue tracker for spec improvements
- Maintain manual overrides for known issues

### Risk 2: Breaking Changes Affect LLM Workflows

**Likelihood:** Medium
**Impact:** High

**Mitigation:**
- Keep tool names unchanged
- Provide comprehensive migration guide
- Add formatting tools before removing markdown output
- Version the MCP server clearly (1.0.0)
- Document breaking changes in CHANGELOG

### Risk 3: Client-Side Pagination Performance Issues

**Likelihood:** Low
**Impact:** Medium

**Mitigation:**
- Document performance implications clearly
- Recommend project-level queries for large datasets
- Plan server-side pagination for Milestone 2+
- Monitor performance metrics

### Risk 4: Too Many Clarification Requests

**Likelihood:** Medium
**Impact:** Medium

**Mitigation:**
- Batch clarification requests by tool
- Prioritize critical ambiguities
- Make reasonable assumptions and document them
- Create FAQ document for common questions

---

## Future Enhancements

### Milestone 2+: Server-Side Pagination

For project-level endpoints that support `start_row` and `number_rows`:

```python
def get_project_tasks(
    product_id: int,
    limit: int = 25,
    offset: int = 0
) -> str:
    """Get tasks for a project with server-side pagination."""
    # Map limit/offset to start_row/number_rows
    start_row = offset + 1  # Spira uses 1-based indexing
    number_rows = limit

    # API call with pagination parameters
    tasks = spira_client.make_spira_api_get_request(
        f"projects/{product_id}/tasks",
        params={"start_row": start_row, "number_rows": number_rows}
    )

    # Get total count from response header or separate call
    total_count = get_total_count(product_id, "tasks")

    # Use server-side pagination helper
    result = paginate_server_side(tasks, limit, offset, total_count)

    return format_success_response(
        data=result["data"],
        pagination=result["pagination"]
    )
```

### Milestone 3+: Field Selection

Allow LLMs to request specific fields:

```python
def get_my_tasks(
    limit: int = 25,
    offset: int = 0,
    fields: List[str] = None  # NEW: Optional field selection
) -> str:
    """Get tasks with optional field selection."""
    all_tasks = spira_client.make_spira_api_get_request("tasks")

    # Filter fields if requested
    if fields:
        all_tasks = [
            {k: v for k, v in task.items() if k in fields}
            for task in all_tasks
        ]

    result = paginate_client_side(all_tasks, limit, offset)
    return format_success_response(data=result["data"], pagination=result["pagination"])
```

### Milestone 4+: Response Caching

Cache responses for frequently accessed data:

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=100)
def get_cached_tasks(user_id: str, cache_key: str) -> List[dict]:
    """Get tasks with caching."""
    return spira_client.make_spira_api_get_request("tasks")

def get_my_tasks(limit: int = 25, offset: int = 0) -> str:
    """Get tasks with caching."""
    user_id = get_current_user_id()
    cache_key = f"{datetime.now().strftime('%Y%m%d%H%M')}"  # 1-minute cache

    all_tasks = get_cached_tasks(user_id, cache_key)
    result = paginate_client_side(all_tasks, limit, offset)
    return format_success_response(data=result["data"], pagination=result["pagination"])
```

---

## Appendix: Complete Tool Signatures

### MyWork Tools

```python
def get_my_tasks(limit: int = 25, offset: int = 0) -> str: ...
def get_my_incidents(limit: int = 25, offset: int = 0) -> str: ...
def get_my_requirements(limit: int = 25, offset: int = 0) -> str: ...
def get_my_test_cases(limit: int = 25, offset: int = 0) -> str: ...
def get_my_test_sets(limit: int = 25, offset: int = 0) -> str: ...
```

### Workspace Tools

```python
def get_products() -> str: ...
def get_programs() -> str: ...
def get_product_templates() -> str: ...
```

### Formatting Tools

```python
def format_artifacts_as_markdown(
    artifact_json: str,
    artifact_type: Literal["task", "incident", "requirement", "test_case", "test_set"]
) -> str: ...
```

---

## Appendix: Error Code Reference

| Error Code | Description | Example |
|------------|-------------|---------|
| INVALID_PARAMETER | Parameter validation failed | limit=1000 (exceeds max) |
| INVALID_TYPE | Parameter has wrong type | limit="abc" (not int) |
| INVALID_VALUE | Parameter value out of range | offset=-1 (negative) |
| API_ERROR | Spira API call failed | Network timeout |
| NOT_FOUND | Resource not found | Task ID doesn't exist |
| AUTHENTICATION_ERROR | Auth credentials invalid | Token expired |
| PERMISSION_DENIED | User lacks permission | Cannot access product |
| RATE_LIMIT_EXCEEDED | Too many requests | API rate limit hit |

---

**End of Design Document**
