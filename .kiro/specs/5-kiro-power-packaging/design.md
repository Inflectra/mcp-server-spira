# Design Document: kiro-power-packaging

## Overview

This feature packages the Spira MCP Server as a Kiro Power and publishes it to PyPI. The work spans six areas:

1. **PyPI packaging consolidation** — make `pyproject.toml` the single source of truth, remove `setup.py`/`setup.cfg`, add the console script entry point, and wire up a GitHub Actions CI/CD pipeline for automated publishing.
2. **POWER.md** — create the Kiro Power descriptor file at the repo root with YAML frontmatter, onboarding instructions, and steering mappings.
3. **Steering assessment** — evaluate existing `.kiro/steering/` files for end-user relevance and document the outcome.
4. **`config.py` module** — read `SPIRA_PROJECT_ID` at startup and expose `resolve_product_id()` so all `product_*` tools can fall back to the default.
5. **Proactive product context** — use FastMCP's `lifespan` to fetch product details and active releases at startup, then expose them as the `spira://active-product` MCP Resource.
6. **Repository cleanup** — audit and remove/gitignore dev-only artefacts, update `MANIFEST.in`, and add missing `.gitignore` entries.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  Repository Root                                                  │
│                                                                   │
│  POWER.md          ← Kiro Power descriptor (new)                 │
│  pyproject.toml    ← Single packaging source of truth (updated)  │
│  MANIFEST.in       ← Updated to include POWER.md                 │
│  .github/workflows/publish.yml  ← PyPI CI/CD (new)               │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  src/mcp_server_spira/                                            │
│                                                                   │
│  server.py         ← Updated: lifespan, resource registration    │
│  config.py         ← New: SPIRA_PROJECT_ID loading               │
│  features/                                                        │
│    context.py      ← New: active product context loading         │
│    common/         ← Existing validation/error utilities         │
│    product*/       ← Updated: product_id becomes optional        │
└──────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    ▼                    ▼
             Spira REST API         MCP Client
             (HTTP/JSON)            (Kiro / Claude)
                                         │
                                         └── reads spira://active-product
```

### Startup sequence

```
server starts
    │
    ├── load_config()              reads SPIRA_PROJECT_ID → int | None
    │
    └── load_active_product_context()
            │
            ├── if no default product_id → skip (no API call)
            │
            └── if product_id set:
                    ├── GET /projects/{id}          → name, description
                    ├── POST /projects/{id}/releases/search → active releases
                    └── store in module-level _active_product_context
```

---

## Components and Interfaces

### 1. `src/mcp_server_spira/config.py` (new)

Responsible for reading and exposing the `SPIRA_PROJECT_ID` environment variable.

```python
import os, logging

_default_product_id: int | None = None

def load_config() -> None:
    """Called once at server startup. Reads SPIRA_PROJECT_ID."""
    global _default_product_id
    raw = os.environ.get("SPIRA_PROJECT_ID")
    if raw is not None:
        try:
            _default_product_id = int(raw)
        except ValueError:
            logging.warning(
                "SPIRA_PROJECT_ID='%s' is not a valid integer, ignoring", raw
            )

def get_default_product_id() -> int | None:
    return _default_product_id

def resolve_product_id(explicit: int | None) -> int | None:
    """Returns explicit if provided, otherwise the default. May return None."""
    return explicit if explicit is not None else _default_product_id
```

**Callers:** `server.py` (calls `load_config()` in lifespan), all `product_*` tools (call `resolve_product_id()`).

### 2. `src/mcp_server_spira/features/context.py` (new)

Responsible for fetching and caching the active product context at startup.

```python
import logging, json
from mcp_server_spira.utils.spira_client import get_client
from mcp_server_spira.config import get_default_product_id

_active_product_context: dict | None = None

