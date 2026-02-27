# Design Document: artifact-schema-tool

## Overview

The `artifact-schema-tool` feature reduces the token budget consumed by the
`tools/list` MCP response. Currently, every tool docstring embeds a verbose
"Key Fields" section that lists artifact fields inline. These sections are
repeated across 22+ files and inflate every LLM interaction even when the
field information is not needed.

The solution has two parts:

1. A new `system_get_artifact_schema` MCP tool that returns hardcoded field
   schema data for any of the 11 supported Spira artifact types, on demand.
2. A docstring trimming pass that removes "Key Fields" sections from all
   existing tool docstrings and replaces each with a single pointer line
   directing callers to the new tool.

The new tool is local-only (no Spira API call), following the same pattern as
`format_artifacts_as_markdown`.

## Architecture

```
MCP Client (LLM)
      │
      │  tools/list  ──►  concise docstrings (no Key Fields inline)
      │
      │  system_get_artifact_schema("task")
      │       │
      ▼       ▼
  MCP Server
      │
      ├── formatting/tools/artifact_schema.py   ← new, local-only
      │       _impl(artifact_type) → JSON str
      │       ARTIFACT_SCHEMAS dict (hardcoded)
      │
      └── formatting/tools/format_artifacts.py  ← unchanged
```

No changes to `features/__init__.py`. The `formatting` feature's existing
`register` call already delegates to `tools.register_tools(mcp)`, so adding
the new tool to `formatting/tools/__init__.py` is sufficient.

## Components and Interfaces

### New file: `artifact_schema.py`

```
src/mcp_server_spira/features/formatting/tools/artifact_schema.py
```

**Module-level constant:**

```python
VALID_ARTIFACT_TYPES: tuple[str, ...] = (
    "task", "incident", "requirement", "test_case", "release",
    "risk", "test_set", "test_run", "automation_host",
    "capability", "milestone",
)
```

Exposing this constant at module level lets tests import it directly rather
than duplicating the list.

**Public interface:**

```python
def register_tools(mcp) -> None: ...
def _get_artifact_schema_impl(artifact_type: str) -> str: ...
```

`_get_artifact_schema_impl` is the testable unit; `register_tools` wires it
into the MCP decorator.

**Tool registration:**

```python
@mcp.tool(
    name="system_get_artifact_schema",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": False,
    },
)
def get_artifact_schema(artifact_type: str) -> str:
    """Returns the field schema for a Spira artifact type as JSON.

    Args:
        artifact_type: One of: task, incident, requirement, test_case,
            release, risk, test_set, test_run, automation_host,
            capability, milestone

    Returns:
        JSON: {"artifact_type": "...", "fields": [{"name", "type",
            "description"}, ...]}
        or {"error": "...", "valid_types": [...]} for unknown types.

    Call system_get_artifact_schema(artifact_type='task') to see fields.
    """
```

### Updated file: `formatting/tools/__init__.py`

Add import and registration call for `artifact_schema`:

```python
from . import artifact_schema, format_artifacts

def register_tools(mcp) -> None:
    format_artifacts.register_tools(mcp)
    artifact_schema.register_tools(mcp)
```

### Docstring trimming (22+ existing tool files)

Each "Key Fields" block is replaced with:

```
Call system_get_artifact_schema(artifact_type='<type>') to see available fields.
```

The replacement is applied to all files listed in the requirements summary.
All other docstring sections (Args, Returns, Example Usage, Related Tools,
Error Responses, When to Use, When NOT to Use) are preserved unchanged.

## Data Models

### Field descriptor

```python
{
    "name": str,         # Python/API field name, e.g. "TaskId"
    "type": str,         # "int", "str", "float", "bool", "datetime"
    "description": str,  # one-line human description
}
```

### Schema response (success)

```python
{
    "artifact_type": str,          # echoes the input
    "fields": list[FieldDescriptor],
}
```

### Schema response (error)

```python
{
    "error": str,                  # human-readable message
    "valid_types": list[str],      # sorted list of valid artifact types
}
```

### Schema data source

The authoritative source for all field data is **`SpiraRestAPI-v7.0-OpenAPI.json`**, specifically the `components/schemas` section. Each supported artifact type maps to a named schema object:

