# Implementation Plan: Milestone 1 - Fix Existing Tools

## Overview

Transform existing MCP tools from markdown-based output to JSON-first architecture. This milestone establishes the foundation for all future tool development by creating clear patterns for tool implementation, documentation generation from OpenAPI specs, and optional markdown formatting.

**Key Changes:**
- Convert all tools to return structured JSON
- Add explicit client-side pagination to "my work" tools
- Implement comprehensive input validation
- Create generic markdown formatting tool
- Generate tool documentation from OpenAPI spec

---

## Tasks

- [x] 1. Set up core infrastructure modules
  - Create validation, pagination, response formatting, and error handling utilities
  - Establish patterns for all future tool development
  - _Requirements: US-1.4 (Input Validation), US-1.3 (Pagination)_

  - [x] 1.1 Create validation module
    - Implement `ParameterValidator` class with methods for validating positive integers and pagination parameters
    - Return structured error dictionaries (not exceptions) for easy JSON serialization
    - _Requirements: AC-1.4.1 through AC-1.4.9_

  - [x] 1.2 Create pagination module
    - Implement `paginate_client_side()` function for slicing results and calculating metadata
    - Implement `paginate_server_side()` function for future use (Milestone 2+)
    - Include `pagination_type` field to distinguish implementation types
    - _Requirements: AC-1.3.1 through AC-1.3.10_

  - [x] 1.3 Create response formatting module
    - Implement `format_success_response()` for consistent JSON output
    - Implement `format_error_response()` for structured error messages
    - Define `ErrorCodes` constants class
    - _Requirements: AC-1.4.5 through AC-1.4.8_

  - [x] 1.4 Create error classes module
    - Implement `SpiraMCPError` base exception class
    - Implement `ValidationError`, `APIError`, and `AuthenticationError` subclasses
    - Add `to_dict()` method for JSON serialization
    - _Requirements: AC-1.4.8_

  - [x] 1.5 Write unit tests for infrastructure modules
    - Test validation logic for all parameter types
    - Test pagination calculations for edge cases (empty, first page, last page, partial page)
    - Test response formatting with various data types
    - Test error class serialization
    - _Requirements: AC-1.8.1 through AC-1.8.10_

- [x] 2. Create documentation generation tooling
  - Build automated system for generating tool documentation from OpenAPI spec
  - Establish process for identifying areas needing human clarification
  - _Requirements: US-1.5 (Rich Tool Definitions), US-1.6 (Systematic Documentation), US-1.7 (Human Clarification)_

  - [x] 2.1 Implement OpenAPI documentation generator script
    - Create `OpenAPIDocGenerator` class that parses OpenAPI JSON
    - Implement `extract_endpoint_info()` to get operation details
    - Implement `extract_schema_info()` to get response schema details
    - Implement `generate_docstring_template()` to create tool docstrings
    - _Requirements: AC-1.6.8 through AC-1.6.12_

  - [x] 2.2 Implement clarification detection
    - Implement `identify_clarifications_needed()` to flag ambiguous descriptions
    - Check for missing parameter descriptions, vague field descriptions, and complex schemas
    - Generate specific questions with context from OpenAPI spec
    - _Requirements: AC-1.7.1 through AC-1.7.10_

  - [x] 2.3 Generate documentation report
    - Implement `generate_documentation_report()` to create markdown output
    - Include generated docstrings and clarification questions for each tool
    - Test with existing "my work" tools
    - _Requirements: AC-1.5.10, AC-1.6.12_

  - [x] 2.4 Create tool definition guide document
    - Write `docs/tool_definition_guide.md` with process for creating tool definitions
    - Include template for tool docstrings with all required sections
    - Document scenarios requiring human clarification with examples
    - _Requirements: AC-1.6.1 through AC-1.6.7_

  - [x] 2.5 Write unit tests for documentation generator
    - Test OpenAPI parsing with sample endpoints
    - Test docstring template generation
    - Test clarification detection logic
    - _Requirements: AC-1.8.1, AC-1.8.9_

- [x] 3. Checkpoint - Verify infrastructure and tooling
  - Ensure all utility modules pass tests
  - Verify documentation generator produces usable output
  - Ask the user if questions arise

