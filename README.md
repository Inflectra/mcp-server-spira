# MCP Inflectra Spira Server

**Status:** Active Development - Milestone 0 (Foundation & Infrastructure) Complete

A Model Context Protocol (MCP) server enabling AI assistants to interact with Spira by Inflectra.

## Overview
This project implements a Model Context Protocol (MCP) server that allows AI assistants (like Claude) to interact with the Inflectra Spira platform, providing a bridge between natural language interactions and the Spira REST API.

This server supports all three editions of Spira:
- **SpiraTest:** Test Management When You Need Quality, Agility & Speed
- **SpiraTeam:** Project, Requirements Management & ALM For Agile Teams
- **SpiraPlan:** Program Management & ALM For Scaling Agile & Enterprises


## Features
The Spira MCP server current implements the following features:

### My Work
This feature provides easy access to the list of artifacts that have been assigned to the current user

- **My Tasks:** Provides operations for working with the Spira tasks I have been assigned
- **My Requirements:** Provides operations for working with the Spira requirements I have been assigned
- **My Incidents:** Provides operations for working with the Spira incidents I have been assigned
- **My Test Cases:** Provides operations for working with the Spira test cases I have been assigned
- **My Test Sets:** Provides operations for working with the Spira test sets I have been assigned

### Workspaces
This feature provides tools that let you retrieve and modify the different workspaces inside Spira

- **Programs:** Provides operations for working with Spira programs
- **Products:** Provides operations for working with Spira products
- **Product Templates:** Provides operations for working with Spira product templates

### Program Artifacts
This feature provides tools that let you retrieve and modify the different artifacts inside a Spira program

- **Capabilities:** Provides operations for working with the Spira capabilities in a program backlog
- **Milestones:** Provides operations for working with the Spira milestones in a program

### Product Artifacts
This feature provides tools that let you retrieve and modify the different artifacts inside a Spira product

- **Requirements:** Provides operations for working with the Spira requirements in a product
- **Releases:** Provides operations for working with the Spira releases in a product
- **Test Cases:** Provides operations for working with the Spira test case folders and test cases in a product
- **Test Sets:** Provides operations for working with the Spira test set folders and test sets in a product
- **Test Runs:** Provides operations for working with the Spira test runs in a product
- **Tasks:** Provides operations for working with the Spira tasks in a product
- **Incidents:** Provides operations for working with the Spira incidents (e.g. bugs, enhancements, issues, etc.) in a product
- **Automation Hosts:** Provides operations for working with the Spira automation hosts in a product

### Template Configuration
This feature provides tools that let you view and modify the configuration and settings of Spira product templates

- **Artifact Types:** Retrieves information on the artifact types in a product template, and their sub-types
- **Custom Properties:** Retrieves information on the artifact types in a product template, and their custom properties

### Automation
This feature provides tools that let you integrate automated DevOps tools such as test automation frameworks and CI/CD pipelines

- **Automated Test Runs:** Provides operations for recording automated test run results into Spira
- **Builds:** Provides operations for recording the results of CI/CD builds into Spira

### Specifications
Provides operations for retrieving the product specification files that
can be used to build the functionality of the product using AI.
This is used by Agentic AI development tools such as Amazon Kiro
for building applications from a formal spec.

This module provides the following MCP tools for retrieving the entire product specifications:
- **get_specification_requirements** - returns the data for populating the `requirements.md` file
- **get_specification_design** - returns the data for populating the `design.md` file
- **get_specification_tasks** - returns the data for populating the `tasks.md` file
- **get_specification_test_cases** - returns the data for populating the `test-cases.md` file

## Getting Started

### Prerequisites

- Python 3.13+ (specified in `.python-version` file)
- Inflectra Spira cloud account with appropriate permissions
- Username and active API Key (RSS Token) for this instance

### Installation

```bash
# Clone the repository
git clone https://github.com/Inflectra/mcp-server-spira.git
cd mcp-server-spira

# Simple development mode install
pip install -e .

# Install into a virtual development environment (you may need to create one with uv venv)
uv pip install -e ".[dev]"

# Install from PyPi
pip install mcp-server-spira
```

### Configuration

Create a `.env` file in the project root with the following variables:

```
INFLECTRA_SPIRA_BASE_URL=The base URL for your instance of Spira (typically https://mycompany.spiraservice.net or https://demo-xx.spiraservice.net/mycompany)
INFLECTRA_SPIRA_USERNAME=The login name you use to access Spira
INFLECTRA_SPIRA_API_KEY=The API Key (RSS Token) you use to access the Spira REST API
```

Note: Make sure your API Key is active and saved in your Spira user profile.

