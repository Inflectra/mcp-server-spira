# Requirements Document

## Introduction

The Spira MCP Server currently embeds verbose "Key Fields" sections in every tool's docstring to document the fields available on each artifact type. This inflates the `tools/list` response, consuming unnecessary token budget on every LLM interaction. This feature introduces a `system_get_artifact_schema` tool that serves field documentation on-demand, and trims the verbose field sections from existing tool docstrings, replacing them with a pointer to the new tool.

The new tool is a local-only utility — it returns hardcoded schema data with no Spira API call, following the same pattern as `format_artifacts_as_markdown`.

## Glossary

- **Schema_Tool**: The new `system_get_artifact_schema` MCP tool defined in this spec
- **Artifact_Type**: One of the supported Spira artifact identifiers: `task`, `incident`, `requirement`, `test_case`, `release`, `risk`, `test_set`, `test_run`, `automation_host`, `capability`, `milestone`
- **Field_Schema**: A JSON object describing the fields available on a given artifact type, including field name, type, and a brief description
- **Tool_Docstring**: The Python docstring attached to a registered MCP tool function, which is surfaced to LLMs via the `tools/list` response
- **Token_Budget**: The total number of tokens consumed by the `tools/list` response; reducing it lowers cost and latency for every LLM interaction
- **Local_Only_Tool**: An MCP tool that performs no external API call; `openWorldHint` is `False`
- **Key_Fields_Section**: The verbose block in existing tool docstrings that lists artifact fields inline

## Requirements

### Requirement 1: Artifact Schema Tool

**User Story:** As an AI assistant using the Spira MCP Server, I want to retrieve the field schema for a specific artifact type on demand, so that I know which fields are available without that information consuming token budget on every interaction.

#### Acceptance Criteria

1. THE Schema_Tool SHALL accept a single `artifact_type` parameter constrained to the literal values: `task`, `incident`, `requirement`, `test_case`, `release`, `risk`, `test_set`, `test_run`, `automation_host`, `capability`, `milestone`
2. WHEN a valid `artifact_type` is provided, THE Schema_Tool SHALL return a JSON string containing the field names, types, and descriptions for that artifact type
3. IF an unrecognised `artifact_type` is provided, THEN THE Schema_Tool SHALL return a JSON error object with an `"error"` key and a message listing the valid artifact types
4. THE Schema_Tool SHALL perform no external API call; all schema data SHALL be hardcoded within the tool module
5. THE Schema_Tool SHALL be registered with MCP annotations `readOnlyHint=True`, `destructiveHint=False`, `openWorldHint=False`
6. THE Schema_Tool SHALL be named `system_get_artifact_schema` following the `scope_verb` naming convention
7. THE Schema_Tool SHALL have a docstring of no more than 10 lines, directing callers to use the tool rather than embedding field lists inline

### Requirement 2: Module Placement

**User Story:** As a developer maintaining the Spira MCP Server, I want the schema tool placed in a predictable location, so that I can find and update it without searching the codebase.

#### Acceptance Criteria

1. THE Schema_Tool SHALL be implemented in `src/mcp_server_spira/features/formatting/tools/artifact_schema.py`, co-located with the existing `format_artifacts_as_markdown` local-only tool
2. THE Schema_Tool SHALL be registered via the `formatting` feature module's existing `register` call, with no changes required to `features/__init__.py`
3. THE Schema_Tool SHALL follow the `register_tools(mcp)` / `_impl` separation pattern used by all other tool modules

### Requirement 3: Docstring Trimming for Existing Tools

**User Story:** As an AI assistant using the Spira MCP Server, I want tool docstrings to be concise, so that the `tools/list` response consumes a minimal token budget.

#### Acceptance Criteria

1. WHEN a tool docstring contains a "Key Fields" section listing artifact fields inline, THE Server SHALL replace that section with a single pointer line: `Call system_get_artifact_schema(artifact_type='<type>') to see available fields.`
2. THE Server SHALL preserve all other docstring sections (Args, Returns, Example Usage, Related Tools, Error Responses, When to Use, When NOT to Use) unchanged
3. THE Server SHALL apply the docstring trimming to all tools that currently contain inline Key_Fields_Section content
4. WHILE the docstring trimming is applied, THE Server SHALL maintain the total `tools/list` character count below the threshold defined in `test_token_budget.py`

### Requirement 4: Test Coverage

**User Story:** As a developer maintaining the Spira MCP Server, I want automated tests for the schema tool and updated annotation/count tests, so that regressions are caught immediately.

#### Acceptance Criteria

1. THE test suite SHALL include unit tests for Schema_Tool covering: valid artifact type returns correct JSON, all 11 artifact types return non-empty field lists, invalid artifact type returns a JSON error object with an `"error"` key
2. THE test suite SHALL include a round-trip property: FOR ALL valid `artifact_type` values, the JSON returned by Schema_Tool SHALL be parseable back to a Python dict without error
3. THE `test_tool_annotations.py` file SHALL be updated to include `system_get_artifact_schema` in `EXPECTED_ANNOTATIONS` with `readOnlyHint=True`, `destructiveHint=False`, `openWorldHint=False`
4. IF the total registered tool count changes, THEN `test_server_description.py` SHALL be updated to assert the new count
