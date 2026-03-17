# MCP Inflectra Spira Server

A Model Context Protocol (MCP) server that lets AI assistants interact with [Inflectra Spira](https://www.inflectra.com/SpiraPlan/) — covering project management, test management, and requirements management.

Works with SpiraTest, SpiraTeam, and SpiraPlan.

---

## Table of Contents

- [Quick Start (Users)](#quick-start-users)
- [Quick Start (Developers)](#quick-start-developers)
- [Configuration](#configuration)
- [Available Tools](#available-tools)
- [Usage Examples](#usage-examples)
- [Development](#development)
- [Documentation](#documentation)

---

## Quick Start (Users)

Install from PyPI and add to your MCP client config:

```bash
pip install mcp-server-spira
```

### Kiro (`mcp.json`)

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

### Cline (`cline_mcp_settings.json`)

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
      },
      "type": "stdio"
    }
  }
}
```

### Claude Desktop

```bash
mcp install src/mcp_server_spira/server.py --name "Inflectra Spira Server"
```

---

## Quick Start (Developers)

```bash
git clone https://github.com/Inflectra/mcp-server-spira.git
cd mcp-server-spira

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
pre-commit install
```

Run with the MCP Inspector for local testing:

```bash
mcp dev src/mcp_server_spira/server.py
```

Run tests:

```bash
pytest
```

---

## Configuration

Create a `.env` file in the project root:

```
INFLECTRA_SPIRA_BASE_URL=https://mycompany.spiraservice.net
INFLECTRA_SPIRA_USERNAME=mylogin
INFLECTRA_SPIRA_API_KEY={XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXX}
SPIRA_PROJECT_ID=55
```

| Variable | Required | Description |
|---|---|---|
| `INFLECTRA_SPIRA_BASE_URL` | Yes | Base URL for your Spira instance |
| `INFLECTRA_SPIRA_USERNAME` | Yes | Your Spira login name |
| `INFLECTRA_SPIRA_API_KEY` | Yes | API Key (RSS Token) from your Spira user profile |
| `SPIRA_PROJECT_ID` | No | Default project ID — skips needing `product_id` on every call |

---

## Available Tools

### My Work
Tools for the current user's assigned artifacts.

| Tool | Description |
|---|---|
| `get_my_tasks` | My assigned tasks |
| `get_my_incidents` | My assigned incidents |
| `get_my_requirements` | My assigned requirements |
| `get_my_testcases` | My assigned test cases |
| `get_my_testsets` | My assigned test sets |

### Workspaces
| Tool | Description |
|---|---|
| `get_products` | All products/projects |
| `get_product_by_id` | Single product by ID |
| `get_programs` | All programs |
| `get_program_products` | Products within a program |
| `get_product_templates` | All product templates |

### Product Artifacts
| Tool | Description |
|---|---|
| `get_requirements` | Requirements in a product |
| `get_tasks` | Tasks in a product |
| `get_incidents` | Incidents in a product |
| `get_test_cases` | Test cases in a product |
| `get_test_sets` | Test sets in a product |
| `get_test_runs` | Test runs in a product |
| `get_releases` | Releases in a product |
| `get_automation_hosts` | Automation hosts in a product |

### Program Artifacts
| Tool | Description |
|---|---|
| `get_capabilities` | Capabilities in a program |
| `get_milestones` | Milestones in a program |

### Automation & CI/CD
| Tool | Description |
|---|---|
| `record_automated_test_run` | Record automated test results |
| `create_build` | Record a CI/CD build result |

### Specifications (for Agentic AI)
| Tool | Description |
|---|---|
| `get_specification_requirements` | Requirements spec for a release |
| `get_specification_design` | Design spec for a release |
| `get_specification_tasks` | Tasks spec for a release |
| `get_specification_test_cases` | Test cases spec for a release |

All tools return structured JSON. Most list tools support `limit` and `offset` for pagination.

---

## Usage Examples

Try these prompts with your AI assistant once the server is connected:

```
Show me my assigned tasks in Spira
```

```
List all products in my Spira instance
```

```
Get the requirements for product 55
```

```
Show me open incidents in project 55
```

```
Get the specification requirements for product 55, release 10
```

---

## Development

### Prerequisites

- Python 3.12+
- Git

### Running Tests

```bash
# All tests with coverage
pytest

# Specific file
pytest tests/test_server.py

# Unit tests only
pytest -m unit
```

### Code Quality

Pre-commit hooks run automatically on `git commit`:
- **Ruff** — linting and formatting
- **Black** — code formatting
- **Mypy** — type checking
- **Pytest** — test suite

Run manually:

```bash
pre-commit run --all-files
```

### Project Structure

```
src/mcp_server_spira/
├── server.py                  # Entry point
├── utils/spira_client.py      # HTTP client for Spira REST API
└── features/                  # Tools organized by domain
    ├── mywork/
    ├── workspaces/
    ├── programs/
    ├── products/
    ├── automation/
    └── specifications/
```

---

## Documentation

- [Development Setup](docs/development_setup.md) — full environment setup guide
- [Architecture](docs/architecture.md) — design patterns and project structure
- [Testing Guide](TESTING_GUIDE.md) — test structure and coverage

---

## License

MIT — see [LICENSE](LICENSE).

Built with [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) · [Spira REST API v7.0](https://spiradoc.inflectra.com/Developers/API-Overview/)

<!-- mcp-name: io.github.Inflectra/mcp-server-spira -->
