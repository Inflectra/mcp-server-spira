# Tool Definition Guide

**Version:** 1.0
**Last Updated:** 2026-02-05
**Purpose:** Systematic approach to creating MCP tool definitions from OpenAPI specifications

---

## Overview

This guide provides a systematic process for creating high-quality MCP tool definitions from the Spira OpenAPI specification. It ensures consistency, completeness, and clarity across all tools while establishing clear criteria for when to seek human clarification.

**Key Principles:**
1. **JSON-First:** All data-retrieval tools return structured JSON
2. **Explicit Pagination:** Never truncate results silently
3. **Comprehensive Documentation:** Rich docstrings with examples
4. **Input Validation:** Validate before API calls
5. **Structured Errors:** Consistent error response format

---

## Tool Definition Process

### Step 1: Identify the API Endpoint

Start by locating the relevant endpoint in `SpiraRestAPI-v7.0-OpenAPI.json`:

```json
{
  "paths": {
    "/projects/{project_id}/tasks/{task_id}": {
      "get": {
        "operationId": "Task_RetrieveById",
        "summary": "Retrieves a single task by its ID",
        "parameters": [...],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/RemoteTask"
                }
              }
            }
          }
        }
      }
    }
  }
}
```

**Extract:**
- Path and HTTP method
- Operation ID and summary
- Parameters (path, query, body)
- Response schema reference
- Error responses

### Step 2: Extract Schema Information

Locate the response schema in the `components/schemas` section:

```json
{
  "components": {
    "schemas": {
      "RemoteTask": {
        "type": "object",
        "properties": {
          "TaskId": {
            "type": "integer",
            "nullable": true,
            "description": "The id of the task"
          },
          "Name": {
            "type": "string",
            "nullable": true,
            "description": "The name of the task"
          },
          "EstimatedEffort": {
            "type": "integer",
            "nullable": true,
            "description": "The originally estimated effort (in minutes) of the task"
          }
        }
      }
    }
  }
}
```

**Extract:**
- All property names and types
- Nullable vs required fields
- Field descriptions
- Nested objects and arrays
- Enum values

### Step 3: Design the Tool Signature

Create the Python function signature with appropriate parameters:

```python
@mcp.tool()
def get_task_by_id(product_id: int, task_id: int) -> str:
    """Tool implementation"""
```

**Guidelines:**
- Use descriptive parameter names (not just `id`)
- Include type hints for all parameters
- Return type is always `str` (JSON string)
- Add pagination parameters for list operations (`limit`, `offset`)
- Use default values where appropriate

### Step 4: Write the Docstring

Use the comprehensive docstring template (see Template section below).

**Required Sections:**
1. One-line summary
2. API mapping (endpoint reference)
3. Detailed description and use cases
4. Args section with parameter documentation
5. Returns section with JSON structure example
6. Key Fields section explaining important fields
7. When to Use section with scenarios
8. Related Tools section
9. Error Responses section with examples
10. Example Usage section

### Step 5: Implement the Tool Logic

Follow the standard implementation pattern:

```python
def register_tools(mcp) -> None:
    """Register tools with MCP server."""

    @mcp.tool()
    def get_task_by_id(product_id: int, task_id: int) -> str:
        """[Comprehensive docstring here]"""
        try:
            # 1. Validate inputs
            validation_error = ParameterValidator.validate_positive_integer(
                product_id, "product_id"
            )
            if validation_error:
                return format_error_response(**validation_error)

            validation_error = ParameterValidator.validate_positive_integer(
                task_id, "task_id"
            )
            if validation_error:
                return format_error_response(**validation_error)

            # 2. Get Spira client
            spira_client = get_spira_client()

            # 3. Make API call
            task = spira_client.make_spira_api_get_request(
                f"projects/{product_id}/tasks/{task_id}"
            )

            # 4. Return formatted response
            return format_success_response(data=task)

        except Exception as e:
            return format_error_response(
                error="Failed to retrieve task",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check product_id and task_id are valid"
            )
```

### Step 6: Identify Clarification Needs

