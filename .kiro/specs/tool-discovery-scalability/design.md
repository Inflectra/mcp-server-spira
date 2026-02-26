# Design Document: Tool Discovery & Scalability

## Overview

This design addresses the tool discovery and scalability concerns for the Spira MCP Server as it grows from 33 to 80+ tools. The approach is deliberately minimal: we rename tools using the `name=` parameter in `@mcp.tool()`, add annotation metadata, update the server description, and add two new test files. No Python function names change, no new abstractions are introduced, and no architectural refactoring is needed.

The changes fall into three categories:
1. **Server metadata** — add a `description=` to the `FastMCP()` constructor
2. **Tool registration changes** — add `name=` and `annotations=` parameters to every `@mcp.tool()` call
3. **Test infrastructure** — update the existing docstring test and add two new test files

## Architecture

The architecture remains unchanged. The only modification is at the registration layer:

```
┌─────────┐         ┌─────────────┐         ┌──────────────┐
│   LLM   │ ◄─────► │ MCP Server  │ ◄─────► │  Spira API   │
│ (Kiro)  │   MCP   │  (Python)   │  HTTP   │ (REST/Auth)  │
└─────────┘         └─────────────┘         └──────────────┘
```

All changes are confined to:
- `server.py` — one-line change to add `description=`
- `features/*/tools/*.py` — update `@mcp.tool()` decorators with `name=` and `annotations=`
- `tests/` — update existing test, add two new test files

No new modules, classes, or abstractions are introduced.

## Components and Interfaces

### 1. Server Description (Requirement 1)

**File:** `src/mcp_server_spira/server.py`

Change the `FastMCP()` constructor call to include a description:

```python
mcp = FastMCP(
    "inflectra-spira",
    description=(
        "Inflectra Spira MCP Server — project management, testing, and requirements tools. "
        "Tools are prefixed by scope: "
        "my_ (current user's work items), "
        "product_ (product-scoped artifacts), "
        "program_ (program-scoped artifacts), "
        "template_ (product template configuration), "
        "system_ (instance-wide operations), "
        "spec_ (specification document structures), "
        "format_ (data display transformations). "
        "32 tools available."
    ),
)
```

This is under 1000 characters and lists every scope prefix with a one-line explanation. The `automation_` prefix is omitted from the server description since no current tools use it, but it remains a valid prefix in the naming validation test for future CI/CD tools.

### 2. Scope-Prefixed Tool Names (Requirement 2)

**Approach:** Use the `name=` parameter in `@mcp.tool()` to set the MCP-visible tool name without renaming the Python function. This is the lowest-risk change — no imports, no call sites, no test mocks need updating.

**Example (before):**
```python
@mcp.tool()
def get_my_tasks(limit: int = 25, offset: int = 0) -> str:
```

**Example (after):**
```python
@mcp.tool(
    name="my_get_tasks",
    annotations={"readOnlyHint": True, "openWorldHint": True},
)
def get_my_tasks(limit: int = 25, offset: int = 0) -> str:
```

### 3. Complete Tool Name Migration Mapping (Requirement 4)

