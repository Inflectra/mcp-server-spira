# MCP Inflectra Spira Server

**Status:** Active Development - Milestone 0 (Foundation & Infrastructure) Complete

A Model Context Protocol (MCP) server enabling AI assistants to interact with Spira by Inflectra.

## Overview
This project implements a Model Context Protocol (MCP) server that allows AI assistants (like Claude) to interact with the Inflectra Spira platform, providing a bridge between natural language interactions and the Spira REST API.

This server supports all three editions of Spira:
- **SpiraTest:** Test Management When You Need Quality, Agility & Speed
- **SpiraTeam:** Project, Requirements Management & ALM For Agile Teams
- **SpiraPlan:** Program Management & ALM For Scaling Agile & Enterprises


## Features
The Spira MCP server current implements the following features:

### My Work
This feature provides easy access to the list of artifacts that have been assigned to the current user

- **My Tasks:** Provides operations for working with the Spira tasks I have been assigned
- **My Requirements:** Provides operations for working with the Spira requirements I have been assigned
- **My Incidents:** Provides operations for working with the Spira incidents I have been assigned
- **My Test Cases:** Provides operations for working with the Spira test cases I have been assigned
- **My Test Sets:** Provides operations for working with the Spira test sets I have been assigned

### Workspaces
This feature provides tools that let you retrieve and modify the different workspaces inside Spira

- **Programs:** Provides operations for working with Spira programs
- **Products:** Provides operations for working with Spira products
- **Product Templates:** Provides operations for working with Spira product templates

### Program Artifacts
This feature provides tools that let you retrieve and modify the different artifacts inside a Spira program

- **Capabilities:** Provides operations for working with the Spira capabilities in a program backlog
- **Milestones:** Provides operations for working with the Spira milestones in a program

### Product Artifacts
This feature provides tools that let you retrieve and modify the different artifacts inside a Spira product

- **Requirements:** Provides operations for working with the Spira requirements in a product
- **Releases:** Provides operations for working with the Spira releases in a product
- **Test Cases:** Provides operations for working with the Spira test case folders and test cases in a product
- **Test Sets:** Provides operations for working with the Spira test set folders and test sets in a product
- **Test Runs:** Provides operations for working with the Spira test runs in a product
- **Tasks:** Provides operations for working with the Spira tasks in a product
- **Incidents:** Provides operations for working with the Spira incidents (e.g. bugs, enhancements, issues, etc.) in a product
- **Automation Hosts:** Provides operations for working with the Spira automation hosts in a product

### Template Configuration
This feature provides tools that let you view and modify the configuration and settings of Spira product templates

- **Artifact Types:** Retrieves information on the artifact types in a product template, and their sub-types
- **Custom Properties:** Retrieves information on the artifact types in a product template, and their custom properties

### Automation
This feature provides tools that let you integrate automated DevOps tools such as test automation frameworks and CI/CD pipelines

- **Automated Test Runs:** Provides operations for recording automated test run results into Spira
- **Builds:** Provides operations for recording the results of CI/CD builds into Spira

### Specifications
Provides operations for retrieving the product specification files that
can be used to build the functionality of the product using AI.
This is used by Agentic AI development tools such as Amazon Kiro
for building applications from a formal spec.

This module provides the following MCP tools for retrieving the entire product specifications:
- **get_specification_requirements** - returns the data for populating the `requirements.md` file
- **get_specification_design** - returns the data for populating the `design.md` file
- **get_specification_tasks** - returns the data for populating the `tasks.md` file
- **get_specification_test_cases** - returns the data for populating the `test-cases.md` file

## Getting Started

### Prerequisites

- Python 3.13+ (specified in `.python-version` file)
- Inflectra Spira cloud account with appropriate permissions
- Username and active API Key (RSS Token) for this instance

### Installation

```bash
# Clone the repository
git clone https://github.com/Inflectra/mcp-server-spira.git
cd mcp-server-spira

# Simple development mode install
pip install -e .

# Install into a virtual development environment (you may need to create one with uv venv)
uv pip install -e ".[dev]"

# Install from PyPi
pip install mcp-server-spira
```

### Configuration

Create a `.env` file in the project root with the following variables:

```
INFLECTRA_SPIRA_BASE_URL=The base URL for your instance of Spira (typically https://mycompany.spiraservice.net or https://demo-xx.spiraservice.net/mycompany)
INFLECTRA_SPIRA_USERNAME=The login name you use to access Spira
INFLECTRA_SPIRA_API_KEY=The API Key (RSS Token) you use to access the Spira REST API
```