Review the tool definition and flag any ambiguities (see Clarification Scenarios section below).

### Step 7: Write Unit Tests

Create comprehensive unit tests:

```python
def test_get_task_by_id_success(mock_spira_client):
    """Test successful task retrieval."""
    mock_spira_client.make_spira_api_get_request.return_value = {
        "TaskId": 40,
        "Name": "Fix login bug"
    }

    result = get_task_by_id(55, 40)
    data = json.loads(result)

    assert "data" in data
    assert data["data"]["TaskId"] == 40

def test_get_task_by_id_invalid_product_id(mock_spira_client):
    """Test validation error for invalid product_id."""
    result = get_task_by_id(-1, 40)
    data = json.loads(result)

    assert "error" in data
    assert data["error_code"] == "INVALID_VALUE"
```

---

## Docstring Template

Use this template for all tools:

```python
@mcp.tool()
def tool_name(param1: type, param2: type = default) -> str:
    """
    [One-line summary of what the tool does]

    Maps to Spira API: [HTTP_METHOD] [/endpoint/path]

    [2-3 sentences describing the tool's purpose and when to use it.
    Include context about what data it returns and typical use cases.]

    **Pagination:** [If applicable, explain pagination type and limitations]

    **For Display:** [If applicable, explain when to use formatting vs natural LLM formatting]

    Args:
        param1: [Description of parameter]
            [Additional context about valid values, format, or constraints]
        param2: [Description of parameter] (default: [value])
            [Additional context]

    Returns:
        JSON string with structure:
        {
            "data": [
                {
                    "Field1": value,
                    "Field2": value,
                    "Field3": value
                }
            ],
            "pagination": {  // Only for paginated responses
                "limit": 25,
                "offset": 0,
                "returned_count": 25,
                "total_count": 150,
                "has_more": true,
                "pagination_type": "client-side"
            }
        }

    Key Fields:
        - Field1: [Explanation of what this field represents and when it's used]
        - Field2: [Explanation with context about relationships or calculations]
        - Field3: [Explanation of special values or edge cases]

    When to Use:
        - [Scenario 1: Specific use case]
        - [Scenario 2: Another use case]
        - [Scenario 3: When to use this vs related tools]

    Related Tools:
        - tool_name_1: [Brief description of relationship]
        - tool_name_2: [Brief description of relationship]

    Error Responses:
        {
            "error": "[Human-readable error message]",
            "error_code": "[MACHINE_READABLE_CODE]",
            "details": {
                "parameter": "[param_name]",
                "value": [invalid_value],
                "expected": "[expected_format]"
            },
            "suggestion": "[Actionable suggestion for fixing the error]"
        }

    Example Usage:
        # [Comment describing the scenario]
        result_json = tool_name(param1, param2)
        data = json.loads(result_json)
        # [Show how to use the returned data]

        # [Another example for a different scenario]
        filtered_json = tool_name(param1, param2=custom_value)
        # [Show processing or filtering]
    """
```

---

## Field Documentation Guidelines

### Extracting Field Information from OpenAPI

For each field in the response schema:

1. **Basic Information:**
   - Name (exact case from API)
   - Type (integer, string, boolean, array, object)
   - Nullable (can it be null?)
   - Description from OpenAPI spec

2. **Enhanced Documentation:**
   - **Purpose:** What does this field represent?
   - **When Used:** When is it populated vs null?
   - **Relationships:** Does it reference another artifact?
   - **Calculations:** Is it computed from other fields?
   - **Units:** For numeric fields (minutes, hours, percentage)
   - **Format:** For dates, strings (ISO 8601, etc.)

### Example: Documenting Task Effort Fields

**From OpenAPI:**
```json
{
  "EstimatedEffort": {
    "type": "integer",
    "nullable": true,
    "description": "The originally estimated effort (in minutes) of the task"
  },
  "ActualEffort": {
    "type": "integer",
    "nullable": true,
    "description": "The actual effort (in minutes) of the task"
  },
  "RemainingEffort": {
    "type": "integer",
    "nullable": true,
    "description": "The remaining effort (in minutes) of the task"
  },
  "ProjectedEffort": {
    "type": "integer",
    "nullable": true,
    "description": "The projected effort (in minutes) of the task"
  }
}
```

