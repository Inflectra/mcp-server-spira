# Spira Requirements Traceability

This steering file provides context for working with Spira requirements, user stories, test coverage, and task progress. Load it when the user is asking about requirements, user stories, features, requirement status, test coverage, task progress, or traceability between requirements and other artifacts.

## Key Concepts

### Requirement Types

Requirements are identified by an `RQ:` token (e.g. RQ:12). They come in two flavors:

- **Standard requirements** — leaf-level requirements with no children. They can have a point estimate set directly, and their status can be changed manually (or automatically via workflow rules).
- **Parent requirements** — any requirement that has at least one child. Displayed in **bold** in the list. Their estimate and status are derived automatically from their children and are read-only.

When you indent a requirement under another, the parent becomes a summary (parent) requirement. When you outdent the last child, the parent reverts to a standard requirement.

Both types can be assigned to a release, have an owner, carry test coverage, and follow a workflow.

### Requirement Hierarchy

Requirements are organized in a tree structure similar to a Work Breakdown Structure (WBS). The hierarchy can be as deep as needed, but keeping it shallow (2–3 levels) improves performance and reporting.

Parent requirements roll up key metrics from their children:
- **Estimate points** — sum of all children's estimates
- **Status** — derived from children's statuses (see Status Flow below)
- **Test coverage** — sum of all test cases assigned to the parent itself plus all test cases assigned to any descendant

### Status Flow

Standard requirements move through a defined lifecycle. The typical progression is:

```
Requested → Accepted → Planned → In Progress → Developed → Tested → Completed
```

Additional statuses that may appear depending on workflow configuration:
- **Under Review** / **Ready for Review** — awaiting stakeholder sign-off
- **Rejected** — will not be implemented
- **Obsolete** — no longer relevant
- **Design in Process** / **Design Approval** / **Documented** — design-phase statuses
- **Ready for Test** / **Released** — post-development statuses

#### Automatic Status Transitions

Spira can update requirement status automatically based on task activity (configurable per product):

- Assigning a release/sprint to a requirement → status moves to **Planned**
- At least one associated task moves from "Not Started" to "In Progress" → requirement moves to **In Progress**
- All associated tasks reach "Completed" → requirement moves to **Completed**

#### Parent Status Derivation

Parent requirement status is calculated from its children:

| Children's statuses                                                                                                                                                     | Parent status                                                                                            |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Any child is "Under Review", "Accepted", "Planned", or "In Progress"                                                                                                    | Matches the rightmost (most advanced) of those statuses                                                  |
| Some (but not all) children are "Developed", "Tested", or "Completed"                                                                                                   | **In Progress**                                                                                          |
| All children are a mix of "Developed", "Tested", or "Completed"                                                                                                         | The earliest of those statuses (e.g. if children are "Developed" and "Completed", parent is "Developed") |
| All children share the same status from: "Rejected", "Obsolete", "Ready for Review", "Ready for Test", "Released", "Design in Process", "Design Approval", "Documented" | That same status                                                                                         |

## Requirements List Columns

### Test Coverage Column

The test coverage column shows a **mini bar chart** for each requirement. Each segment of the bar represents the proportion of test cases in a given execution status.

- The chart is calculated from the current execution status of every test case mapped to that requirement (including test cases mapped to any child requirements — coverage rolls up)
- If a requirement has no test cases mapped, the column is empty
- Hovering over the mini chart shows a tooltip with exact counts per status

**Example:** A requirement has 3 test cases: 2 Passed, 1 Not Run → the bar shows a green segment (2/3) and a gray segment (1/3).

**Execution status colors in the mini chart:**

| Status  | Color  |
| ------- | ------ |
| Passed  | Green  |
| Failed  | Red    |
| Blocked | Orange |
| Caution | Yellow |
| Not Run | Gray   |

Coverage rolls up through the hierarchy: a parent requirement's mini chart reflects the combined test cases of all its descendants plus its own directly-mapped test cases.

### Task Progress Column

Requirements with at least one active task show a **task progress mini chart**. The chart has four segments:

| Segment       | Color  | Meaning                                                                                           |
| ------------- | ------ | ------------------------------------------------------------------------------------------------- |
| On Schedule   | Green  | Task has work in progress and is not overdue (end date is not in the past)                        |
| Running Late  | Red    | Task is overdue (end date in the past), has some work done, but is not complete                   |
| Starting Late | Yellow | Task has no work done yet but its start date has already passed                                   |
| Not Started   | Gray   | Task has no work done and has not yet started (start date in the future, or status is "Deferred") |

Inactive tasks (status: "Rejected", "Obsolete", or "Duplicate") are excluded from the chart entirely.