- [x] 4. Convert "my work" tools to JSON with pagination
  - Transform all 5 "my work" tools to return JSON with client-side pagination
  - Add comprehensive input validation and error handling
  - _Requirements: US-1.1 (Structured JSON), US-1.3 (Pagination), US-1.4 (Validation)_

  - [x] 4.1 Convert get_my_tasks to JSON with pagination
    - Update tool to accept `limit` (default: 25, max: 500) and `offset` (default: 0) parameters
    - Validate pagination parameters using `ParameterValidator`
    - Retrieve all tasks from API and apply client-side pagination
    - Return JSON with `{"data": [...], "pagination": {...}}` structure
    - Update docstring with comprehensive documentation including field descriptions from OpenAPI
    - _Requirements: AC-1.1.1, AC-1.3.1 through AC-1.3.10, AC-1.5.1 through AC-1.5.10_

  - [x] 4.2 Write unit tests for get_my_tasks
    - Test successful retrieval with pagination
    - Test pagination edge cases (first page, last page, partial page, empty results)
    - Test input validation errors (limit too high/low, negative offset)
    - Test API error handling
    - Verify JSON structure and pagination metadata accuracy
    - _Requirements: AC-1.8.1 through AC-1.8.10_

  - [x] 4.3 Convert get_my_incidents to JSON with pagination
    - Follow same pattern as get_my_tasks
    - Update docstring with incident-specific field descriptions
    - _Requirements: AC-1.1.2, AC-1.3.1 through AC-1.3.10_

  - [x] 4.4 Write unit and integration tests for get_my_incidents
    - Write unit tests with mocked Spira client (same scenarios as get_my_tasks)
    - Write integration tests in `tests/integration/test_myincidents_json.py`
    - Test successful retrieval, pagination, validation, error handling
    - Test with real API to verify JSON structure and data preservation
    - _Requirements: AC-1.8.1 through AC-1.8.10_

  - [x] 4.5 Convert get_my_requirements to JSON with pagination
    - Follow same pattern as get_my_tasks
    - Update docstring with requirement-specific field descriptions
    - _Requirements: AC-1.1.3, AC-1.3.1 through AC-1.3.10_

  - [x] 4.6 Write unit and integration tests for get_my_requirements
    - Write unit tests with mocked Spira client (same scenarios as get_my_tasks)
    - Write integration tests in `tests/integration/test_myrequirements_json.py`
    - Test successful retrieval, pagination, validation, error handling
    - Test with real API to verify JSON structure and data preservation
    - _Requirements: AC-1.8.1 through AC-1.8.10_

  - [x] 4.7 Convert get_my_test_cases to JSON with pagination
    - Follow same pattern as get_my_tasks
    - Update docstring with test case-specific field descriptions
    - _Requirements: AC-1.1.4, AC-1.3.1 through AC-1.3.10_

  - [x] 4.8 Write unit and integration tests for get_my_test_cases
    - Write unit tests with mocked Spira client (same scenarios as get_my_tasks)
    - Write integration tests in `tests/integration/test_mytestcases_json.py`
    - Test successful retrieval, pagination, validation, error handling
    - Test with real API to verify JSON structure and data preservation
    - _Requirements: AC-1.8.1 through AC-1.8.10_

  - [x] 4.9 Convert get_my_test_sets to JSON with pagination
    - Follow same pattern as get_my_tasks
    - Update docstring with test set-specific field descriptions
    - _Requirements: AC-1.1.5, AC-1.3.1 through AC-1.3.10_

  - [x] 4.10 Write unit and integration tests for get_my_test_sets
    - Write unit tests with mocked Spira client (same scenarios as get_my_tasks)
    - Write integration tests in `tests/integration/test_mytestsets_json.py`
    - Test successful retrieval, pagination, validation, error handling
    - Test with real API to verify JSON structure and data preservation
    - _Requirements: AC-1.8.1 through AC-1.8.10_

- [x] 5. Checkpoint - Verify "my work" tools
  - Ensure all 5 tools return valid JSON
  - Verify pagination works correctly across all tools
  - Confirm input validation catches all error cases
  - Ask the user if questions arise

- [x] 6. Create generic artifact formatting tool
  - Build single formatter that handles all artifact types
  - Refactor existing formatting utilities for reuse
  - _Requirements: US-1.2 (Optional Markdown Formatting)_

  - [x] 6.1 Refactor existing formatting module
    - Extract common formatting logic to `src/mcp_server_spira/features/formatting/common.py`
    - Create helper functions for formatting individual artifact types
    - Ensure consistent markdown structure across artifact types
    - _Requirements: AC-1.2.3, AC-1.2.4_

  - [x] 6.2 Implement format_artifacts_as_markdown tool
    - Create tool that accepts `artifact_json` (string) and `artifact_type` (enum) parameters
    - Handle both full responses with pagination and data arrays
    - Implement formatters for all 5 artifact types: task, incident, requirement, test_case, test_set
    - Add comprehensive error handling for invalid JSON, unknown types, and missing fields
    - Update docstring to explain when to use formatting vs natural LLM formatting
    - _Requirements: AC-1.2.1 through AC-1.2.10_

  - [x] 6.3 Write unit tests for formatting tool
    - Test formatting full responses with pagination metadata
    - Test formatting data arrays without pagination
    - Test all 5 artifact types
    - Test empty lists, invalid JSON, unknown artifact types, and missing required fields
    - _Requirements: AC-1.8.1 through AC-1.8.10_

- [x] 7. Convert workspace tools to JSON
  - Update workspace tools to return structured JSON
  - Maintain consistent error handling patterns
  - _Requirements: US-1.1 (Structured JSON)_

  - [x] 7.1 Convert get_products to JSON
    - Update tool to return JSON with `{"data": [...]}` structure
    - Update docstring with product field descriptions from OpenAPI
    - Add error handling with structured error responses
    - _Requirements: AC-1.1.6, AC-1.1.7 through AC-1.1.10_

  - [x] 7.2 Convert get_programs to JSON
    - Follow same pattern as get_products
    - Update docstring with program field descriptions
    - _Requirements: AC-1.1.6, AC-1.1.7 through AC-1.1.10_

  - [x] 7.3 Convert get_product_templates to JSON
    - Follow same pattern as get_products
    - Update docstring with template field descriptions
    - _Requirements: AC-1.1.6, AC-1.1.7 through AC-1.1.10_

  - [x] 7.4 Write unit and integration tests for workspace tools
    - Write unit tests with mocked Spira client for all 3 tools
    - Write integration tests in `tests/integration/test_workspace_json.py`
    - Test successful data retrieval, JSON structure validation, error handling
    - Test with real API to verify data preservation and structure
    - _Requirements: AC-1.8.1 through AC-1.8.10_

- [x] 8. Checkpoint - Verify workspace tools
  - Ensure workspace tools return valid JSON
  - Verify consistent error handling
  - Confirm formatting tool works with all artifact types
  - Ask the user if questions arise

- [x] 9. Complete workspace tools coverage
  - Add comprehensive unit tests for all workspace tool functions
  - Ensure >= 80% coverage for workspace tools module
  - _Requirements: US-1.8 (Test Coverage)_

  - [x] 9.1 Add unit tests for products.py helper functions
    - Test `_get_product_by_id_impl` with valid/invalid IDs
    - Test `_get_program_products_impl` with various program IDs
    - Test tool registration and MCP tool wrappers
    - Test error handling for all functions
    - _Requirements: AC-1.8.1 through AC-1.8.10_

  - [x] 9.2 Add unit tests for programs.py helper functions
    - Test `_get_program_by_id_impl` (if exists) with valid/invalid IDs
    - Test tool registration and MCP tool wrappers
    - Test error handling for all functions
    - _Requirements: AC-1.8.1 through AC-1.8.10_

  - [x] 9.3 Add unit tests for product_templates.py helper functions
    - Test `_get_product_template_impl` (if exists) with valid/invalid IDs
    - Test tool registration and MCP tool wrappers
    - Test error handling for all functions
    - _Requirements: AC-1.8.1 through AC-1.8.10_