**Enhanced Documentation:**
```
Key Fields:
    - EstimatedEffort: Original estimate in minutes (set at task creation, doesn't change)
    - ActualEffort: Time logged so far in minutes (increases as work progresses)
    - RemainingEffort: Developer's estimate of time remaining (updated manually)
    - ProjectedEffort: Calculated as ActualEffort + RemainingEffort (auto-computed)
    - CompletionPercent: Calculated as (ActualEffort / ProjectedEffort) * 100
```

**Why This Matters:**
- LLMs need to understand the difference between these similar fields
- Knowing which fields are calculated vs manual helps with data integrity
- Understanding the workflow (estimate → actual → remaining → projected) enables better tool usage

---

## Scenarios Requiring Human Clarification

### 1. Ambiguous or Missing Field Descriptions

**Trigger:** OpenAPI description is vague, generic, or missing

**Example:**
```json
{
  "TaskId": {
    "type": "integer",
    "nullable": true,
    "description": "The id of the task"
  }
}
```

**Problem:** "The id of the task" doesn't explain:
- When would TaskId be null?
- Is this the same as the task number in the UI (TK:40)?
- Is this unique across all products or just within a product?

**Clarification Request:**
```
Question: TaskId field clarification needed

Context: The OpenAPI spec describes TaskId as "The id of the task" which is generic.

Specific Questions:
1. When would TaskId be null? (Only for unsaved tasks? Never?)
2. Is TaskId the same as the task number shown in the UI (e.g., TK:40)?
3. Is TaskId unique globally or only within a product?
4. Should LLMs use TaskId or some other identifier when referencing tasks?

OpenAPI Reference: RemoteTask.TaskId
```

### 2. Multiple Similar Fields

**Trigger:** Several fields with similar names or purposes

**Example:**
```json
{
  "TaskStatusId": {"type": "integer"},
  "TaskStatusName": {"type": "string"},
  "TaskTypeId": {"type": "integer"},
  "TaskTypeName": {"type": "string"}
}
```

**Problem:** When should LLMs use ID vs Name?

**Clarification Request:**
```
Question: When to use ID vs Name fields?

Context: Many artifacts have both ID and Name fields (TaskStatusId/TaskStatusName, etc.)

Specific Questions:
1. Should LLMs filter/search by ID or Name?
2. Are Names guaranteed to be unique within a product?
3. Can Names change over time (making ID more stable)?
4. What's the performance difference between filtering by ID vs Name?
5. Should tool documentation recommend one over the other?

OpenAPI Reference: RemoteTask.TaskStatusId, RemoteTask.TaskStatusName
```

### 3. Business Logic and Workflows

**Trigger:** Unclear how fields relate to business processes

**Example:**
```json
{
  "StartDate": {"type": "string", "format": "date-time"},
  "EndDate": {"type": "string", "format": "date-time"},
  "CreationDate": {"type": "string", "format": "date-time"}
}
```

**Problem:** What's the difference between these dates?

**Clarification Request:**
```
Question: Task date fields - meaning and usage

Context: Tasks have StartDate, EndDate, and CreationDate fields.

Specific Questions:
1. StartDate: Is this when work should begin or when it actually began?
2. EndDate: Is this a deadline or actual completion date?
3. Can StartDate be in the future (scheduled work)?
4. What happens to EndDate when a task is completed early/late?
5. Should LLMs use these dates for "overdue" calculations?

OpenAPI Reference: RemoteTask.StartDate, RemoteTask.EndDate
```

### 4. Data Relationships

**Trigger:** Fields reference other artifacts but relationship is unclear

**Example:**
```json
{
  "RequirementId": {"type": "integer", "nullable": true},
  "RequirementName": {"type": "string", "nullable": true},
  "ReleaseId": {"type": "integer", "nullable": true},
  "ReleaseVersionNumber": {"type": "string", "nullable": true}
}
```

