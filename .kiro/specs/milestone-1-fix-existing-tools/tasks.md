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

- [ ] 4. Convert "my work" tools to JSON with pagination
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

- [ ] 5. Checkpoint - Verify "my work" tools
  - Ensure all 5 tools return valid JSON
  - Verify pagination works correctly across all tools
  - Confirm input validation catches all error cases
  - Ask the user if questions arise

- [ ] 6. Create generic artifact formatting tool
  - Build single formatter that handles all artifact types
  - Refactor existing formatting utilities for reuse
  - _Requirements: US-1.2 (Optional Markdown Formatting)_

  - [ ] 6.1 Refactor existing formatting module
    - Extract common formatting logic to `src/mcp_server_spira/features/formatting/common.py`
    - Create helper functions for formatting individual artifact types
    - Ensure consistent markdown structure across artifact types
    - _Requirements: AC-1.2.3, AC-1.2.4_

  - [ ] 6.2 Implement format_artifacts_as_markdown tool
    - Create tool that accepts `artifact_json` (string) and `artifact_type` (enum) parameters
    - Handle both full responses with pagination and data arrays
    - Implement formatters for all 5 artifact types: task, incident, requirement, test_case, test_set
    - Add comprehensive error handling for invalid JSON, unknown types, and missing fields
    - Update docstring to explain when to use formatting vs natural LLM formatting
    - _Requirements: AC-1.2.1 through AC-1.2.10_

  - [ ]* 6.3 Write unit tests for formatting tool
    - Test formatting full responses with pagination metadata
    - Test formatting data arrays without pagination
    - Test all 5 artifact types
    - Test empty lists, invalid JSON, unknown artifact types, and missing required fields
    - _Requirements: AC-1.8.1 through AC-1.8.10_

- [ ] 7. Convert workspace tools to JSON
  - Update workspace tools to return structured JSON
  - Maintain consistent error handling patterns
  - _Requirements: US-1.1 (Structured JSON)_

  - [ ] 7.1 Convert get_products to JSON
    - Update tool to return JSON with `{"data": [...]}` structure
    - Update docstring with product field descriptions from OpenAPI
    - Add error handling with structured error responses
    - _Requirements: AC-1.1.6, AC-1.1.7 through AC-1.1.10_

  - [ ] 7.2 Convert get_programs to JSON
    - Follow same pattern as get_products
    - Update docstring with program field descriptions
    - _Requirements: AC-1.1.6, AC-1.1.7 through AC-1.1.10_

  - [ ] 7.3 Convert get_product_templates to JSON
    - Follow same pattern as get_products
    - Update docstring with template field descriptions
    - _Requirements: AC-1.1.6, AC-1.1.7 through AC-1.1.10_

  - [ ]* 7.4 Write unit and integration tests for workspace tools
    - Write unit tests with mocked Spira client for all 3 tools
    - Write integration tests in `tests/integration/test_workspace_json.py`
    - Test successful data retrieval, JSON structure validation, error handling
    - Test with real API to verify data preservation and structure
    - _Requirements: AC-1.8.1 through AC-1.8.10_

- [ ] 8. Checkpoint - Verify all tools
  - Ensure all 8 tools return valid JSON
  - Verify consistent error handling across all tools
  - Confirm formatting tool works with all artifact types
  - Ask the user if questions arise

- [ ] 9. Update project documentation and versioning
  - Document breaking changes and migration path
  - Update version to 1.0.0 to signal major release
  - _Requirements: US-1.9 (Versioning)_

  - [ ] 9.1 Update version number and changelog
    - Bump version from 0.5.x to 1.0.0 in project configuration
    - Create/update CHANGELOG.md with breaking changes section
    - Document what changed (output format, pagination, truncation) and what stayed the same (tool names, authentication)
    - _Requirements: AC-1.9.1 through AC-1.9.5_

  - [ ] 9.2 Create migration guide
    - Write migration guide for LLM prompts showing before/after examples
    - Document how to use new JSON output and pagination parameters
    - Explain when to use formatting tool vs natural LLM formatting
    - Include example workflows for common use cases
    - _Requirements: US-1.2 (Formatting Tool Usage)_

  - [ ] 9.3 Update README with examples
    - Add examples of JSON output from all tool types
    - Show pagination usage patterns
    - Demonstrate formatting tool usage for complex workflows
    - Include error handling examples
    - _Requirements: AC-1.5.1 through AC-1.5.10_

  - [ ] 9.4 Generate final tool documentation
    - Run documentation generator on all updated tools
    - Review generated documentation for accuracy
    - Add workflow context and "when to use" guidance
    - Resolve any remaining clarification questions
    - _Requirements: AC-1.5.1 through AC-1.5.10, AC-1.6.1 through AC-1.6.7_

- [ ] 10. Final validation and testing
  - Run complete test suite and verify coverage
  - Perform integration testing with real API
  - _Requirements: US-1.8 (Test Coverage)_

  - [ ] 10.1 Run complete test suite
    - Execute all unit tests for infrastructure, tools, and formatting
    - Verify test coverage is >= 80% for all modified code
    - Fix any failing tests
    - _Requirements: AC-1.8.9, AC-1.8.10_

  - [ ] 10.2 Perform integration testing
    - Test all tools against real Spira API (if available)
    - Verify JSON output matches OpenAPI schema
    - Test pagination with various result set sizes
    - Verify error handling with invalid inputs and API failures
    - _Requirements: AC-1.8.6_

  - [ ] 10.3 Validate documentation completeness
    - Review all tool docstrings for completeness
    - Verify all examples are accurate and tested
    - Ensure migration guide covers all breaking changes
    - Confirm tool definition guide is clear and actionable
    - _Requirements: AC-1.5.1 through AC-1.5.10_

- [ ] 11. Final checkpoint - Release readiness
  - Confirm all tests pass with >= 80% coverage
  - Verify all documentation is complete and accurate
  - Ensure version is bumped to 1.0.0
  - Ask the user if ready to release

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

**Phase 3: Formatting & Workspace (Tasks 6-8)** - Days 8-10
- Generic formatting tool for all artifact types
- Workspace tools conversion to JSON
- Complete tool coverage

**Phase 4: Documentation & Release (Tasks 9-11)** - Days 11-12
- Version bump and changelog
- Migration guide and examples
- Final validation and testing

---

## Success Criteria

- ✅ All 8 existing tools return valid JSON
- ✅ All 5 "my work" tools support client-side pagination
- ✅ All tools validate inputs before API calls
- ✅ All tools return structured error responses
- ✅ Formatting tool handles all 5 artifact types
- ✅ Documentation generator produces usable templates
- ✅ >= 80% test coverage for all modified code
- ✅ All tests pass in CI/CD pipeline
- ✅ Version bumped to 1.0.0 with complete changelog
- ✅ Migration guide is comprehensive and tested
