---
name: "spira"
displayName: "Inflectra SpiraPlan / SpiraTeam"
description: "Connect Kiro to Inflectra Spira for AI-assisted project management, test management, requirements management, and incident tracking."
keywords:
  - spira
  - spiratest
  - spirateam
  - spiraplan
  - requirements
  - test cases
  - testcases
  - test management
  - testmanagement
  - incidents
  - tasks
  - releases
  - sprints
  - project management
  - projectmanagement
  - inflectra
  - defects
  - bugs
---

This power connects Kiro to your Inflectra Spira instance, giving it read and write access across your entire project portfolio. Tool categories include personal work items (my tasks, my requirements, my incidents, my test cases, my test sets), product artifacts (requirements, incidents, tasks, releases, risks, test cases, test sets, test runs, automation hosts), program-level artifacts (capabilities, milestones), specifications, and workspace/template configuration. Use it to query, create, and update Spira data directly from your IDE without leaving your flow.

# Onboarding

## Configure environment variables

Set the following in your MCP client configuration or `.env` file:

| Variable                 | Required | Description                                                                                          |
| ------------------------ | -------- | ---------------------------------------------------------------------------------------------------- |
| INFLECTRA_SPIRA_BASE_URL | Yes      | Base URL of your Spira instance (e.g. https://mycompany.spiraservice.net)                            |
| INFLECTRA_SPIRA_USERNAME | Yes      | Your Spira login username                                                                            |
| INFLECTRA_SPIRA_API_KEY  | Yes      | Your Spira API Key (RSS Token). Find it under your user avatar → Profile → API Key / RSS Token.      |
| SPIRA_PROJECT_ID         | No       | Numeric ID of your default project. When set, product-specific tools use this project automatically. |

> **Default project:** When `SPIRA_PROJECT_ID` is set, the server fetches that project's name, description, and active releases at startup and surfaces them automatically. All product-specific tools default to that project, so you don't need to pass `product_id` on every call.

# When to load steering files

Load the relevant steering file when working in one of these areas to give Kiro deeper context about Spira's workflows:

- Working with test cases, test sets, test runs, or test execution → `spira-test-management.md`
- Working with requirements, user stories, coverage, or task progress → `spira-requirements-traceability.md`
- Working with incidents, bugs, defects, or issue triage → `spira-incident-workflow.md`
