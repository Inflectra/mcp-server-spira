# Implementation Plan: Tool Discovery & Scalability

## Overview

Rename all 32 MCP tools with scope prefixes using `name=` in `@mcp.tool()`, add `annotations=` metadata to every tool, add a server description to `FastMCP()`, and create 4 new test files plus verify the existing docstring compliance test picks up the new names. All changes are decorator-level — no Python function names change, no new abstractions.

## Tasks

- [ ] 1. Add server description to FastMCP constructor
  - [ ] 1.1 Update `src/mcp_server_spira/server.py` to add `description=` parameter to `FastMCP()` call
    - Description must summarize server purpose, list all scope prefixes with one-line explanations, and include total tool count
    - Must be under 1000 characters
    - Omit `automation_` prefix from description since no current tools use it
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 2. Rename mywork tools and add annotations
  - [ ] 2.1 Update `src/mcp_server_spira/features/mywork/tools/mytasks.py`
    - Add `name="my_get_tasks"` and `annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True}` to `@mcp.tool()`
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_
  - [ ] 2.2 Update `src/mcp_server_spira/features/mywork/tools/myincidents.py`
    - Add `name="my_get_incidents"` and same read-only annotations
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_
  - [ ] 2.3 Update `src/mcp_server_spira/features/mywork/tools/myrequirements.py`
    - Add `name="my_get_requirements"` and same read-only annotations
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_
  - [ ] 2.4 Update `src/mcp_server_spira/features/mywork/tools/mytestcases.py`
    - Add `name="my_get_test_cases"` and same read-only annotations
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_
  - [ ] 2.5 Update `src/mcp_server_spira/features/mywork/tools/mytestsets.py`
    - Add `name="my_get_test_sets"` and same read-only annotations
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_

- [ ] 3. Rename productartifacts tools and add annotations
  - [ ] 3.1 Update `src/mcp_server_spira/features/productartifacts/tools/tasks.py`
    - Add `name="product_get_tasks"` and read-only annotations
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_
  - [ ] 3.2 Update `src/mcp_server_spira/features/productartifacts/tools/incidents.py`
    - Add `name="product_get_incidents"` and read-only annotations
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_
  - [ ] 3.3 Update `src/mcp_server_spira/features/productartifacts/tools/requirements.py`
    - Add `name="product_get_requirements"` and read-only annotations
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_
  - [ ] 3.4 Update `src/mcp_server_spira/features/productartifacts/tools/releases.py`
    - Add `name="product_get_releases"` and `name="product_get_release_by_id"` with read-only annotations
    - This file contains two tools: `get_releases` and `get_release_by_id`
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_
  - [ ] 3.5 Update `src/mcp_server_spira/features/productartifacts/tools/risks.py`
    - Add `name="product_get_risks"` and read-only annotations
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_
  - [ ] 3.6 Update `src/mcp_server_spira/features/productartifacts/tools/testruns.py`
    - Add `name="product_get_test_runs"` and read-only annotations
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_
  - [ ] 3.7 Update `src/mcp_server_spira/features/productartifacts/tools/testcases.py`
    - Add `name="product_get_test_cases"` and read-only annotations
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_
  - [ ] 3.8 Update `src/mcp_server_spira/features/productartifacts/tools/testsets.py`
    - Add `name="product_get_test_sets"` and read-only annotations
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_
  - [ ] 3.9 Update `src/mcp_server_spira/features/productartifacts/tools/automationhosts.py`
    - Add `name="product_get_automation_hosts"` and read-only annotations
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_

