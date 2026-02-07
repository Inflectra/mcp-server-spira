# OpenAPI Coverage Tracker - Design

**Feature Name:** openapi-tracker
**Version:** 1.0
**Status:** Draft
**Created:** 2026-02-04
**Owner:** Development Team

---

## Overview

This document describes the technical design for the OpenAPI Coverage Tracker, a standalone utility tool for tracking the implementation status of API endpoints defined in an OpenAPI specification. The tool provides parsing, storage, reporting, and CLI capabilities to monitor which endpoints have been implemented as MCP tools.

**Related Documents:**
- [Requirements](./requirements.md)

---

## Architecture

### System Context

```
┌─────────────────────────────────────────────────────────────┐
│              OpenAPI Coverage Tracker                        │
│                                                              │
│  ┌──────────────────────────────────────┐                  │
│  │   API Coverage Tracker               │                  │
│  │                                      │                  │
│  │  ┌────────────┐  ┌────────────┐    │                  │
│  │  │  Parser    │  │  Database  │    │                  │
│  │  │            │  │            │    │                  │
│  │  │  OpenAPI   │  │  JSON      │    │                  │
│  │  │  → Data    │  │  Storage   │    │                  │
│  │  └────────────┘  └────────────┘    │                  │
│  │                                      │                  │
│  │  ┌────────────┐  ┌────────────┐    │                  │
│  │  │  Reporter  │  │  Updater   │    │                  │
│  │  │            │  │            │    │                  │
│  │  │  Data →    │  │  Status    │    │                  │
│  │  │  Markdown  │  │  Updates   │    │                  │
│  │  └────────────┘  └────────────┘    │                  │
│  └──────────────────────────────────────┘                  │
│                                                              │
│  Input: SpiraRestAPI-v7.0-OpenAPI.json                      │
│  Output: data/api_coverage.json, docs/api_coverage.md       │
└─────────────────────────────────────────────────────────────┘
```

---

## Components and Interfaces


### 1. Data Model

#### 1.1 Endpoint Dataclass

```python
from dataclasses import dataclass
from typing import List, Dict, Optional, Literal

Status = Literal["implemented", "planned", "excluded", "deprecated"]

@dataclass
class Endpoint:
    """Represents a single API endpoint."""
    id: str                          # Unique identifier (e.g., "incident_retrieve_by_id")
    path: str                        # API path (e.g., "/projects/{id}/incidents/{incident_id}")
    method: str                      # HTTP method (GET, POST, PUT, DELETE)
    tag: str                         # OpenAPI tag (e.g., "Incident")
    operation_id: str                # OpenAPI operationId
    description: str                 # Endpoint description
    parameters: List[Dict]           # Parameter definitions
    tool_name: Optional[str]         # MCP tool name (if implemented)
    status: Status                   # Implementation status
    milestone: Optional[str]         # Target milestone (e.g., "milestone-2")
    implemented_date: Optional[str]  # ISO 8601 date when implemented
    notes: str                       # Additional notes
```

#### 1.2 CoverageDatabase Dataclass

```python
@dataclass
class CoverageDatabase:
    """Main coverage tracking database."""
    spec_version: str                # OpenAPI spec version (e.g., "7.0")
    spec_file: str                   # Path to OpenAPI spec file
    last_updated: str                # ISO 8601 timestamp
    base_url_note: str               # Note about customer-specific base URLs
    endpoints: List[Endpoint]        # All tracked endpoints
    summary: Dict                    # Coverage summary statistics
```

---

### 2. APIParser Component

**Purpose:** Parse OpenAPI specification and extract endpoint information.

**Interface:**

```python
class APIParser:
    """Parses OpenAPI specification."""

    def parse_openapi(self, spec_path: Path) -> List[Endpoint]:
        """
        Parse OpenAPI spec and extract endpoints.

        Args:
            spec_path: Path to OpenAPI JSON file

        Returns:
            List of Endpoint objects

        Raises:
            FileNotFoundError: If spec file doesn't exist
            json.JSONDecodeError: If spec file is invalid JSON
            ValueError: If spec structure is invalid
        """
        pass

    def _extract_endpoints(self, spec: Dict) -> List[Endpoint]:
        """Extract endpoints from parsed spec."""
        pass

    def _generate_endpoint_id(self, path: str, method: str) -> str:
        """Generate unique endpoint ID."""
        pass
```

