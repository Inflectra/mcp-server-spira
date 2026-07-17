# MCP Inflectra Spira Server

A Model Context Protocol (MCP) server that lets AI assistants interact with [Inflectra Spira](https://www.inflectra.com/SpiraPlan/) — covering project management, test management, and requirements management.

Works with SpiraTest, SpiraTeam, and SpiraPlan.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Available Tools](#available-tools)
- [Usage Examples](#usage-examples)
- [License](#license)

---

## Quick Start

Install from PyPI:

```bash
pip install mcp-server-spira
```

Add to your MCP client config:

```json
{
  "mcpServers": {
    "inflectra-spira": {
      "command": "python",
      "args": ["-m", "mcp_server_spira"],
      "env": {
        "INFLECTRA_SPIRA_BASE_URL": "https://myinstance.spiraservice.net",
        "INFLECTRA_SPIRA_USERNAME": "mylogin",
        "INFLECTRA_SPIRA_API_KEY": "{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXX}"
      }
    }
  }
}
```

For Cline, add `"type": "stdio"` to the server config. For Claude Desktop:

```bash
mcp install src/mcp_server_spira/server.py --name "Inflectra Spira Server"
```

---

## Configuration

Set these environment variables (or use a `.env` file):

| Variable | Required | Description |
|---|---|---|
| `INFLECTRA_SPIRA_BASE_URL` | Yes | Base URL for your Spira instance |
| `INFLECTRA_SPIRA_USERNAME` | Yes | Your Spira login name |
| `INFLECTRA_SPIRA_API_KEY` | Yes | API Key (RSS Token) from your Spira user profile |
| `SPIRA_PROJECT_ID` | No | Default product ID — avoids passing `product_id` on every call |

---

## Available Tools

13 tools organized by scope. All data-retrieval tools return structured JSON
with field projection, filtering, and a consistent response envelope.

### Search Tools
| Tool | Description |
|---|---|
| `mywork_search_artifacts` | Your assigned items (task, incident, requirement, test_case, test_set) with filtering and field projection |
| `product_search_artifacts` | Search artifacts in a product (11 types). Supports cross-product fan-out, server-side filtering, and nested sub-artifact includes. |
| `product_get_artifact` | Single artifact by ID with full details and optional sub-artifact includes |
| `program_search_artifacts` | Search program-level artifacts (capability, milestone) |

### Write Tools
| Tool | Description |
|---|---|
| `product_create_artifact` | Create artifacts (incident, task, requirement, test_case, risk, release, test_set, build, test_step, mitigation, requirement_step) |
| `product_update_artifact` | Update existing artifacts |
| `product_record_test_run` | Record automated test results from CI/CD |
| `create_comment` | Add a comment to an artifact |
| `create_association` | Link two artifacts (related-to, depends-on, coverage) |

### Workspace & Configuration Tools
| Tool | Description |
|---|---|
| `workspace_search` | List products, programs, or product templates with field projection |
| `workspace_get` | Get a single product, program, or template by ID |
| `template_get_metadata` | Types, statuses, priorities, severities, custom properties, and more for a template |
| `get_artifact_schema` | Field schema for any artifact type (local-only, no API call) |

---

## Usage Examples

Try these prompts with your AI assistant:

```
Show me my assigned tasks in Spira
```

```
List all products in my Spira instance
```

```
Get the open incidents in product 55
```

```
Search for critical requirements across products 55 and 60
```

```
Get the field schema for incidents
```

---

## License

MIT — see [LICENSE](LICENSE).

Built with [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) · [Spira REST API v7.0](https://spiradoc.inflectra.com/Developers/API-Overview/)

<!-- mcp-name: io.github.Inflectra/mcp-server-spira -->
