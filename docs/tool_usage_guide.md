# Spira MCP Server - Tool Usage Guide

**Version:** 1.0.0
**Last Updated:** 2026-02-15

This guide provides comprehensive usage information for all Spira MCP Server tools, including workflow context, "when to use" guidance, and practical examples.

---

## Table of Contents

- [Overview](#overview)
- [Tool Categories](#tool-categories)
- [MyWork Tools](#mywork-tools)
- [Workspace Tools](#workspace-tools)
- [Product Artifacts Tools](#product-artifacts-tools)
- [Program Artifacts Tools](#program-artifacts-tools)
- [Template Configuration Tools](#template-configuration-tools)
- [Automation Tools](#automation-tools)
- [Specification Tools](#specification-tools)
- [Formatting Tool](#formatting-tool)
- [Common Workflows](#common-workflows)

---

## Overview

All Spira MCP Server tools follow a **JSON-first architecture** that enables programmatic data processing by LLMs. This guide explains when and how to use each tool effectively.

### Key Principles

1. **JSON Output:** All data-retrieval tools return structured JSON
2. **Explicit Pagination:** "My work" tools support `limit` and `offset` parameters
3. **Input Validation:** All tools validate inputs before API calls
4. **Structured Errors:** Errors include error codes, details, and suggestions
5. **Optional Formatting:** Use `format_artifacts_as_markdown` for filtered/processed data

---

## Tool Categories

### MyWork Tools (5 tools)
Personal artifacts assigned to the current user with client-side pagination.

### Workspace Tools (6 tools)
Products, programs, and templates the user has access to.

### Product Artifacts Tools (9 tools)
Artifacts within a specific product (tasks, incidents, requirements, etc.).

### Program Artifacts Tools (2 tools)
Artifacts within a specific program (capabilities, milestones).

### Template Configuration Tools (2 tools)
Configuration and settings for product templates.

### Automation Tools (2 tools)
Integration with CI/CD pipelines and test automation frameworks.

### Specification Tools (4 tools)
Product specification files for agentic AI development tools.

### Formatting Tool (1 tool)
Convert JSON to markdown for complex workflows.

---

## MyWork Tools

### get_my_tasks

**Purpose:** Retrieve tasks assigned to the current user

**When to Use:**
- Getting personal task list for daily standup
- Analyzing personal workload and capacity
- Finding tasks by status or priority (filter the JSON)
- Tracking progress on assigned work
- Generating personal productivity reports

**When NOT to Use:**
- Getting all tasks in a product → Use `get_tasks(product_id)`
- Getting tasks assigned to other users → Use product-level queries
- Creating or updating tasks → Use automation tools (future milestone)

**Pagination:** Client-side (API returns all results, paginated in Python)

**Example Workflows:**
```python
# Daily standup: Get my tasks and show critical ones
tasks_json = get_my_tasks(limit=100)
tasks = json.loads(tasks_json)
critical = [t for t in tasks["data"] if t["TaskPriorityName"] == "Critical"]

# Workload analysis: Calculate total effort
total_remaining = sum(t.get("RemainingEffort", 0) for t in tasks["data"])
print(f"Remaining work: {total_remaining/60:.1f} hours")

# Find overdue tasks
from datetime import datetime
now = datetime.now()
overdue = [t for t in tasks["data"]
           if t.get("EndDate") and datetime.fromisoformat(t["EndDate"].replace("Z", "+00:00")) < now]
```

**Related Tools:**
- `get_tasks(product_id)` - Get all tasks in a product
- `format_artifacts_as_markdown` - Format filtered results for display

---

### get_my_incidents

**Purpose:** Retrieve incidents (bugs, issues) assigned to the current user

**When to Use:**
- Getting personal bug list for triage
- Tracking incident resolution progress
- Finding critical or high-priority incidents
- Analyzing incident workload
- Generating bug fix reports

**When NOT to Use:**
- Getting all incidents in a product → Use `get_incidents(product_id)`
- Getting incidents assigned to other users → Use product-level queries
- Creating or updating incidents → Use automation tools (future milestone)

**Pagination:** Client-side

**Example Workflows:**
```python
# Triage: Get critical incidents
incidents_json = get_my_incidents(limit=100)
incidents = json.loads(incidents_json)
critical = [i for i in incidents["data"] if i["PriorityName"] == "1 - Critical"]

# Find incidents by release
release_incidents = [i for i in incidents["data"]
                     if i.get("ResolvedReleaseVersionNumber") == "1.5.0"]

# Group by status
from collections import defaultdict
by_status = defaultdict(list)
for incident in incidents["data"]:
    by_status[incident["IncidentStatusName"]].append(incident)
```

**Related Tools:**
- `get_incidents(product_id)` - Get all incidents in a product
- `format_artifacts_as_markdown` - Format filtered results for display

---

### get_my_requirements

**Purpose:** Retrieve requirements assigned to the current user

**When to Use:**
- Getting personal requirement list for sprint planning
- Tracking requirement implementation progress
- Analyzing requirement workload and story points
- Finding requirements by importance or status
- Generating sprint reports

**When NOT to Use:**
- Getting all requirements in a product → Use `get_requirements(product_id)`
- Getting requirements assigned to other users → Use product-level queries
- Creating or updating requirements → Use write operations (future milestone)

**Pagination:** Client-side

**Example Workflows:**
```python
# Sprint planning: Get requirements by importance
requirements_json = get_my_requirements(limit=100)
requirements = json.loads(requirements_json)
critical = [r for r in requirements["data"] if r["ImportanceName"] == "Critical"]

# Calculate story points
total_points = sum(r.get("EstimatePoints", 0) for r in requirements["data"])

# Find requirements with test coverage issues
low_coverage = [r for r in requirements["data"]
                if r.get("CoverageCountTotal", 0) < 3]
```

**Related Tools:**
- `get_requirements(product_id)` - Get all requirements in a product
- `format_artifacts_as_markdown` - Format filtered results for display

---

### get_my_testcases

**Purpose:** Retrieve test cases assigned to the current user

**When to Use:**
- Getting personal test case list for test execution planning
- Tracking test case authoring progress
- Finding test cases by status or priority
- Analyzing test coverage for assigned requirements
- Generating test execution reports

**When NOT to Use:**
- Getting all test cases in a product → Use `get_test_cases(product_id)`
- Getting test cases assigned to other users → Use product-level queries
- Creating or updating test cases → Use write operations (future milestone)

**Pagination:** Client-side

**Example Workflows:**
```python
# Test execution planning: Get test cases by priority
testcases_json = get_my_testcases(limit=100)
testcases = json.loads(testcases_json)
critical = [tc for tc in testcases["data"] if tc["TestCasePriorityName"] == "1 - Critical"]

# Find failed test cases
failed = [tc for tc in testcases["data"] if tc["ExecutionStatusName"] == "Failed"]

# Calculate test execution time
total_duration = sum(tc.get("EstimatedDuration", 0) for tc in testcases["data"])
```

**Related Tools:**
- `get_test_cases(product_id)` - Get all test cases in a product
- `format_artifacts_as_markdown` - Format filtered results for display

---

### get_my_testsets

**Purpose:** Retrieve test sets (test suites) assigned to the current user

**When to Use:**
- Getting personal test set list for test execution planning
- Tracking test suite execution progress
- Finding test sets by status or release
- Analyzing test suite results
- Generating test execution reports

**When NOT to Use:**
- Getting all test sets in a product → Use `get_test_sets(product_id)`
- Getting test sets assigned to other users → Use product-level queries
- Creating or updating test sets → Use write operations (future milestone)

**Pagination:** Client-side

**Example Workflows:**
```python
# Test execution: Get test sets by status
testsets_json = get_my_testsets(limit=100)
testsets = json.loads(testsets_json)
in_progress = [ts for ts in testsets["data"] if ts["TestSetStatusName"] == "In Progress"]

# Find test sets with failures
failed = [ts for ts in testsets["data"] if ts["CountFailed"] > 0]

# Calculate test execution time
total_duration = sum(ts.get("ActualDuration", 0) for ts in testsets["data"])
```

**Related Tools:**
- `get_test_sets(product_id)` - Get all test sets in a product
- `format_artifacts_as_markdown` - Format filtered results for display

---

## Workspace Tools

### get_products

**Purpose:** Retrieve all products (projects) the user has access to

**When to Use:**
- Discovering available products before querying product-specific data
- Listing products for user selection
- Validating product IDs before other operations
- Getting product metadata for reporting
- Finding active vs inactive products

**When NOT to Use:**
- Getting detailed information about a single product → Use `get_product_by_id(product_id)`
- Getting products in a specific program → Use `get_program_products(program_id)`

**Example Workflows:**
```python
# List all active products
products_json = get_products()
products = json.loads(products_json)
active = [p for p in products["data"] if p["Active"]]

# Find product by name
web_app = next((p for p in products["data"] if "Web" in p["Name"]), None)

# Get product IDs for batch operations
product_ids = [p["ProjectId"] for p in products["data"]]
```

**Related Tools:**
- `get_product_by_id(product_id)` - Get single product details
- `get_programs()` - Get program-level groupings
- `get_program_products(program_id)` - Get products in a program

---

### get_programs

**Purpose:** Retrieve all programs the user has access to

**When to Use:**
- Discovering available programs
- Listing programs for user selection
- Validating program IDs before other operations
- Getting program metadata for reporting
- Finding active vs inactive programs

**When NOT to Use:**
- Getting products within a program → Use `get_program_products(program_id)`
- Getting program-level artifacts → Use `get_capabilities` or `get_milestones`

**Example Workflows:**
```python
# List all active programs
programs_json = get_programs()
programs = json.loads(programs_json)
active = [p for p in programs["data"] if p["isActive"]]

# Find program by name
eng_program = next((p for p in programs["data"] if "Engineering" in p["Name"]), None)
```

**Related Tools:**
- `get_program_products(program_id)` - Get products in a program
- `get_capabilities(program_id)` - Get capabilities in a program
- `get_milestones(program_id)` - Get milestones in a program

---

### get_product_templates

**Purpose:** Retrieve all product templates the user has access to

**When to Use:**
- Discovering available templates for creating new products
- Listing templates for user selection
- Validating template IDs before product creation
- Getting template metadata for configuration

**When NOT to Use:**
- Getting detailed template configuration → Use `get_product_template(template_id)`
- Getting artifact types in a template → Use `get_artifact_types(template_id)`
- Getting custom properties in a template → Use `get_custom_properties(template_id)`

**Example Workflows:**
```python
# List all active templates
templates_json = get_product_templates()
templates = json.loads(templates_json)
active = [t for t in templates["data"] if t["IsActive"]]

# Find template by name
scrum_template = next((t for t in templates["data"] if "Scrum" in t["Name"]), None)
```

**Related Tools:**
- `get_product_template(template_id)` - Get single template details
- `get_artifact_types(template_id)` - Get artifact types in template
- `get_custom_properties(template_id)` - Get custom properties in template

---

## Product Artifacts Tools

### get_tasks (product-level)

**Purpose:** Retrieve all tasks in a specific product

**When to Use:**
- Getting all tasks in a product for reporting
- Finding tasks across all users and releases
- Analyzing product-wide task metrics
- Generating product-level reports

**When NOT to Use:**
- Getting only your assigned tasks → Use `get_my_tasks()`
- Getting a single task → Use `get_task_by_id` (future milestone)
- Filtering tasks by complex criteria → Use search/filter tools (future milestone)

**API Method:** POST (uses `/search` endpoint with empty filter array)

**Example Workflows:**
```python
# Get all tasks in product
tasks_json = get_tasks(product_id=55)
tasks = json.loads(tasks_json)

# Find unassigned tasks
unassigned = [t for t in tasks["data"] if not t.get("OwnerId")]

# Group by release
from collections import defaultdict
by_release = defaultdict(list)
for task in tasks["data"]:
    release = task.get("ReleaseVersionNumber", "Unscheduled")
    by_release[release].append(task)
```

**Related Tools:**
- `get_my_tasks()` - Get only your assigned tasks
- `format_artifacts_as_markdown` - Format filtered results

---

### get_incidents (product-level)

**Purpose:** Retrieve all incidents in a specific product

**When to Use:**
- Getting all incidents in a product for reporting
- Finding incidents across all users and releases
- Analyzing product-wide incident metrics
- Generating product-level bug reports

**When NOT to Use:**
- Getting only your assigned incidents → Use `get_my_incidents()`
- Getting a single incident → Use `get_incident_by_id` (future milestone)
- Filtering incidents by complex criteria → Use search/filter tools (future milestone)

**API Method:** POST (uses `/search` endpoint)

**Example Workflows:**
```python
# Get all incidents in product
incidents_json = get_incidents(product_id=55)
incidents = json.loads(incidents_json)

# Find critical open incidents
critical_open = [i for i in incidents["data"]
                 if i["PriorityName"] == "1 - Critical" and i["IncidentStatusOpenStatus"]]

# Group by type
from collections import defaultdict
by_type = defaultdict(list)
for incident in incidents["data"]:
    by_type[incident["IncidentTypeName"]].append(incident)
```

**Related Tools:**
- `get_my_incidents()` - Get only your assigned incidents
- `format_artifacts_as_markdown` - Format filtered results

---

## Formatting Tool

### format_artifacts_as_markdown

**Purpose:** Convert JSON data to human-readable markdown for complex workflows

**When to Use:**
✅ After filtering or processing JSON data (can't re-call API with filters)
✅ After aggregating or sorting data
✅ When combining multiple artifact types in one display
✅ When you need consistent formatting across operations

**When NOT to Use:**
❌ Simple "show me my tasks" requests (LLM can format naturally)
❌ Direct display of unmodified API results
❌ Programmatic processing (work with JSON directly)

**Supported Artifact Types:**
- `"task"` - Tasks
- `"incident"` - Incidents
- `"requirement"` - Requirements
- `"test_case"` - Test cases
- `"test_set"` - Test sets

**Example Workflows:**
```python
# Filter and format
tasks_json = get_my_tasks(limit=100)
tasks = json.loads(tasks_json)
critical = [t for t in tasks["data"] if t["TaskPriorityName"] == "Critical"]
markdown = format_artifacts_as_markdown(json.dumps({"data": critical}), "task")

# Combine multiple types
tasks = get_my_tasks()
incidents = get_my_incidents()
combined = (
    "# My Tasks\n\n" + format_artifacts_as_markdown(tasks, "task") +
    "\n\n# My Incidents\n\n" + format_artifacts_as_markdown(incidents, "incident")
)

# Sort and format
tasks_json = get_my_tasks(limit=100)
tasks = json.loads(tasks_json)
sorted_tasks = sorted(tasks["data"], key=lambda t: t.get("EndDate", "9999-12-31"))
markdown = format_artifacts_as_markdown(json.dumps({"data": sorted_tasks}), "task")
```

---

## Common Workflows

### Workflow 1: Daily Standup Report

```python
# Get all my tasks
tasks_json = get_my_tasks(limit=100)
tasks = json.loads(tasks_json)

# Sort by priority
priority_order = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}
sorted_tasks = sorted(tasks["data"], key=lambda t: priority_order.get(t["TaskPriorityName"], 5))

# Format for display
markdown = format_artifacts_as_markdown(json.dumps({"data": sorted_tasks}), "task")
print(markdown)
```

### Workflow 2: Sprint Planning

```python
# Get requirements for current sprint
requirements_json = get_my_requirements(limit=100)
requirements = json.loads(requirements_json)

# Filter by release
sprint_requirements = [r for r in requirements["data"]
                       if r.get("ReleaseVersionNumber") == "Sprint 23"]

# Calculate story points
total_points = sum(r.get("EstimatePoints", 0) for r in sprint_requirements)
print(f"Sprint 23: {len(sprint_requirements)} requirements, {total_points} story points")
```

### Workflow 3: Bug Triage

```python
# Get all incidents
incidents_json = get_my_incidents(limit=100)
incidents = json.loads(incidents_json)

# Group by priority
from collections import defaultdict
by_priority = defaultdict(list)
for incident in incidents["data"]:
    by_priority[incident["PriorityName"]].append(incident)

# Display critical incidents
critical = by_priority.get("1 - Critical", [])
if critical:
    markdown = format_artifacts_as_markdown(json.dumps({"data": critical}), "incident")
    print(f"Critical Incidents ({len(critical)}):\n{markdown}")
```

### Workflow 4: Test Execution Planning

```python
# Get test sets
testsets_json = get_my_testsets(limit=100)
testsets = json.loads(testsets_json)

# Find test sets for current release
release_testsets = [ts for ts in testsets["data"]
                    if ts.get("ReleaseVersionNumber") == "1.5.0"]

# Calculate execution time
total_duration = sum(ts.get("EstimatedDuration", 0) for ts in release_testsets)
print(f"Release 1.5.0: {len(release_testsets)} test sets, {total_duration} minutes")
```

---

## Best Practices

### 1. Always Check Pagination Metadata

```python
result = get_my_tasks(limit=25)
data = json.loads(result)

if data["pagination"]["has_more"]:
    print(f"Showing {data['pagination']['returned_count']} of {data['pagination']['total_count']} tasks")
    print("Use limit/offset parameters to get more results")
```

### 2. Handle Errors Gracefully

```python
result = get_my_tasks(limit=25)
data = json.loads(result)

if "error" in data:
    print(f"Error: {data['error']}")
    print(f"Suggestion: {data.get('suggestion', 'Check parameters')}")
else:
    # Process successful response
    tasks = data["data"]
```

### 3. Use Formatting Tool Judiciously

```python
# ✅ Good: Format filtered data
tasks_json = get_my_tasks(limit=100)
tasks = json.loads(tasks_json)
critical = [t for t in tasks["data"] if t["TaskPriorityName"] == "Critical"]
markdown = format_artifacts_as_markdown(json.dumps({"data": critical}), "task")

# ❌ Bad: Format unmodified data (LLM can do this naturally)
tasks_json = get_my_tasks()
markdown = format_artifacts_as_markdown(tasks_json, "task")  # Unnecessary!
```

### 4. Validate Product IDs

```python
# ✅ Good: Validate before calling
product_id = 55
if product_id > 0:
    result = get_tasks(product_id=product_id)
else:
    print("Invalid product ID")

# ❌ Bad: Let API fail
result = get_tasks(product_id=-1)  # Will return validation error
```

---

**Version:** 1.0.0
**Last Updated:** 2026-02-15
**See Also:** [MIGRATION.md](../MIGRATION.md), [CHANGELOG.md](../CHANGELOG.md), [README.md](../README.md)