| artifact_type      | OpenAPI schema name         |
|--------------------|-----------------------------|
| `task`             | `RemoteTask`                |
| `incident`         | `RemoteIncident`            |
| `requirement`      | `RemoteRequirement`         |
| `test_case`        | `RemoteTestCase`            |
| `release`          | `RemoteRelease`             |
| `risk`             | `RemoteRisk`                |
| `test_set`         | `RemoteTestSet`             |
| `test_run`         | `RemoteTestRun`             |
| `automation_host`  | `RemoteAutomationHost`      |
| `capability`       | `RemoteCapability`          |
| `milestone`        | `RemoteMilestone`           |

Each `Remote*` schema in the OpenAPI file has a `properties` object where every key is a field name and every value contains `"type"` and `"description"`. For example, `RemoteTask.properties.TaskId` gives `{"type": "integer", "description": "The id of the task"}`.

**During implementation**, the developer SHALL:
1. Open `SpiraRestAPI-v7.0-OpenAPI.json` and locate the `Remote*` schema for each artifact type.
2. Transcribe every property from that schema into the corresponding entry in the `ARTIFACT_SCHEMAS` dict in `artifact_schema.py`, mapping OpenAPI types to Python type strings (`"integer"` → `"int"`, `"string"` → `"str"`, `"boolean"` → `"bool"`, `"string"/"date-time"` → `"datetime"`, `"array"` → `"list"`).
3. Use the OpenAPI `"description"` value verbatim as the field description.

The hardcoded dict in `artifact_schema.py` is therefore a **curated snapshot** of the OpenAPI spec, not an independent invention. If the Spira API adds or renames fields in a future version, the OpenAPI file is updated first and `artifact_schema.py` is updated to match.

Example (task), derived directly from `RemoteTask` in the OpenAPI spec:

```python
"task": {
    "artifact_type": "task",
    "fields": [
        {"name": "TaskId", "type": "int", "description": "The id of the task"},
        {"name": "Name", "type": "str", "description": "The name of the task"},
        {"name": "TaskStatusId", "type": "int", "description": "The id of the status of the task"},
        {"name": "TaskStatusName", "type": "str", "description": "The display name of the status of the task"},
        {"name": "TaskTypeId", "type": "int", "description": "The id of the type of the task (null for default)"},
        {"name": "TaskTypeName", "type": "str", "description": "The display name of the type of the task"},
        {"name": "TaskPriorityId", "type": "int", "description": "The id of the priority of the task"},
        {"name": "TaskPriorityName", "type": "str", "description": "The display name of the priority of the task"},
        {"name": "OwnerId", "type": "int", "description": "The id of the user that the task is assigned-to"},
        {"name": "OwnerName", "type": "str", "description": "The display name of the user who the task is assigned-to"},
        {"name": "EstimatedEffort", "type": "int", "description": "The originally estimated effort (in minutes) of the task"},
        {"name": "ActualEffort", "type": "int", "description": "The actual effort expended so far (in minutes) for the task"},
        {"name": "RemainingEffort", "type": "int", "description": "The effort remaining as reported by the developer"},
        {"name": "CompletionPercent", "type": "int", "description": "The completion percentage (value = 0-100) of the task"},
        {"name": "StartDate", "type": "datetime", "description": "The scheduled start date for the task"},
        {"name": "EndDate", "type": "datetime", "description": "The scheduled end date for the task"},
        {"name": "ReleaseId", "type": "int", "description": "The id of the release/iteration that the task is scheduled for"},
        {"name": "ReleaseVersionNumber", "type": "str", "description": "The version number of the release/iteration the task is scheduled for"},
        {"name": "RequirementId", "type": "int", "description": "The id of the parent requirement that the task belongs to"},
        {"name": "RequirementName", "type": "str", "description": "The name of the requirement that the task is associated with"},
        {"name": "Description", "type": "str", "description": "The detailed description of the task"},
        {"name": "ProjectId", "type": "int", "description": "The id of the project that the artifact belongs to"},
        {"name": "CustomProperties", "type": "list", "description": "The list of associated custom properties/fields for this artifact"},
        {"name": "Tags", "type": "str", "description": "The list of meta-tags that should be associated with the artifact"},
        {"name": "Guid", "type": "str", "description": "The unique identifier for the artifact"},
    ],
}
```

All 11 artifact types follow the same structure, with field data transcribed from their respective `Remote*` schemas in the OpenAPI file.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all
valid executions of a system — essentially, a formal statement about what the
system should do. Properties serve as the bridge between human-readable
specifications and machine-verifiable correctness guarantees.*