- [x] 10. Convert product artifacts tools to JSON
  - Transform all product artifact tools to use consistent POST /search endpoints
  - All endpoints support RemoteFilter arrays for future filtering capabilities
  - Add input validation and error handling
  - Use server-side pagination (unlike "my work" tools which use client-side)
  - _Requirements: US-1.1 (Structured JSON), US-1.4 (Validation)_
  - **Note**: All tools use empty filter array `[]` for now; dedicated filter tool will be added in future milestone

  - [x] 10.1 Convert get_tasks (product) to JSON
    - **API Endpoint**: `POST /projects/{product_id}/tasks/search`
    - **Query Parameters**: starting_row, number_of_rows, sort_field, sort_direction
    - **Request Body**: `[]` (empty RemoteFilter array - no filtering for now)
    - Update tool to return JSON with `{"data": [...]}` structure
    - Add `product_id` validation (must be positive integer)
    - Update docstring with task field descriptions from OpenAPI
    - Support server-side pagination via starting_row and number_of_rows
    - _Requirements: AC-1.1.7 through AC-1.1.10_

  - [x] 10.2 Convert get_incidents (product) to JSON
    - **API Endpoint**: `POST /projects/{product_id}/incidents/search`
    - **Query Parameters**: start_row, number_rows, sort_by
    - **Request Body**: `[]` (empty RemoteFilter array)
    - Follow same pattern as get_tasks
    - Update docstring with incident field descriptions
    - _Requirements: AC-1.1.7 through AC-1.1.10_

  - [x] 10.3 Convert get_requirements (product) to JSON
    - **API Endpoint**: `POST /projects/{product_id}/requirements/search`
    - **Query Parameters**: starting_row, number_of_rows
    - **Request Body**: `[]` (empty RemoteFilter array)
    - Follow same pattern as get_tasks
    - Update docstring with requirement field descriptions
    - _Requirements: AC-1.1.7 through AC-1.1.10_

  - [x] 10.4 Convert get_test_cases (product) to JSON
    - **API Endpoint**: `POST /projects/{product_id}/test-cases/search`
    - **Query Parameters**: starting_row, number_of_rows, sort_field, sort_direction
    - **Request Body**: `[]` (empty RemoteFilter array)
    - Follow same pattern as get_tasks
    - Update docstring with test case field descriptions
    - _Requirements: AC-1.1.7 through AC-1.1.10_

  - [x] 10.5 Convert get_test_sets (product) to JSON
    - **API Endpoint**: `POST /projects/{product_id}/test-sets/search`
    - **Query Parameters**: starting_row, number_of_rows, sort_field, sort_direction
    - **Request Body**: `[]` (empty RemoteFilter array)
    - Follow same pattern as get_tasks
    - Update docstring with test set field descriptions
    - _Requirements: AC-1.1.7 through AC-1.1.10_

  - [x] 10.6 Convert get_releases to JSON
    - **API Endpoint**: `POST /projects/{product_id}/releases/search`
    - **Query Parameters**: starting_row, number_of_rows, sort_field, sort_direction
    - **Request Body**: `[]` (empty RemoteFilter array)
    - Follow same pattern as get_tasks
    - Update docstring with release field descriptions
    - Handle both get_releases (list) and get_release_by_id (single)
    - _Requirements: AC-1.1.7 through AC-1.1.10_

  - [x] 10.7 Convert get_risks to JSON
    - **API Endpoint**: `POST /projects/{product_id}/risks/search`
    - **Query Parameters**: starting_row, number_of_rows, sort_field, sort_direction
    - **Request Body**: `[]` (empty RemoteFilter array)
    - Follow same pattern as get_tasks
    - Update docstring with risk field descriptions
    - _Requirements: AC-1.1.7 through AC-1.1.10_

  - [x] 10.8 Convert get_test_runs to JSON
    - **API Endpoint**: `POST /projects/{product_id}/test-runs/search`
    - **Query Parameters**: starting_row, number_of_rows, sort_field, sort_direction
    - **Request Body**: `[]` (empty RemoteFilter array)
    - Follow same pattern as get_tasks
    - Update docstring with test run field descriptions
    - _Requirements: AC-1.1.7 through AC-1.1.10_

  - [x] 10.9 Convert get_automation_hosts to JSON
    - **API Endpoint**: `POST /projects/{product_id}/automation-hosts/search`
    - **Query Parameters**: starting_row, number_of_rows
    - **Request Body**: `[]` (empty RemoteFilter array)
    - Follow same pattern as get_tasks
    - Update docstring with automation host field descriptions
    - _Requirements: AC-1.1.7 through AC-1.1.10_

  - [x] 10.10 Write unit tests for all product artifact tools
    - Write unit tests with mocked Spira client for all 9 tools
    - Test successful data retrieval with POST requests and empty filter arrays
    - Test JSON structure validation, error handling
    - Test input validation (product_id must be positive)
    - Verify all fields are preserved in JSON output
    - Test pagination parameters (starting_row/start_row, number_of_rows/number_rows)
    - _Requirements: AC-1.8.1 through AC-1.8.10_

