# Milestone 1: Fix Existing Tools - Requirements

**Feature Name:** milestone-1-fix-existing-tools
**Version:** 1.0
**Status:** Draft
**Created:** 2026-02-05
**Owner:** Development Team

---

## Overview

Transform existing MCP tools from markdown-based output to JSON-first architecture while improving tool definitions, documentation, and usability. This milestone establishes the foundation for all future tool development by creating clear patterns for tool implementation, documentation generation from OpenAPI specs, and optional markdown formatting.

**Parent Document:** [SPIRA_MCP_ENHANCEMENT_MASTER_PLAN.md](../../../SPIRA_MCP_ENHANCEMENT_MASTER_PLAN.md)

---

## Goals

1. Convert all existing tools to return structured JSON by default
2. Add explicit pagination parameters to all list operations
3. Implement comprehensive input validation with clear error messages
4. Create optional JSON-to-Markdown formatting tools
5. Generate rich tool definitions and examples from OpenAPI spec
6. Establish patterns for future tool development
7. Achieve 80%+ test coverage for all modified tools
8. Optimize tool documentation for efficient LLM parsing and reduced token usage

---

## User Stories

### US-1.1: As an LLM, I need structured JSON data for processing
**Priority:** Critical
**Story Points:** 5

I want all data-retrieval tools to return JSON so that I can filter, sort, aggregate, and compose operations programmatically.

**Acceptance Criteria:**
- AC-1.1.1: `get_my_tasks` returns valid JSON array of task objects
- AC-1.1.2: `get_my_incidents` returns valid JSON array of incident objects
- AC-1.1.3: `get_my_requirements` returns valid JSON array of requirement objects
- AC-1.1.4: `get_my_test_cases` returns valid JSON array of test case objects
- AC-1.1.5: `get_my_test_sets` returns valid JSON array of test set objects
- AC-1.1.6: All workspace tools (products, programs, templates) return JSON
- AC-1.1.7: JSON output is properly formatted with 2-space indentation
- AC-1.1.8: All fields from the OpenAPI schema are preserved in output
- AC-1.1.9: Null values are represented as JSON null, not empty strings
- AC-1.1.10: Date/time values maintain ISO 8601 format from API

**Rationale:** LLMs need structured data to perform operations like filtering by status, sorting by priority, or aggregating effort estimates. Markdown output forces string parsing which is error-prone and limits functionality.

---

### US-1.2: As a user, I want optional markdown formatting for complex workflows
**Priority:** Medium
**Story Points:** 2

I want the ability to convert JSON data to human-readable markdown for complex workflows where I've filtered or processed the data, without losing the JSON-first architecture.

**Acceptance Criteria:**
- AC-1.2.1: A new tool `format_artifacts_as_markdown` accepts JSON and artifact type, returns markdown
- AC-1.2.2: Formatting tool handles tasks, incidents, requirements, test cases, test sets
- AC-1.2.3: Formatting tool preserves all critical information from JSON
- AC-1.2.4: Formatting tool uses consistent markdown structure per artifact type
- AC-1.2.5: Formatting tool handles arrays of items (batch formatting)
- AC-1.2.6: Formatting tool handles single items
- AC-1.2.7: Tool description clearly explains when to use formatting vs natural LLM formatting
- AC-1.2.8: Tool description emphasizes use for **filtered/processed** data
- AC-1.2.9: Data retrieval tools note that LLMs can format JSON naturally for simple display
- AC-1.2.10: Tool descriptions include examples of both simple and complex workflows

**Rationale:**
- Modern LLMs can format JSON naturally for simple display
- Formatting tool is valuable for **filtered/processed** results where you can't re-call the API
- Single generic formatter is simpler than 5 separate tools
- Positions formatting as utility for complex workflows, not requirement for basic display