| #   | Old Tool Name                    | New Tool Name                       | Scope Prefix | Rationale                                                                      |
| --- | -------------------------------- | ----------------------------------- | ------------ | ------------------------------------------------------------------------------ |
| 1   | `get_my_tasks`                   | `my_get_tasks`                      | `my_`        | Current user's assigned tasks                                                  |
| 2   | `get_my_incidents`               | `my_get_incidents`                  | `my_`        | Current user's assigned incidents                                              |
| 3   | `get_my_requirements`            | `my_get_requirements`               | `my_`        | Current user's assigned requirements                                           |
| 4   | `get_my_testcases`               | `my_get_test_cases`                 | `my_`        | Current user's assigned test cases                                             |
| 5   | `get_my_testsets`                | `my_get_test_sets`                  | `my_`        | Current user's assigned test sets                                              |
| 6   | `get_tasks`                      | `product_get_tasks`                 | `product_`   | Tasks scoped to a specific product                                             |
| 7   | `get_incidents`                  | `product_get_incidents`             | `product_`   | Incidents scoped to a specific product                                         |
| 8   | `get_requirements`               | `product_get_requirements`          | `product_`   | Requirements scoped to a specific product                                      |
| 9   | `get_releases`                   | `product_get_releases`              | `product_`   | Releases scoped to a specific product                                          |
| 10  | `get_release_by_id`              | `product_get_release_by_id`         | `product_`   | Single release lookup within a product                                         |
| 11  | `get_risks`                      | `product_get_risks`                 | `product_`   | Risks scoped to a specific product                                             |
| 12  | `get_test_runs`                  | `product_get_test_runs`             | `product_`   | Test runs scoped to a specific product                                         |
| 13  | `get_test_cases`                 | `product_get_test_cases`            | `product_`   | Test cases scoped to a specific product                                        |
| 14  | `get_test_sets`                  | `product_get_test_sets`             | `product_`   | Test sets scoped to a specific product                                         |
| 15  | `get_automation_hosts`           | `product_get_automation_hosts`      | `product_`   | Automation hosts scoped to a specific product                                  |
| 16  | `get_milestones`                 | `program_get_milestones`            | `program_`   | Milestones scoped to a specific program                                        |
| 17  | `get_capabilities`               | `program_get_capabilities`          | `program_`   | Capabilities scoped to a specific program                                      |
| 18  | `get_products`                   | `system_get_products`               | `system_`    | Lists all products in the Spira instance                                       |
| 19  | `get_product_by_id`              | `system_get_product_by_id`          | `system_`    | Single product lookup across instance                                          |
| 20  | `get_programs`                   | `system_get_programs`               | `system_`    | Lists all programs in the Spira instance                                       |
| 21  | `get_program_products`           | `system_get_program_products`       | `system_`    | Products within a program (instance-level)                                     |
| 22  | `get_product_templates`          | `system_get_product_templates`      | `system_`    | Lists all product templates in instance                                        |
| 23  | `get_product_template`           | `system_get_product_template`       | `system_`    | Single product template lookup                                                 |
| 24  | `get_artifact_types`             | `system_get_artifact_types`         | `system_`    | System-level list of all available artifact types                              |
| 25  | `get_custom_properties`          | `template_get_custom_properties`    | `template_`  | Custom properties from a product template                                      |
| 26  | `record_automated_test_run`      | `product_create_automated_test_run` | `product_`   | Creates an automated test run record within a product (POST, takes product_id) |
| 27  | `create_build`                   | `product_create_build`              | `product_`   | Creates a build record within a product (POST, takes product_id)               |
| 28  | `get_specification_requirements` | `spec_get_requirements`             | `spec_`      | Requirements from a specification doc                                          |
| 29  | `get_specification_design`       | `spec_get_design`                   | `spec_`      | Design elements from a specification doc                                       |
| 30  | `get_specification_tasks`        | `spec_get_tasks`                    | `spec_`      | Tasks from a specification doc                                                 |
| 31  | `get_specification_test_cases`   | `spec_get_test_cases`               | `spec_`      | Test cases from a specification doc                                            |
| 32  | `format_artifacts_as_markdown`   | `format_artifacts_as_markdown`      | `format_`    | Local-only markdown formatting (no rename needed)                              |

Total: 32 tools. 31 renamed, 1 (`format_artifacts_as_markdown`) already has the correct prefix. No current tools use the `automation_` prefix; it is reserved for future write-heavy CI/CD tools.

### 4. Tool Annotations (Requirement 3)

Every tool gets an `annotations=` dict in its `@mcp.tool()` call. The annotation values are determined by the tool's behavior:

| Annotation        | `True` when                         | `False` when                                 |
| ----------------- | ----------------------------------- | -------------------------------------------- |
| `readOnlyHint`    | Tool only reads data (GET requests) | Tool creates/modifies data (POST/PUT/DELETE) |
| `destructiveHint` | Tool modifies data irreversibly     | Tool is read-only or creates new data        |
| `openWorldHint`   | Tool calls the Spira API (external) | Tool performs local-only transformations     |

**Annotation assignments by tool:**

