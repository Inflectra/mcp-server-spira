# Spira Incident Workflow

This steering file provides context for working with Spira incidents, bugs, defects, and issue triage. Load it when the user is asking about incidents, bugs, defects, issues, risks, triage, effort tracking, or the incident board.

## Key Concepts

### Incident Types

Incidents are identified by an `IN:` token (e.g. IN:42). The type of an incident is admin-configured per product template. Common built-in types include:

- **Bug** — a defect found during testing or production use
- **Issue** — a general problem or concern (not necessarily a code defect)
- **Enhancement** — a potential future improvement of the product

Admins can define additional custom types. A special category called **Issues** is a subset of incidents: admins mark certain incident types as "also an issue", and filtering by "Issues" shows all incidents of those types together.

### Incident Statuses

Statuses are fully admin-configurable per product template. Each status is flagged as either **open** or **closed** by the admin. This flag drives the sidebar charts and the special filter options:

- **All Open** — shows all incidents whose current status is flagged as open
- **All Closed** — shows all incidents whose current status is flagged as closed
- **Specific status** — filter to a single named status

The sidebar on the incident list shows two donut charts: open vs closed ratio, and priority mix of open incidents.

### Effort Tracking Fields

Each incident has four editable effort fields (in hours or minutes, depending on product configuration):

| Field            | Description                                         |
| ---------------- | --------------------------------------------------- |
| Estimated Effort | The original estimate of how long the fix will take |
| Actual Effort    | Time already spent on the incident                  |
| Remaining Effort | Time still needed to complete the fix               |

Two additional fields are **calculated automatically** and are read-only:

| Calculated Field | Formula                                                                                                                        |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Projected Effort | `Actual Effort + Remaining Effort` (if Actual Effort is blank, falls back to Estimated Effort)                                 |
| Percent Complete | `(Estimated Effort − Remaining Effort) / Estimated Effort × 100` — e.g. if Est = 7h and Remaining = 1h, Percent Complete ≈ 85% |

A **progress indicator** bar is also shown:

| Bar color    | Condition                                     |
| ------------ | --------------------------------------------- |
| Fully gray   | 0% complete, no start date or start in future |
| Fully yellow | 0% complete, start date in the past           |
| Partly green | Between 0% and 100% complete                  |
| Fully green  | 100% complete                                 |

Unlike tasks, the progress bar never turns red (incidents have no hard due date).

### Associations

From the incident detail page, the **Associations** tab links an incident to other artifacts:

| Artifact         | Notes                                                                                                                                                                               |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Requirements** | Link the incident to the requirement(s) it affects. Incidents linked automatically during test execution appear with a locked checkbox — these links are not editable.              |
| **Test Cases**   | Link the incident to the test case(s) that uncovered it. Auto-linked when a tester logs an incident during a test run; those links are also locked.                                 |
| **Test Runs**    | When a tester logs an incident during test execution, the incident is automatically associated with the test run. This provides full traceability from defect back to the test run. |
| **Releases**     | Link the incident to the release it was detected in or is planned to be fixed in.                                                                                                   |

Associations created automatically by the test execution process are read-only. Manually added associations can be removed.

## Converting Incidents to Requirements

Sometimes an enhancement or change request logged as an incident needs to become a formal requirement (e.g. for sprint planning, so test cases and tasks can be created from it).

### From the Incident List (bulk)

1. Select the checkboxes of one or more incidents
2. Click **Tools > Convert Into Requirements**

Spira creates one new requirement per selected incident and automatically creates an association between each new requirement and its source incident.

### From the Incident Detail Page (single)

1. Go to the **Associations** tab
2. Click **Add**
3. In the panel that appears, click **Create Requirement from this Incident**

#### What gets copied to the new requirement

| Incident field                                   | Requirement field                                                               |
| ------------------------------------------------ | ------------------------------------------------------------------------------- |
| Name                                             | Name                                                                            |
| Description                                      | Description                                                                     |
| Owner                                            | Owner                                                                           |
| Detected By                                      | Author                                                                          |
| Component (single only)                          | Component                                                                       |
| Planned Release                                  | Release                                                                         |
| Priority                                         | Importance (matched by name)                                                    |
| Estimated Effort                                 | Estimate (hours converted to points)                                            |
| Custom list/multilist fields with matching names | Corresponding custom fields                                                     |
| Comments                                         | Comments (original author preserved; creation date is the conversion date)      |
| Attachments                                      | Linked (not copied — same attachment objects are linked to the new requirement) |

Note: the conversion does **not** enforce the requirement workflow, so required fields on the requirement may be left blank.

## Incident Board (Kanban View)

The incident board is a kanban-style view available in SpiraTeam and SpiraPlan. It visualizes incidents across a product in a configurable grid of columns and rows.

### Accessing the Board

Navigate to **Tracking > Incidents** and switch to the Board view.