Note: Make sure your API Key is active and saved in your Spira user profile.

### Running the Server directly

```bash
# Development mode with the MCP Inspector
mcp dev src/mcp_server_spira/server.py

# Production mode using shell / command line
python -m mcp_server_spira

# Install in Claude Desktop
mcp install src/mcp_server_spira/server.py --name "Inflectra Spira Server"
```

### Running the MCP Server from Cline

To run the MCP server from within Cline, you don't use the commands above, instead you add the Inflectra MCP server to the configuration JSON file `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "inflectra-spira": {
      "autoApprove": [
        "get_my_incidents",
        "get_products",
        "get_test_cases"
      ],
      "timeout": 60,
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Git\\mcp-server-spira",
        "run",
        "main.py"
      ],
      "env": {
        "INFLECTRA_SPIRA_BASE_URL": "https://mycompany.spiraservice.net",
        "INFLECTRA_SPIRA_USERNAME": "login",
        "INFLECTRA_SPIRA_API_KEY": "{XXXXXX-XXXXXXX-XXXXXXX-XXXXXXX-XXXXX}"
      },
      "type": "stdio"
    }
  }
}
```

### Running the MCP Server from Kiro

To run the MCP server from within Kiro, you don't use the commands above, instead you add the Inflectra MCP server to the configuration JSON file `mcp.json`:

```json
{
  "mcpServers": {
    "inflectra-spira": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Git\\mcp-server-spira",
        "run",
        "main.py"
      ],
      "env": {
        "INFLECTRA_SPIRA_BASE_URL": "https://myinstance.spiraservice.net",
        "INFLECTRA_SPIRA_USERNAME": "mylogin",
        "INFLECTRA_SPIRA_API_KEY": "{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXX}"
      },
      "disabled": false,
      "autoApprove": [
        "get_specification_requirements",
        "get_specification_design",
        "get_specification_tasks",
        "get_specification_test_cases"
      ]
    }
  }
}
```

## Usage Examples

### Quick Start Examples

#### Get Assigned Artifacts

```
Get me my assigned tasks in Spira
```

```
Get me my assigned requirements in Spira
```

#### View Project Structure

```
List all projects in my organization and show me the iterations for the Development team
```

---

## Detailed Usage Guide

### JSON Output Examples

All data-retrieval tools return structured JSON for programmatic processing by LLMs.

#### Example 1: Get My Tasks (with Pagination)

```python
# Get first 25 tasks (default)
result = get_my_tasks()

# Response structure:
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
      "EstimatedEffort": 120,
      "ActualEffort": 60,
      "RemainingEffort": 60,
      "ProjectedEffort": 120,
      "CompletionPercent": 50,
      "StartDate": "2024-01-15T09:00:00Z",
      "EndDate": "2024-01-16T17:00:00Z",
      "CreationDate": "2024-01-10T08:00:00Z",
      "LastUpdateDate": "2024-01-15T14:30:00Z",
      "ReleaseId": 10,
      "ReleaseVersionNumber": "1.5.0",
      "RequirementId": 45,
      "RequirementName": "User Authentication",
      "ProjectId": 55,
      "ProjectName": "Web Application",
      "ComponentId": 3,
      "CreatorId": 4,
      "TaskFolderId": null,
      "CustomProperties": [],
      "Tags": "bug,security",
      "IsAttachments": false
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
```

#### Example 2: Get Products (Workspace Tool)

```python
# Get all products user has access to
result = get_products()

# Response structure:
{
  "data": [
    {
      "ProjectId": 55,
      "Name": "Web Application",
      "Description": "Main web application project",
      "Active": true,
      "CreationDate": "2023-01-15T10:00:00Z",
      "ProjectGroupId": 10,
      "ProjectTemplateId": 1,
      "Website": "https://example.com",
      "WorkingHours": 8,
      "WorkingDays": 5,
      "StartDate": "2023-01-01T00:00:00Z",
      "EndDate": "2024-12-31T00:00:00Z",
      "PercentComplete": 45,
      "RequirementCount": 150
    }
  ]
}
```

#### Example 3: Get Incidents (Product Artifact Tool)

```python
# Get incidents for a specific product
result = get_incidents(product_id=55)