**Implementation Details:**

1. Load OpenAPI JSON file
2. Validate spec structure (check for "paths" key)
3. Iterate through all paths
4. For each path, iterate through all methods
5. Extract operation details (operationId, tags, description, parameters)
6. Generate unique endpoint ID
7. Create Endpoint object
8. Handle missing or optional fields gracefully

---

### 3. CoverageTracker Component

**Purpose:** Manage coverage tracking database (load, save, update, query).

**Interface:**

```python
class CoverageTracker:
    """Manages coverage tracking database."""

    def __init__(self, db_path: Path):
        """Initialize tracker with database path."""
        self.db_path = db_path
        self.db: Optional[CoverageDatabase] = None

    def load(self) -> CoverageDatabase:
        """Load database from JSON file."""
        pass

    def save(self):
        """Save database to JSON file."""
        pass

    def update_endpoint(
        self,
        path: str,
        method: str,
        tool_name: Optional[str] = None,
        status: Optional[Status] = None,
        milestone: Optional[str] = None,
        notes: Optional[str] = None
    ):
        """Update an endpoint's tracking information."""
        pass

    def find_endpoint(self, path: str, method: str) -> Optional[Endpoint]:
        """Find endpoint by path and method."""
        pass

    def get_summary(self) -> Dict:
        """Calculate coverage summary statistics."""
        pass

    def filter_endpoints(
        self,
        tag: Optional[str] = None,
        status: Optional[Status] = None,
        milestone: Optional[str] = None
    ) -> List[Endpoint]:
        """Filter endpoints by criteria."""
        pass
```

**Implementation Details:**

1. **load()**: Read JSON file, deserialize to CoverageDatabase
2. **save()**: Serialize CoverageDatabase to JSON with indentation
3. **update_endpoint()**: Find endpoint, update fields, set implemented_date if status=implemented
4. **find_endpoint()**: Linear search through endpoints list
5. **get_summary()**: Calculate total, by_status, by_tag, coverage_percentage
6. **filter_endpoints()**: Filter by tag AND status AND milestone

---

### 4. ReportGenerator Component

**Purpose:** Generate coverage reports in various formats.

**Interface:**

```python
class ReportGenerator:
    """Generates coverage reports."""

    def __init__(self, tracker: CoverageTracker):
        """Initialize with coverage tracker."""
        self.tracker = tracker

    def generate_markdown(
        self,
        output_path: Path,
        filter_tag: Optional[str] = None,
        filter_status: Optional[Status] = None
    ):
        """Generate Markdown coverage report."""
        pass

    def generate_json(self, output_path: Path):
        """Generate JSON coverage report."""
        pass

    def _format_summary_table(self) -> str:
        """Format summary table for Markdown."""
        pass

    def _format_milestone_table(self) -> str:
        """Format milestone table for Markdown."""
        pass

    def _format_endpoint_section(self, endpoints: List[Endpoint], title: str) -> str:
        """Format endpoint section for Markdown."""
        pass
```

**Implementation Details:**

1. **generate_markdown()**: Create formatted Markdown with tables and sections
2. **generate_json()**: Serialize database to JSON
3. **_format_summary_table()**: Create table grouped by tag
4. **_format_milestone_table()**: Create table grouped by milestone
5. **_format_endpoint_section()**: Create table of endpoints with details

---

## Data Models

### Database Schema (JSON)

```json
{
  "spec_version": "7.0",
  "spec_file": "SpiraRestAPI-v7.0-OpenAPI.json",
  "last_updated": "2026-02-04T00:00:00Z",
  "base_url_note": "Base URL is customer-specific. OpenAPI spec contains example only.",
  "endpoints": [
    {
      "id": "incident_retrieve_by_id",
      "path": "/projects/{project-id}/incidents/{incident-id}",
      "method": "GET",
      "tag": "Incident",
      "operation_id": "Incident_RetrieveById",
      "description": "Retrieves a single incident by ID",
      "parameters": [
        {"name": "project-id", "in": "path", "required": true, "type": "integer"},
        {"name": "incident-id", "in": "path", "required": true, "type": "integer"}
      ],
      "tool_name": null,
      "status": "planned",
      "milestone": "milestone-2",
      "implemented_date": null,
      "notes": "Core CRUD operation - high priority"
    }
  ],
  "summary": {
    "total_endpoints": 450,
    "by_status": {
      "implemented": 0,
      "planned": 50,
      "excluded": 0,
      "deprecated": 0
    },
    "by_tag": {
      "Incident": {"total": 25, "implemented": 0},
      "Task": {"total": 25, "implemented": 0}
    },
    "coverage_percentage": 0.0
  }
}
```

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property Reflection