- [ ] 4. Rename automation, program, workspace, template, spec, and format tools
  - [ ] 4.1 Update `src/mcp_server_spira/features/automation/tools/automatedtestruns.py`
    - Add `name="product_create_automated_test_run"` and write annotations: `readOnlyHint=False, destructiveHint=False, openWorldHint=True`
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.3, 3.5, 4.1_
  - [ ] 4.2 Update `src/mcp_server_spira/features/automation/tools/builds.py`
    - Add `name="product_create_build"` and write annotations: `readOnlyHint=False, destructiveHint=False, openWorldHint=True`
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.3, 3.5, 4.1_
  - [ ] 4.3 Update `src/mcp_server_spira/features/programartifacts/tools/milestones.py`
    - Add `name="program_get_milestones"` and read-only annotations
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_
  - [ ] 4.4 Update `src/mcp_server_spira/features/programartifacts/tools/capabilities.py`
    - Add `name="program_get_capabilities"` and read-only annotations
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_
  - [ ] 4.5 Update `src/mcp_server_spira/features/workspaces/tools/products.py`
    - Add `name="system_get_products"` and `name="system_get_product_by_id"` with read-only annotations
    - This file contains two tools: `get_products` and `get_product_by_id`
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_
  - [ ] 4.6 Update `src/mcp_server_spira/features/workspaces/tools/programs.py`
    - Add `name="system_get_programs"` and `name="system_get_program_products"` with read-only annotations
    - This file contains two tools: `get_programs` and `get_program_products`
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_
  - [ ] 4.7 Update `src/mcp_server_spira/features/workspaces/tools/product_templates.py`
    - Add `name="system_get_product_templates"` and `name="system_get_product_template"` with read-only annotations
    - This file contains two tools: `get_product_templates` and `get_product_template`
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_
  - [ ] 4.8 Update `src/mcp_server_spira/features/templateconfiguration/tools/artifacttypes.py`
    - Add `name="system_get_artifact_types"` and read-only annotations
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_
  - [ ] 4.9 Update `src/mcp_server_spira/features/templateconfiguration/tools/customproperties.py`
    - Add `name="template_get_custom_properties"` and read-only annotations
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_
  - [ ] 4.10 Update `src/mcp_server_spira/features/specifications/tools/productspecification.py`
    - Add `name=` for all 4 spec tools: `spec_get_requirements`, `spec_get_design`, `spec_get_tasks`, `spec_get_test_cases` with read-only annotations
    - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2, 3.5, 4.1_
  - [ ] 4.11 Update `src/mcp_server_spira/features/formatting/tools/format_artifacts.py`
    - Add `name="format_artifacts_as_markdown"` and local-only annotations: `readOnlyHint=True, destructiveHint=False, openWorldHint=False`
    - This tool already has the correct prefix; only annotations need adding
    - _Requirements: 2.1, 2.2, 3.1, 3.2, 3.5, 4.1_

- [ ] 5. Checkpoint — Verify all tool renames and annotations
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Create naming convention test
  - [ ] 6.1 Create `tests/test_naming_convention.py`
    - Define `VALID_PREFIXES` tuple with all 8 prefixes including `automation_`
    - Use `@pytest.mark.parametrize` over all registered tool names from `mcp._tool_manager._tools`
    - Test that every tool name starts with a valid prefix (Property 1)
    - Test that after stripping the prefix, the remaining name starts with a recognized verb: `get_`, `create_`, `record_`, `format_`, `list_` (Property 2)
    - Report non-compliant tool names on failure
    - _Requirements: 2.3, 6.1, 6.2, 6.3_
  - [ ]* 6.2 Write property test for naming convention
    - **Property 1: All tool names start with a valid scope prefix**
    - **Property 2: All tool names follow the prefix-verb convention**
    - **Validates: Requirements 2.1, 2.3, 2.4, 6.1, 6.2, 6.3**

- [ ] 7. Create tool annotations test
  - [ ] 7.1 Create `tests/test_tool_annotations.py`
    - Define expected annotations for all 32 tools (read-only tools get `readOnlyHint=True`, write tools get `readOnlyHint=False`, only `format_artifacts_as_markdown` gets `openWorldHint=False`)
    - Use `@pytest.mark.parametrize` over all registered tools
    - Verify each tool has annotations set and values match expected behavior (Property 3)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  - [ ]* 7.2 Write property test for annotation correctness
    - **Property 3: All tools have correct annotations matching their behavior**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

- [ ] 8. Create server description test
  - [ ] 8.1 Create `tests/test_server_description.py`
    - Test that `mcp` has a description set (not None/empty)
    - Test that description is under 1000 characters
    - Test that description contains each active scope prefix (`my_`, `product_`, `program_`, `template_`, `system_`, `spec_`, `format_`)
    - Test that description includes the tool count
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 9. Create token budget monitoring test
  - [ ] 9.1 Create `tests/test_token_budget.py`
    - Build the full tools/list response text from all tool names, docstrings, and parameter schemas
    - Estimate token count using `len(text) / 4` (4 chars per token)
    - Warn at 40,000 tokens, fail at 60,000 tokens
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  - [ ]* 9.2 Write property test for token estimation formula
    - **Property 5: Token estimation uses the 4-character-per-token ratio**
    - Use Hypothesis to generate random strings and verify `len(s) // 4` holds
    - **Validates: Requirements 7.4**

- [ ] 10. Verify existing docstring compliance test picks up new names
  - Update the header comment in `tests/test_docstring_compliance.py` to reflect the new tool names in the line count listing
  - Verify the parametrized test dynamically reads from `mcp._tool_manager._tools` and picks up the renamed tools without code changes
  - _Requirements: 5.1, 5.2, 5.3_

- [ ] 11. Final checkpoint — Run full test suite
  - Ensure all tests pass, ask the user if questions arise.
  - Verify test coverage remains at 80%+
  - Confirm all 32 tools are registered with new names, annotations, and compliant docstrings

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties from the design document
- All changes are decorator-level — no Python function names, imports, or call sites change
- The `automation_` prefix is kept in the valid prefix set for future use but no current tools use it