- [x] 11. Convert program artifacts tools to JSON
  - Transform program artifact tools to return JSON
  - Add input validation and error handling
  - _Requirements: US-1.1 (Structured JSON), US-1.4 (Validation)_

  - [x] 11.1 Convert get_capabilities to JSON
    - Update tool to return JSON with `{"data": [...]}` structure
    - Add `program_id` validation (must be positive integer)
    - Update docstring with capability field descriptions from OpenAPI
    - _Requirements: AC-1.1.7 through AC-1.1.10_

  - [x] 11.2 Convert get_milestones to JSON
    - Follow same pattern as get_capabilities
    - Update docstring with milestone field descriptions
    - _Requirements: AC-1.1.7 through AC-1.1.10_

  - [x] 11.3 Write unit tests for program artifact tools
    - Write unit tests with mocked Spira client for both tools
    - Test successful data retrieval, JSON structure validation, error handling
    - Test input validation (program_id must be positive)
    - _Requirements: AC-1.8.1 through AC-1.8.10_

- [x] 12. Convert automation tools to JSON
  - Transform automation tools to return JSON
  - Add input validation and error handling
  - _Requirements: US-1.1 (Structured JSON), US-1.4 (Validation)_

  - [x] 12.1 Convert record_automated_test_run to JSON
    - Update tool to return JSON response with test run ID
    - Add validation for all input parameters
    - Update docstring with comprehensive parameter descriptions
    - Return structured error responses for validation failures
    - _Requirements: AC-1.1.7 through AC-1.1.10, AC-1.4.1 through AC-1.4.9_

  - [x] 12.2 Convert create_build to JSON
    - Update tool to return JSON response with build ID
    - Add validation for all input parameters
    - Update docstring with comprehensive parameter descriptions
    - Return structured error responses for validation failures
    - _Requirements: AC-1.1.7 through AC-1.1.10, AC-1.4.1 through AC-1.4.9_

  - [x] 12.3 Write unit tests for automation tools
    - Write unit tests with mocked Spira client for both tools
    - Test successful operations, JSON structure validation, error handling
    - Test input validation for all parameters
    - _Requirements: AC-1.8.1 through AC-1.8.10_

- [x] 13. Convert template configuration tools to JSON
  - Transform template configuration tools to return JSON
  - Add input validation and error handling
  - _Requirements: US-1.1 (Structured JSON), US-1.4 (Validation)_

  - [x] 13.1 Convert get_artifact_types to JSON
    - Update tool to return JSON with `{"data": [...]}` structure
    - Add `template_id` validation (must be positive integer)
    - Update docstring with artifact type field descriptions
    - _Requirements: AC-1.1.7 through AC-1.1.10_

  - [x] 13.2 Convert get_custom_properties to JSON
    - Follow same pattern as get_artifact_types
    - Update docstring with custom property field descriptions
    - _Requirements: AC-1.1.7 through AC-1.1.10_

  - [x] 13.3 Write unit tests for template configuration tools
    - Write unit tests with mocked Spira client for both tools
    - Test successful data retrieval, JSON structure validation, error handling
    - Test input validation (template_id must be positive)
    - _Requirements: AC-1.8.1 through AC-1.8.10_

- [x] 14. Convert specification tools to JSON
  - Transform specification tools to return JSON or keep as markdown (special case)
  - Add input validation and error handling
  - _Requirements: US-1.1 (Structured JSON), US-1.4 (Validation)_

  - [x] 14.1 Review specification tools for conversion strategy
    - Analyze get_specification_requirements, get_specification_design, get_specification_tasks, get_specification_test_cases
    - Determine if these should return JSON or remain as markdown (they generate documentation)
    - Document decision and rationale
    - _Requirements: AC-1.1.7 through AC-1.1.10_

  - [x] 14.2 Add input validation to specification tools
    - Add `product_id` and `release_id` validation (must be positive integers or null)
    - Return structured error responses for validation failures
    - Update docstrings with comprehensive parameter descriptions
    - _Requirements: AC-1.4.1 through AC-1.4.9_

  - [x] 14.3 Write unit tests for specification tools
    - Write unit tests with mocked Spira client for all 4 tools
    - Test successful data retrieval, error handling
    - Test input validation for all parameters
    - Achieve >= 80% coverage for this module
    - _Requirements: AC-1.8.1 through AC-1.8.10_

- [x] 15. Checkpoint - Verify all tools converted
  - Ensure all tools return valid JSON (or documented markdown for special cases)
  - Verify consistent error handling across all tools
  - Confirm >= 80% test coverage for all tool modules
  - Ask the user if questions arise

  - [x] 15.1 Fix test failures and verify all tests passing
    - Fix style issues in verification script
    - Run full test suite and confirm all tests pass
    - _Requirements: AC-1.8.10_

  - [x] 15.2 Add workspace tools test coverage
    - Add unit tests for `_get_product_by_id_impl` helper function
    - Add unit tests for `_get_program_products_impl` helper function
    - Add unit tests for `_get_product_template_impl` helper function
    - Add tests for MCP tool wrappers
    - Target: Increase workspace tools coverage from 73-74% to >85%
    - _Requirements: AC-1.8.1 through AC-1.8.10_

  - [x] 15.3 Add program artifact tools test coverage
    - Add unit tests for MCP tool wrappers in capabilities.py
    - Add unit tests for MCP tool wrappers in milestones.py
    - Add tests for error handling paths
    - Target: Increase program artifact tools coverage from 76% to >85%
    - _Requirements: AC-1.8.1 through AC-1.8.10_

  - [x] 15.4 Complete high coverage modules
    - Add edge case tests for formatting/common.py
    - Add MCP wrapper tests for templateconfiguration tools
    - Add MCP wrapper tests for automation tools
    - Add edge case tests for formatting/tools/format_artifacts.py
    - Target: Increase modules from 87-97% to >95%
    - _Requirements: AC-1.8.1 through AC-1.8.10_

  - [x] 15.5 Add product artifact tools test coverage (high priority)
    - Add unit tests for productartifacts/tools/tasks.py
    - Add unit tests for productartifacts/tools/incidents.py
    - Add unit tests for productartifacts/tools/requirements.py
    - Add unit tests for productartifacts/tools/testcases.py
    - Add unit tests for productartifacts/tools/testsets.py
    - Test helper function implementations (_get_tasks_impl, etc.)
    - Test MCP tool wrappers
    - Test validation error paths
    - Test API error handling
    - Target: Increase coverage from 48-52% to >70%
    - _Requirements: AC-1.8.1 through AC-1.8.10_

  - [x] 15.6 Verify 80%+ coverage achieved
    - Run full test suite with coverage report
    - Verify overall coverage is >= 80%
    - Verify all critical modules have adequate coverage
    - Document final coverage metrics
    - _Requirements: AC-1.8.9, AC-1.8.10_