# Response structure:
{
  "data": [
    {
      "IncidentId": 456,
      "Name": "Login page crashes on mobile",
      "Description": "The login page crashes when accessed from mobile devices",
      "IncidentStatusId": 1,
      "IncidentStatusName": "New",
      "IncidentStatusOpenStatus": true,
      "IncidentTypeId": 1,
      "IncidentTypeName": "Bug",
      "PriorityId": 1,
      "PriorityName": "1 - Critical",
      "SeverityId": 1,
      "SeverityName": "1 - Critical",
      "OwnerId": 5,
      "OwnerName": "John Doe",
      "OpenerId": 4,
      "OpenerName": "Jane Smith",
      "EstimatedEffort": 240,
      "ActualEffort": 120,
      "RemainingEffort": 120,
      "ProjectedEffort": 240,
      "CompletionPercent": 50,
      "StartDate": "2024-01-15T09:00:00Z",
      "EndDate": "2024-01-18T17:00:00Z",
      "ClosedDate": null,
      "CreationDate": "2024-01-14T10:00:00Z",
      "LastUpdateDate": "2024-01-16T14:30:00Z",
      "DetectedReleaseId": 8,
      "DetectedReleaseVersionNumber": "1.4.0",
      "ResolvedReleaseId": 10,
      "ResolvedReleaseVersionNumber": "1.5.0",
      "ProjectId": 55,
      "ProjectName": "Web Application"
    }
  ]
}
```

---

### Pagination Usage Patterns

#### Pattern 1: Get First Page (Default)

```python
# Get first 25 items (default behavior)
result = get_my_tasks()
data = json.loads(result)

print(f"Showing {data['pagination']['returned_count']} of {data['pagination']['total_count']} tasks")
# Output: Showing 25 of 150 tasks
```

#### Pattern 2: Get More Items

```python
# Get first 100 items
result = get_my_tasks(limit=100, offset=0)
data = json.loads(result)

# Check if more items exist
if data['pagination']['has_more']:
    print(f"There are {data['pagination']['total_count'] - 100} more tasks")
```

#### Pattern 3: Paginate Through All Results

```python
# Get all tasks by paginating
all_tasks = []
limit = 50
offset = 0

while True:
    result = get_my_tasks(limit=limit, offset=offset)
    data = json.loads(result)

    all_tasks.extend(data["data"])

    if not data["pagination"]["has_more"]:
        break

    offset += limit

print(f"Retrieved {len(all_tasks)} total tasks")
```

#### Pattern 4: Get Specific Page

```python
# Get page 3 (items 51-75)
page = 3
limit = 25
offset = (page - 1) * limit

result = get_my_tasks(limit=limit, offset=offset)
```

---

### Formatting Tool Usage

The `format_artifacts_as_markdown` tool converts JSON to human-readable markdown for **complex workflows** where data has been filtered or processed.

#### When to Use Formatting Tool

✅ **Use when:**
- You've filtered JSON data (can't re-call API with filters)
- You've aggregated or sorted data
- You need consistent formatting across operations
- You're combining multiple artifact types

❌ **Don't use when:**
- Simple display of unmodified API results (LLM can format naturally)
- Programmatic processing (work with JSON directly)

#### Example 1: Filter and Format

```python
# Get tasks
tasks_json = get_my_tasks(limit=100)
tasks = json.loads(tasks_json)

# Filter for critical priority
critical_tasks = [t for t in tasks["data"] if t["TaskPriorityName"] == "Critical"]

# Format filtered results for display
critical_json = json.dumps({"data": critical_tasks})
markdown = format_artifacts_as_markdown(critical_json, "task")

# Output:
"""
## Task [TK:123] - Fix login bug
Users cannot log in with special characters
- **Status:** In Progress
- **Type:** Development
- **Priority:** Critical
- **Owner:** John Doe
- **Effort:** 60/120 min (50% complete)
- **Due Date:** 2024-01-16
- **Release:** 1.5.0

## Task [TK:124] - Update security documentation
...
"""
```

#### Example 2: Combine Multiple Artifact Types

```python
# Get tasks and incidents
tasks = get_my_tasks()
incidents = get_my_incidents()

# Format both for combined display
combined_markdown = (
    "# My Tasks\n\n" +
    format_artifacts_as_markdown(tasks, "task") +
    "\n\n# My Incidents\n\n" +
    format_artifacts_as_markdown(incidents, "incident")
)
```

#### Example 3: Sort and Format

```python
# Get tasks
tasks_json = get_my_tasks(limit=100)
tasks = json.loads(tasks_json)

# Sort by due date
sorted_tasks = sorted(
    tasks["data"],
    key=lambda t: t.get("EndDate", "9999-12-31")
)