async def load_active_product_context() -> None:
    """Fetches product details and active releases. Called once in lifespan."""
    global _active_product_context
    product_id = get_default_product_id()
    if product_id is None:
        return
    try:
        client = get_client()
        product = client.make_spira_api_get_request(f"projects/{product_id}")
        releases = client.make_spira_api_post_request(
            f"projects/{product_id}/releases/search", {}
        )
        active_releases = [
            {
                "ReleaseId": r["ReleaseId"],
                "Name": r["Name"],
                "VersionNumber": r["VersionNumber"],
            }
            for r in releases
            if r.get("Active", True)
        ]
        _active_product_context = {
            "product_id": product_id,
            "name": product.get("Name"),
            "description": product.get("Description"),
            "active_releases": active_releases,
        }
    except Exception as e:
        logging.warning("Failed to load active product context: %s", e)

def get_active_product_context() -> dict | None:
    return _active_product_context
```

### 3. `src/mcp_server_spira/server.py` (updated)

Adds the `lifespan` context manager and the `spira://active-product` resource.

```python
from contextlib import asynccontextmanager
from mcp_server_spira.config import load_config
from mcp_server_spira.features.context import (
    load_active_product_context,
    get_active_product_context,
)

@asynccontextmanager
async def lifespan(server):
    load_config()
    await load_active_product_context()
    yield
    # shutdown: nothing needed

mcp = FastMCP("inflectra-spira", lifespan=lifespan, instructions=...)

@mcp.resource("spira://active-product")
def active_product_resource() -> str:
    ctx = get_active_product_context()
    if ctx is None:
        return json.dumps({"error": "No active product context available"})
    return json.dumps(ctx, indent=2)
```

The resource is always registered but returns a structured error when no context was loaded. This avoids the complexity of conditional resource registration.

### 4. `product_*` tool signature change

All tools that currently require `product_id: int` are updated to `product_id: int | None = None`. At the top of each tool:

```python
from mcp_server_spira.config import resolve_product_id

resolved = resolve_product_id(product_id)
if resolved is None:
    return format_error_response(
        error="product_id is required",
        error_code=ErrorCodes.INVALID_PARAMETER,
        details={"parameter": "product_id"},
        suggestion="Pass product_id explicitly or set SPIRA_PROJECT_ID in your environment",
    )
```

Affected feature modules: `productartifacts`, `automation`, `specifications`.

### 5. `pyproject.toml` additions

```toml
[project]
authors = [{name = "Inflectra Corporation", email = "support@inflectra.com"}]

[project.scripts]
mcp-server-spira = "mcp_server_spira.server:main"
```

The `[build-system]` block already exists. No other changes to the build config are needed.

### 6. `MANIFEST.in` replacement

```
include POWER.md README.md LICENSE
```

Replaces the current `include CLAUDE.md` line.

### 7. `.github/workflows/publish.yml` (new)

GitHub Actions workflow using PyPI Trusted Publisher (OIDC — no API tokens stored in secrets):

```yaml
name: Publish to PyPI
on:
  push:
    tags: ["v*.*.*"]
jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12"}
      - run: pip install build
      - run: python -m build
      - uses: pypa/gh-action-pypi-publish@release/v1
```

The `environment: pypi` maps to a GitHub Environment configured with the PyPI Trusted Publisher. No `PYPI_API_TOKEN` secret is needed.

---

## Data Models

### Active Product Context (`dict`)

```python
{
    "product_id": int,           # e.g. 55
    "name": str | None,          # e.g. "My Project"
    "description": str | None,   # e.g. "Main development project"
    "active_releases": [
        {
            "ReleaseId": int,        # e.g. 12
            "Name": str,             # e.g. "Sprint 3"
            "VersionNumber": str,    # e.g. "1.0.3"
        },
        ...
    ]
}
```

This dict is stored in `features/context._active_product_context` and returned verbatim by the `spira://active-product` resource as JSON.

### Config State

```python
# config._default_product_id: int | None
# None  → SPIRA_PROJECT_ID not set or invalid
# int   → parsed value of SPIRA_PROJECT_ID
```

---

## Steering Assessment

### Existing files in `.kiro/steering/`

