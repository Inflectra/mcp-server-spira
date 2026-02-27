# Requirements Document

## Introduction

The Spira MCP Server currently exposes 33 tools in a flat namespace. As the tool count scales toward 80+, LLMs will struggle with tool selection due to token overhead, ambiguous naming, and lack of organizational signals. This feature restructures tool naming, adds metadata annotations, introduces a server-level description, and prepares the architecture for sub-server composition — all to keep tool discovery fast and accurate as the catalog grows.

## Glossary

- **MCP_Server**: The FastMCP-based Python server that exposes Spira API operations as MCP tools
- **Tool**: A single callable function registered with the MCP_Server and exposed to LLM clients
- **Tool_Name**: The string identifier used by LLM clients to invoke a Tool (e.g., `product_get_tasks`)
- **Tool_Annotation**: MCP-spec metadata attached to a Tool describing its behavior (e.g., `readOnlyHint`, `destructiveHint`, `openWorldHint`)
- **Server_Description**: A human-readable text block returned by the MCP_Server in its `server/info` response, providing an overview of available tool groups
- **Scope_Prefix**: A short string prepended to a Tool_Name indicating the operational scope (e.g., `my_`, `product_`, `program_`, `template_`, `system_`)
- **Sub_Server**: A mounted FastMCP server instance that namespaces a group of tools under a common prefix via server composition
- **Tool_Catalog**: A structured listing of all available tools organized by scope, returned as a tool itself for dynamic discovery
- **LLM_Client**: Any AI model or agent that connects to the MCP_Server and invokes tools

## Requirements

### Requirement 1: Server Description

**User Story:** As an LLM_Client, I want the MCP_Server to return a description of its capabilities and tool organization, so that I can understand the available tool groups before reading individual tool docstrings.

#### Acceptance Criteria

1. THE MCP_Server SHALL include a Server_Description in its initialization that summarizes the server purpose, lists all Scope_Prefixes with their meanings, and provides the total tool count.
2. WHEN an LLM_Client connects, THE MCP_Server SHALL return the Server_Description as part of the server metadata.
3. THE Server_Description SHALL be no longer than 1000 characters to minimize token overhead.
4. THE Server_Description SHALL list each Scope_Prefix with a one-line explanation of the tools in that scope.

### Requirement 2: Scope-Prefixed Tool Names

**User Story:** As an LLM_Client, I want tool names to include a scope prefix, so that I can identify the operational context of a tool without reading its full docstring.

#### Acceptance Criteria

1. THE MCP_Server SHALL prefix every Tool_Name with a Scope_Prefix that indicates the tool's operational scope.
2. THE MCP_Server SHALL use the following Scope_Prefixes:
   - `my_` for tools that operate on the current user's personal work items
   - `product_` for tools scoped to a specific Spira product
   - `program_` for tools scoped to a specific Spira program
   - `template_` for tools that read product template configuration
   - `system_` for tools that operate across the entire Spira instance (e.g., workspace listing)
   - `automation_` for tools related to CI/CD build and test run recording
   - `spec_` for tools that retrieve specification document structures
   - `format_` for tools that transform data for display
3. WHEN a Tool_Name is registered, THE MCP_Server SHALL validate that the Tool_Name starts with one of the defined Scope_Prefixes.
4. THE MCP_Server SHALL maintain the existing verb convention after the prefix (e.g., `get_`, `create_`, `record_`, `format_`).

### Requirement 3: Tool Annotations

**User Story:** As an LLM_Client, I want each tool to carry MCP-spec annotations, so that I can distinguish read-only tools from write operations and make safer tool selections.

#### Acceptance Criteria

1. THE MCP_Server SHALL attach a Tool_Annotation to every registered Tool.
2. WHEN a Tool performs only read operations, THE MCP_Server SHALL set `readOnlyHint` to `true` on that Tool.
3. WHEN a Tool creates or modifies data, THE MCP_Server SHALL set `readOnlyHint` to `false` on that Tool.
4. WHEN a Tool creates or modifies data in a way that cannot be undone, THE MCP_Server SHALL set `destructiveHint` to `true` on that Tool.
5. THE MCP_Server SHALL set `openWorldHint` to `true` on Tools that interact with external systems (the Spira API) and `false` on Tools that perform local-only transformations.