### Release Selector

The board has a **release dropdown** that scopes which incidents are shown:

| Selection          | What is shown                                                               |
| ------------------ | --------------------------------------------------------------------------- |
| All Releases       | Incidents planned for any open release (planned, in progress, or completed) |
| A specific release | Incidents planned for that release and its child sprints                    |
| A specific sprint  | Incidents planned for that sprint only                                      |

### Board Configuration (Columns and Rows)

Both columns and rows can be independently set to any of:

- **Priority** — group by incident priority
- **Release** — group by release/sprint assignment
- **Status** — group by incident status
- **Type** — group by incident type (Bug, Issue, Risk, etc.)
- **Severity** — group by incident severity
- **Person** — group by assigned owner (supports Team grouping when rows = Person)

When grouping by Priority, Release, Severity, or Person, an "Unassigned" section is shown for incidents with no value in that field.

### Card Options

Each incident card on the board can optionally display:

- Incident ID and name
- Type, priority, severity
- Assigned owner
- **Progress** — a mini histogram of percent complete (hover for tooltip with exact values)

### Common Board Workflows

- **Triage by priority**: set columns = Priority, rows = Status to see how many open incidents exist at each priority level
- **Sprint planning**: set release = current sprint, columns = Status to track incident resolution progress within the sprint
- **Team workload**: set rows = Person, columns = Status to see each team member's open incident count
- **Severity review**: set columns = Severity to identify high-severity incidents that need immediate attention

## Incident List Features

### Inline Editing

Click **Edit** on any row (or double-click a cell) to edit that incident inline. Multiple rows can be edited simultaneously — click **Edit** on each row, make changes, then click the single **Save** button. Use the **fill** icon to propagate a value to all selected rows in the same column (e.g. bulk-change status from "Resolved" to "Closed").

### Cloning

Select one or more incidents and click **Clone** (under Edit menu or from the New dropdown on the detail page). The clone gets the name prefixed with "Copy of...". Standard fields, custom fields, description, comments, attachments, and associations are all cloned. Followers and history are not cloned.

### Filtering

Use the standard filter bar to filter by any field. Special filter options for incidents:

- **Incident Type: Issues** — shows all incidents whose type is flagged as an "issue" type by the admin
- **Incident Status: All Open** — shows all incidents in any status flagged as open
- **Incident Status: All Closed** — shows all incidents in any status flagged as closed

## Available MCP Tools

The server uses two unified product tools — there are no longer separate per-artifact tools.

| Tool                        | What it does                                                    |
| --------------------------- | --------------------------------------------------------------- |
| `product_search_artifacts`  | Search incidents (and any other artifact type) in a product     |
| `product_get_artifact`      | Retrieve a single incident by ID                                |
| `mywork_search_artifacts`   | List incidents assigned to the current user across all products |

Both product tools accept `product_ids` (optional list; falls back to `SPIRA_PROJECT_ID`). Pass multiple IDs for cross-product fan-out.

### Response envelope

All search results come back in a consistent envelope:

```json
{
  "data": [...],
  "artifact_type": "incident",
  "fields_returned": ["IncidentId", "Name", "IncidentStatusName"],
  "fields_available": ["Description", "ActualEffort", "..."],
  "pagination": {"starting_row": 1, "number_of_rows": 100, "total_returned": 25},
  "warnings": []
}
```

Use `fields` to request specific fields, or omit it to get the default summary fields. Call `get_artifact_schema(artifact_type="incident")` to discover all available field names.

## Common Workflows

### List all incidents for a product
```
product_search_artifacts(artifact_type="incident", product_ids=[55])
```

### List open incidents only
```
product_search_artifacts(artifact_type="incident", product_ids=[55], status="open")
```
`status` is a case-insensitive substring filter on the status name — `"open"` matches any status containing that word.

### Find all bugs by priority
```
product_search_artifacts(artifact_type="incident", product_ids=[55], priority="high")
```

### Get details of a specific incident
```
product_get_artifact(artifact_type="incident", artifact_id=42, product_id=55)
```
Returns the full incident object including all fields, effort values, status, type, priority, severity, and associations.

### List incidents assigned to the current user
```
mywork_search_artifacts(artifact_type=["incident"])
```
Returns incidents across all products assigned to the authenticated user. Supports the same `status`, `priority`, `fields`, `limit`, and `offset` parameters.

### Search across multiple products
```
product_search_artifacts(artifact_type="incident", product_ids=[55, 56, 57], status="open")
```
Returns a multi-product envelope with one entry per product. Failed products get an error entry rather than aborting the whole call.

### Find incidents linked to a specific requirement
```
product_search_artifacts(artifact_type="incident", product_ids=[55])
```
Check the `RequirementId` associations on returned incidents, or retrieve the requirement directly with `product_get_artifact(artifact_type="requirement", artifact_id=12)` and examine its incident count fields.
