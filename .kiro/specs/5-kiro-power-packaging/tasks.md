# Implementation Tasks: kiro-power-packaging

## Task List

- [x] 1. Consolidate packaging configuration in `pyproject.toml`
  - [x] 1.1 Add `[project.scripts]` entry `mcp-server-spira = "mcp_server_spira.server:main"` to `pyproject.toml`
  - [x] 1.2 Add `authors = [{name = "Inflectra Corporation", email = "support@inflectra.com"}]` to `[project]` in `pyproject.toml`
  - [x] 1.3 Delete `setup.py` (entry point and all metadata now in `pyproject.toml`)
  - [x] 1.4 Delete `setup.cfg` (only contained `description-file`, fully redundant)
  - [x] 1.5 Update `MANIFEST.in` to `include POWER.md README.md LICENSE` (replacing `include CLAUDE.md`)

- [x] 2. Repository cleanup
  - [x] 2.1 Add `coverage.json` and `workspace.code-workspace` to `.gitignore`
  - [x] 2.2 Delete `main.py` (redundant with the `mcp-server-spira` console script entry point)
  - [x] 2.3 Delete `CLAUDE.md` (dev-only AI instructions, not needed in the published repo)
  - [x] 2.4 Delete `SPIRA_MCP_ENHANCEMENT_MASTER_PLAN.md` (dev-only planning doc)
  - [x] 2.5 Add a reference to `TESTING_GUIDE.md` in `README.md` under a "Contributing" or "Development" section

- [x] 3. Create `src/mcp_server_spira/config.py`
  - [x] 3.1 Implement `load_config()` — reads `SPIRA_PROJECT_ID` from env, parses to int, logs warning on invalid value, stores in module-level `_default_product_id`
  - [x] 3.2 Implement `get_default_product_id() -> int | None` — returns `_default_product_id`
  - [x] 3.3 Implement `resolve_product_id(explicit: int | None) -> int | None` — returns explicit if not None, else `_default_product_id`

- [x] 4. Create `src/mcp_server_spira/features/context.py`
  - [x] 4.1 Implement `load_active_product_context()` — async, calls `GET projects/{id}` and `POST projects/{id}/releases/search`, filters active releases, stores result in module-level `_active_product_context`; swallows exceptions with `logging.warning`
  - [x] 4.2 Implement `get_active_product_context() -> dict | None` — returns `_active_product_context`

- [x] 5. Update `src/mcp_server_spira/server.py`
  - [x] 5.1 Add `asynccontextmanager` lifespan that calls `load_config()` then `await load_active_product_context()`
  - [x] 5.2 Pass `lifespan=lifespan` to the `FastMCP(...)` constructor
  - [x] 5.3 Register `@mcp.resource("spira://active-product")` that returns `get_active_product_context()` as JSON, or `{"error": "No active product context available"}` when context is None
  - [x] 5.4 Add `import json` to server.py imports

- [x] 6. Update `product_*` tools to support optional `product_id`
  - [x] 6.1 Update all tools in `src/mcp_server_spira/features/productartifacts/tools/` — change `product_id: int` to `product_id: int | None = None`, call `resolve_product_id(product_id)` at the top, return structured error if result is None
  - [x] 6.2 Update all tools in `src/mcp_server_spira/features/automation/tools/` — same pattern as 6.1
  - [x] 6.3 Update all tools in `src/mcp_server_spira/features/specifications/tools/` — same pattern as 6.1

- [x] 7. Create `POWER.md`
  - [x] 7.1 Create `POWER.md` at the repo root with YAML frontmatter (`name`, `displayName`, `description`, `keywords` covering project management, test management, requirements, incidents, tasks, releases, sprints, defects)
  - [x] 7.2 Add onboarding section with a table of all four environment variables (`INFLECTRA_SPIRA_BASE_URL`, `INFLECTRA_SPIRA_USERNAME`, `INFLECTRA_SPIRA_API_KEY`, `SPIRA_PROJECT_ID`) including required/optional status and description
  - [x] 7.3 Add a note in the onboarding section explaining that when `SPIRA_PROJECT_ID` is set, product-specific tools default to that project and the server surfaces project context automatically
  - [x] 7.4 Add `# When to load steering files` section mapping the three scenarios to their steering files: test cases/test sets/test runs/execution → `spira-test-management.md`, requirements/user stories/coverage/task progress → `spira-requirements-traceability.md`, incidents/bugs/defects/triage → `spira-incident-workflow.md`