After analyzing all acceptance criteria, I've identified the following consolidations to eliminate redundancy:

**Consolidations:**
1. Properties 1.1-1.4 (parsing various fields) can be combined into a single comprehensive parsing property
2. Properties 2.2 and 2.3 (storing endpoint fields) can be combined into a single data persistence property
3. Properties 5.1-5.3 (filtering by different criteria) can be combined into a single filtering property
4. Properties 4.4 and 4.5 (grouping by tag/milestone) can be combined into a single grouping property
5. Properties 4.6 and 4.7 (listing implemented/planned endpoints) are covered by the general report content property

**Properties to Keep:**
- Parsing completeness and correctness
- Data persistence (save/load round trip)
- Endpoint uniqueness
- Status validation
- Update functionality
- Error handling
- Filtering logic
- Report generation
- Version handling

---

### Correctness Properties

**Property 1: Parsing Completeness**
*For any* valid OpenAPI 3.0 specification, parsing should extract all endpoints with all required fields (path, method, tag, operation_id, description, parameters) present and correct.
**Validates: Requirements 1.1, 1.2, 1.3, 1.4**

**Property 2: Endpoint ID Uniqueness**
*For any* OpenAPI specification, all generated endpoint IDs should be unique (no duplicates).
**Validates: Requirements 1.5**

**Property 3: Malformed Spec Error Handling**
*For any* malformed OpenAPI specification (invalid JSON, missing required fields, invalid structure), the parser should return a descriptive error message rather than crashing.
**Validates: Requirements 1.6**

**Property 4: Data Persistence Round Trip**
*For any* coverage database, saving to JSON and then loading should produce an equivalent database with all endpoint data preserved.
**Validates: Requirements 2.2, 2.3, 2.8**

**Property 5: Status Value Validation**
*For any* endpoint update, attempting to set a status value that is not one of {implemented, planned, excluded, deprecated} should be rejected with an error.
**Validates: Requirements 2.4, 3.6**

**Property 6: Timestamp Updates**
*For any* database modification, the last_updated timestamp should be updated to reflect the current time.
**Validates: Requirements 2.6**

**Property 7: Endpoint Lookup Correctness**
*For any* endpoint in the database, updating it by path and method should modify exactly that endpoint and no others.
**Validates: Requirements 3.1**

**Property 8: Implemented Date Recording**
*For any* endpoint, when its status is changed to "implemented", the implemented_date field should be automatically set to the current date.
**Validates: Requirements 3.3**

**Property 9: Update Persistence**
*For any* endpoint update, the changes should be immediately persisted to disk such that loading the database returns the updated values.
**Validates: Requirements 3.5**

**Property 10: Non-existent Endpoint Error**
*For any* path and method combination that doesn't exist in the database, attempting to update it should return an error.
**Validates: Requirements 3.4**

**Property 11: Summary Statistics Accuracy**
*For any* coverage database, the calculated summary statistics (total_endpoints, by_status counts, by_tag counts, coverage_percentage) should accurately reflect the actual endpoint data.
**Validates: Requirements 4.3**

**Property 12: Report Grouping Correctness**
*For any* coverage database, endpoints in generated reports should be correctly grouped by tag and milestone with no endpoints missing or duplicated.
**Validates: Requirements 4.4, 4.5**

**Property 13: Filtering Logic**
*For any* combination of filter criteria (tag, status, milestone), the filtered results should include only endpoints that match all specified criteria (AND logic).
**Validates: Requirements 5.1, 5.2, 5.3, 5.4**

**Property 14: CLI Error Messages**
*For any* CLI command that fails (invalid arguments, missing files, etc.), the system should display a clear, actionable error message rather than a stack trace.
**Validates: Requirements 6.7**

**Property 15: CLI Success Confirmation**
*For any* successful CLI command, the system should display a confirmation message indicating what action was completed.
**Validates: Requirements 6.8**

