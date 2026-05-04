# Spira Specification Workflow

This steering file guides building specification documents (requirements.md, design.md, tasks.md, test-cases.md) from Spira data using `product_search_artifacts` and `product_get_artifact` with the `include` parameter. Load it when the user asks to generate a spec, build a specification, or pull structured project data from Spira into markdown documents.

## Key Concepts

### The include Parameter

Both `product_search_artifacts` and `product_get_artifact` accept an optional `include` parameter that fetches nested/related data inline with parent artifacts. This eliminates the need for separate API calls to get sub-artifact details.

Available include types by parent artifact:

| Parent artifact | include value  | What it fetches                        |
| --------------- | -------------- | -------------------------------------- |
| requirement     | `"steps"`      | Requirement scenario steps (use cases) |
| test_case       | `"test_steps"` | Test case steps with expected results  |
| risk            | `"mitigations"`| Risk mitigation entries                |

Pass include values as a list: `include=["steps"]` or `include=["test_steps"]`.

### The requirement_id Filter

`product_search_artifacts` accepts an optional `requirement_id` parameter when searching for tasks. This filters tasks client-side to return only tasks belonging to a specific requirement. Only supported for `artifact_type="task"`.

### Result Capping with include

When `include` is active on `product_search_artifacts`, results are capped at 50 artifacts to prevent excessive API calls for nested data. If you need more than 50 artifacts with nested data, paginate with multiple calls.

### Multi-Product Limitation

The `include` parameter is not supported when searching across multiple products (`product_ids` with more than one ID). Use a single product at a time when fetching nested data.

## Building a Requirements Specification

### Step 1: Fetch requirements with scenario steps

```
product_search_artifacts(
    artifact_type="requirement",
    include=["steps"],
    fields=["RequirementId", "Name", "Description", "StatusName",
            "ImportanceName", "OwnerName", "ReleaseVersionNumber"]
)
```

This returns each requirement with its scenario steps (acceptance criteria / use case steps) embedded under the `"steps"` key.

### Step 2: Format into requirements.md

For each requirement in the response:
1. Use `Name` and `Description` as the requirement heading and body
2. Use the `steps` array to build the acceptance criteria section — each step has `Description` and `Position`
3. Group by release using `ReleaseVersionNumber` if building a release-scoped spec
4. Include `StatusName` and `ImportanceName` as metadata

If a requirement has no steps, it has no scenario-level acceptance criteria defined in Spira.

### Step 3: Get details for specific requirements (optional)

For requirements that need full detail beyond what the search returned:

```
product_get_artifact(
    artifact_type="requirement",
    artifact_id=12,
    include=["steps"]
)
```

## Building a Design Specification

### Step 1: Fetch risks with mitigations

```
product_search_artifacts(
    artifact_type="risk",
    include=["mitigations"],
    fields=["RiskId", "Name", "Description", "RiskStatusName",
            "RiskProbabilityName", "OwnerName"]
)
```

Each risk is returned with its mitigation entries under the `"mitigations"` key.

### Step 2: Format into design.md

For each risk:
1. Use `Name` and `Description` as the risk heading and body
2. Use the `mitigations` array to list mitigation strategies — each has `Description`, `IsActive`, and `Position`
3. Include `RiskProbabilityName` and `RiskStatusName` as metadata

## Building a Tasks Specification

### Step 1: Fetch all requirements (for grouping)

```
product_search_artifacts(
    artifact_type="requirement",
    fields=["RequirementId", "Name", "StatusName"]
)
```

### Step 2: Fetch tasks for each requirement

For each requirement, fetch its associated tasks using the `requirement_id` filter:

```
product_search_artifacts(
    artifact_type="task",
    requirement_id=12,
    fields=["TaskId", "Name", "TaskStatusName", "TaskPriorityName",
            "OwnerName", "CompletionPercent"]
)
```

This returns only tasks belonging to requirement RQ:12.

### Step 3: Format into tasks.md

Group tasks under their parent requirement:
1. List each requirement as a section heading
2. Under each requirement, list its tasks with status, priority, owner, and completion percentage
3. Tasks with no `requirement_id` match are unassigned — fetch them separately with a broad task search

### Alternative: Fetch all tasks at once

If the product has fewer than 50 tasks total, fetch them all and group client-side:

```
product_search_artifacts(
    artifact_type="task",
    fields=["TaskId", "Name", "TaskStatusName", "TaskPriorityName",
            "RequirementId", "OwnerName", "CompletionPercent"]
)
```

Then group by `RequirementId` in the output.

## Building a Test Cases Specification

### Step 1: Fetch test cases with steps

```
product_search_artifacts(
    artifact_type="test_case",
    include=["test_steps"],
    fields=["TestCaseId", "Name", "TestCaseStatusName",
            "TestCasePriorityName", "OwnerName"]
)
```

Each test case is returned with its test steps under the `"test_steps"` key.

### Step 2: Format into test-cases.md

For each test case:
1. Use `Name` as the test case heading
2. Use the `test_steps` array to build the steps table — each step has `Description`, `ExpectedResult`, `SampleData`, and `Position`
3. Order steps by `Position`
4. Include `TestCaseStatusName` and `TestCasePriorityName` as metadata

### Step 3: Get details for specific test cases (optional)

```
product_get_artifact(
    artifact_type="test_case",
    artifact_id=42,
    include=["test_steps"]
)
```

## Release-Scoped Specifications

To build a spec for a specific release, add `release_id` to all search calls:

```
product_search_artifacts(
    artifact_type="requirement",
    release_id=12,
    include=["steps"],
    fields=["RequirementId", "Name", "Description", "StatusName",
            "ImportanceName", "OwnerName"]
)
```

Repeat for risks, tasks, and test cases with the same `release_id` to scope the entire specification to that release.

## Response Structure

When `include` is used, the response contains:
- `data`: array of artifacts, each with nested data under the include type key (e.g. `"steps"`, `"test_steps"`, `"mitigations"`)
- `includes_fetched`: list of include types that were processed (on search only)
- `warnings`: any issues encountered during enrichment

When an artifact has no nested data (e.g. a requirement with no steps), the include key contains an empty array.