# Format sorted results
sorted_json = json.dumps({"data": sorted_tasks})
markdown = format_artifacts_as_markdown(sorted_json, "task")
```

---

### Error Handling Examples

All tools return structured error responses for validation failures and API errors.

#### Example 1: Validation Error

```python
# Invalid pagination parameter
result = get_my_tasks(limit=1000, offset=0)

# Error response:
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
```

#### Example 2: Invalid Product ID

```python
# Negative product ID
result = get_tasks(product_id=-1)

# Error response:
{
  "error": "Invalid product_id parameter",
  "error_code": "INVALID_VALUE",
  "details": {
    "parameter": "product_id",
    "value": -1,
    "expected": ">= 1"
  },
  "suggestion": "product_id must be >= 1"
}
```

#### Example 3: API Error

```python
# API connection failure
result = get_my_tasks()

# Error response:
{
  "error": "Failed to retrieve tasks",
  "error_code": "API_ERROR",
  "details": {
    "message": "Connection timeout"
  },
  "suggestion": "Check API connectivity and authentication"
}
```

#### Error Handling Pattern

```python
result = get_my_tasks(limit=25, offset=0)
data = json.loads(result)

# Check for errors
if "error" in data:
    print(f"Error: {data['error']}")
    print(f"Code: {data['error_code']}")
    if "suggestion" in data:
        print(f"Suggestion: {data['suggestion']}")
    # Handle error appropriately
else:
    # Process successful response
    tasks = data["data"]
    pagination = data["pagination"]
    print(f"Retrieved {pagination['returned_count']} tasks")
```

---

### Common Workflow Examples

#### Workflow 1: Find Overdue Tasks

```python
from datetime import datetime

# Get all my tasks
tasks_json = get_my_tasks(limit=100)
tasks = json.loads(tasks_json)

# Filter overdue tasks
now = datetime.now()
overdue = [
    t for t in tasks["data"]
    if t.get("EndDate") and datetime.fromisoformat(t["EndDate"].replace("Z", "+00:00")) < now
]

print(f"Found {len(overdue)} overdue tasks")
```

#### Workflow 2: Calculate Workload

```python
# Get all my tasks
tasks_json = get_my_tasks(limit=500)
tasks = json.loads(tasks_json)

# Calculate effort totals
total_estimated = sum(t.get("EstimatedEffort", 0) for t in tasks["data"])
total_actual = sum(t.get("ActualEffort", 0) for t in tasks["data"])
total_remaining = sum(t.get("RemainingEffort", 0) for t in tasks["data"])

print(f"Workload Summary:")
print(f"  Estimated: {total_estimated/60:.1f} hours")
print(f"  Actual: {total_actual/60:.1f} hours")
print(f"  Remaining: {total_remaining/60:.1f} hours")
```

#### Workflow 3: Group Tasks by Release

```python
from collections import defaultdict

# Get all my tasks
tasks_json = get_my_tasks(limit=100)
tasks = json.loads(tasks_json)

# Group by release
by_release = defaultdict(list)
for task in tasks["data"]:
    release = task.get("ReleaseVersionNumber", "Unscheduled")
    by_release[release].append(task)

# Display summary
for release, tasks in by_release.items():
    print(f"{release}: {len(tasks)} tasks")
```

#### Workflow 4: Find Related Incidents

```python
# Get my tasks
tasks_json = get_my_tasks(limit=100)
tasks = json.loads(tasks_json)

# Get my incidents
incidents_json = get_my_incidents(limit=100)
incidents = json.loads(incidents_json)

# Find incidents with same release
task_releases = {t.get("ReleaseId") for t in tasks["data"] if t.get("ReleaseId")}
related_incidents = [
    i for i in incidents["data"]
    if i.get("ResolvedReleaseId") in task_releases
]

print(f"Found {len(related_incidents)} incidents related to your task releases")
```

---

### Tool Categories and Examples

#### MyWork Tools (with Pagination)

```python
# Get my tasks
get_my_tasks(limit=25, offset=0)

# Get my incidents
get_my_incidents(limit=25, offset=0)

# Get my requirements
get_my_requirements(limit=25, offset=0)

# Get my test cases
get_my_testcases(limit=25, offset=0)

# Get my test sets
get_my_testsets(limit=25, offset=0)
```

#### Workspace Tools (no pagination)

```python
# Get all products
get_products()

# Get all programs
get_programs()

# Get all product templates
get_product_templates()

# Get specific product
get_product_by_id(product_id=55)

# Get products in a program
get_program_products(program_id=10)