**Property 16: Version Change Detection**
*For any* two different OpenAPI spec versions, initializing the database with the new version should detect the version change.
**Validates: Requirements 7.2**

**Property 17: Data Preservation on Version Update**
*For any* existing tracking information (tool_name, status, milestone, notes), updating to a new spec version should preserve this information for endpoints that still exist.
**Validates: Requirements 7.3**

**Property 18: New Endpoint Addition**
*For any* endpoints that exist in a new spec version but not in the current database, they should be added with default status "planned".
**Validates: Requirements 7.4**

**Property 19: Deprecated Endpoint Marking**
*For any* endpoints that exist in the current database but not in a new spec version, they should be marked with status "deprecated".
**Validates: Requirements 7.5**

---

## Error Handling

### Error Categories

1. **File Errors**
   - OpenAPI spec file not found
   - Database file not found (on load)
   - Permission errors on file operations
   - Invalid JSON in files

2. **Validation Errors**
   - Invalid OpenAPI spec structure
   - Invalid status values
   - Invalid endpoint path/method
   - Missing required fields

3. **CLI Errors**
   - Invalid command arguments
   - Missing required arguments
   - Invalid filter criteria

### Error Response Format

All errors should be returned in a consistent format:

```python
{
    "error": "Brief error description",
    "details": "More detailed explanation",
    "suggestion": "What the user should do to fix it"
}
```

### Error Handling Strategy

1. **Validate Early**: Check inputs before processing
2. **Fail Gracefully**: Never crash with unhandled exceptions
3. **Provide Context**: Include relevant information in error messages
4. **Suggest Solutions**: Tell users how to fix the problem

---

## Testing Strategy

### Unit Tests

**Test Coverage:**
- APIParser: parsing, field extraction, ID generation, error handling
- CoverageTracker: load, save, update, find, filter, summary
- ReportGenerator: markdown generation, JSON generation, formatting
- CLI: command parsing, argument validation, error handling

**Testing Approach:**
- Use pytest for all tests
- Use fixtures for sample data (OpenAPI specs, databases)
- Mock file I/O where appropriate
- Test both success and failure cases
- Aim for 80%+ code coverage

**Example Test Structure:**

```python
# tests/test_api_parser.py
class TestAPIParser:
    def test_parse_complete_spec(self, sample_spec):
        """Test parsing a complete OpenAPI spec."""
        parser = APIParser()
        endpoints = parser.parse_openapi(sample_spec)
        assert len(endpoints) == 3
        assert all(e.path for e in endpoints)
        assert all(e.method for e in endpoints)

    def test_parse_malformed_spec(self, malformed_spec):
        """Test error handling for malformed spec."""
        parser = APIParser()
        with pytest.raises(ValueError) as exc:
            parser.parse_openapi(malformed_spec)
        assert "invalid" in str(exc.value).lower()
```

### Property-Based Tests

**Property Test Configuration:**
- Use hypothesis library for property-based testing
- Minimum 100 iterations per property test
- Each test references its design document property

**Example Property Test:**

```python
# tests/test_properties.py
from hypothesis import given, strategies as st

@given(st.lists(st.text(), min_size=1, max_size=100))
def test_endpoint_id_uniqueness(paths):
    """
    Property 2: Endpoint ID Uniqueness
    Feature: openapi-tracker, Property 2: For any OpenAPI specification,
    all generated endpoint IDs should be unique.
    """
    parser = APIParser()
    # Create mock spec with given paths
    spec = create_mock_spec(paths)
    endpoints = parser.parse_openapi(spec)
    ids = [e.id for e in endpoints]
    assert len(ids) == len(set(ids))  # No duplicates
```

### Integration Tests

**Test Scenarios:**
1. Full workflow: init → update → report
2. Version update workflow: init → update spec → re-init
3. CLI command integration
4. File I/O integration

---

## CLI Interface Design

### Command Structure

```bash
python scripts/api_coverage_tracker.py <command> [options]
```

### Commands

#### 1. init - Initialize Database

```bash
python scripts/api_coverage_tracker.py init --spec <path>

Options:
  --spec PATH    Path to OpenAPI specification file (required)
  --output PATH  Output database path (default: data/api_coverage.json)
  --force        Overwrite existing database

Example:
  python scripts/api_coverage_tracker.py init --spec SpiraRestAPI-v7.0-OpenAPI.json
```