| New Tool Name                       | readOnlyHint | destructiveHint | openWorldHint |
| ----------------------------------- | ------------ | --------------- | ------------- |
| `my_get_tasks`                      | `true`       | `false`         | `true`        |
| `my_get_incidents`                  | `true`       | `false`         | `true`        |
| `my_get_requirements`               | `true`       | `false`         | `true`        |
| `my_get_test_cases`                 | `true`       | `false`         | `true`        |
| `my_get_test_sets`                  | `true`       | `false`         | `true`        |
| `product_get_tasks`                 | `true`       | `false`         | `true`        |
| `product_get_incidents`             | `true`       | `false`         | `true`        |
| `product_get_requirements`          | `true`       | `false`         | `true`        |
| `product_get_releases`              | `true`       | `false`         | `true`        |
| `product_get_release_by_id`         | `true`       | `false`         | `true`        |
| `product_get_risks`                 | `true`       | `false`         | `true`        |
| `product_get_test_runs`             | `true`       | `false`         | `true`        |
| `product_get_test_cases`            | `true`       | `false`         | `true`        |
| `product_get_test_sets`             | `true`       | `false`         | `true`        |
| `product_get_automation_hosts`      | `true`       | `false`         | `true`        |
| `program_get_milestones`            | `true`       | `false`         | `true`        |
| `program_get_capabilities`          | `true`       | `false`         | `true`        |
| `system_get_products`               | `true`       | `false`         | `true`        |
| `system_get_product_by_id`          | `true`       | `false`         | `true`        |
| `system_get_programs`               | `true`       | `false`         | `true`        |
| `system_get_program_products`       | `true`       | `false`         | `true`        |
| `system_get_product_templates`      | `true`       | `false`         | `true`        |
| `system_get_product_template`       | `true`       | `false`         | `true`        |
| `system_get_artifact_types`         | `true`       | `false`         | `true`        |
| `template_get_custom_properties`    | `true`       | `false`         | `true`        |
| `product_create_automated_test_run` | `false`      | `false`         | `true`        |
| `product_create_build`              | `false`      | `false`         | `true`        |
| `spec_get_requirements`             | `true`       | `false`         | `true`        |
| `spec_get_design`                   | `true`       | `false`         | `true`        |
| `spec_get_tasks`                    | `true`       | `false`         | `true`        |
| `spec_get_test_cases`               | `true`       | `false`         | `true`        |
| `format_artifacts_as_markdown`      | `true`       | `false`         | `false`       |

Notes:
- `product_create_automated_test_run` and `product_create_build` are write operations (`readOnlyHint: false`) but create new records rather than modifying/deleting existing ones, so `destructiveHint: false`.
- `format_artifacts_as_markdown` is the only tool with `openWorldHint: false` since it performs local-only data transformation.

### 5. Test Changes (Requirements 5, 6, 7)

**5a. Update existing docstring compliance test** (`tests/test_docstring_compliance.py`)

The test already reads tool names dynamically from `mcp._tool_manager._tools`. Since we're using `name=` in `@mcp.tool()`, the tool manager will store tools under their new prefixed names. The test will automatically pick up the new names — no code change needed beyond updating the header comment with new line counts.

**5b. New naming validation test** (`tests/test_naming_convention.py`)

A new test file that:
- Defines the valid prefix set: `{"my_", "product_", "program_", "template_", "system_", "automation_", "spec_", "format_"}`
- Iterates all registered tools from `mcp._tool_manager._tools`
- Asserts each tool name starts with one of the valid prefixes
- Reports non-compliant tool names on failure

**5c. New token budget monitoring test** (`tests/test_token_budget.py`)

A new test file that:
- Builds the full `tools/list` response text (tool names + docstrings + parameter schemas)
- Estimates token count using `len(text) / 4` (4 chars per token)
- Warns at 40,000 tokens
- Fails at 60,000 tokens

## Data Models

No new data models are introduced. The only data structures involved are:

1. **Tool annotations dict** — a plain Python dict passed to `@mcp.tool()`:
   ```python
   {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True}
   ```

2. **Valid prefixes set** — used in the naming validation test:
   ```python
   VALID_PREFIXES = ("my_", "product_", "program_", "template_", "system_", "automation_", "spec_", "format_")
   ```

   Note: The `automation_` prefix is retained in the valid set for future use by write-heavy CI/CD tools, but no current tools use it. The migration mapping reflects this — all former `automation_`-prefixed tools have been moved to `product_` since they take a `product_id` and are product-scoped create operations.

No database changes, no new API models, no configuration files beyond what already exists.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: All tool names start with a valid scope prefix

*For any* registered tool in the MCP server, its tool name must start with one of the defined scope prefixes: `my_`, `product_`, `program_`, `template_`, `system_`, `automation_`, `spec_`, `format_`.

