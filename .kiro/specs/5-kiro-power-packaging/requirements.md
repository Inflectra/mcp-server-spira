# Requirements Document

## Introduction

This feature packages the Spira MCP Server as a Kiro Power and publishes it to PyPI. The goal is to make the server installable via `uvx mcp-server-spira@latest`, provide a `POWER.md` file that enables Kiro to discover and onboard the power, and make the power proactive by reading a `SPIRA_PROJECT_ID` from the environment to automatically surface context about the active Spira product when the power activates.

## Glossary

- **Power**: A Kiro extension that bundles an MCP server with a `POWER.md` file containing metadata, onboarding instructions, and steering mappings.
- **POWER.md**: A markdown file with YAML frontmatter that describes the power to Kiro, including keywords, name, description, onboarding steps, and steering file mappings.
- **Steering File**: A markdown file in `.kiro/steering/` that provides persistent context to the AI assistant during a session.
- **PyPI**: The Python Package Index — the standard public registry for Python packages.
- **uvx**: A tool from the `uv` ecosystem that runs Python packages in isolated environments without a manual install step.
- **SPIRA_PROJECT_ID**: An environment variable that identifies the default Spira product (project) the user is working on.
- **Activation Context**: Structured information about the active Spira product (name, description, active releases) that the server surfaces automatically when `SPIRA_PROJECT_ID` is set.
- **Spira_Client**: The HTTP client in `src/mcp_server_spira/utils/spira_client.py` used to call the Spira REST API.
- **MCP_Server**: The FastMCP server instance defined in `src/mcp_server_spira/server.py`.
- **Product**: A Spira project, identified by a numeric `ProjectId`.
- **Release**: A Spira release or sprint within a product, identified by a numeric `ReleaseId`.
- **lifespan**: A FastMCP context manager that runs startup and shutdown logic around the server's lifecycle, used to perform one-time initialisation such as fetching product context.
- **MCP Resource**: A URI-addressable data source exposed by an MCP server that clients can read on demand, identified by a URI scheme such as `spira://active-product`.
- **Repository Cleanup**: The process of auditing and removing or reorganising files in the repository root to reduce noise and clarify purpose.

---

## Requirements

### Requirement 1: PyPI Packaging

**User Story:** As a developer, I want to install the Spira MCP Server with a single command, so that I can start using it without cloning the repository or managing a virtual environment manually.

#### Acceptance Criteria

1. THE MCP_Server SHALL be installable via `pip install mcp-server-spira`.
2. THE MCP_Server SHALL be runnable via `uvx mcp-server-spira` after installation from PyPI.
3. THE MCP_Server SHALL expose a `mcp-server-spira` console script entry point that starts the server.
4. WHEN the package is built, THE Build_System SHALL include all required source files under `src/mcp_server_spira/` and the `POWER.md` file in the distribution.
5. THE `pyproject.toml` SHALL declare all runtime dependencies required to run the server.
6. THE `pyproject.toml` SHALL set `requires-python = ">=3.12"` to match the project's stated minimum Python version.
7. WHEN a new version is released, THE Package_Version in `pyproject.toml` and `setup.py` SHALL be identical and follow semantic versioning (MAJOR.MINOR.PATCH).

---

### Requirement 2: POWER.md File

**User Story:** As a Kiro user, I want the Spira MCP Server to be discoverable and self-describing as a Kiro Power, so that Kiro can onboard me and configure the server automatically.

#### Acceptance Criteria

1. THE Repository SHALL contain a `POWER.md` file at the project root.
2. THE `POWER.md` SHALL include a YAML frontmatter block containing at minimum: `name`, `description`, and `keywords` fields.
3. THE `POWER.md` SHALL include an onboarding section that lists the required environment variables (`INFLECTRA_SPIRA_BASE_URL`, `INFLECTRA_SPIRA_USERNAME`, `INFLECTRA_SPIRA_API_KEY`) and the optional `SPIRA_PROJECT_ID` variable with a description of each.
4. THE `POWER.md` SHALL include a steering mappings section that references the steering files identified as end-user-relevant by the Steering_Assessment in Requirement 3.
5. WHEN `SPIRA_PROJECT_ID` is set, THE `POWER.md` onboarding section SHALL instruct the user that product-specific tools will default to that project ID.
6. THE `POWER.md` keywords SHALL include terms that enable discovery of the power for project management, test management, requirements management, and incident tracking use cases.

---

### Requirement 3: Steering File Assessment

**User Story:** As a Kiro Power author, I want to assess whether the existing `.kiro/steering/` files are appropriate for end users of the published power, and whether dedicated end-user steering files would add value beyond what `POWER.md` alone provides, so that users get useful AI context without irrelevant or noisy guidance.

#### Acceptance Criteria

1. THE Steering_Assessment SHALL evaluate each file in `.kiro/steering/` for relevance to end users of the published power (as opposed to developers of the server itself).
2. WHEN a steering file contains guidance relevant only to server development (e.g., how to add new tools), THE Steering_Assessment SHALL recommend excluding it from the power's steering mappings or marking it with `inclusion: manual`.
3. WHEN a steering file contains guidance useful to end users of the power (e.g., tool usage patterns, API conventions), THE Steering_Assessment SHALL recommend including it with `inclusion: always` or `inclusion: fileMatch`.
4. THE Steering_Assessment SHALL evaluate whether the instructions in `POWER.md` alone are sufficient for end-user onboarding, or whether creating new dedicated end-user steering files would provide additional value.
5. IF the `POWER.md` instructions are sufficient for end-user context, THEN creating new end-user steering files SHALL be considered optional and the assessment SHALL document that rationale.
6. THE `POWER.md` steering mappings section SHALL reflect the outcome of the steering assessment.

