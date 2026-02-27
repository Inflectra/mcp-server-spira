# Implementation Plan: artifact-schema-tool

## Overview

Introduce `system_get_artifact_schema`, a local-only MCP tool that returns
hardcoded field schema data for any of the 11 supported Spira artifact types.
Then trim verbose "Key Fields" sections from 22+ existing tool docstrings,
replacing each with a single pointer line. Finally, update tests to cover the
new tool and verify no docstring contains inline field lists.

## Tasks

- [x] 1. Implement `artifact_schema.py` — core module
  - [x] 1.1 Create `src/mcp_server_spira/features/formatting/tools/artifact_schema.py`
    - Define `VALID_ARTIFACT_TYPES: tuple[str, ...]` with all 11 artifact type strings
    - Implement `_get_artifact_schema_impl(artifact_type: str) -> str` with validation and JSON return
    - Implement `register_tools(mcp)` wiring `_get_artifact_schema_impl` into the MCP decorator with `name="system_get_artifact_schema"` and annotations `readOnlyHint=True, destructiveHint=False, openWorldHint=False`
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 2.1, 2.3_

  - [x] 1.2 Populate `ARTIFACT_SCHEMAS` dict for all 11 artifact types
    - Open `SpiraRestAPI-v7.0-OpenAPI.json` and locate each `Remote*` schema under `components/schemas`
    - Transcribe every property for: `RemoteTask`, `RemoteIncident`, `RemoteRequirement`, `RemoteTestCase`, `RemoteRelease`, `RemoteRisk`, `RemoteTestSet`, `RemoteTestRun`, `RemoteAutomationHost`, `RemoteCapability`, `RemoteMilestone`
    - Map OpenAPI types: `"integer"→"int"`, `"string"→"str"`, `"boolean"→"bool"`, `"string/date-time"→"datetime"`, `"array"→"list"`
    - Use OpenAPI `"description"` values verbatim
    - _Requirements: 1.2, 1.4_

- [x] 2. Wire `artifact_schema` into the formatting feature
  - [x] 2.1 Update `src/mcp_server_spira/features/formatting/tools/__init__.py`
    - Import `artifact_schema` alongside existing `format_artifacts`
    - Call `artifact_schema.register_tools(mcp)` inside `register_tools`
    - _Requirements: 2.2_

- [x] 3. Write unit and property tests for `artifact_schema`
  - [x] 3.1 Create `tests/features/formatting/test_artifact_schema.py`
    - `test_valid_task_returns_fields` — call `_impl("task")`, assert `fields` non-empty, each entry has `name`, `type`, `description`
    - `test_all_artifact_types_return_fields` — parametrize over all 11 types, assert non-empty `fields` list
    - `test_invalid_type_returns_error` — call `_impl("bogus")`, assert `"error"` key present
    - `test_invalid_type_lists_valid_types` — assert `"valid_types"` key present and contains all 11 types
    - `test_valid_type_echoed_in_response` — assert `artifact_type` key in response matches input
    - _Requirements: 4.1_

  - [x] 3.2 Write property test — Property 1: valid types return parseable schema with non-empty fields
    - **Property 1: Valid artifact type returns parseable schema with non-empty fields**
    - **Validates: Requirements 1.1, 1.2, 4.2**
    - Use `@given(artifact_type=sampled_from(VALID_ARTIFACT_TYPES))` with `@settings(max_examples=100)`
    - Assert JSON parses, `artifact_type` echoed, `fields` non-empty, every field has `name`/`type`/`description`

  - [x] 3.3 Write property test — Property 2: invalid types return JSON error object
    - **Property 2: Invalid artifact type returns JSON error object**
    - **Validates: Requirements 1.1, 1.3**
    - Use `@given(artifact_type=text().filter(lambda s: s not in VALID_ARTIFACT_TYPES))` with `@settings(max_examples=100)`
    - Assert JSON parses, `"error"` key present with non-empty string, `"valid_types"` key present