### Running the Server directly

```bash
# Development mode with the MCP Inspector
mcp dev src/mcp_server_spira/server.py

# Production mode using shell / command line
python -m mcp_server_spira

# Install in Claude Desktop
mcp install src/mcp_server_spira/server.py --name "Inflectra Spira Server"
```

### Running the MCP Server from Cline

To run the MCP server from within Cline, you don't use the commands above, instead you add the Inflectra MCP server to the configuration JSON file `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "inflectra-spira": {
      "autoApprove": [
        "get_my_incidents",
        "get_products",
        "get_test_cases"
      ],
      "timeout": 60,
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Git\\mcp-server-spira",
        "run",
        "main.py"
      ],
      "env": {
        "INFLECTRA_SPIRA_BASE_URL": "https://mycompany.spiraservice.net",
        "INFLECTRA_SPIRA_USERNAME": "login",
        "INFLECTRA_SPIRA_API_KEY": "{XXXXXX-XXXXXXX-XXXXXXX-XXXXXXX-XXXXX}"
      },
      "type": "stdio"
    }
  }
}
```

### Running the MCP Server from Kiro

To run the MCP server from within Kiro, you don't use the commands above, instead you add the Inflectra MCP server to the configuration JSON file `mcp.json`:

```json
{
  "mcpServers": {
    "inflectra-spira": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Git\\mcp-server-spira",
        "run",
        "main.py"
      ],
      "env": {
        "INFLECTRA_SPIRA_BASE_URL": "https://myinstance.spiraservice.net",
        "INFLECTRA_SPIRA_USERNAME": "mylogin",
        "INFLECTRA_SPIRA_API_KEY": "{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXX}"
      },
      "disabled": false,
      "autoApprove": [
        "get_specification_requirements",
        "get_specification_design",
        "get_specification_tasks",
        "get_specification_test_cases"
      ]
    }
  }
}
```

## Usage Examples

### Get Assigned Artifacts

```
Get me my assigned tasks in Spira/
```

```
Get me my assigned requirements in Spira/
```


### View Project Structure

```
List all projects in my organization and show me the iterations for the Development team
```

## Documentation

For comprehensive information about the project:

- **[Development Setup Guide](docs/development_setup.md)** - Complete guide for setting up your development environment
- **[Architecture Documentation](docs/architecture.md)** - Detailed explanation of the project structure and design patterns
- **[Master Plan](SPIRA_MCP_ENHANCEMENT_MASTER_PLAN.md)** - Roadmap and enhancement plan for the project

## Development

### Setting Up Development Environment

For detailed setup instructions, see the [Development Setup Guide](docs/development_setup.md).

Quick start:

```bash
# Clone the repository
git clone https://github.com/Inflectra/mcp-server-spira.git
cd mcp-server-spira

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .
```

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. The hooks automatically run linting, formatting, type checking, and tests before each commit.

#### Installing Pre-commit Hooks

```bash
# Install the pre-commit hooks
pre-commit install
```

#### Running Hooks Manually

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run hooks on staged files only
pre-commit run
```

#### Skipping Hooks (Use Sparingly)

For urgent commits where you need to bypass the hooks:

```bash
git commit --no-verify -m "urgent fix"
```

**Note:** Only use `--no-verify` when absolutely necessary. The hooks are there to catch issues early.

#### What the Hooks Check

- **Trailing whitespace**: Removes trailing whitespace from files
- **End of file fixer**: Ensures files end with a newline
- **YAML/JSON validation**: Checks syntax of YAML and JSON files
- **Large files**: Prevents accidentally committing large files (>1MB)
- **Merge conflicts**: Detects unresolved merge conflict markers
- **Private keys**: Detects accidentally committed private keys
- **Ruff**: Fast Python linter and formatter
- **Black**: Python code formatter
- **Mypy**: Static type checker
- **Pytest**: Runs the test suite

### Running Tests

This project uses pytest for testing with coverage reporting.

#### Basic Test Commands

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_server.py

# Run tests matching a pattern
pytest -k "test_server"
```

#### Coverage Reports

```bash
# Run tests with coverage report (terminal output)
pytest --cov

# Run tests with detailed coverage showing missing lines
pytest --cov --cov-report=term-missing

# Generate HTML coverage report
pytest --cov --cov-report=html