---

### Requirement 4: Default Project ID from Environment

**User Story:** As a Spira user, I want to set a default project ID once in my `.env` file, so that I don't have to specify `product_id` on every tool call.

#### Acceptance Criteria

1. WHEN `SPIRA_PROJECT_ID` is set in the environment, THE MCP_Server SHALL read it at startup and store it as the default product ID.
2. WHEN a product-specific tool is called without an explicit `product_id` argument and `SPIRA_PROJECT_ID` is set, THE Tool SHALL use the value of `SPIRA_PROJECT_ID` as the `product_id`.
3. WHEN a product-specific tool is called with an explicit `product_id` argument, THE Tool SHALL use the explicit argument and ignore `SPIRA_PROJECT_ID`.
4. IF `SPIRA_PROJECT_ID` is not set and no `product_id` is provided to a product-specific tool, THEN THE Tool SHALL return a structured error indicating that `product_id` is required.
5. IF `SPIRA_PROJECT_ID` is set to a non-integer value, THEN THE MCP_Server SHALL log a warning at startup and treat `SPIRA_PROJECT_ID` as unset.
6. THE `SPIRA_PROJECT_ID` environment variable SHALL be documented in the `README.md` configuration section alongside the existing required variables.

---

### Requirement 5: Proactive Product Context on Activation

**User Story:** As a Spira user, I want the power to automatically surface information about my active Spira product when it starts, so that the AI assistant has immediate context about the project without me having to ask.

#### Acceptance Criteria

1. WHEN `SPIRA_PROJECT_ID` is set and the MCP_Server starts, THE MCP_Server SHALL use the FastMCP `lifespan` context manager to fetch the product details (name, description) for that product ID from the Spira API once at startup.
2. WHEN `SPIRA_PROJECT_ID` is set and the MCP_Server starts, THE MCP_Server SHALL use the FastMCP `lifespan` context manager to fetch the list of active releases for that product ID from the Spira API once at startup.
3. WHEN the product details and releases are successfully fetched, THE MCP_Server SHALL expose this information as an MCP Resource with the URI `spira://active-product` that the AI assistant can read on demand.
4. WHEN `SPIRA_PROJECT_ID` is not set, THE MCP_Server SHALL NOT attempt to fetch product context and the `spira://active-product` MCP Resource SHALL NOT be registered.
5. IF the Spira API call to fetch product context fails at startup, THEN THE MCP_Server SHALL log the error and continue starting normally without the `spira://active-product` MCP Resource.
6. THE `spira://active-product` MCP Resource SHALL return a JSON object containing at minimum: `product_id`, `name`, `description`, and `active_releases` (list of release names and IDs).
7. WHEN the `spira://active-product` MCP Resource is read, THE MCP_Server SHALL return the data cached in the module-level `active_product_context` variable without making an additional API call.

---

### Requirement 6: Round-Trip Configuration Integrity

**User Story:** As a developer maintaining the package, I want the packaging configuration to be consistent and verifiable, so that published releases are reproducible.

#### Acceptance Criteria

1. THE Package_Version declared in `pyproject.toml` SHALL match the version declared in `setup.py` at all times.
2. WHEN the package is built with `python -m build`, THE Build_System SHALL produce both a source distribution (`.tar.gz`) and a wheel (`.whl`) without errors.
3. WHEN the wheel is installed in a clean environment, THE `mcp-server-spira` entry point SHALL be executable and SHALL start the MCP server.
4. THE `MANIFEST.in` SHALL include the `POWER.md` file so it is present in the source distribution.

---

### Requirement 7: Repository File Structure Cleanup

**User Story:** As a contributor or maintainer, I want the repository root to contain only purposeful files, so that the project is easy to navigate and the published package is not cluttered with development artefacts.

#### Acceptance Criteria

1. THE Repository_Cleanup SHALL audit each file and directory at the repository root and document its purpose, categorising it as one of: (a) required in the published package, (b) useful for contributors but not published, (c) a generated artefact that should be gitignored, or (d) redundant or obsolete and safe to delete.
2. WHEN a file's purpose cannot be determined from its name or content alone, THE Repository_Cleanup SHALL investigate the file before recommending any action, and SHALL NOT delete it without confirming its purpose.
3. THE `pyproject.toml` SHALL be the single source of truth for packaging configuration; WHEN `setup.py` or `setup.cfg` contain only information already present in `pyproject.toml`, THE Repository_Cleanup SHALL recommend removing the redundant file.
4. WHEN `setup.py` or `setup.cfg` contain configuration not yet present in `pyproject.toml`, THE Repository_Cleanup SHALL recommend migrating that configuration to `pyproject.toml` before removing the legacy file.
5. THE `.gitignore` SHALL include entries for all generated artefacts identified during the audit, including at minimum `coverage.json` and `htmlcov/`.
6. WHEN a file is identified as a development-only artefact not needed by end users or contributors (e.g., `CLAUDE.md`, `SPIRA_MCP_ENHANCEMENT_MASTER_PLAN.md`, `workspace.code-workspace`), THE Repository_Cleanup SHALL recommend removing it from the repository or adding it to `.gitignore` as appropriate.
7. WHEN a file is identified as potentially useful to contributors (e.g., `TESTING_GUIDE.md`, `scripts/`), THE Repository_Cleanup SHALL recommend retaining it and ensuring it is referenced from `README.md` or `CONTRIBUTING.md`.
8. THE `SpiraRestAPI-v7.0-OpenAPI.json` file SHALL be assessed for inclusion in the published package; IF it is not required at runtime, THEN THE Repository_Cleanup SHALL recommend excluding it from the wheel via `.gitignore` or packaging configuration while retaining it in the repository for development use.