### Property 1: Valid artifact type returns parseable schema with non-empty fields

*For any* value in `VALID_ARTIFACT_TYPES`, calling `_get_artifact_schema_impl`
should return a string that: (a) parses as JSON without error, (b) is a dict
with an `"artifact_type"` key equal to the input, and (c) has a `"fields"`
key whose value is a non-empty list where every entry contains `"name"`,
`"type"`, and `"description"` keys.

**Validates: Requirements 1.1, 1.2, 4.2**

### Property 2: Invalid artifact type returns JSON error object

*For any* string that is not in `VALID_ARTIFACT_TYPES`, calling
`_get_artifact_schema_impl` should return a string that parses as JSON and
contains an `"error"` key with a non-empty string value, and a `"valid_types"`
key listing all valid artifact types.

**Validates: Requirements 1.1, 1.3**

### Property 3: No registered tool description contains "Key Fields"

*For all* tools registered with the MCP server, the tool's description string
should not contain the substring `"Key Fields"`.

**Validates: Requirements 3.1, 3.3**

## Error Handling

| Condition | Behaviour |
|---|---|
| `artifact_type` not in `VALID_ARTIFACT_TYPES` | Return `{"error": "...", "valid_types": [...]}` |
| Unexpected exception in `_impl` | Caught at `register_tools` boundary; return `{"error": str(e)}` |

No external I/O means the error surface is small. The only expected error path
is an unrecognised `artifact_type`.

## Testing Strategy

### Unit tests — `tests/features/formatting/test_artifact_schema.py`

Specific examples and edge cases:

- `test_valid_task_returns_fields` — call `_impl("task")`, assert `fields` is
  non-empty and each entry has `name`, `type`, `description`.
- `test_all_artifact_types_return_fields` — parametrize over all 11 types,
  assert non-empty `fields` list.
- `test_invalid_type_returns_error` — call `_impl("bogus")`, assert `"error"`
  key present.
- `test_invalid_type_lists_valid_types` — assert `"valid_types"` key present
  and contains all 11 types.
- `test_valid_type_echoed_in_response` — assert `artifact_type` key in
  response matches input.

### Property-based tests — same file, using `hypothesis`

**Property 1 test** (min 100 examples):

```python
# Feature: artifact-schema-tool, Property 1: Valid artifact type returns
# parseable schema with non-empty fields
@given(artifact_type=sampled_from(VALID_ARTIFACT_TYPES))
@settings(max_examples=100)
def test_valid_type_schema_round_trip(artifact_type):
    result = json.loads(_get_artifact_schema_impl(artifact_type))
    assert result["artifact_type"] == artifact_type
    assert len(result["fields"]) > 0
    for field in result["fields"]:
        assert "name" in field
        assert "type" in field
        assert "description" in field
```

**Property 2 test** (min 100 examples):

```python
# Feature: artifact-schema-tool, Property 2: Invalid artifact type returns
# JSON error object
@given(artifact_type=text().filter(lambda s: s not in VALID_ARTIFACT_TYPES))
@settings(max_examples=100)
def test_invalid_type_returns_error(artifact_type):
    result = json.loads(_get_artifact_schema_impl(artifact_type))
    assert "error" in result
    assert "valid_types" in result
```

**Property 3 test** — in `tests/test_tool_annotations.py` or a dedicated
integration test:

```python
# Feature: artifact-schema-tool, Property 3: No registered tool description
# contains "Key Fields"
@pytest.mark.parametrize("tool_name", get_all_tool_names())
def test_no_tool_description_contains_key_fields(tool_name):
    tool = mcp._tool_manager._tools[tool_name]
    description = tool.fn.__doc__ or ""
    assert "Key Fields" not in description
```

### Updates to existing test files

- `tests/test_tool_annotations.py` — add `system_get_artifact_schema` to
  `EXPECTED_ANNOTATIONS` with `readOnlyHint=True`, `destructiveHint=False`,
  `openWorldHint=False`. Update the comment from 32 to 33 tools.
- `tests/test_server_description.py` — update the hardcoded count assertion
  from `"32"` to `"33"` and update the comment.

### PBT library

Use `hypothesis` (already a common Python PBT library). Each property test
must run a minimum of 100 examples via `@settings(max_examples=100)`.
