# OpenAPI Coverage Tracker - Requirements

**Feature Name:** openapi-tracker
**Version:** 1.0
**Status:** Draft
**Created:** 2026-02-04
**Owner:** Development Team

---

## Introduction

The OpenAPI Coverage Tracker is a standalone utility tool for tracking the implementation status of API endpoints defined in an OpenAPI specification. It provides a systematic way to monitor which endpoints have been implemented as MCP tools, which are planned, and which are excluded, enabling better project planning and progress tracking.

---

## Glossary

- **OpenAPI Spec**: A JSON file following the OpenAPI 3.0 specification that defines REST API endpoints
- **Endpoint**: A unique combination of HTTP method and path (e.g., GET /projects/{id}/tasks)
- **Coverage Database**: A JSON file storing tracking information for all endpoints
- **Status**: The implementation state of an endpoint (implemented, planned, excluded, deprecated)
- **Tag**: An OpenAPI tag used to group related endpoints (e.g., "Incident", "Task")
- **Milestone**: A project phase or release version
- **Tool Name**: The name of the MCP tool that implements an endpoint
- **Base URL**: The customer-specific server URL (not part of the tracker, configured separately)

---

## Requirements

### Requirement 1: Parse OpenAPI Specification

**User Story:** As a developer, I want to parse an OpenAPI specification file, so that I can extract all API endpoints for tracking.

#### Acceptance Criteria

1. WHEN an OpenAPI JSON file is provided, THE Parser SHALL extract all endpoint paths
2. WHEN parsing endpoints, THE Parser SHALL extract the HTTP method for each path
3. WHEN parsing endpoints, THE Parser SHALL extract the operation ID, tags, and description
4. WHEN parsing endpoints, THE Parser SHALL extract parameter definitions
5. WHEN parsing endpoints, THE Parser SHALL generate a unique identifier for each endpoint
6. IF the OpenAPI file is malformed, THEN THE Parser SHALL return a descriptive error message
7. THE Parser SHALL complete parsing in less than 5 seconds for specifications with up to 500 endpoints

---

### Requirement 2: Store Tracking Information

**User Story:** As a project manager, I want to store tracking information for each endpoint, so that I can monitor implementation progress over time.

#### Acceptance Criteria

1. THE System SHALL store tracking data in a JSON file at `data/api_coverage.json`
2. FOR EACH endpoint, THE System SHALL store: path, method, tag, operation_id, description, parameters
3. FOR EACH endpoint, THE System SHALL store: tool_name, status, milestone, implemented_date, notes
4. THE System SHALL support status values: implemented, planned, excluded, deprecated
5. THE System SHALL record the OpenAPI spec version being tracked
6. THE System SHALL record the last update timestamp
7. THE System SHALL include a note explaining that base URLs are customer-specific
8. WHEN saving the database, THE System SHALL format JSON with indentation for human readability

---

### Requirement 3: Update Endpoint Status

**User Story:** As a developer, I want to update the status of endpoints, so that I can mark them as implemented, planned, or excluded.

#### Acceptance Criteria

1. WHEN an endpoint is updated, THE System SHALL locate it by path and method
2. WHEN updating an endpoint, THE System SHALL allow changing: tool_name, status, milestone, notes
3. WHEN an endpoint is marked as "implemented", THE System SHALL record the implementation date
4. IF an endpoint path and method combination doesn't exist, THEN THE System SHALL return an error
5. WHEN an update is successful, THE System SHALL save the database immediately
6. THE System SHALL validate that status values are one of: implemented, planned, excluded, deprecated

---

### Requirement 4: Generate Coverage Reports

**User Story:** As a project manager, I want to generate coverage reports, so that I can see implementation progress and identify gaps.

#### Acceptance Criteria

1. THE System SHALL generate reports in Markdown format
2. THE System SHALL generate reports in JSON format
3. WHEN generating a report, THE System SHALL include: total endpoints, implemented count, planned count, excluded count, coverage percentage
4. WHEN generating a report, THE System SHALL group endpoints by tag (artifact type)
5. WHEN generating a report, THE System SHALL group endpoints by milestone
6. WHEN generating a report, THE System SHALL list implemented endpoints with their tool names
7. WHEN generating a report, THE System SHALL list planned endpoints with their target milestones
8. WHEN generating a report, THE System SHALL include the OpenAPI spec version
9. WHEN generating a report, THE System SHALL include a note about customer-specific base URLs
10. THE System SHALL complete report generation in less than 2 seconds

---

### Requirement 5: Filter and Search Endpoints

**User Story:** As a developer, I want to filter endpoints by various criteria, so that I can focus on specific subsets of the API.

#### Acceptance Criteria

1. WHEN filtering by tag, THE System SHALL return only endpoints with that tag
2. WHEN filtering by status, THE System SHALL return only endpoints with that status
3. WHEN filtering by milestone, THE System SHALL return only endpoints assigned to that milestone
4. WHEN multiple filters are applied, THE System SHALL return endpoints matching all filters (AND logic)
5. WHEN no endpoints match the filters, THE System SHALL return an empty result with a message

---

### Requirement 6: Provide CLI Interface

**User Story:** As a developer, I want a command-line interface, so that I can easily interact with the tracker.

#### Acceptance Criteria