# Open the HTML coverage report (after generating)
# The report will be in htmlcov/index.html
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
start htmlcov/index.html  # On Windows
```

#### Test Markers

Tests are organized with markers for selective execution:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

#### Current Test Coverage

The project currently has 23% test coverage. Coverage reports are automatically generated when running tests and can be viewed in the `htmlcov/` directory.

### Project Structure

The project is structured into feature modules, each implementing specific Inflectra Spira capabilities:

- `features/mywork`: Accessing a user's assigned artifacts and updating their status/progress
- `features/projects`: Project management capabilities
- `features/programs`: Program management features
- `utils`: Common utilities and client initialization

For more information on development, see the [CLAUDE.md](CLAUDE.md) file.

### Tool Documentation Generator

The project includes a documentation generator script that creates comprehensive tool documentation from the OpenAPI specification.

#### Purpose

The `generate_tool_docs.py` script automates the creation of tool docstrings by:
- Extracting endpoint information from the Spira OpenAPI spec
- Generating structured docstring templates with parameter and return value documentation
- Identifying areas that need human clarification (ambiguous descriptions, business logic questions, etc.)
- Creating a markdown report with generated documentation and clarification checklists

#### Usage

```bash
python scripts/generate_tool_docs.py \
  --spec SpiraRestAPI-v7.0-OpenAPI.json \
  --output docs/tool_documentation_report.md
```

#### Output

The script generates a comprehensive report including:
- Generated docstring templates for each tool
- Structured clarification checklists organized by severity (High/Medium/Low)
- Examples of good clarification requests
- OpenAPI spec references for each issue

Example output:
```
✅ Documentation report generated: docs/tool_documentation_report.md
📄 Generated documentation for 5 tools
⚠️  Total clarifications needed: 162
```

#### Current Scope and Limitations

**Important:** The documentation generator is currently scoped for **Milestone 1** and has the following limitations:

1. **Hardcoded Tool List**: The script documents a fixed set of 5 "my work" tools:
   - `get_my_tasks` → `/tasks`
   - `get_my_incidents` → `/incidents`
   - `get_my_requirements` → `/requirements`
   - `get_my_test_cases` → `/test-cases`
   - `get_my_test_sets` → `/test-sets`

2. **Not Dynamic**: The script does not automatically discover all endpoints in the OpenAPI spec. It only generates documentation for the tools explicitly listed in the `tools` array within the `generate_documentation_report()` method.

3. **Manual Extension Required**: To document additional tools, you must:
   - Edit `scripts/generate_tool_docs.py`
   - Add new entries to the `tools` list in the format: `(tool_name, endpoint_path, http_method, artifact_type)`
   - Ensure the endpoint exists in the OpenAPI spec

#### Example: Adding More Tools

To document workspace tools in addition to "my work" tools:

```python
# In scripts/generate_tool_docs.py, modify the tools list:
tools = [
    # My work tools
    ("get_my_tasks", "/tasks", "get", "task"),
    ("get_my_incidents", "/incidents", "get", "incident"),
    ("get_my_requirements", "/requirements", "get", "requirement"),
    ("get_my_test_cases", "/test-cases", "get", "test_case"),
    ("get_my_test_sets", "/test-sets", "get", "test_set"),
    # Workspace tools (add these)
    ("get_products", "/projects", "get", "product"),
    ("get_programs", "/programs", "get", "program"),
]
```

#### Future Enhancements

Potential improvements for future milestones:
- Dynamic endpoint discovery from OpenAPI spec
- Configuration file for specifying which tools to document
- Filtering by OpenAPI tags or operation IDs
- Command-line options to select specific tool categories

#### Clarification Detection

The script implements comprehensive clarification detection covering:
- Missing or ambiguous descriptions
- Vague field descriptions (e.g., "the id", "the name")
- Complex nested schemas
- Business logic questions (similar fields, ID/Name pairs)
- Workflow context questions
- Performance implications
- Edge cases with nullable fields

For more details, see [docs/clarification_detection_summary.md](docs/clarification_detection_summary.md).

### Spira pytest Integration

This project uses [pytest-spiratest](https://spiradoc.inflectra.com/Unit-Testing-Integration/Integrating-with-PyTest/) to automatically report test results to Spira.

#### Quick Setup

1. Install: `pip install pytest-spiratest`
2. Configure: `cp .env.spira.template .env.spira` and edit with your credentials
3. Run tests: `pytest tests/` - results automatically report to Spira

#### Key Features

- One test class = one Spira test case (24 test classes currently mapped)
- Credentials in `.env.spira` (not in version control)
- Test case mappings in `spira.cfg` (in version control)
- Validation script ensures 100% coverage: `python scripts/validate_spira_integration.py`

See [docs/spira_pytest_integration.md](docs/spira_pytest_integration.md) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- Uses [Inflectra Spira v7.0 REST API](https://spiradoc.inflectra.com/Developers/API-Overview/)

<!-- mcp-name: io.github.Inflectra/mcp-server-spira -->