- [x] 16. Update project documentation and versioning
  - Document breaking changes and migration path
  - Update version to 1.0.0 to signal major release
  - _Requirements: US-1.9 (Versioning)_

  - [x] 16.1 Update version number and changelog
    - Bump version from 0.5.x to 1.0.0 in project configuration
    - Create/update CHANGELOG.md with breaking changes section
    - Document what changed (output format, pagination, truncation) and what stayed the same (tool names, authentication)
    - _Requirements: AC-1.9.1 through AC-1.9.5_

  - [x] 16.2 Create migration guide
    - Write migration guide for LLM prompts showing before/after examples
    - Document how to use new JSON output and pagination parameters
    - Explain when to use formatting tool vs natural LLM formatting
    - Include example workflows for common use cases
    - _Requirements: US-1.2 (Formatting Tool Usage)_

  - [x] 16.3 Update README with examples
    - Add examples of JSON output from all tool types
    - Show pagination usage patterns
    - Demonstrate formatting tool usage for complex workflows
    - Include error handling examples
    - _Requirements: AC-1.5.1 through AC-1.5.10_

  - [x] 16.4 Generate final tool documentation
    - Run documentation generator on all updated tools
    - Review generated documentation for accuracy
    - Add workflow context and "when to use" guidance
    - Resolve any remaining clarification questions
    - _Requirements: AC-1.5.1 through AC-1.5.10, AC-1.6.1 through AC-1.6.7_

- [x] 17. Final validation and testing
  - Run complete test suite and verify coverage
  - Perform integration testing with real API
  - _Requirements: US-1.8 (Test Coverage)_

  - [x] 17.1 Run complete test suite
    - Execute all unit tests for infrastructure, tools, and formatting
    - Verify test coverage is >= 80% for all modified code
    - Fix any failing tests
    - _Requirements: AC-1.8.9, AC-1.8.10_

  - [x] 17.2 Perform integration testing
    - Test all tools against real Spira API (if available)
    - Verify JSON output matches OpenAPI schema
    - Test pagination with various result set sizes (for "my work" tools)
    - Verify error handling with invalid inputs and API failures
    - _Requirements: AC-1.8.6_

  - [x] 17.3 Validate documentation completeness
    - Review all tool docstrings for completeness
    - Verify all examples are accurate and tested
    - Ensure migration guide covers all breaking changes
    - Confirm tool definition guide is clear and actionable
    - _Requirements: AC-1.5.1 through AC-1.5.10_

- [x] 18. Final checkpoint - Release readiness
  - Confirm all tests pass with >= 80% coverage
  - Verify all documentation is complete and accurate
  - Ensure version is bumped to 1.0.0
  - Ask the user if ready to release