**When Formatting Tool is Needed:**
- After filtering JSON (can't re-call API with filters)
- After aggregating or sorting data
- When consistent formatting is critical
- When processing multiple artifact types together

**When Formatting Tool is NOT Needed:**
- Simple "show me my tasks" requests (LLM formats naturally)
- Direct display without processing
- When LLM formatting quality is acceptable

---
### US-1.3: As an LLM, I need explicit pagination controls (client-side)
**Priority:** High
**Story Points:** 2

I want all list operations to expose pagination parameters so that I can control result set size and retrieve data in manageable chunks, even though the underlying API doesn't support server-side pagination.

**Acceptance Criteria:**
- AC-1.3.1: All "get_my_*" tools accept `limit` parameter (default: 25, max: 500)
- AC-1.3.2: All "get_my_*" tools accept `offset` parameter (default: 0)
- AC-1.3.3: Tools return metadata about pagination (total_count, returned_count, has_more)
- AC-1.3.4: Tools never silently truncate results without pagination metadata
- AC-1.3.5: Tool descriptions explain pagination parameters clearly
- AC-1.3.6: Tool descriptions explicitly state this is CLIENT-SIDE pagination
- AC-1.3.7: Invalid pagination parameters return clear error messages
- AC-1.3.8: Response includes pagination info with `pagination_type: "client-side"` indicator
- AC-1.3.9: Performance implications are documented (API returns all results)
- AC-1.3.10: Tool descriptions note that large result sets may be slow

**Rationale:**
Silent truncation (current behavior: `[:25]`) hides data from the LLM and prevents retrieving complete datasets. While the Spira API endpoints for "my work" (`/tasks`, `/incidents`, `/requirements`, `/test-cases`, `/test-sets`) do NOT support server-side pagination, we can still provide a consistent pagination interface by implementing it client-side. This is acceptable because "my work" queries typically return manageable result sets (< 1000 items).

**Implementation Note:**
This is CLIENT-SIDE pagination implemented in Python:
1. Retrieve ALL results from API (one call)
2. Slice results: `all_results[offset:offset+limit]`
3. Calculate pagination metadata from full result set
4. Return sliced data with metadata

This is simpler than server-side pagination but provides the same interface. Future milestones will implement true server-side pagination for project-level endpoints that support `start_row` and `number_rows` parameters.

**Performance Consideration:**
If a user has > 1000 items, the initial API call may be slow. This is documented in tool descriptions with a recommendation to use project-level queries (future milestones) for large datasets.

---

### US-1.4: As an LLM, I need comprehensive input validation
**Priority:** High
**Story Points:** 2

I want all tools to validate inputs before making API calls so that I receive clear, actionable error messages instead of cryptic API failures.

**Acceptance Criteria:**
- AC-1.4.1: All product_id parameters are validated (must be positive integer)
- AC-1.4.2: All artifact ID parameters are validated (must be positive integer)
- AC-1.4.3: Pagination parameters are validated (limit: 1-500, offset: >= 0)
- AC-1.4.4: Required parameters are checked before API calls
- AC-1.4.5: Validation errors return structured JSON with error details
- AC-1.4.6: Error responses include the invalid value and expected format
- AC-1.4.7: Error responses include suggestions for correction
- AC-1.4.8: Custom exception classes for different error types
- AC-1.4.9: All validation logic is unit tested

**Rationale:** Clear validation errors help LLMs self-correct and reduce failed API calls. Structured error responses enable programmatic error handling.

---

### US-1.5: As an LLM, I need rich tool definitions with clear examples
**Priority:** High
**Story Points:** 5

I want tool docstrings to include comprehensive information about parameters, return values, and usage examples so that I can use tools correctly without trial and error.

**Acceptance Criteria:**
- AC-1.5.1: Every tool has a clear one-line summary
- AC-1.5.2: Every tool documents all parameters with types and descriptions
- AC-1.5.3: Every tool documents return value structure with example JSON
- AC-1.5.4: Every tool includes "When to use this tool" section
- AC-1.5.5: Every tool includes "Example Response" section with real data structure
- AC-1.5.6: Every tool documents error conditions and error response format
- AC-1.5.7: Tool descriptions reference OpenAPI spec field descriptions
- AC-1.5.8: Tool descriptions explain relationship to API endpoints
- AC-1.5.9: Tool descriptions include field-level documentation from OpenAPI
- AC-1.5.10: A script generates tool documentation from OpenAPI spec

**Rationale:** Rich documentation reduces LLM errors and improves tool discovery. Generating documentation from OpenAPI spec ensures accuracy and consistency.

---

### US-1.6: As a developer, I need a systematic approach to tool documentation
**Priority:** High
**Story Points:** 5

I want a documented process for creating tool definitions from OpenAPI specs so that all future tools follow consistent patterns and include complete information.

**Acceptance Criteria:**
- AC-1.6.1: A `docs/tool_definition_guide.md` document exists
- AC-1.6.2: Guide explains how to extract endpoint info from OpenAPI spec
- AC-1.6.3: Guide provides template for tool docstrings
- AC-1.6.4: Guide explains how to document parameters from OpenAPI
- AC-1.6.5: Guide explains how to document response schemas from OpenAPI
- AC-1.6.6: Guide includes examples of good vs bad tool definitions
- AC-1.6.7: Guide explains when to ask humans for clarification
- AC-1.6.8: A Python script `scripts/generate_tool_docs.py` automates documentation
- AC-1.6.9: Script can extract endpoint details from OpenAPI JSON
- AC-1.6.10: Script generates docstring templates with parameter info
- AC-1.6.11: Script identifies fields that need human clarification
- AC-1.6.12: Script outputs markdown documentation for review

**Rationale:** Systematic documentation ensures consistency and quality. Automation reduces manual effort and errors.

---

### US-1.7: As a developer, I need clear guidance on when to ask for human input
**Priority:** Medium
**Story Points:** 2

I want explicit criteria for when AI should ask humans for clarification during tool definition creation so that I can work autonomously when possible and seek help when needed.

**Acceptance Criteria:**
- AC-1.7.1: Guide lists scenarios requiring human clarification
- AC-1.7.2: Ambiguous OpenAPI descriptions trigger clarification request
- AC-1.7.3: Missing parameter descriptions trigger clarification request
- AC-1.7.4: Complex nested schemas trigger clarification request
- AC-1.7.5: Business logic questions trigger clarification request
- AC-1.7.6: Unclear "when to use" scenarios trigger clarification request
- AC-1.7.7: Clarification requests include specific questions and context
- AC-1.7.8: Clarification requests reference OpenAPI spec sections
- AC-1.7.9: Script generates clarification checklist for each tool
- AC-1.7.10: Examples of good clarification requests are documented

**Scenarios Requiring Human Clarification:**
1. **Ambiguous field purpose**: OpenAPI description is vague or missing
2. **Business logic**: When to use one field vs another (e.g., EstimatedEffort vs ProjectedEffort)
3. **Workflow context**: When to use this tool vs related tools
4. **Data relationships**: How fields relate to other artifacts
5. **Edge cases**: Behavior with null values, empty arrays, or special states
6. **Performance implications**: Whether to retrieve related data or make separate calls
7. **Security/permissions**: What permissions are needed to use the tool

**Rationale:** Clear criteria prevent unnecessary questions while ensuring critical ambiguities are resolved. This enables efficient AI-human collaboration.

---

### US-1.8: As a developer, I need comprehensive test coverage
**Priority:** High
**Story Points:** 5

I want all modified tools to have thorough unit tests so that refactoring doesn't break functionality and future changes are safe.

**Acceptance Criteria:**
- AC-1.8.1: Every tool has unit tests with mocked SpiraClient
- AC-1.8.2: Tests cover successful data retrieval scenarios
- AC-1.8.3: Tests cover pagination edge cases (first page, last page, empty results)
- AC-1.8.4: Tests cover input validation errors
- AC-1.8.5: Tests cover API error responses
- AC-1.8.6: Tests verify JSON structure matches OpenAPI schema
- AC-1.8.7: Tests verify pagination metadata is correct
- AC-1.8.8: Tests verify error response structure
- AC-1.8.9: Overall test coverage is >= 80% for modified code
- AC-1.8.10: All tests pass before merging changes

**Rationale:** High test coverage ensures reliability and enables confident refactoring. Mocked tests run fast and don't require API access.

---

### US-1.9: As a developer, I need clear versioning for breaking changes
**Priority:** High
**Story Points:** 1

I want the version number to clearly indicate this is a breaking change so users know to expect different behavior.

**Acceptance Criteria:**
- AC-1.9.1: Version number is bumped to 1.0.0 (from 0.5.x)
- AC-1.9.2: Release notes document the JSON-first change
- AC-1.9.3: Tool names remain unchanged (no breaking changes to tool discovery)
- AC-1.9.4: Tool parameter names remain unchanged where possible
- AC-1.9.5: CHANGELOG.md documents breaking changes

**Breaking Changes:**
- Tool output format: Markdown → JSON
- Return structure: String → JSON object with `{"data": [...], "pagination": {...}}`
- Silent truncation: Removed (now explicit pagination)

**What Stays the Same:**
- Tool names: `get_my_tasks`, `get_my_incidents`, etc.
- Tool discovery: Same tool list
- Authentication: No changes
- API endpoints: No changes

**Rationale:**
Version 1.0.0 signals a major release with breaking changes. Modern LLMs that use MCP are adaptable and will work with JSON output. The formatting tool provides a fallback for complex workflows.

---

### US-1.10: As an LLM, I need concise tool documentation for efficient parsing
**Priority:** Medium
**Story Points:** 3

I want tool docstrings to be optimized for LLM consumption by reducing verbosity while maintaining clarity, so that I can parse tool definitions faster and use fewer tokens.

**Acceptance Criteria:**
- AC-1.10.1: Average docstring length reduced from ~150 lines to ~80 lines (47% reduction)
- AC-1.10.2: Returns sections condensed from 50+ line JSON examples to 3-5 line structure descriptions
- AC-1.10.3: Key Fields sections list only 8-10 most important fields per artifact type
- AC-1.10.4: Key Fields sections reference shared documentation for complete field lists
- AC-1.10.5: Error Response sections condensed to format description and common error codes
- AC-1.10.6: Pagination notes standardized to single-line indicators
- AC-1.10.7: Example Usage sections reduced to 3-5 lines with most common use case only
- AC-1.10.8: Shared field reference document created at `docs/artifact_fields_reference.md`
- AC-1.10.9: All 32 tools updated with optimized docstrings
- AC-1.10.10: Optimized docstrings maintain clarity and essential information

**Rationale:**
Post-implementation review (TOOL_DOCUMENTATION_REVIEW.md) identified that comprehensive docstrings are too verbose for efficient LLM parsing. With 32 tools averaging ~150 lines per docstring (~4,800 lines total), LLMs spend significant tokens parsing documentation. Reducing verbosity by 47% while maintaining clarity will improve LLM performance and reduce token usage from ~60,000 to ~32,000 tokens.

**Target Metrics:**
- Total documentation: 4,800 lines → 2,560 lines (47% reduction)
- Average docstring: 150 lines → 80 lines
- Returns section: 50+ lines → 3-5 lines (save ~800 lines across 20 tools)
- Key Fields section: 30+ lines → 10-15 lines (save ~400 lines across 20 tools)
- Error Response section: 10 lines → 2-3 lines (save ~200 lines across 25 tools)
- Pagination notes: 6 lines → 1 line (save ~60 lines across 15 tools)
- Example Usage: 10+ lines → 3-5 lines (save ~125 lines across 25 tools)

**Optimization Strategy:**
1. Replace full JSON examples with concise structure descriptions
2. List only essential fields, reference shared documentation for complete lists
3. Simplify error response documentation to format and common codes
4. Standardize pagination notes to single-line indicators
5. Keep only most illustrative example per tool
6. Create shared field reference to eliminate redundancy

---

## Affected Tools

### MyWork Tools (5 tools)
1. **get_my_tasks** → Returns JSON array of tasks assigned to current user
   - API Endpoint: `GET /tasks`
   - Current: Returns markdown, truncates at 25
   - New: Returns JSON with pagination

2. **get_my_incidents** → Returns JSON array of incidents assigned to current user
   - API Endpoint: `GET /incidents`
   - Current: Returns markdown, truncates at 25
   - New: Returns JSON with pagination

3. **get_my_requirements** → Returns JSON array of requirements assigned to current user
   - API Endpoint: `GET /requirements`
   - Current: Returns markdown, truncates at 25
   - New: Returns JSON with pagination

4. **get_my_test_cases** → Returns JSON array of test cases assigned to current user
   - API Endpoint: `GET /test-cases`
   - Current: Returns markdown, truncates at 25
   - New: Returns JSON with pagination

5. **get_my_test_sets** → Returns JSON array of test sets assigned to current user
   - API Endpoint: `GET /test-sets`
   - Current: Returns markdown, truncates at 25
   - New: Returns JSON with pagination

### Workspace Tools (3 tools)
1. **get_products** → Returns JSON array of products user has access to
2. **get_programs** → Returns JSON array of programs user has access to
3. **get_product_templates** → Returns JSON array of product templates

### New Formatting Tools (1 tool, not 5)
1. **format_artifacts_as_markdown** → Generic formatter for all artifact types
   - Accepts: `artifact_json` (string), `artifact_type` (enum: "task"|"incident"|"requirement"|"test_case"|"test_set")
   - Returns: Markdown formatted string
   - Use case: Formatting filtered/processed results

---

## Tool Definition Strategy

### Automated Documentation Generation

A Python script (`scripts/generate_tool_docs.py`) will:

1. **Parse OpenAPI Spec**: Extract endpoint definitions, parameters, and schemas
2. **Generate Docstring Templates**: Create structured docstrings with:
   - Summary from OpenAPI operation description
   - Parameter documentation from OpenAPI parameters
   - Return value documentation from OpenAPI response schema
   - Example response structure from OpenAPI schema
3. **Identify Clarification Needs**: Flag ambiguous or missing information
4. **Output Review Document**: Generate markdown for human review

### Manual Review Process

For each tool, developers will:

1. **Review Generated Documentation**: Check for accuracy and completeness
2. **Add "When to Use" Section**: Explain use cases and scenarios
3. **Add Workflow Context**: Explain relationship to other tools
4. **Resolve Ambiguities**: Answer clarification questions
5. **Add Examples**: Provide realistic example responses
6. **Validate Against API**: Test tool with real API to verify behavior

### Human Clarification Triggers

Ask humans when:

1. **OpenAPI description is missing or vague**
   - Example: Field description is just "The id" without context
   - Question: "What is the purpose of field X? When would it be null?"

2. **Multiple similar fields exist**
   - Example: EstimatedEffort, ActualEffort, RemainingEffort, ProjectedEffort
   - Question: "What's the difference between these fields? When should each be used?"

3. **Business logic is unclear**
   - Example: When to use TaskStatusId vs TaskStatusName
   - Question: "Should LLMs filter by ID or name? What's the recommended approach?"

4. **Workflow context is missing**
   - Example: When to use get_my_tasks vs search_tasks (future tool)
   - Question: "When should an LLM use this tool vs related tools?"

5. **Data relationships are complex**
   - Example: Task → Requirement → Release relationships
   - Question: "Should this tool include related data or require separate calls?"

6. **Edge cases are unclear**
   - Example: Behavior when user has no assigned tasks
   - Question: "Should this return empty array or error message?"

7. **Performance implications exist**
   - Example: Retrieving 500 tasks with all custom properties
   - Question: "What's the recommended limit for performance? Any fields to exclude?"

### Documentation Template

```python
@mcp.tool()
def get_my_tasks(limit: int = 25, offset: int = 0) -> str:
    """
    Retrieves tasks assigned to the current user.

    Maps to Spira API: GET /tasks

    This tool returns tasks where the current user is the Owner (assigned to).
    Use this for personal task lists, daily standup reports, or workload analysis.

    **For Display to Users:** Modern LLMs can format JSON naturally for simple display.
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
                    "EstimatedEffort": 120,  // minutes
                    "ActualEffort": 60,      // minutes
                    "RemainingEffort": 60,   // minutes
                    "CompletionPercent": 50,
                    "StartDate": "2024-01-15T09:00:00Z",
                    "EndDate": "2024-01-16T17:00:00Z",
                    "ReleaseId": 10,
                    "ReleaseVersionNumber": "1.5.0",
                    "RequirementId": 45,
                    "RequirementName": "User Authentication",
                    "ProjectId": 55,
                    "ProjectName": "Web Application",
                    "CustomProperties": [...],
                    "Tags": "bug,security"
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
        - EstimatedEffort: Original estimate in minutes
        - ActualEffort: Time spent so far in minutes
        - RemainingEffort: Developer's estimate of time remaining
        - CompletionPercent: Auto-calculated from effort values
        - ReleaseId/ReleaseVersionNumber: Sprint/iteration assignment
        - RequirementId/RequirementName: Parent requirement link

    When to Use:
        - Getting personal task list for current user
        - Generating daily standup reports
        - Analyzing personal workload
        - Finding tasks by status or priority (filter the JSON)

    Related Tools:
        - format_artifacts_as_markdown: Format filtered/processed results for display
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
        # Show readable to user
    """
```

```python
@mcp.tool()
def format_artifacts_as_markdown(artifact_json: str, artifact_type: str) -> str:
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
        combined = format_artifacts_as_markdown(tasks, "task") + "\n\n" + \
                   format_artifacts_as_markdown(incidents, "incident")
    """
```


---

## OpenAPI Spec Integration

### Field Documentation Extraction

For each tool, extract from OpenAPI spec:

1. **Endpoint Information**
   - Path: `/tasks`
   - Method: `GET`
   - Operation ID: `Task_RetrieveForCurrentUser`
   - Description: Operation-level description

2. **Parameter Information**
   - Name, type, required/optional
   - Description from spec
   - Default values
   - Validation rules (min, max, pattern)

3. **Response Schema**
   - Schema name: `RemoteTask`
   - All properties with types and descriptions
   - Nullable fields
   - Nested objects and arrays

4. **Field-Level Details**
   - Extract description for each field
   - Note nullable vs required
   - Identify relationships (foreign keys)
   - Document enums and valid values

### Example: RemoteTask Schema Mapping

From OpenAPI spec:
```json
{
  "TaskId": {
    "type": "integer",
    "nullable": true,
    "description": "The id of the task"
  },
  "EstimatedEffort": {
    "type": "integer",
    "nullable": true,
    "description": "The originally estimated effort (in minutes) of the task"
  }
}
```

To Tool Documentation:
```
- TaskId: Unique identifier for the task (integer, may be null for new tasks)
- EstimatedEffort: Original estimate in minutes (integer, null if not estimated)
```

---

## Non-Functional Requirements

### NFR-1.1: Performance
- JSON serialization adds < 10ms overhead per request
- Pagination reduces memory usage for large result sets
- Response size for 100 tasks < 500KB

### NFR-1.2: Compatibility
- JSON output is valid per JSON specification
- All existing tool names remain unchanged (backward compatibility)
- New formatting tools use clear naming convention

### NFR-1.3: Maintainability
- Tool documentation is generated from OpenAPI spec
- Changes to OpenAPI spec trigger documentation review
- Consistent error response format across all tools

### NFR-1.4: Usability
- LLMs can parse JSON without additional instructions
- Error messages are actionable and specific
- Tool descriptions enable self-service usage

---

## Technical Constraints

1. **Spira API Limitations**
   - Some endpoints don't support pagination (document these)
   - API returns all fields (cannot select specific fields)
   - Rate limiting may apply (not documented in OpenAPI)

2. **MCP Framework**
   - Tools must return strings (JSON as string)
   - Tool names must be valid Python identifiers
   - Docstrings are the primary documentation mechanism

3. **Python Version**
   - Must work with Python 3.13+
   - Use type hints for all parameters
   - Follow PEP 8 style guidelines

---

## Dependencies

### External Dependencies
- OpenAPI spec: `SpiraRestAPI-v7.0-OpenAPI.json`
- Existing SpiraClient implementation
- Existing formatting module (to be refactored)

### Internal Dependencies
- Milestone 0 must be complete (dev environment, linting, testing)
- API coverage tracker (from openapi-tracker spec)

---

## Out of Scope

The following are explicitly **not** included in this milestone:

1. **New Tools**: No new artifact types (covered in Milestones 2-5)
2. **Write Operations**: No create/update/delete (covered in Milestone 2)
3. **Advanced Search**: No RemoteFilter implementation (covered in Milestone 6)
4. **Metadata Tools**: No status/priority/type lookups (covered in Milestone 3)
5. **Modular Loading**: No selective tool loading (covered in Milestone 4)
6. **Performance Optimization**: No caching or connection pooling (covered in Milestone 6)
7. **Prompts**: No workflow prompts (covered in Milestone 7)

---

## Success Metrics

### Quantitative Metrics
- 100% of existing tools return valid JSON
- 100% of list tools support pagination
- 80%+ test coverage for modified code
- 0 silent truncations in production
- < 5% of tool calls result in validation errors
- Average docstring length reduced to ~80 lines (47% reduction from ~150 lines)
- Total documentation reduced to ~2,560 lines (47% reduction from ~4,800 lines)
- Estimated LLM token usage reduced to ~32,000 tokens (47% reduction from ~60,000 tokens)

### Qualitative Metrics
- LLMs can successfully filter and aggregate data
- Tool documentation is clear without additional explanation
- Developers can create new tools following established patterns
- Human clarification requests are specific and actionable
- Optimized docstrings maintain clarity while reducing verbosity
- LLMs can parse tool definitions more efficiently

---

## Risks and Mitigations

### Risk 1: OpenAPI spec is incomplete or inaccurate
**Likelihood:** Medium
**Impact:** High
**Mitigation:**
- Test all tools against real API
- Document discrepancies between spec and reality
- Create issue tracker for spec improvements
- Maintain manual overrides for known issues

### Risk 2: Breaking changes affect existing LLM workflows
**Likelihood:** Medium
**Impact:** High
**Mitigation:**
- Keep tool names unchanged
- Provide migration guide for LLM prompts
- Add formatting tools before removing markdown output
- Version the MCP server clearly

### Risk 3: Pagination implementation is complex
**Likelihood:** Low
**Impact:** Medium
**Mitigation:**
- Start with simple offset/limit pagination
- Document Spira API pagination behavior
- Test edge cases thoroughly
- Provide clear examples in documentation

### Risk 4: Too many clarification requests slow development
**Likelihood:** Medium
**Impact:** Medium
**Mitigation:**
- Batch clarification requests by tool
- Prioritize critical ambiguities
- Make reasonable assumptions and document them
- Create FAQ document for common questions

---

## Implementation Plan

### Phase 1: Infrastructure (Week 1, Days 1-2)
1. Create error response classes
2. Create input validation utilities
3. Create pagination utilities
4. Create JSON response wrapper
5. Write tests for utilities

### Phase 2: Documentation Tooling (Week 1, Days 3-4)
1. Create `scripts/generate_tool_docs.py`
2. Implement OpenAPI parsing
3. Implement docstring generation
4. Implement clarification detection
5. Test with existing tools

### Phase 3: MyWork Tools (Week 1, Day 5 - Week 2, Day 2)
1. Convert `get_my_tasks` to JSON
2. Convert `get_my_incidents` to JSON
3. Convert `get_my_requirements` to JSON
4. Convert `get_my_test_cases` to JSON
5. Convert `get_my_test_sets` to JSON
6. Add pagination to all
7. Add input validation to all
8. Write comprehensive tests

### Phase 4: Formatting Tool (Week 2, Days 3-4)
1. Refactor existing formatting module
2. Create `format_artifacts_as_markdown` (single generic formatter)
3. Implement artifact type detection/handling
4. Write tests for all artifact types
5. Update documentation

### Phase 5: Workspace Tools (Week 2, Day 5)
1. Convert workspace tools to JSON
2. Add pagination where applicable
3. Update documentation
4. Write tests

### Phase 6: Documentation & Review (Week 2, Days 6-7)
1. Generate documentation for all tools
2. Review and refine tool descriptions
3. Create tool definition guide
4. Update README with examples
5. Final testing and validation

---

## Open Questions

### Q1: Should pagination metadata be in response or separate?
**Options:**
A. Include in response: `{"data": [...], "pagination": {...}}`
B. Separate tool: `get_pagination_info()`

**Recommendation:** Option A - keeps data and metadata together
**Decision:** [To be decided]

### Q2: How should we handle endpoints that don't support server-side pagination?
**Context:** The "my work" endpoints (`/tasks`, `/incidents`, `/requirements`, `/test-cases`, `/test-sets`) do NOT have `start_row`/`number_rows` parameters in the OpenAPI spec. They return ALL results.

**Options:**
A. Implement client-side pagination (retrieve all, slice in Python)
B. Document limitation and don't add pagination parameters
C. Wait for server-side pagination in future API version

**Analysis:**
- "My work" endpoints typically return < 1000 items (manageable)
- Client-side pagination provides consistent interface
- Future project-level endpoints DO support server-side pagination
- Users benefit from explicit pagination even if client-side

**Recommendation:** Option A - implement client-side pagination for consistency
- Document clearly that it's client-side
- Note performance implications for large result sets
- Plan for server-side pagination in Milestone 2+ for project endpoints

**Decision:** [To be decided]

### Q3: Should formatting tools accept JSON strings or Python objects?
**Options:**
A. JSON strings (consistent with MCP string-only interface)
B. Python objects (more flexible for internal use)

**Recommendation:** Option A - maintains MCP consistency
**Decision:** [To be decided]

### Q4: How detailed should error messages be?
**Options:**
A. Minimal (error type and message only)
B. Detailed (include suggestions, related docs, examples)

**Recommendation:** Option B - helps LLMs self-correct
**Decision:** [To be decided]

### Q5: Should we maintain a v0.5 compatibility mode?
**Options:**
A. Clean break with version bump (0.5 → 1.0)
B. Add `output_format` parameter to all tools
C. Maintain separate v0.5 and v1.0 branches

**Analysis:**
- Option A: Simplest, clearest, forces migration
- Option B: Complex, every tool needs parameter, confusing
- Option C: Maintenance burden, splits development effort

**Recommendation:** Option A - clean break with clear migration guide
**Decision:** [To be decided]

---

## API Endpoint Pagination Analysis

### Endpoints WITHOUT Server-Side Pagination

The following "my work" endpoints return ALL results with no pagination parameters:

| Endpoint | Operation ID | Returns | Pagination Support |
|----------|--------------|---------|-------------------|
| `GET /tasks` | `Task_RetrieveForOwner` | All tasks owned by current user | ❌ None |
| `GET /incidents` | `Incident_RetrieveForOwner` | All incidents owned by current user | ❌ None |
| `GET /requirements` | `Requirement_RetrieveForOwner` | All requirements owned by current user | ❌ None |
| `GET /test-cases` | `TestCase_RetrieveForOwner` | All test cases owned by current user | ❌ None |
| `GET /test-sets` | `TestSet_RetrieveForOwner` | All test sets owned by current user | ❌ None |

**Implication:** We implement **client-side pagination** by:
1. Retrieving all results from API
2. Slicing results in Python based on `limit` and `offset`
3. Calculating pagination metadata from full result set
4. Documenting this clearly in tool descriptions

**Performance Consideration:**
- Typical "my work" result sets: 10-500 items
- Acceptable for client-side pagination
- If user has > 1000 items, may be slow (document this)

### Endpoints WITH Server-Side Pagination

Project-level endpoints (to be implemented in Milestone 2+) support pagination:

| Endpoint Pattern | Parameters | Example |
|-----------------|------------|---------|
| `GET /projects/{id}/tasks` | `start_row`, `number_rows` | Get tasks 0-100 |
| `GET /projects/{id}/incidents` | `start_row`, `number_rows` | Get incidents 0-100 |
| `GET /projects/{id}/requirements` | `start_row`, `number_rows` | Get requirements 0-100 |

**Future Implementation:** Milestone 2+ will use server-side pagination for project-level queries.

### Pagination Strategy Summary

**Milestone 1 (This Spec):**
- Client-side pagination for "my work" endpoints
- Consistent interface: `limit` and `offset` parameters
- Clear documentation that it's client-side
- Performance warnings for large result sets

**Milestone 2+:**
- Server-side pagination for project-level endpoints
- Map `limit`/`offset` to `number_rows`/`start_row`
- Same interface, different implementation
- Better performance for large datasets

---

## Glossary

- **JSON-First**: Architecture where tools return structured JSON by default
- **Client-Side Pagination**: Retrieving all data from API and slicing in application code
- **Server-Side Pagination**: API supports limiting results via parameters (start_row, number_rows)
- **Pagination**: Retrieving data in chunks using limit and offset parameters
- **OpenAPI Spec**: Machine-readable API documentation (formerly Swagger)
- **Tool Definition**: MCP tool docstring with parameters and return value docs
- **Clarification Request**: Specific question for human when AI needs guidance
- **Silent Truncation**: Limiting results without informing the caller (anti-pattern)
- **Validation**: Checking input parameters before making API calls
- **Breaking Change**: Modification that requires users to update their code
- **Backward Compatibility**: Maintaining support for previous versions

---

## References

- [Master Plan](../../../SPIRA_MCP_ENHANCEMENT_MASTER_PLAN.md)
- [OpenAPI Spec](../../../SpiraRestAPI-v7.0-OpenAPI.json)
- [Current Analysis](../../../MCP_SERVER_ANALYSIS_AND_RECOMMENDATIONS.md)
- [Milestone 0 Requirements](../milestone-0-foundation/requirements.md)
- [OpenAPI Tracker Spec](../openapi-tracker/requirements.md)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [JSON Schema](https://json-schema.org/)

---

## Appendix A: Example Tool Transformation

### Before (Current Implementation)
```python
@mcp.tool()
def get_my_tasks() -> str:
    """Retrieves a list of the open tasks that are assigned to me"""
    tasks = spira_client.make_spira_api_get_request("tasks")
    if not tasks:
        return "The current user does not have any tasks."

    formatted_results = []
    for task in tasks[:25]:  # Silent truncation!
        task_info = format_task(task)  # Returns markdown
        formatted_results.append(task_info)

    return "\n\n".join(formatted_results)
```

### After (New Implementation)
```python
@mcp.tool()
def get_my_tasks(limit: int = 25, offset: int = 0) -> str:
    """
    Retrieves tasks assigned to the current user.

    [Full docstring as shown in template above]

    Note: This endpoint uses CLIENT-SIDE pagination. The API returns all tasks,
    and we slice the results in Python. This is acceptable for "my work" queries
    which typically return < 500 items. For large result sets, consider using
    project-level queries with server-side pagination (available in Milestone 2+).
    """
    # Validate inputs
    if not (1 <= limit <= 500):
        return json.dumps({
            "error": "Invalid limit parameter",
            "error_code": "INVALID_PARAMETER",
            "details": {"parameter": "limit", "value": limit, "expected": "1-500"},
            "suggestion": "Use limit between 1 and 500"
        })

    if offset < 0:
        return json.dumps({
            "error": "Invalid offset parameter",
            "error_code": "INVALID_PARAMETER",
            "details": {"parameter": "offset", "value": offset, "expected": ">= 0"},
            "suggestion": "Use offset >= 0"
        })

    try:
        # Get ALL tasks from API (no server-side pagination available)
        all_tasks = spira_client.make_spira_api_get_request("tasks")

        # Apply CLIENT-SIDE pagination
        total_count = len(all_tasks)
        paginated_tasks = all_tasks[offset:offset + limit]
        returned_count = len(paginated_tasks)
        has_more = (offset + returned_count) < total_count

        # Return JSON with pagination metadata
        return json.dumps({
            "data": paginated_tasks,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "returned_count": returned_count,
                "total_count": total_count,
                "has_more": has_more,
                "pagination_type": "client-side"  # Indicates implementation
            }
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": "Failed to retrieve tasks",
            "error_code": "API_ERROR",
            "details": {"message": str(e)},
            "suggestion": "Check API connectivity and authentication"
        })
```

### New Formatting Tool
```python
@mcp.tool()
def format_tasks_as_markdown(tasks_json: str) -> str:
    """
    Converts task JSON to human-readable markdown format.

    Args:
        tasks_json: JSON string containing task data (from get_my_tasks)
            Can be full response with pagination or just data array.

    Returns:
        Markdown formatted string with task information

    When to Use:
        - Presenting tasks to humans for review
        - Generating reports or summaries
        - Creating readable documentation

    Example:
        tasks = get_my_tasks(limit=10)
        markdown = format_tasks_as_markdown(tasks)
    """
    try:
        data = json.loads(tasks_json)

        # Handle both full response and data array
        tasks = data.get("data", data) if isinstance(data, dict) else data

        if not tasks:
            return "No tasks to display."

        formatted_results = []
        for task in tasks:
            task_info = f"""
## Task [TK:{task['TaskId']}] - {task['Name']}
{task.get('Description', '')}
- **Status:** {task['TaskStatusName']}
- **Type:** {task['TaskTypeName']}
- **Priority:** {task['TaskPriorityName']}
- **Owner:** {task['OwnerName']}
- **Effort:** {task.get('ActualEffort', 0)}/{task.get('EstimatedEffort', 0)} min ({task['CompletionPercent']}% complete)
- **Due Date:** {task.get('EndDate', 'Not set')}
- **Release:** {task.get('ReleaseVersionNumber', 'Unscheduled')}
"""
            formatted_results.append(task_info)

        return "\n\n".join(formatted_results)

    except json.JSONDecodeError:
        return "Error: Invalid JSON input"
    except KeyError as e:
        return f"Error: Missing required field: {e}"
```

---

## Appendix B: Clarification Request Template

When AI needs human input, use this format:

```markdown
## Clarification Request: [Tool Name]

**Context:**
- Tool: get_my_tasks
- API Endpoint: GET /tasks
- OpenAPI Operation: Task_RetrieveForCurrentUser

**Issue:**
The OpenAPI spec has multiple effort-related fields that are unclear:
- EstimatedEffort: "The originally estimated effort (in minutes) of the task"
- ActualEffort: "The actual effort expended so far (in minutes) for the task"
- RemainingEffort: "The effort remaining as reported by the developer"
- ProjectedEffort: "The projected actual effort of the task when it is completed"

**Questions:**
1. What's the relationship between these fields? Is ProjectedEffort = ActualEffort + RemainingEffort?
2. Which field should LLMs use for workload analysis?
3. Can any of these fields be null? What does null mean?
4. Should the tool documentation explain the calculation logic?

**Proposed Documentation:**
```
Key Effort Fields:
- EstimatedEffort: Original estimate before work begins (set once)
- ActualEffort: Time logged so far (increases as work progresses)
- RemainingEffort: Developer's current estimate of time left (updated manually)
- ProjectedEffort: Calculated as ActualEffort + RemainingEffort (read-only)
- CompletionPercent: Calculated as (ActualEffort / ProjectedEffort) * 100

For workload analysis, use ProjectedEffort as it represents total expected time.
```

**Request:**
Please review and confirm/correct the proposed documentation.
```

---

**End of Requirements Document**