| File                         | Content                                                                 | End-user relevant?                                        | Recommendation                                                |
| ---------------------------- | ----------------------------------------------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------- |
| `spira-mcp-overview.md`      | Dev guide: architecture, design principles, tool patterns, dev phases   | No — describes how to build the server, not how to use it | Exclude from power steering mappings; set `inclusion: manual` |
| `spira-mcp-phase1-guide.md`  | Dev guide: Phase 1 implementation tasks, code patterns for contributors | No — contributor-only                                     | Already `inclusion: manual`; no change needed                 |
| `spira-mcp-tool-patterns.md` | Dev guide: copy-paste patterns for writing new tools                    | No — contributor-only                                     | Already `inclusion: manual`; no change needed                 |

**Conclusion:** None of the existing steering files are appropriate for end users. Three new end-user-focused steering files will be created in `power-spira/steering/` to guide the AI through Spira's key workflows. These are distinct from the dev-only files in `.kiro/steering/` and will be shipped as part of the published power.

### New end-user steering files

| File                                  | Trigger scenario                                                                 | Content summary                                                                                      |
| ------------------------------------- | -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `spira-test-management.md`            | Working with test cases, test sets, test runs, or test execution                 | Test case structure, test sets as collections, execution flow, statuses, traceability to requirements |
| `spira-requirements-traceability.md`  | Working with requirements, user stories, coverage, or task progress              | Requirement hierarchy, status flow, test coverage column, task progress, associations                 |
| `spira-incident-workflow.md`          | Working with incidents, bugs, defects, or issue triage                           | Incident types, status filtering, effort tracking, associations, incident board, converting to requirements |

---

## POWER.md Structure

```markdown
---
name: "spira"
displayName: "Inflectra SpiraPlan / SpiraTeam"
description: "Connect Kiro to Inflectra Spira for AI-assisted project management, test management, requirements management, and incident tracking."
keywords:
  - spira
  - spirateam
  - spiraplan
  - requirements
  - test cases
  - test management
  - incidents
  - tasks
  - releases
  - sprints
  - project management
  - inflectra
  - defects
  - bugs
---

# Onboarding

## Step 1: Configure environment variables

Set the following in your MCP client configuration or `.env` file:

| Variable                 | Required | Description                                                                                          |
| ------------------------ | -------- | ---------------------------------------------------------------------------------------------------- |
| INFLECTRA_SPIRA_BASE_URL | Yes      | Base URL of your Spira instance (e.g. https://mycompany.spiraservice.net)                            |
| INFLECTRA_SPIRA_USERNAME | Yes      | Your Spira login username                                                                            |
| INFLECTRA_SPIRA_API_KEY  | Yes      | Your Spira API Key (RSS Token) from your profile page                                                |
| SPIRA_PROJECT_ID         | No       | Numeric ID of your default project. When set, product-specific tools use this project automatically. |

## Step 2: (Optional) Set a default project

If you work primarily in one Spira project, set `SPIRA_PROJECT_ID` to its numeric ID.
The server will surface that project's details and active releases automatically on startup,
and all product-specific tools will default to that project — no need to pass `product_id` on every call.

# When to load steering files

- Working with test cases, test sets, test runs, or test execution → `spira-test-management.md`
- Working with requirements, user stories, coverage, or task progress → `spira-requirements-traceability.md`
- Working with incidents, bugs, defects, or issue triage → `spira-incident-workflow.md`
```

---

## Repository File Audit