- [x] 19. Optimize tool docstrings for LLM consumption
  - Reduce verbosity in tool documentation based on TOOL_DOCUMENTATION_REVIEW.md findings
  - Target: Reduce average docstring length from ~150 lines to ~80 lines (47% reduction)
  - _Requirements: US-1.10 (Concise Tool Documentation)_

  - [x] 19.1 Condense Returns sections across all tools
    - Replace full JSON examples with concise structure descriptions
    - Change from 50+ line JSON examples to 3-5 line summaries
    - Format: "JSON: {"data": [artifacts], "pagination": {...}}" with reference to Key Fields
    - Apply to all 32 tools (mywork, product artifacts, workspace, program, template, automation, specification)
    - _Target: Save ~40 lines per tool × 20 tools = 800 lines_
    - _Requirements: AC-1.10.2_
    - **Status: Partially complete - 14/24 files done (58%)**
    - **Completed:** All 5 MyWork tools + All 9 Product Artifacts tools
    - **Remaining:** 3 Workspace, 2 Program, 2 Template, 2 Automation, 4 Specification tools

  - [x] 19.1.1 Complete remaining Returns section condensing
    - Update 3 Workspace tools: products.py (3 tools), programs.py, product_templates.py (2 tools)
    - Update 2 Program artifacts tools: capabilities.py, milestones.py
    - Update 2 Template configuration tools: artifacttypes.py, customproperties.py
    - Update 2 Automation tools: automatedtestruns.py, builds.py
    - Update 4 Specification tools in productspecification.py
    - _Target: Complete remaining 10 files containing 13 tools_
    - _Requirements: AC-1.10.2_

  - [x] 19.2 Reduce Key Fields sections to essential fields only
    - List only 8-10 most important fields per artifact type
    - Add note: "Additional fields available: [list], see API documentation for complete list"
    - Create shared field reference for common artifact types (tasks, incidents, requirements, test cases, test sets)
    - Apply to all artifact-returning tools
    - _Target: Save ~20 lines per tool × 20 tools = 400 lines_
    - _Requirements: AC-1.10.3, AC-1.10.4_

  - [x] 19.3 Update design.md with docstring best practices
    - Add "Docstring Best Practices for MCP Tools" section to design.md
    - Define hard line limits per section (50 lines total max per tool)
    - Document all prohibited patterns with before/after examples:
      - Dead file references (e.g. `See docs/artifact_fields_reference.md`)
      - References to non-existent / future tools
      - Pseudo-code with undefined functions (e.g. `is_late()`)
      - Internal implementation details (client-side slicing, milestone roadmap notes)
      - Full JSON examples in Returns sections
    - Define required docstring structure and section order
    - Provide a canonical reference example (get_my_tasks) showing compliant output
    - Document the docstring compliance test that enforces the 50-line limit
    - _This task is the reference all per-file tasks below depend on. Complete it first._
    - _Requirements: AC-1.10.1 through AC-1.10.10_
    - **STATUS: COMPLETE** - Section added to design.md on 2026-02-23

  - [x] 19.4 Write docstring compliance test
    - Create `tests/test_docstring_compliance.py`
    - Import all registered MCP tools by loading the server
    - For each tool, count lines in `tool.__doc__`
    - Assert each docstring is <= 50 lines; report line count for all tools
    - This test must pass before any per-file task below is considered done
    - Run as part of standard `pytest` suite (no special flags needed)
    - _Requirements: AC-1.10.1, AC-1.8.9_

  - [x] 19.5 Rewrite docstrings: mywork tools
    - Apply the canonical docstring pattern from design.md to all 5 files
    - **Instructions for each file:**
      - Remove all `See docs/artifact_fields_reference.md` references
      - Remove all `(future)` tool references from Related Tools
      - Remove all pseudo-code examples with undefined functions
      - Replace multi-line pagination explanation with single line: `**Pagination:** Client-side (API returns all, sliced in Python).`
      - Replace full JSON Returns block with 3-line structure description
      - Reduce Example Usage to max 4 lines of real executable code
      - Reduce Key Fields to 8-10 fields + one `Additional fields available:` line
      - Reduce Error Responses to 2 lines
      - Verify final docstring is <= 50 lines
    - **Files:**
      - `src/mcp_server_spira/features/mywork/tools/mytasks.py`
      - `src/mcp_server_spira/features/mywork/tools/myincidents.py`
      - `src/mcp_server_spira/features/mywork/tools/myrequirements.py`
      - `src/mcp_server_spira/features/mywork/tools/mytestcases.py`
      - `src/mcp_server_spira/features/mywork/tools/mytestsets.py`
    - _Requirements: AC-1.10.1 through AC-1.10.10_

  - [x] 19.6 Rewrite docstrings: productartifacts tools
    - Apply the canonical docstring pattern from design.md to all 9 files
    - Same instructions as 19.5
    - **Files:**
      - `src/mcp_server_spira/features/productartifacts/tools/tasks.py`
      - `src/mcp_server_spira/features/productartifacts/tools/incidents.py`
      - `src/mcp_server_spira/features/productartifacts/tools/requirements.py`
      - `src/mcp_server_spira/features/productartifacts/tools/testcases.py`
      - `src/mcp_server_spira/features/productartifacts/tools/testsets.py`
      - `src/mcp_server_spira/features/productartifacts/tools/releases.py`
      - `src/mcp_server_spira/features/productartifacts/tools/risks.py`
      - `src/mcp_server_spira/features/productartifacts/tools/testruns.py`
      - `src/mcp_server_spira/features/productartifacts/tools/automationhosts.py`
    - _Requirements: AC-1.10.1 through AC-1.10.10_

  - [x] 19.7 Rewrite docstrings: workspace tools
    - Apply the canonical docstring pattern from design.md to all 3 files
    - Same instructions as 19.5
    - **Files:**
      - `src/mcp_server_spira/features/workspaces/tools/products.py`
      - `src/mcp_server_spira/features/workspaces/tools/programs.py`
      - `src/mcp_server_spira/features/workspaces/tools/product_templates.py`
    - _Requirements: AC-1.10.1 through AC-1.10.10_

  - [x] 19.8 Rewrite docstrings: programartifacts tools
    - Apply the canonical docstring pattern from design.md to both files
    - Same instructions as 19.5
    - **Files:**
      - `src/mcp_server_spira/features/programartifacts/tools/capabilities.py`
      - `src/mcp_server_spira/features/programartifacts/tools/milestones.py`
    - _Requirements: AC-1.10.1 through AC-1.10.10_

  - [x] 19.9 Rewrite docstrings: templateconfiguration tools
    - Apply the canonical docstring pattern from design.md to both files
    - Same instructions as 19.5
    - **Files:**
      - `src/mcp_server_spira/features/templateconfiguration/tools/artifacttypes.py`
      - `src/mcp_server_spira/features/templateconfiguration/tools/customproperties.py`
    - _Requirements: AC-1.10.1 through AC-1.10.10_

  - [x] 19.10 Rewrite docstrings: automation tools
    - Apply the canonical docstring pattern from design.md to both files
    - Same instructions as 19.5; note these are write tools not list tools - no pagination section needed
    - **Files:**
      - `src/mcp_server_spira/features/automation/tools/automatedtestruns.py`
      - `src/mcp_server_spira/features/automation/tools/builds.py`
    - _Requirements: AC-1.10.1 through AC-1.10.10_

  - [x] 19.11 Rewrite docstrings: specification tools
    - Apply the canonical docstring pattern from design.md
    - Same instructions as 19.5; note these return markdown not JSON - Returns section should reflect that
    - **Files:**
      - `src/mcp_server_spira/features/specifications/tools/productspecification.py`
    - _Requirements: AC-1.10.1 through AC-1.10.10_

  - [x] 19.12 Rewrite docstrings: formatting tool
    - Apply the canonical docstring pattern from design.md
    - Same instructions as 19.5; remove any pseudo-code examples with undefined functions
    - **Files:**
      - `src/mcp_server_spira/features/formatting/tools/format_artifacts.py`
    - _Requirements: AC-1.10.1 through AC-1.10.10_

- [x] 20. Thematic verification: dead references
  - Scan all tool files for any remaining `See docs/` or file path references in docstrings
  - Run: `grep -r "See docs/" src/mcp_server_spira/features/`
  - Run: `grep -r "\.md" src/mcp_server_spira/features/` and review each hit
  - All hits must be removed or replaced with inline text
  - _Requirements: AC-1.10.4_