# Get specific product template
get_product_template(template_id=1)
```

#### Product Artifacts Tools

```python
# Get tasks in a product
get_tasks(product_id=55)

# Get incidents in a product
get_incidents(product_id=55)

# Get requirements in a product
get_requirements(product_id=55)

# Get test cases in a product
get_test_cases(product_id=55)

# Get test sets in a product
get_test_sets(product_id=55)

# Get releases in a product
get_releases(product_id=55)

# Get specific release
get_release_by_id(product_id=55, release_id=10)

# Get risks in a product
get_risks(product_id=55)

# Get test runs in a product
get_test_runs(product_id=55)

# Get automation hosts in a product
get_automation_hosts(product_id=55)
```

#### Program Artifacts Tools

```python
# Get capabilities in a program
get_capabilities(program_id=10)

# Get milestones in a program
get_milestones(program_id=10)
```

#### Template Configuration Tools

```python
# Get artifact types in a template
get_artifact_types(template_id=1)

# Get custom properties in a template
get_custom_properties(template_id=1)
```

#### Automation Tools

```python
# Record automated test run
record_automated_test_run(
    product_id=55,
    test_name="Login Test",
    short_message="Test passed",
    long_message="All login scenarios passed successfully",
    error_count=0,
    test_case_id=123,
    execution_status_id=2  # 2 = Passed
)

# Create build
create_build(
    product_id=55,
    release_id=10,
    build_status_id=2,  # 2 = Passed
    name="Build 1.5.0.123",
    description="Production build for release 1.5.0",
    commits=["abc123", "def456"]
)
```

#### Specification Tools

```python
# Get requirements specification
get_specification_requirements(product_id=55, release_id=10)

# Get design specification
get_specification_design(product_id=55, release_id=10)

# Get tasks specification
get_specification_tasks(product_id=55, release_id=10)

# Get test cases specification
get_specification_test_cases(product_id=55, release_id=10)
```

## Documentation

For comprehensive information about the project:

- **[Development Setup Guide](docs/development_setup.md)** - Complete guide for setting up your development environment
- **[Architecture Documentation](docs/architecture.md)** - Detailed explanation of the project structure and design patterns
- **[Master Plan](SPIRA_MCP_ENHANCEMENT_MASTER_PLAN.md)** - Roadmap and enhancement plan for the project

## Development

### Setting Up Development Environment

For detailed setup instructions, see the [Development Setup Guide](docs/development_setup.md).

Quick start:

```bash
# Clone the repository
git clone https://github.com/Inflectra/mcp-server-spira.git
cd mcp-server-spira

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .
```

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. The hooks automatically run linting, formatting, type checking, and tests before each commit.

#### Installing Pre-commit Hooks

```bash
# Install the pre-commit hooks
pre-commit install
```

#### Running Hooks Manually

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run hooks on staged files only
pre-commit run
```

#### Skipping Hooks (Use Sparingly)

For urgent commits where you need to bypass the hooks:

```bash
git commit --no-verify -m "urgent fix"
```

**Note:** Only use `--no-verify` when absolutely necessary. The hooks are there to catch issues early.

#### What the Hooks Check

- **Trailing whitespace**: Removes trailing whitespace from files
- **End of file fixer**: Ensures files end with a newline
- **YAML/JSON validation**: Checks syntax of YAML and JSON files
- **Large files**: Prevents accidentally committing large files (>1MB)
- **Merge conflicts**: Detects unresolved merge conflict markers
- **Private keys**: Detects accidentally committed private keys
- **Ruff**: Fast Python linter and formatter
- **Black**: Python code formatter
- **Mypy**: Static type checker
- **Pytest**: Runs the test suite

### Running Tests

This project uses pytest for testing with coverage reporting.

#### Basic Test Commands

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_server.py

# Run tests matching a pattern
pytest -k "test_server"
```

#### Coverage Reports

```bash
# Run tests with coverage report (terminal output)
pytest --cov

# Run tests with detailed coverage showing missing lines
pytest --cov --cov-report=term-missing

# Generate HTML coverage report
pytest --cov --cov-report=html