| File / Dir                             | Category                                          | Action                                                                                                               |
| -------------------------------------- | ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `pyproject.toml`                       | Required — packaging config                       | Keep; add `[project.scripts]` and `authors`                                                                          |
| `README.md`                            | Required — published with package                 | Keep; add `SPIRA_PROJECT_ID` docs                                                                                    |
| `LICENSE`                              | Required — published with package                 | Keep                                                                                                                 |
| `POWER.md`                             | Required — published with package                 | Create (new)                                                                                                         |
| `MANIFEST.in`                          | Required — controls sdist                         | Update: replace `CLAUDE.md` with `POWER.md README.md LICENSE`                                                        |
| `setup.py`                             | Redundant — duplicates pyproject.toml             | Delete after confirming entry point is in pyproject.toml                                                             |
| `setup.cfg`                            | Redundant — only has `description-file`           | Delete                                                                                                               |
| `TESTING_GUIDE.md`                     | Contributor-useful                                | Keep; reference from README.md                                                                                       |
| `samples/`                             | Contributor-useful                                | Keep                                                                                                                 |
| `scripts/`                             | Contributor-useful                                | Keep                                                                                                                 |
| `CLAUDE.md`                            | Dev-only AI instructions                          | Remove from repo (or add to .gitignore)                                                                              |
| `SPIRA_MCP_ENHANCEMENT_MASTER_PLAN.md` | Dev-only planning doc                             | Remove from repo                                                                                                     |
| `workspace.code-workspace`             | Dev-only VS Code file                             | Add to .gitignore                                                                                                    |
| `main.py`                              | Redundant — entry point already in pyproject.toml | Delete                                                                                                               |
| `SpiraRestAPI-v7.0-OpenAPI.json`       | Dev-only API spec (not needed at runtime)         | Keep in repo; exclude from wheel via `[tool.setuptools.package-data]` exclusion or by not including in `MANIFEST.in` |
| `server.json`                          | MCP registry metadata                             | Keep (investigate before touching)                                                                                   |
| `coverage.json`                        | Generated artefact                                | Add to `.gitignore`                                                                                                  |
| `htmlcov/`                             | Generated artefact                                | Already in `.gitignore`                                                                                              |
| `.env.spira`                           | Credentials — gitignored                          | Already in `.gitignore`                                                                                              |
| `spira.cfg`                            | Generated credentials — gitignored                | Already in `.gitignore`                                                                                              |

`.gitignore` additions needed:
```
coverage.json
workspace.code-workspace
```

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Version consistency

*For any* state of the repository where `setup.py` still exists, the version string in `pyproject.toml` and the version string in `setup.py` must be identical.

**Validates: Requirements 1.7, 6.1**

### Property 2: Config loads valid integer SPIRA_PROJECT_ID

*For any* string that is a valid decimal integer representation, when `SPIRA_PROJECT_ID` is set to that string and `load_config()` is called, `get_default_product_id()` must return the corresponding integer value.

**Validates: Requirements 4.1**

### Property 3: Config ignores non-integer SPIRA_PROJECT_ID

*For any* string that cannot be parsed as an integer (e.g. `"abc"`, `"1.5"`, `""`), when `SPIRA_PROJECT_ID` is set to that string and `load_config()` is called, `get_default_product_id()` must return `None`.

**Validates: Requirements 4.5**

### Property 4: resolve_product_id precedence

*For any* explicit `product_id` value that is not `None`, `resolve_product_id(explicit)` must return that explicit value regardless of what `_default_product_id` is set to. When `explicit` is `None`, `resolve_product_id(None)` must return `get_default_product_id()`.

**Validates: Requirements 4.2, 4.3**

### Property 5: Active product context fetches both endpoints

*For any* valid product ID set as the default, when `load_active_product_context()` is called with a mock client, the client must receive exactly one call to `projects/{id}` (GET) and one call to `projects/{id}/releases/search` (POST).

**Validates: Requirements 5.1, 5.2**

### Property 6: Active product context contains required fields

*For any* successful API response, after `load_active_product_context()` completes, `get_active_product_context()` must return a dict containing all four required keys: `product_id`, `name`, `description`, and `active_releases`, where `active_releases` is a list.

**Validates: Requirements 5.3, 5.6**

### Property 7: Resource reads use cached data

*For any* number of calls to `active_product_resource()` after a successful `load_active_product_context()`, the underlying API client must not be called again — all reads return the value cached at startup.

**Validates: Requirements 5.7**

---

## Error Handling

### `load_config()`
- `SPIRA_PROJECT_ID` absent → `_default_product_id` stays `None`, no log
- `SPIRA_PROJECT_ID` non-integer → `logging.warning(...)`, `_default_product_id` stays `None`
- Never raises; startup always continues

### `load_active_product_context()`
- No default product ID → returns immediately, no API call, no log
- API call fails (network error, 401, 404) → `logging.warning(...)`, `_active_product_context` stays `None`, server continues
- Never raises; startup always continues

### `active_product_resource()`
- Context is `None` → returns `{"error": "No active product context available"}` as JSON
- Context present → returns full context JSON