- [x] 21. Thematic verification: phantom tool references
  - Scan all tool files for `(future)` references in docstrings
  - Run: `grep -r "future" src/mcp_server_spira/features/`
  - Cross-check every tool name listed in any `Related Tools:` section against the actual registered tools in `server.py`
  - Remove any reference to a tool that does not currently exist
  - _Requirements: AC-1.10.9_

- [x] 22. Thematic verification: pseudo-code and undefined functions
  - Scan all Example Usage sections for function calls that are not MCP tools or standard Python builtins
  - Run: `grep -rn "is_late\|is_overdue\|filter_by\|parse_date" src/mcp_server_spira/features/`
  - Replace any such examples with real executable code or remove them
  - _Requirements: AC-1.10.9_

- [x] 23. Thematic verification: implementation detail leakage
  - Scan all docstrings for roadmap/milestone references
  - Run: `grep -rn "Milestone [0-9]" src/mcp_server_spira/features/`
  - Run: `grep -rn "client-side\|server-side\|slices in Python\|slice the results" src/mcp_server_spira/features/`
  - All multi-line implementation explanations must be reduced to the single-line format defined in design.md
  - _Requirements: AC-1.10.6_

- [x] 24. Run docstring compliance test suite and enforce 50-line limit
  - Run `pytest tests/test_docstring_compliance.py -v`
  - Every tool must pass the 50-line limit check
  - Fix any remaining violations found
  - Run full test suite to confirm no regressions: `pytest --tb=short`
  - Record final per-tool line counts in a comment at the top of `tests/test_docstring_compliance.py`
  - _Requirements: AC-1.10.1_

- [x] 25. General sanity check - identify any new problems
  - Read through 3 randomly selected tool docstrings from different feature areas
  - Check each against the design.md canonical example for any issues not covered by the thematic checks above
  - Look specifically for: confusing wording, missing Args documentation, incorrect return type descriptions, sections in wrong order
  - Fix any issues found and document them in a comment in this task
  - _Requirements: AC-1.10.9, AC-1.10.10_
  - **Initial findings (6 tools checked):**
    - Specification tools (4): Unclear Returns section for markdown output - FIXED
    - get_risks: Missing blank lines between sections - FIXED
    - Issue rate: ~33% (2 out of 6 tools had issues)
  - **Action: Comprehensive check of ALL tools needed**

  - [x] 25.1 Sanity check: MyWork tools (5 tools)
    - **CRITICAL: Follow design.md section "Docstring Best Practices for MCP Tools" (lines 2400-2625)**
    - **FORBIDDEN PATTERNS (design.md lines 2450-2500):**
      - ❌ `See docs/artifact_fields_reference.md` references
      - ❌ References to non-existent/future tools (e.g., `get_task_by_id (future)`)
      - ❌ Pseudo-code with undefined functions (e.g., `is_late()`, `filter_by()`)
      - ❌ Multi-line pagination explanations (use single line: `**Pagination:** Client-side`)
      - ❌ Full JSON examples in Returns sections (use 3-line structure description)
    - Check all 5 tools in `src/mcp_server_spira/features/mywork/tools/`
    - Verify: structure, formatting, blank lines, Args, Returns, Key Fields, Examples
    - Fix any issues found
    - Document findings in this subtask
    - _Files: mytasks.py, myincidents.py, myrequirements.py, mytestcases.py, mytestsets.py_

  - [x] 25.2 Sanity check: ProductArtifacts tools (9 tools)
    - **CRITICAL: Follow design.md section "Docstring Best Practices for MCP Tools" (lines 2400-2625)**
    - **FORBIDDEN PATTERNS (design.md lines 2450-2500):**
      - ❌ `See docs/artifact_fields_reference.md` references
      - ❌ References to non-existent/future tools
      - ❌ Pseudo-code with undefined functions
      - ❌ Multi-line pagination explanations
      - ❌ Full JSON examples in Returns sections
    - Check all 9 tools in `src/mcp_server_spira/features/productartifacts/tools/`
    - Verify: structure, formatting, blank lines, Args, Returns, Key Fields, Examples
    - Fix any issues found
    - Document findings in this subtask
    - _Files: tasks.py, incidents.py, requirements.py, testcases.py, testsets.py, releases.py, risks.py, testruns.py, automationhosts.py_

  - [x] 25.3 Sanity check: Workspace tools (3 tools)
    - **CRITICAL: Follow design.md section "Docstring Best Practices for MCP Tools" (lines 2400-2625)**
    - **FORBIDDEN PATTERNS (design.md lines 2450-2500):**
      - ❌ `See docs/artifact_fields_reference.md` references
      - ❌ References to non-existent/future tools
      - ❌ Pseudo-code with undefined functions
      - ❌ Multi-line pagination explanations
      - ❌ Full JSON examples in Returns sections
    - Check all 3 tools in `src/mcp_server_spira/features/workspaces/tools/`
    - Verify: structure, formatting, blank lines, Args, Returns, Key Fields, Examples
    - Fix any issues found
    - Document findings in this subtask
    - _Files: products.py (3 tools), programs.py, product_templates.py (2 tools)_

  - [x] 25.4 Sanity check: ProgramArtifacts tools (2 tools)
    - **CRITICAL: Follow design.md section "Docstring Best Practices for MCP Tools" (lines 2400-2625)**
    - **FORBIDDEN PATTERNS (design.md lines 2450-2500):**
      - ❌ `See docs/artifact_fields_reference.md` references
      - ❌ References to non-existent/future tools
      - ❌ Pseudo-code with undefined functions
      - ❌ Multi-line pagination explanations
      - ❌ Full JSON examples in Returns sections
    - Check all 2 tools in `src/mcp_server_spira/features/programartifacts/tools/`
    - Verify: structure, formatting, blank lines, Args, Returns, Key Fields, Examples
    - Fix any issues found
    - Document findings in this subtask
    - _Files: capabilities.py, milestones.py_

  - [x] 25.5 Sanity check: TemplateConfiguration tools (2 tools)
    - **CRITICAL: Follow design.md section "Docstring Best Practices for MCP Tools" (lines 2400-2625)**
    - **FORBIDDEN PATTERNS (design.md lines 2450-2500):**
      - ❌ `See docs/artifact_fields_reference.md` references
      - ❌ References to non-existent/future tools
      - ❌ Pseudo-code with undefined functions
      - ❌ Multi-line pagination explanations
      - ❌ Full JSON examples in Returns sections
    - Check all 2 tools in `src/mcp_server_spira/features/templateconfiguration/tools/`
    - Verify: structure, formatting, blank lines, Args, Returns, Key Fields, Examples
    - Fix any issues found
    - Document findings in this subtask
    - _Files: artifacttypes.py, customproperties.py_

  - [x] 25.6 Sanity check: Automation tools (2 tools)
    - **CRITICAL: Follow design.md section "Docstring Best Practices for MCP Tools" (lines 2400-2625)**
    - **FORBIDDEN PATTERNS (design.md lines 2450-2500):**
      - ❌ `See docs/artifact_fields_reference.md` references
      - ❌ References to non-existent/future tools
      - ❌ Pseudo-code with undefined functions
      - ❌ Full JSON examples in Returns sections (no pagination for write ops)
    - Check all 2 tools in `src/mcp_server_spira/features/automation/tools/`
    - Verify: structure, formatting, blank lines, Args, Returns, Examples (no Key Fields for write ops)
    - Fix any issues found
    - Document findings in this subtask
    - _Files: automatedtestruns.py, builds.py_

  - [x] 25.7 Sanity check: Specification tools (4 tools)
    - **CRITICAL: Follow design.md section "Docstring Best Practices for MCP Tools" (lines 2400-2625)**
    - **FORBIDDEN PATTERNS (design.md lines 2450-2500):**
      - ❌ `See docs/artifact_fields_reference.md` references
      - ❌ References to non-existent/future tools
      - ❌ Pseudo-code with undefined functions
      - ❌ Full markdown examples in Returns sections (these return markdown, not JSON)
    - Check all 4 tools in `src/mcp_server_spira/features/specifications/tools/`
    - Verify: structure, formatting, blank lines, Args, Returns (markdown not JSON), Examples
    - Fix any issues found
    - Document findings in this subtask
    - _Files: productspecification.py (4 tools)_

  - [x] 25.8 Sanity check: Formatting tool (1 tool)
    - **CRITICAL: Follow design.md section "Docstring Best Practices for MCP Tools" (lines 2400-2625)**
    - **FORBIDDEN PATTERNS (design.md lines 2450-2500):**
      - ❌ `See docs/artifact_fields_reference.md` references
      - ❌ References to non-existent/future tools
      - ❌ Pseudo-code with undefined functions
      - ❌ Full examples in Returns sections
    - Check the formatting tool in `src/mcp_server_spira/features/formatting/tools/`
    - Verify: structure, formatting, blank lines, Args, Returns, Examples
    - Fix any issues found
    - Document findings in this subtask
    - _Files: format_artifacts.py_

  - [x] 25.9 Final verification and summary
    - Run full docstring compliance test: `pytest tests/test_docstring_compliance.py -v`
    - Verify all 33 tools pass
    - Create summary report of all issues found and fixed across all subtasks
    - Confirm 100% of tools are now compliant with canonical format