### Requirement 4: Tool Name Migration Mapping

**User Story:** As a developer, I want a documented mapping from old tool names to new tool names, so that I can update client code and prompts during the migration.

#### Acceptance Criteria

1. THE MCP_Server repository SHALL contain a migration mapping that lists every old Tool_Name alongside its new Tool_Name.
2. THE migration mapping SHALL cover all 33 existing tools.
3. WHEN a new Scope_Prefix is assigned to a tool, THE migration mapping SHALL record the rationale for the prefix choice.

### Requirement 5: Docstring Compliance Under New Names

**User Story:** As a developer, I want the existing 50-line docstring limit to remain enforced after renaming, so that tool metadata stays concise as the catalog grows.

#### Acceptance Criteria

1. WHILE tools are registered with the MCP_Server, THE docstring compliance test SHALL enforce a maximum of 50 lines per Tool docstring.
2. WHEN a Tool is renamed with a Scope_Prefix, THE Tool's docstring SHALL include the Scope_Prefix context in its first-line summary without exceeding the 50-line limit.
3. THE docstring compliance test SHALL validate all tools by their new Tool_Names.

### Requirement 6: Naming Validation Test

**User Story:** As a developer, I want an automated test that validates all tool names follow the prefix convention, so that naming drift is caught before merge.

#### Acceptance Criteria

1. THE MCP_Server test suite SHALL include a test that verifies every registered Tool_Name starts with a valid Scope_Prefix.
2. WHEN a Tool is registered with an invalid or missing Scope_Prefix, THE test SHALL fail and report the non-compliant Tool_Name.
3. THE test SHALL maintain a list of valid Scope_Prefixes that matches the defined set in Requirement 2.

### Requirement 7: Token Budget Monitoring

**User Story:** As a developer, I want to track the total token footprint of the `tools/list` response, so that I can detect when the tool catalog approaches LLM context limits.

#### Acceptance Criteria

1. THE MCP_Server test suite SHALL include a test that estimates the total token count of the `tools/list` response.
2. WHEN the estimated token count exceeds 40,000 tokens, THE test SHALL emit a warning.
3. WHEN the estimated token count exceeds 60,000 tokens, THE test SHALL fail.
4. THE token estimation SHALL use a character-to-token ratio of 4 characters per token as the approximation method.


## Future Research (Optional / Deferred)

The following requirements were identified during initial analysis but deferred. With only 33 tools currently registered, these optimizations are not yet necessary. They should be revisited if the tool count approaches 80+.

### Tool Catalog Discovery Tool

**User Story:** As an LLM_Client, I want a tool that returns a structured catalog of all available tools grouped by scope, so that I can discover relevant tools without parsing the full `tools/list` response.

#### Acceptance Criteria

1. THE MCP_Server SHALL provide a Tool named `list_tool_catalog` that returns a JSON listing of all registered tools grouped by Scope_Prefix.
2. WHEN `list_tool_catalog` is invoked, THE MCP_Server SHALL return for each tool: the Tool_Name, a one-line summary, and the Tool_Annotation values.
3. WHEN `list_tool_catalog` is invoked with a `scope` parameter, THE MCP_Server SHALL return only tools matching that Scope_Prefix.
4. THE `list_tool_catalog` Tool SHALL set `readOnlyHint` to `true` and `openWorldHint` to `false` in its own Tool_Annotation.

### Sub-Server Composition Readiness

**User Story:** As a developer, I want the tool registration architecture to support mounting feature modules as sub-servers, so that the server can scale beyond 80 tools with proper namespacing.

#### Acceptance Criteria

1. THE MCP_Server registration architecture SHALL organize tools into feature modules that can each be mounted as a Sub_Server.
2. WHEN a feature module is mounted as a Sub_Server, THE MCP_Server SHALL namespace that module's tools under the module's Scope_Prefix.
3. THE MCP_Server SHALL support both flat registration (current approach with prefixed names) and Sub_Server composition (future approach) without changing tool implementations.
4. THE feature module interface SHALL expose a `create_sub_server()` function that returns a FastMCP instance ready for mounting.