### `product_*` tools with `resolve_product_id`
- `resolve_product_id` returns `None` → tool returns structured error with `error_code: INVALID_PARAMETER` and a suggestion to set `SPIRA_PROJECT_ID`
- `resolve_product_id` returns a valid int → tool proceeds normally

---

## Testing Strategy

### Unit tests

Focus on specific examples, edge cases, and error conditions:

- `test_config.py`
  - `load_config()` with valid integer string → `get_default_product_id()` returns int
  - `load_config()` with non-integer string → `get_default_product_id()` returns `None`
  - `load_config()` with `SPIRA_PROJECT_ID` absent → `get_default_product_id()` returns `None`
  - `resolve_product_id(5)` with default 10 → returns 5
  - `resolve_product_id(None)` with default 10 → returns 10
  - `resolve_product_id(None)` with no default → returns `None`

- `test_context.py`
  - `load_active_product_context()` with no default → no API call, context is `None`
  - `load_active_product_context()` with failing client → no exception, context is `None`
  - `load_active_product_context()` with mock client → context has all required keys
  - `active_product_resource()` with `None` context → returns error JSON
  - `active_product_resource()` with populated context → returns context JSON

- `test_packaging.py`
  - `pyproject.toml` declares `[project.scripts]` with `mcp-server-spira` entry point
  - `POWER.md` exists at repo root
  - `POWER.md` frontmatter contains `name`, `description`, `keywords`
  - `POWER.md` content mentions all required env vars
  - `MANIFEST.in` includes `POWER.md`
  - `.gitignore` includes `coverage.json`

### Property-based tests

Use `hypothesis` (Python property-based testing library). Each test runs a minimum of 100 iterations.

- `test_config_properties.py`

  ```python
  # Feature: kiro-power-packaging, Property 2: Config loads valid integer SPIRA_PROJECT_ID
  @given(st.integers())
  def test_load_config_valid_integer(n):
      with patch.dict(os.environ, {"SPIRA_PROJECT_ID": str(n)}):
          load_config()
          assert get_default_product_id() == n

  # Feature: kiro-power-packaging, Property 3: Config ignores non-integer SPIRA_PROJECT_ID
  @given(st.text().filter(lambda s: not s.lstrip("-").isdigit()))
  def test_load_config_non_integer(s):
      with patch.dict(os.environ, {"SPIRA_PROJECT_ID": s}):
          load_config()
          assert get_default_product_id() is None

  # Feature: kiro-power-packaging, Property 4: resolve_product_id precedence
  @given(st.integers(), st.integers() | st.none())
  def test_resolve_product_id_explicit_wins(explicit, default):
      # When explicit is not None, it always wins
      with patch("mcp_server_spira.config._default_product_id", default):
          assert resolve_product_id(explicit) == explicit

  @given(st.integers() | st.none())
  def test_resolve_product_id_falls_back_to_default(default):
      with patch("mcp_server_spira.config._default_product_id", default):
          assert resolve_product_id(None) == default
  ```

- `test_context_properties.py`

  ```python
  # Feature: kiro-power-packaging, Property 6: Active product context contains required fields
  @given(st.integers(min_value=1), st.text(), st.text(), st.lists(st.fixed_dictionaries({
      "ReleaseId": st.integers(), "Name": st.text(), "VersionNumber": st.text(), "Active": st.booleans()
  })))
  async def test_context_has_required_fields(product_id, name, description, releases):
      mock_client = Mock()
      mock_client.make_spira_api_get_request.return_value = {"Name": name, "Description": description}
      mock_client.make_spira_api_post_request.return_value = releases
      with patch("mcp_server_spira.config._default_product_id", product_id):
          with patch("mcp_server_spira.features.context.get_client", return_value=mock_client):
              await load_active_product_context()
              ctx = get_active_product_context()
              assert ctx is not None
              assert "product_id" in ctx
              assert "name" in ctx
              assert "description" in ctx
              assert "active_releases" in ctx
              assert isinstance(ctx["active_releases"], list)
  ```

Both unit tests and property tests are complementary. Unit tests catch concrete bugs and edge cases; property tests verify general correctness across the input space.