#### 2. update - Update Endpoint Status

```bash
python scripts/api_coverage_tracker.py update --path <path> --method <method> [options]

Options:
  --path PATH        Endpoint path (required)
  --method METHOD    HTTP method (required)
  --tool NAME        Tool name
  --status STATUS    Status (implemented|planned|excluded|deprecated)
  --milestone NAME   Milestone name
  --notes TEXT       Additional notes

Example:
  python scripts/api_coverage_tracker.py update \
    --path "/projects/{project-id}/incidents/{incident-id}" \
    --method GET \
    --tool get_incident_by_id \
    --status implemented \
    --milestone milestone-2
```

#### 3. report - Generate Coverage Report

```bash
python scripts/api_coverage_tracker.py report [options]

Options:
  --format FORMAT    Output format (markdown|json, default: markdown)
  --output PATH      Output file path
  --tag TAG          Filter by tag
  --status STATUS    Filter by status
  --milestone NAME   Filter by milestone

Example:
  python scripts/api_coverage_tracker.py report \
    --format markdown \
    --output docs/api_coverage.md \
    --tag Incident
```

#### 4. summary - Show Coverage Summary

```bash
python scripts/api_coverage_tracker.py summary

Example:
  python scripts/api_coverage_tracker.py summary

Output:
  Total Endpoints: 450
  Implemented: 25 (5.6%)
  Planned: 50 (11.1%)
  Excluded: 10 (2.2%)
  Deprecated: 0 (0.0%)
  Coverage: 5.6%
```

#### 5. list - List Endpoints

```bash
python scripts/api_coverage_tracker.py list [options]

Options:
  --status STATUS    Filter by status
  --tag TAG          Filter by tag
  --milestone NAME   Filter by milestone
  --format FORMAT    Output format (table|json, default: table)

Example:
  python scripts/api_coverage_tracker.py list --status planned --tag Incident
```

---

## Implementation Notes

### File Structure

```
scripts/
  api_coverage_tracker.py    # Main script with all components

data/
  api_coverage.json          # Coverage database (gitignored)
  .gitkeep                   # Keep directory in git

tests/
  test_api_parser.py         # Parser tests
  test_coverage_tracker.py   # Tracker tests
  test_report_generator.py   # Reporter tests
  test_cli.py                # CLI tests
  test_properties.py         # Property-based tests
  fixtures/
    sample_spec.json         # Sample OpenAPI spec
    sample_database.json     # Sample coverage database
```

### Dependencies

**Standard Library Only:**
- json - JSON parsing and serialization
- argparse - CLI argument parsing
- pathlib - Path handling
- datetime - Timestamp handling
- dataclasses - Data models
- typing - Type hints

**No External Dependencies Required**

### Performance Considerations

1. **Parsing**: Use streaming JSON parser for large specs (if needed)
2. **Filtering**: Use list comprehensions (efficient for < 1000 endpoints)
3. **Reporting**: Generate sections incrementally to avoid memory issues
4. **File I/O**: Use buffered I/O for large files

### Maintenance Considerations

1. **Schema Versioning**: Add schema_version field to database for future migrations
2. **Backward Compatibility**: Maintain compatibility with older database versions
3. **Extensibility**: Design for easy addition of new fields and commands
4. **Documentation**: Keep CLI help text in sync with actual behavior

---

## Security Considerations

1. **Path Traversal**: Validate all file paths to prevent directory traversal attacks
2. **File Permissions**: Set appropriate permissions on created files (0644)
3. **Input Validation**: Sanitize all user inputs before processing
4. **No Sensitive Data**: Database contains no sensitive information (API keys, passwords, etc.)

---

## Future Enhancements

1. **Web Dashboard**: Interactive HTML dashboard for coverage visualization
2. **Diff Reports**: Show coverage changes between versions
3. **API Changelog**: Track API changes across spec versions
4. **Bulk Updates**: Update multiple endpoints at once
5. **Export Formats**: Support CSV, Excel, PDF exports
6. **CI/CD Integration**: GitHub Actions workflow for automated reporting
7. **Tool Auto-Detection**: Scan codebase to detect implemented tools
8. **Coverage Goals**: Set and track coverage goals per milestone

---

**End of Design Document**