# Open the HTML coverage report (after generating)
# The report will be in htmlcov/index.html
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
start htmlcov/index.html  # On Windows
```

#### Test Markers

Tests are organized with markers for selective execution:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

#### Current Test Coverage

Coverage reports are automatically generated when running tests and can be viewed in the `htmlcov/` directory.

### Project Structure

The project is structured into feature modules, each implementing specific Inflectra Spira capabilities:

- `features/mywork`: Accessing a user's assigned artifacts and updating their status/progress
- `features/projects`: Project management capabilities
- `features/programs`: Program management features
- `utils`: Common utilities and client initialization

For more information on development, see the [CLAUDE.md](CLAUDE.md) file.

### Tool Documentation Generator

The project includes a documentation generator script that creates comprehensive tool documentation from the OpenAPI specification.

#### Purpose

The `generate_tool_docs.py` script automates the creation of tool docstrings by:
- Extracting endpoint information from the Spira OpenAPI spec
- Generating structured docstring templates with parameter and return value documentation
- Identifying areas that need human clarification (ambiguous descriptions, business logic questions, etc.)
- Creating a markdown report with generated documentation and clarification checklists

#### Usage

```bash
python scripts/generate_tool_docs.py \
  --spec SpiraRestAPI-v7.0-OpenAPI.json \
  --output docs/tool_documentation_report.md
```

#### Output

The script generates a comprehensive report including:
- Generated docstring templates for each tool
- Structured clarification checklists organized by severity (High/Medium/Low)
- Examples of good clarification requests
- OpenAPI spec references for each issue

Example output:
```
✅ Documentation report generated: docs/tool_documentation_report.md
📄 Generated documentation for 5 tools
⚠️  Total clarifications needed: 162
```

#### Current Scope and Limitations

**Important:** The documentation generator is currently scoped for **Milestone 1** and has the following limitations:

1. **Hardcoded Tool List**: The script documents a fixed set of 5 "my work" tools:
   - `get_my_tasks` → `/tasks`
   - `get_my_incidents` → `/incidents`
   - `get_my_requirements` → `/requirements`
   - `get_my_test_cases` → `/test-cases`
   - `get_my_test_sets` → `/test-sets`

2. **Not Dynamic**: The script does not automatically discover all endpoints in the OpenAPI spec. It only generates documentation for the tools explicitly listed in the `tools` array within the `generate_documentation_report()` method.

3. **Manual Extension Required**: To document additional tools, you must:
   - Edit `scripts/generate_tool_docs.py`
   - Add new entries to the `tools` list in the format: `(tool_name, endpoint_path, http_method, artifact_type)`
   - Ensure the endpoint exists in the OpenAPI spec

#### Example: Adding More Tools

To document workspace tools in addition to "my work" tools:

```python
# In scripts/generate_tool_docs.py, modify the tools list:
tools = [
    # My work tools
    ("get_my_tasks", "/tasks", "get", "task"),
    ("get_my_incidents", "/incidents", "get", "incident"),
    ("get_my_requirements", "/requirements", "get", "requirement"),
    ("get_my_test_cases", "/test-cases", "get", "test_case"),
    ("get_my_test_sets", "/test-sets", "get", "test_set"),
    # Workspace tools (add these)
    ("get_products", "/projects", "get", "product"),
    ("get_programs", "/programs", "get", "program"),
]
```

#### Future Enhancements

Potential improvements for future milestones:
- Dynamic endpoint discovery from OpenAPI spec
- Configuration file for specifying which tools to document
- Filtering by OpenAPI tags or operation IDs
- Command-line options to select specific tool categories

#### Clarification Detection

The script implements comprehensive clarification detection covering:
- Missing or ambiguous descriptions
- Vague field descriptions (e.g., "the id", "the name")
- Complex nested schemas
- Business logic questions (similar fields, ID/Name pairs)
- Workflow context questions
- Performance implications
- Edge cases with nullable fields

For more details, see [docs/clarification_detection_summary.md](docs/clarification_detection_summary.md).

### Spira pytest Integration

This project uses [pytest-spiratest](https://spiradoc.inflectra.com/Unit-Testing-Integration/Integrating-with-PyTest/) to automatically report test results to Spira.

#### Quick Setup

1. Install: `pip install pytest-spiratest`
2. Configure: `cp .env.spira.template .env.spira` and edit with your credentials
3. Run tests: `pytest tests/` - results automatically report to Spira

#### Key Features

- One test class = one Spira test case (24 test classes currently mapped)
- Credentials in `.env.spira` (not in version control)
- Test case mappings in `spira.cfg` (in version control)
- Validation script ensures 100% coverage: `python scripts/validate_spira_integration.py`

See [docs/spira_pytest_integration.md](docs/spira_pytest_integration.md) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- Uses [Inflectra Spira v7.0 REST API](https://spiradoc.inflectra.com/Developers/API-Overview/)

<!-- mcp-name: io.github.Inflectra/mcp-server-spira -->