1. THE System SHALL provide an `init` command to initialize the database from an OpenAPI spec
2. THE System SHALL provide an `update` command to modify endpoint tracking information
3. THE System SHALL provide a `report` command to generate coverage reports
4. THE System SHALL provide a `summary` command to show high-level statistics
5. THE System SHALL provide a `list` command to display filtered endpoints
6. WHEN a command is run with `--help`, THE System SHALL display usage information
7. WHEN a command fails, THE System SHALL display a clear error message
8. WHEN a command succeeds, THE System SHALL display a confirmation message

---

### Requirement 7: Handle Spec Version Updates

**User Story:** As a developer, I want to handle OpenAPI spec version updates, so that I can track changes to the API over time.

#### Acceptance Criteria

1. THE System SHALL record the OpenAPI spec version in the database
2. WHEN initializing with a new spec version, THE System SHALL detect version changes
3. WHEN a spec version changes, THE System SHALL preserve existing tracking information
4. WHEN a spec version changes, THE System SHALL add new endpoints
5. WHEN a spec version changes, THE System SHALL mark removed endpoints as deprecated
6. THE System SHALL allow comparing coverage between different spec versions

---

### Requirement 8: Document Base URL Handling

**User Story:** As a developer, I want clear documentation about base URLs, so that I understand they are customer-specific and not part of the tracker.

#### Acceptance Criteria

1. THE Documentation SHALL explain that the OpenAPI spec contains an example base URL
2. THE Documentation SHALL explain that actual base URLs are customer-specific
3. THE Documentation SHALL reference the `SPIRA_BASE_URL` environment variable
4. THE Documentation SHALL clarify that the tracker does not store or manage base URLs
5. THE Coverage Report SHALL include a note about customer-specific base URLs

---

## Non-Functional Requirements

### NFR-1: Performance
- Parsing an OpenAPI spec with 500 endpoints SHALL complete in < 5 seconds
- Generating a coverage report SHALL complete in < 2 seconds
- Database file size SHALL remain < 2MB for 500 endpoints

### NFR-2: Maintainability
- Code SHALL follow PEP 8 style guidelines
- All functions SHALL have type hints
- All public functions SHALL have docstrings
- The database schema SHALL be versioned for future changes

### NFR-3: Usability
- CLI commands SHALL be intuitive and self-documenting
- Error messages SHALL be clear and actionable
- The Markdown report SHALL be human-readable
- The JSON database SHALL be human-readable (formatted with indentation)

### NFR-4: Compatibility
- SHALL work on macOS, Linux, and Windows
- SHALL work with Python 3.10+
- SHALL work with OpenAPI 3.0 specifications
- SHALL minimize external dependencies

---

## Technical Constraints

1. **File Format**: Must use JSON for the database (human-readable, version-controllable)
2. **OpenAPI Version**: Must support OpenAPI 3.0 specification format
3. **Python Version**: Must work with Python 3.10 or higher
4. **Dependencies**: Must minimize external dependencies (use standard library where possible)
5. **Storage**: Database file must be stored in `data/api_coverage.json`

---

## Dependencies

### External Dependencies
- OpenAPI specification file (JSON format)
- Python 3.10+

### Python Package Dependencies
- Standard library only (json, argparse, pathlib, datetime, dataclasses, typing)
- No external packages required

---

## Out of Scope

The following are explicitly **not** included in this tool:

1. Managing or storing base URLs (handled by environment variables)
2. Making actual API calls to test endpoints
3. Generating API client code
4. Validating API responses
5. Performance testing of API endpoints
6. Authentication or authorization management
7. API versioning beyond tracking spec version
8. Automated detection of implemented tools (manual updates only)

---

## Success Metrics

### Quantitative Metrics
- 100% of endpoints in OpenAPI spec are tracked
- Coverage reports generate in < 2 seconds
- Database parsing completes in < 5 seconds
- CLI commands have < 1 second startup time

### Qualitative Metrics
- Developers find the CLI intuitive
- Coverage reports are useful for planning
- The tool integrates smoothly into the development workflow
- Documentation is clear and complete

---

## Risks and Mitigations

### Risk 1: OpenAPI spec structure varies
**Likelihood:** Medium
**Impact:** High
**Mitigation:** Handle missing fields gracefully; validate spec structure; provide clear error messages

### Risk 2: Large OpenAPI specs cause performance issues
**Likelihood:** Low
**Impact:** Medium
**Mitigation:** Optimize parsing; use efficient data structures; test with large specs

### Risk 3: Manual updates are error-prone
**Likelihood:** High
**Impact:** Low
**Mitigation:** Validate all inputs; provide clear error messages; support bulk updates

### Risk 4: Database schema needs to evolve
**Likelihood:** Medium
**Impact:** Medium
**Mitigation:** Version the database schema; provide migration tools; maintain backward compatibility

---

## Open Questions

1. **Q:** Should we support OpenAPI 2.0 (Swagger) specifications?
   **A:** No, focus on OpenAPI 3.0 only. Can add 2.0 support later if needed.

2. **Q:** Should we track response schemas and status codes?
   **A:** No, keep it simple. Focus on endpoint tracking only.

3. **Q:** Should we support SQLite instead of JSON?
   **A:** No, JSON is sufficient and more human-readable. Can migrate later if needed.

4. **Q:** Should we auto-detect implemented tools by scanning code?
   **A:** No, manual updates only. Auto-detection is complex and error-prone.

---

## References

- [OpenAPI 3.0 Specification](https://spec.openapis.org/oas/v3.0.0)
- [Python argparse Documentation](https://docs.python.org/3/library/argparse.html)
- [Python dataclasses Documentation](https://docs.python.org/3/library/dataclasses.html)

---

**End of Requirements Document**