---

## Notes

- Tasks marked with `*` are optional test-related sub-tasks that can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and provide opportunities for user feedback
- All "my work" tools follow the same pattern for consistency
- Client-side pagination is clearly documented as temporary solution until server-side pagination is available in Milestone 2+
- The formatting tool is designed for complex workflows where data has been filtered/processed, not for simple display
- Breaking changes are clearly documented with comprehensive migration guide

---

## Implementation Phases

**Phase 1: Infrastructure (Tasks 1-3)** - Days 1-2
- Core utilities for validation, pagination, responses, and errors
- Documentation generation tooling
- Foundation for all future development

**Phase 2: MyWork Tools (Tasks 4-5)** - Days 3-7
- Convert all 5 "my work" tools to JSON with pagination
- Establish patterns for tool implementation
- Comprehensive testing

**Phase 3: Formatting & Workspace (Tasks 6-9)** - Days 8-12
- Generic formatting tool for all artifact types
- Workspace tools conversion to JSON
- Complete workspace tools test coverage

**Phase 4: Product & Program Artifacts (Tasks 10-11)** - Days 13-18
- Convert all 9 product artifact tools to JSON
- Convert 2 program artifact tools to JSON
- Comprehensive testing for all artifact tools

**Phase 5: Automation, Templates & Specifications (Tasks 12-14)** - Days 19-23
- Convert automation tools to JSON
- Convert template configuration tools to JSON
- Update specification tools with validation
- Comprehensive testing

**Phase 6: Documentation & Release (Tasks 15-18)** - Days 24-26
- Final checkpoint for all tools
- Version bump and changelog
- Migration guide and examples
- Final validation and testing

---

## Success Criteria

- ✅ All ~30+ existing tools return valid JSON (or documented format for special cases)
- ✅ All 5 "my work" tools support client-side pagination
- ✅ All tools validate inputs before API calls
- ✅ All tools return structured error responses
- ✅ Formatting tool handles all 5 artifact types
- ✅ Documentation generator produces usable templates
- ✅ >= 80% test coverage for all modified code
- ✅ All tests pass in CI/CD pipeline
- ✅ Version bumped to 1.0.0 with complete changelog
- ✅ Migration guide is comprehensive and tested
- ✅ All product artifact tools (9) converted to JSON
- ✅ All program artifact tools (2) converted to JSON
- ✅ All automation tools (2) converted to JSON
- ✅ All template configuration tools (2) converted to JSON
- ✅ All specification tools (4) have proper validation
- ✅ All workspace tools have >= 80% test coverage
