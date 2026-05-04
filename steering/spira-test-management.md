# Spira Test Management

This steering file provides context for working with Spira test cases, test sets, test runs, and test execution. Load it when the user is asking about test cases, test sets, test runs, test execution, or requirements coverage via tests.

## Key Concepts

### Test Cases

A test case describes how to validate a feature or process. It contains an ordered list of **test steps**, each with:
- **Description** — what the tester should do
- **Expected Result** — what the system should do in response
- **Sample Data** — example inputs to use (supports parameter tokens like `${username}`)

Test cases are organized in folders and identified by a `TC:` token (e.g. TC:42). Each test case tracks its most recent execution status across all runs.

#### Linked Test Cases (Reuse)

A test step can embed an entire other test case as a **linked step**. This avoids duplicating common sequences (e.g. a login flow). When a linked test case has parameters, the parent test case can override the default parameter values for that specific link. Parameter overrides cascade: once a value is overridden at a given level in the chain, higher-level test cases cannot override it again.

#### Parameters

Test cases can declare named parameters with optional default values. Parameters are referenced in test step fields using `${parameter_name}` tokens. Parameters make test cases reusable across different data scenarios without duplication.

### Test Sets

A test set is a **collection of test cases** grouped for a specific testing purpose (e.g. regression suite for Sprint 3). Key properties:
- Assigned to a **release or sprint** — execution results are recorded against that release
- Can pre-populate custom list properties (e.g. operating system, browser) that are inherited by all test runs created from the set
- Identified by a `TX:` token

When a tester executes a test set, the release and custom property values are pre-populated from the test set and cannot be changed at execution time (unless they were not set on the test set).

### Test Runs

A test run is an **immutable record** of a single execution of a test case (or a group of test cases from a test set). Once finished, a test run cannot be amended. Key fields:
- `TestRunId` — unique identifier
- `Name` — name of the test case that was run
- `ExecutionStatusName` — overall result (see statuses below)
- `EndDate` — when the run was completed
- `ReleaseId` / `ReleaseName` — the release it was executed against
- `TestSetId` / `TestSetName` — the test set it came from (if any)
- `TesterId` — who ran it

Test runs are identified by a `TR:` token.

#### Execution Statuses

| Status         | Meaning                                             |
| -------------- | --------------------------------------------------- |
| Passed         | All steps passed (or passed + N/A)                  |
| Failed         | At least one step failed                            |
| Blocked        | At least one step blocked, none failed              |
| Caution        | At least one step cautioned, none blocked or failed |
| Not Run        | No steps have been executed yet                     |
| Not Applicable | Step was marked as not applicable to this run       |

The overall test case status is determined by the most severe step status: Failed > Blocked > Caution > Passed/N/A.

### Pending Test Runs

When a tester leaves a test execution session before finishing (by clicking "Leave"), the test run is saved as **pending**. Pending test runs appear under "My Pending Test Runs" on the tester's home page. The tester can resume from exactly where they left off — all previously recorded step results are preserved.

If a tester tries to execute a test case they are already mid-way through, Spira prompts them to either resume one of the existing pending runs or start a new one.

## Execution Flow

The standard test execution flow is:

1. **Select test cases or a test set** on the Test Cases or Test Sets list page, then click "Execute"
2. **Choose a release** (required if the product has releases) and optionally set custom properties (e.g. OS, browser)
3. **Work through test steps** — for each step, compare actual behaviour to the expected result and record a status:
   - Click **Pass** if the step behaves as expected
   - Click **Fail**, **Blocked**, or **Caution** and enter a description of the actual result if it does not
   - Use **Pass All** to pass all remaining steps in a test case at once
4. **Log incidents** (optional but common on failures) — fill in the incident form that appears below the step, or link to an existing incident
5. **Finish or Leave**:
   - Click **Finish** (orange stop button) to archive the test run as a permanent record
   - Click **Leave** (eject button) to save progress as a pending test run and return later

## Traceability: Test Cases → Requirements

Test cases can be linked to one or more requirements. This creates **requirements coverage**: when all test cases covering a requirement pass, the requirement is considered fully tested.

- The Requirements list shows a coverage mini-chart for each requirement (proportions of Passed / Failed / Blocked / Caution / Not Run)
- The Test Case details page has a "Requirements Coverage" tab to add or remove requirement links
- Adding a requirement link to a test case also adds any releases assigned to that requirement to the test case's release mapping

Individual **test steps** can also be linked to requirements (for industries requiring step-level traceability).

## Available MCP Tools

The server uses two unified product tools — there are no longer separate per-artifact tools.

| Tool                        | What it does                                                                  |
| --------------------------- | ----------------------------------------------------------------------------- |
| `product_search_artifacts`  | Search test cases, test sets, or test runs in a product                       |
| `product_get_artifact`      | Retrieve a single test case, test set, or test run by ID                      |
| `mywork_search_artifacts`   | List test cases or test sets assigned to the current user                     |

Both product tools accept `product_ids` (optional list; falls back to `SPIRA_PROJECT_ID`). Pass multiple IDs for cross-product fan-out.

### Response envelope

All search results come back in a consistent envelope:

```json
{
  "data": [...],
  "artifact_type": "test_case",
  "fields_returned": ["TestCaseId", "Name", "ExecutionStatusName"],
  "fields_available": ["Description", "TesterId", "..."],
  "pagination": {"starting_row": 1, "number_of_rows": 100, "total_returned": 30},
  "warnings": []
}
```

Use `fields` to request specific fields, or omit it to get the default summary fields. Call `get_artifact_schema(artifact_type="test_case")` (or `"test_set"` / `"test_run"`) to discover all available field names.

### Inline test steps

`product_get_artifact` supports an `include` parameter for test cases:

```
product_get_artifact(artifact_type="test_case", artifact_id=42, product_id=55, include=["test_steps"])
```

This returns the test case with its steps embedded inline — no separate call needed.

## Common Workflows

### Find all failed test runs for a release
```
product_search_artifacts(artifact_type="test_run", product_ids=[55], status="failed")
```
`status` is a case-insensitive substring filter. Add `release_id` if you want to scope to a specific release.

### Check test coverage for a product
```
product_search_artifacts(artifact_type="test_case", product_ids=[55])
```
Look at `ExecutionStatusName` on each test case to see which are Not Run, Passed, Failed, etc.

### Find test sets assigned to a specific release
```
product_search_artifacts(artifact_type="test_set", product_ids=[55], release_id=10)
```
`release_id` scopes the search to test sets assigned to that release or sprint.

### Get a test case with its steps
```
product_get_artifact(artifact_type="test_case", artifact_id=42, product_id=55, include=["test_steps"])
```

### List test cases assigned to the current user
```
mywork_search_artifacts(artifact_type=["test_case"])
```
Supports the same `status`, `priority`, `fields`, `limit`, and `offset` parameters.

### Search across multiple products
```
product_search_artifacts(artifact_type="test_run", product_ids=[55, 56], status="failed")
```
Returns a multi-product envelope with one entry per product.

### Resume a pending test run
Pending test runs cannot be resumed via the MCP API — the tester must log into the Spira web UI, go to "My Pending Test Runs" on their home page, and click "Resume".