**Problem:** How do these relationships work?

**Clarification Request:**
```
Question: Task relationship fields - when populated and how to use

Context: Tasks can be linked to Requirements and Releases.

Specific Questions:
1. Can a task be linked to multiple requirements? (Or just one?)
2. Is RequirementId/Name always populated or only when linked?
3. Does ReleaseId represent a sprint/iteration assignment?
4. Should LLMs retrieve related requirement/release data separately or is this sufficient?
5. What's the recommended workflow for linking tasks to requirements?

OpenAPI Reference: RemoteTask.RequirementId, RemoteTask.ReleaseId
```

### 5. Edge Cases and Special Values

**Trigger:** Unclear behavior with null, empty, or special values

**Example:**
```json
{
  "CompletionPercent": {
    "type": "integer",
    "nullable": true,
    "description": "The completion percentage of the task"
  }
}
```

**Problem:** What do different values mean?

**Clarification Request:**
```
Question: CompletionPercent field - calculation and edge cases

Context: CompletionPercent field represents task progress.

Specific Questions:
1. Is this calculated automatically or set manually?
2. If calculated, what's the formula? (ActualEffort / ProjectedEffort)?
3. What does null mean? (Not started? No estimate?)
4. Can it exceed 100%? (If actual > estimated?)
5. Should LLMs trust this value or calculate their own?

OpenAPI Reference: RemoteTask.CompletionPercent
```

### 6. Performance and Best Practices

**Trigger:** Unclear performance implications or recommended usage patterns

**Example:**
```json
{
  "CustomProperties": {
    "type": "array",
    "items": {"$ref": "#/components/schemas/RemoteCustomProperty"}
  }
}
```

**Problem:** Should this always be retrieved?

**Clarification Request:**
```
Question: CustomProperties field - performance and usage recommendations

Context: Tasks include a CustomProperties array with custom field data.

Specific Questions:
1. How many custom properties does a typical task have?
2. Is there a performance cost to retrieving custom properties?
3. Should tools retrieve custom properties by default or only when needed?
4. Can custom properties be filtered/searched efficiently?
5. What's the recommended approach for tools that don't need custom data?

OpenAPI Reference: RemoteTask.CustomProperties
```

### 7. Workflow Context

**Trigger:** Unclear when to use this tool vs related tools

**Example:**
- `get_my_tasks()` - Returns tasks assigned to current user
- `get_tasks_by_product()` - Returns all tasks in a product (future)
- `search_tasks()` - Advanced search with filters (future)

**Problem:** When should each be used?

**Clarification Request:**
```
Question: Task retrieval tools - when to use each

Context: Multiple tools will retrieve tasks with different scopes.

Specific Questions:
1. When should LLMs use get_my_tasks vs get_tasks_by_product?
2. Is get_my_tasks sufficient for personal productivity workflows?
3. Should get_tasks_by_product be used for team-level reporting?
4. When is search_tasks necessary vs simple filtering of get_my_tasks results?
5. Are there performance differences between these approaches?

Tools: get_my_tasks, get_tasks_by_product (future), search_tasks (future)
```

---

## Good vs Bad Tool Definitions

### Example 1: Task Retrieval Tool

#### ❌ BAD - Minimal Documentation

```python
@mcp.tool()
def get_task(product_id: int, task_id: int) -> str:
    """Gets a task."""
    spira_client = get_spira_client()
    task = spira_client.make_spira_api_get_request(
        f"projects/{product_id}/tasks/{task_id}"
    )
    return json.dumps(task)
```

**Problems:**
- No parameter descriptions
- No return value documentation
- No error handling
- No usage examples
- No field explanations
- No validation

#### ✅ GOOD - Comprehensive Documentation