- [x] 4. Checkpoint — verify new tool works end-to-end
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Trim "Key Fields" sections from artifact-typed tool docstrings
  - [x] 5.1 Update mywork tools — replace "Key Fields" with pointer line
    - `features/mywork/tools/mytasks.py` → `artifact_type='task'`
    - `features/mywork/tools/myincidents.py` → `artifact_type='incident'`
    - `features/mywork/tools/myrequirements.py` → `artifact_type='requirement'`
    - `features/mywork/tools/mytestcases.py` → `artifact_type='test_case'`
    - `features/mywork/tools/mytestsets.py` → `artifact_type='test_set'`
    - Replacement line: `Call system_get_artifact_schema(artifact_type='<type>') to see available fields.`
    - _Requirements: 3.1, 3.2, 3.3_

  - [x] 5.2 Update productartifacts tools — replace "Key Fields" with pointer line
    - `features/productartifacts/tools/tasks.py` → `artifact_type='task'`
    - `features/productartifacts/tools/incidents.py` → `artifact_type='incident'`
    - `features/productartifacts/tools/requirements.py` → `artifact_type='requirement'`
    - `features/productartifacts/tools/releases.py` → `artifact_type='release'` (2 tools in this file)
    - `features/productartifacts/tools/risks.py` → `artifact_type='risk'`
    - `features/productartifacts/tools/testruns.py` → `artifact_type='test_run'`
    - `features/productartifacts/tools/testcases.py` → `artifact_type='test_case'`
    - `features/productartifacts/tools/testsets.py` → `artifact_type='test_set'`
    - `features/productartifacts/tools/automationhosts.py` → `artifact_type='automation_host'`
    - _Requirements: 3.1, 3.2, 3.3_

  - [x] 5.3 Update programartifacts and workspaces tools — remove "Key Fields"
    - `features/programartifacts/tools/milestones.py` → `artifact_type='milestone'`
    - `features/programartifacts/tools/capabilities.py` → `artifact_type='capability'`
    - `features/workspaces/tools/products.py` → no artifact_type; remove "Key Fields" section entirely (3 tools)
    - `features/workspaces/tools/programs.py` → no artifact_type; remove "Key Fields" section entirely
    - `features/workspaces/tools/product_templates.py` → no artifact_type; remove "Key Fields" section entirely (2 tools)
    - _Requirements: 3.1, 3.2, 3.3_

  - [x] 5.4 Update templateconfiguration and specifications tools — remove "Key Fields"
    - `features/templateconfiguration/tools/artifacttypes.py` → no artifact_type; remove "Key Fields" section entirely
    - `features/templateconfiguration/tools/customproperties.py` → no artifact_type; remove "Key Fields" section entirely
    - `features/specifications/tools/productspecification.py` → no artifact_type; remove "Key Fields" section entirely
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 6. Update server tool count
  - [x] 6.1 Update `src/mcp_server_spira/server.py`
    - Change `"32 tools total"` to `"33 tools total"` in the instructions string
    - _Requirements: 4.4_

- [x] 7. Update existing test files
  - [x] 7.1 Update `tests/test_tool_annotations.py`
    - Add `system_get_artifact_schema` to `EXPECTED_ANNOTATIONS` with `readOnlyHint=True, destructiveHint=False, openWorldHint=False`
    - Update tool count comment from 32 to 33
    - _Requirements: 4.3_

  - [x] 7.2 Update `tests/test_server_description.py`
    - Change hardcoded count assertion from `"32"` to `"33"`
    - _Requirements: 4.4_

  - [x] 7.3 Write property test — Property 3: no registered tool description contains "Key Fields"
    - **Property 3: No registered tool description contains "Key Fields"**
    - **Validates: Requirements 3.1, 3.3**
    - Add parametrized test to `tests/test_tool_annotations.py` iterating over all registered tool names
    - Assert `"Key Fields"` not in each tool's `__doc__`

- [x] 8. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- `VALID_ARTIFACT_TYPES` is exported from `artifact_schema.py` so tests can import it directly rather than duplicating the list
- For tools with no matching artifact type (workspaces, templateconfiguration, specifications), remove the "Key Fields" section entirely rather than adding a pointer line
- The `ARTIFACT_SCHEMAS` dict is a curated snapshot of the OpenAPI spec; if Spira adds fields in a future version, update `SpiraRestAPI-v7.0-OpenAPI.json` first, then `artifact_schema.py`
- Property tests use `hypothesis`; ensure it is listed in test dependencies