**Validates: Requirements 2.1, 2.3, 6.1, 6.2, 6.3**

### Property 2: All tool names follow the prefix-verb convention

*For any* registered tool in the MCP server, after stripping the scope prefix, the remaining name must start with a recognized verb (`get_`, `create_`, `record_`, `format_`, `list_`).

**Validates: Requirements 2.4**

### Property 3: All tools have correct annotations matching their behavior

*For any* registered tool in the MCP server, the tool must have annotations set, and those annotations must match the expected values: `readOnlyHint` is `true` for read-only tools and `false` for write tools; `openWorldHint` is `true` for tools that call the Spira API and `false` for local-only tools; `destructiveHint` is `false` for all current tools.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

### Property 4: All tool docstrings are within the 50-line limit

*For any* registered tool in the MCP server, its docstring must be no longer than 50 lines.

**Validates: Requirements 5.1, 5.2**

### Property 5: Token estimation uses the 4-character-per-token ratio

*For any* string input, the token estimation function must return `len(input) / 4` (integer division), consistent with the defined approximation method.

**Validates: Requirements 7.4**

## Error Handling

No new error handling is required. The changes are purely at the registration/metadata layer:

- **Invalid prefix at registration time:** Caught by the naming validation test (`test_naming_convention.py`) during CI, not at runtime. No runtime validation is added — this is a developer-facing guard, not a user-facing one.
- **Missing annotations:** Caught by the annotation correctness test during CI.
- **Token budget exceeded:** The token budget test emits a warning at 40k tokens and fails at 60k tokens. This is a CI-time signal, not a runtime error.

All existing error handling in tool implementations (API errors, validation errors, etc.) remains unchanged.

## Testing Strategy

### Dual Testing Approach

This feature uses both unit tests (specific examples) and property-based tests (universal properties across all tools).

All existing tests must continue to pass after these changes, and test coverage must remain at or above the current level (80%+). Since the changes are confined to decorator parameters and new test files, existing test mocks and assertions should be unaffected — but this must be verified before merge.

**Unit tests** cover:
- Server description exists, is under 1000 characters, and contains all scope prefixes (Req 1)
- Migration mapping covers all 33 tools (Req 4)
- Token budget is within warning/failure thresholds at current tool count (Req 7)

**Property-based tests** cover:
- All tool names start with valid prefixes (Property 1)
- All tool names follow prefix-verb convention (Property 2)
- All tools have correct annotations (Property 3)
- All tool docstrings are within 50-line limit (Property 4)
- Token estimation formula correctness (Property 5)

### Property-Based Testing Configuration

- **Library:** [Hypothesis](https://hypothesis.readthedocs.io/) (Python's standard PBT library, already compatible with pytest)
- **Minimum iterations:** 100 per property test
- **Tag format:** Each test includes a comment: `# Feature: tool-discovery-scalability, Property {N}: {description}`

Note: Properties 1–4 are "for all tools in the registry" properties. Since the tool set is finite (33 tools), these are exhaustive checks over the full set rather than randomized. They are still universally quantified properties — they assert a rule that must hold for every element. Property 5 tests the token estimation function with randomly generated strings using Hypothesis.

### Test Files

| File                                 | Type               | Properties/Tests                                                              |
| ------------------------------------ | ------------------ | ----------------------------------------------------------------------------- |
| `tests/test_docstring_compliance.py` | Existing (updated) | Property 4 — docstring line limit (already exists, just picks up new names)   |
| `tests/test_naming_convention.py`    | New                | Property 1 — prefix validation, Property 2 — verb convention                  |
| `tests/test_token_budget.py`         | New                | Property 5 — token estimation, plus unit tests for warning/failure thresholds |
| `tests/test_tool_annotations.py`     | New                | Property 3 — annotation correctness                                           |
| `tests/test_server_description.py`   | New                | Unit tests for server description (Req 1)                                     |

Each property-based test must be implemented as a single test function referencing its design property number. Example:

```python
# Feature: tool-discovery-scalability, Property 1: All tool names start with a valid scope prefix
@pytest.mark.parametrize("tool_name", get_all_tool_names())
def test_tool_name_has_valid_prefix(tool_name):
    assert any(tool_name.startswith(p) for p in VALID_PREFIXES), (
        f"Tool '{tool_name}' does not start with a valid prefix: {VALID_PREFIXES}"
    )
```