```python
@mcp.tool()
def get_task_by_id(product_id: int, task_id: int) -> str:
    """
    Retrieves a single task by its ID.

    Maps to Spira API: GET /projects/{project_id}/tasks/{task_id}

    Returns complete details for a specific task including status, effort tracking,
    assignments, and relationships to requirements and releases. Use this when you
    need full details for a single task rather than a list of tasks.

    Args:
        product_id: The numeric ID of the product (e.g., 55 for PR:55)
            This is the ProjectId field from get_products()
        task_id: The numeric ID of the task (e.g., 40 for TK:40)
            This is the TaskId field from get_my_tasks() or other task lists

    Returns:
        JSON string with structure:
        {
            "data": {
                "TaskId": 40,
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
                "RequirementId": 45,
                "RequirementName": "User Authentication",
                "ReleaseId": 10,
                "ReleaseVersionNumber": "1.5.0"
            }
        }

    Key Fields:
        - TaskId: Unique identifier for the task
        - EstimatedEffort: Original estimate in minutes (set at creation)
        - ActualEffort: Time logged so far in minutes
        - RemainingEffort: Developer's estimate of time remaining
        - ProjectedEffort: Calculated as ActualEffort + RemainingEffort
        - CompletionPercent: Calculated as (ActualEffort / ProjectedEffort) * 100
        - RequirementId/Name: Parent requirement link (null if not linked)
        - ReleaseId/VersionNumber: Sprint/iteration assignment (null if not assigned)

    When to Use:
        - Getting full details for a specific task
        - Retrieving task after creation to confirm details
        - Checking current status and effort tracking
        - Getting task data for update operations

    Related Tools:
        - get_my_tasks: Get list of tasks assigned to current user
        - get_products: Get product_id values
        - format_artifacts_as_markdown: Format task for display

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

        {
            "error": "Task not found",
            "error_code": "NOT_FOUND",
            "details": {
                "product_id": 55,
                "task_id": 999
            },
            "suggestion": "Check that task_id exists in this product"
        }

    Example Usage:
        # Get task details
        task_json = get_task_by_id(product_id=55, task_id=40)
        task = json.loads(task_json)["data"]
        print(f"Task: {task['Name']}")
        print(f"Status: {task['TaskStatusName']}")
        print(f"Progress: {task['CompletionPercent']}%")

        # Check if task is overdue
        from datetime import datetime
        end_date = datetime.fromisoformat(task['EndDate'].replace('Z', '+00:00'))
        if end_date < datetime.now() and task['TaskStatusName'] != 'Completed':
            print("Task is overdue!")
    """
    try:
        # Validate inputs
        validation_error = ParameterValidator.validate_positive_integer(
            product_id, "product_id"
        )
        if validation_error:
            return format_error_response(**validation_error)

        validation_error = ParameterValidator.validate_positive_integer(
            task_id, "task_id"
        )
        if validation_error:
            return format_error_response(**validation_error)

        # Get Spira client
        spira_client = get_spira_client()

        # Make API call
        task = spira_client.make_spira_api_get_request(
            f"projects/{product_id}/tasks/{task_id}"
        )

        # Return formatted response
        return format_success_response(data=task)

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve task",
            error_code=ErrorCodes.API_ERROR,
            details={
                "message": str(e),
                "product_id": product_id,
                "task_id": task_id
            },
            suggestion="Check that product_id and task_id are valid and you have access"
        )
```

**Why This is Good:**
- Clear one-line summary
- API endpoint reference
- Detailed parameter descriptions with examples
- Complete return value structure
- Field-level documentation with context
- Multiple usage scenarios
- Related tools for discovery
- Comprehensive error examples
- Practical usage examples with code
- Input validation
- Structured error handling

---

## Checklist for Tool Definitions

Use this checklist to ensure completeness:

### Documentation
- [ ] One-line summary is clear and specific
- [ ] API endpoint is documented (HTTP method + path)
- [ ] All parameters have descriptions with examples
- [ ] Return value structure is shown with example JSON
- [ ] Key fields are explained with context
- [ ] "When to Use" section lists 3-5 scenarios
- [ ] Related tools are listed with brief descriptions
- [ ] Error responses show structure with examples
- [ ] Example usage includes 2-3 realistic scenarios
- [ ] Pagination type is documented (if applicable)
- [ ] Display guidance is provided (if applicable)