- [x] 8. Document `SPIRA_PROJECT_ID` in `README.md`
  - [x] 8.1 Add `SPIRA_PROJECT_ID` to the configuration/environment variables section of `README.md`, describing it as optional and explaining the default project ID behaviour

- [x] 9. Create GitHub Actions publish workflow
  - [x] 9.1 Create `.github/workflows/publish.yml` — triggers on `v*.*.*` tag push, uses `pypa/gh-action-pypi-publish@release/v1` with OIDC Trusted Publisher (no API token), builds with `python -m build`, targets Python 3.12

- [x] 10. Write tests for `config.py`
  - [x] 10.1 Write unit tests in `tests/test_config.py` covering: valid integer env var, non-integer env var, absent env var, `resolve_product_id` with explicit value, `resolve_product_id` with None and a default, `resolve_product_id` with None and no default
  - [x] 10.2 Write property-based tests in `tests/test_config_properties.py` using `hypothesis` for Properties 2, 3, and 4 (valid integer loading, non-integer rejection, resolve precedence); tag each test with `# Feature: kiro-power-packaging, Property N: ...`

- [x] 11. Write tests for `features/context.py`
  - [x] 11.1 Write unit tests in `tests/test_context.py` covering: no default product ID (no API call), API failure (no exception raised, context is None), successful load (context has all required keys), `active_product_resource()` with None context, `active_product_resource()` with populated context
  - [x] 11.2 Write property-based tests in `tests/test_context_properties.py` using `hypothesis` for Properties 5, 6, and 7 (endpoint calls, required fields, caching); tag each test with `# Feature: kiro-power-packaging, Property N: ...`

- [x] 12. Write packaging integrity tests
  - [x] 12.1 Write tests in `tests/test_packaging.py` covering: `pyproject.toml` has `[project.scripts]` with correct entry point, `POWER.md` exists at repo root, `POWER.md` frontmatter has `name`/`description`/`keywords`, `POWER.md` mentions all required env vars, `MANIFEST.in` includes `POWER.md`, `.gitignore` includes `coverage.json`

- [x] 13. Create end-user steering files for the power
  - [x] 13.1 Create `power-spira/steering/spira-test-management.md` using https://raw.githubusercontent.com/Inflectra/spira-documentation/main/docs/Spira-User-Manual/Test-Case-Management.md and https://raw.githubusercontent.com/Inflectra/spira-documentation/main/docs/Spira-User-Manual/Test-Execution.md as source material — cover test case structure (steps, parameters, linked test cases), test sets as collections assigned to a release, the full execution flow (select release → execute → pass/fail/block steps → log incidents), execution statuses (Passed, Failed, Blocked, Caution, Not Run, Not Applicable), test runs as immutable execution records, how to resume pending test runs, and traceability from test cases to requirements coverage
  - [x] 13.2 Create `power-spira/steering/spira-requirements-traceability.md` using https://raw.githubusercontent.com/Inflectra/spira-documentation/main/docs/Spira-User-Manual/Requirements-Management.md as source material — cover requirement hierarchy (parent summary requirements vs standard requirements), the status flow (Requested → Accepted → Planned → In Progress → Developed → Tested → Completed), the test coverage column (mini chart showing execution status proportions), the task progress column (On Schedule / Running Late / Starting Late / Not Started), creating test cases and test sets directly from a requirement, and associations between requirements and incidents, risks, and releases
  - [x] 13.3 Create `power-spira/steering/spira-incident-workflow.md` using https://raw.githubusercontent.com/Inflectra/spira-documentation/main/docs/Spira-User-Manual/Incident-Tracking.md as source material — cover incident types (Bug, Issue, Risk), status filtering (open vs closed based on admin-configured flags), effort tracking fields (Estimated, Actual, Remaining, Projected = Actual + Remaining, Percent Complete = (Est − Remaining) / Est × 100), associations between incidents and requirements and test runs, converting incidents to requirements via Tools > Convert Into Requirements, and the incident board (kanban view configurable by release/sprint, priority, severity, assignee)