The chart segments are proportional: a task that is 40% complete contributes 0.4 to its category (e.g. "Running Late") and 0.6 to "Not Started".

Hovering over the mini chart shows a tooltip with exact counts per category.

### Task Effort Columns

Each effort column sums the effort values from all tasks associated with the requirement (and rolls up to parent requirements):

| Column           | Calculation                                              |
| ---------------- | -------------------------------------------------------- |
| Task Effort      | Sum of all tasks' estimated efforts                      |
| Actual Effort    | Sum of all tasks' actual efforts                         |
| Remaining Effort | Sum of all tasks' remaining efforts                      |
| Projected Effort | Sum of all tasks' projected efforts (Actual + Remaining) |

## Creating Test Cases and Test Sets from Requirements

### Create Test Cases from Requirements

From the requirements list, select one or more requirements and choose **Tools > Create Test Cases**. Spira creates a new test case for each selected requirement:

- The test case name matches the requirement name
- If the requirement has **use case steps** (scenario steps defined on a "Use Case" type requirement), each step becomes a test step in the new test case
- The new test case is automatically linked to the requirement, contributing to its test coverage

This is the fastest way to bootstrap test coverage for a new set of requirements.

### Create a Test Set from Requirements

From the requirements list, select one or more requirements and choose **Tools > Create Test Set**. Spira creates a single new test set containing all test cases already mapped to the selected requirements.

This is useful when you want to run a focused regression suite for a specific feature area.

### Create a Single Test Case from a Requirement Detail Page

On the requirement's detail page, go to the **Test Coverage** tab and click **"Create Test Case from This Requirement"**. This creates one new test case linked directly to the requirement — useful for quickly generating an initial covering test to flesh out later.

## Associations

From the requirement detail page, the **Associations** tab links a requirement to:

| Artifact         | Notes                                                                                                                                                                      |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Releases**     | Link the requirement to the release it was first delivered in, plus any other relevant releases                                                                            |
| **Requirements** | Link related requirements to each other (e.g. dependencies, related features)                                                                                              |
| **Incidents**    | Link bugs or issues that affect this requirement. Incidents can also be linked automatically when a tester logs an incident during a test run that covers this requirement |
| **Risks**        | Link risks that threaten delivery of this requirement                                                                                                                      |

Incidents linked via a test run execution appear in the Associations tab with a locked checkbox — these links are not editable because they were created automatically by the test execution process.

## Requirement Detail Page Tabs

| Tab           | Contents                                                                                                       |
| ------------- | -------------------------------------------------------------------------------------------------------------- |
| Overview      | Standard fields (status, type, importance, owner, release, estimate), description, and use case scenario steps |
| Test Coverage | Test cases mapped to this requirement; add/remove test cases; create a new test case directly                  |
| Tasks         | Tasks that break down the work for this requirement; create, remove, or edit tasks inline                      |
| Attachments   | Files and URLs attached to the requirement                                                                     |
| History       | Audit log of all changes                                                                                       |
| Associations  | Links to releases, other requirements, incidents, and risks                                                    |

## Available MCP Tools

| Tool                         | What it does                               |
| ---------------------------- | ------------------------------------------ |
| `product_get_requirements`   | List requirements in a product (paginated) |
| `product_get_requirement`    | Get a single requirement by ID             |
| `product_create_requirement` | Create a new requirement                   |
| `product_update_requirement` | Update an existing requirement             |

All tools accept `product_id` (optional if `SPIRA_PROJECT_ID` is set) and standard pagination parameters where applicable.

## Common Workflows

### Check overall requirements status for a product
```
product_get_requirements(product_id=55)
```
Look at `StatusName` on each requirement. Filter for `"Requested"` or `"Accepted"` to find requirements not yet planned.

### Find requirements with failing test coverage
```
product_get_requirements(product_id=55)
```
Examine the `CoverageFailed` and `CoverageBlocked` counts on each requirement. Requirements where these are non-zero have test cases that are failing or blocked.

### Find requirements not yet assigned to a release
```
product_get_requirements(product_id=55)
```
Filter the returned JSON for requirements where `ReleaseId` is `null` — these have not been scheduled into a release yet.

### Get details of a specific requirement
```
product_get_requirement(product_id=55, requirement_id=12)
```
Returns the full requirement object including all fields, status, owner, release assignment, and estimate.

### Create a new requirement
```
product_create_requirement(product_id=55, name="User can reset password", status_id=1, importance_id=2)
```
`status_id=1` corresponds to "Requested". Use `product_get_requirements` to discover valid status and importance IDs for the product.

### Update a requirement's status
```
product_update_requirement(product_id=55, requirement_id=12, status_id=4)
```
`status_id=4` typically corresponds to "In Progress" — verify the exact IDs by checking the requirement's current data.