### Implementation
- [ ] All parameters have type hints
- [ ] Input validation is performed before API calls
- [ ] Spira client is obtained correctly
- [ ] API call uses correct endpoint and method
- [ ] Response is formatted using format_success_response()
- [ ] Errors are caught and formatted using format_error_response()
- [ ] Error responses include actionable suggestions

### Testing
- [ ] Unit test for successful operation
- [ ] Unit test for each validation error
- [ ] Unit test for API errors
- [ ] Unit test for edge cases (null values, empty results)
- [ ] Tests use mocked SpiraClient
- [ ] Tests verify JSON structure

### Clarification
- [ ] Ambiguous field descriptions are flagged
- [ ] Similar fields are differentiated
- [ ] Business logic is clear
- [ ] Data relationships are explained
- [ ] Edge cases are documented
- [ ] Performance implications are noted
- [ ] Workflow context is provided

---

## Automation with generate_tool_docs.py

The `scripts/generate_tool_docs.py` script automates much of this process:

### What It Does

1. **Parses OpenAPI Spec:** Extracts endpoint and schema information
2. **Generates Docstring Templates:** Creates structured docstrings with parameter info
3. **Identifies Clarifications:** Flags ambiguous or missing information
4. **Outputs Review Document:** Creates markdown for human review

### How to Use

```bash
# Generate documentation for all endpoints
python scripts/generate_tool_docs.py

# Generate documentation for specific endpoints
python scripts/generate_tool_docs.py --endpoints tasks incidents

# Output to specific file
python scripts/generate_tool_docs.py --output docs/tool_docs_review.md
```

### Review Process

1. **Run the script** to generate initial documentation
2. **Review generated docstrings** for accuracy
3. **Answer clarification questions** with domain knowledge
4. **Add workflow context** and "when to use" guidance
5. **Add realistic examples** based on actual use cases
6. **Validate against API** by testing with real data

### What Requires Human Input

The script cannot determine:
- **Workflow context:** When to use this tool vs related tools
- **Business logic:** How fields relate to business processes
- **Best practices:** Recommended usage patterns
- **Performance implications:** Which operations are expensive
- **Edge cases:** Behavior with unusual inputs
- **Realistic examples:** Actual use cases from domain knowledge

---

## Summary

Creating high-quality tool definitions requires:

1. **Systematic extraction** of information from OpenAPI spec
2. **Comprehensive documentation** using the standard template
3. **Clear identification** of ambiguities requiring human input
4. **Thorough testing** of all scenarios
5. **Validation** against real API behavior

By following this guide, you ensure consistency, completeness, and clarity across all MCP tools, enabling LLMs to use them effectively without trial and error.

---

## Quick Reference

### Essential Imports

```python
from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.validation import ParameterValidator
from mcp_server_spira.features.common.pagination import paginate_client_side
from mcp_server_spira.features.common.responses import (
    format_success_response,
    format_error_response,
    ErrorCodes
)
import json
```

### Standard Tool Pattern

```python
@mcp.tool()
def tool_name(param: type) -> str:
    """[Comprehensive docstring]"""
    try:
        # 1. Validate
        error = ParameterValidator.validate_positive_integer(param, "param")
        if error:
            return format_error_response(**error)

        # 2. Get client
        spira_client = get_spira_client()

        # 3. API call
        data = spira_client.make_spira_api_get_request("endpoint")

        # 4. Return
        return format_success_response(data=data)

    except Exception as e:
        return format_error_response(
            error="Operation failed",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e)},
            suggestion="Check parameters and try again"
        )
```

### When to Ask for Clarification

Ask when you encounter:
- Vague or missing field descriptions
- Multiple similar fields without clear differentiation
- Unclear business logic or workflows
- Complex data relationships
- Ambiguous edge case behavior
- Unknown performance implications
- Unclear tool usage scenarios

**Always provide:**
- Specific questions with context
- Reference to OpenAPI spec location
- Examples of the ambiguity
- Why it matters for tool usage
