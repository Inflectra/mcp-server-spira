# Scripts Directory

This directory contains utility scripts for the Spira MCP Server project.

## Available Scripts

### `generate_tool_docs.py`

Generates tool documentation from the OpenAPI specification.

**Purpose:** Automates the creation of comprehensive MCP tool docstrings by extracting information from the Spira OpenAPI spec.

**Usage:**
```bash
python scripts/generate_tool_docs.py \
    --spec SpiraRestAPI-v7.0-OpenAPI.json \
    --output docs/tool_documentation_report.md
```

**Options:**
- `--spec` (required): Path to OpenAPI JSON file
- `--output` (required): Path to output markdown file

**Features:**
- Extracts endpoint and schema information from OpenAPI spec
- Generates complete docstring templates with all required sections
- Identifies areas needing human clarification
- Produces markdown reports for developer review

**Current Scope:**
- **Milestone 1 Focus**: Currently documents 5 "my work" tools only
- **Hardcoded Tool List**: Tools are explicitly defined in the script, not auto-discovered
- **Manual Extension**: To add more tools, edit the `tools` list in `generate_documentation_report()`

**Limitations:**
The script does not automatically discover all endpoints in the OpenAPI spec. It only generates documentation for tools explicitly listed in the code:
```python
tools = [
    ("get_my_tasks", "/tasks", "get", "task"),
    ("get_my_incidents", "/incidents", "get", "incident"),
    ("get_my_requirements", "/requirements", "get", "requirement"),
    ("get_my_test_cases", "/test-cases", "get", "test_case"),
    ("get_my_test_sets", "/test-sets", "get", "test_set"),
]
```

To document additional tools, add entries to this list following the same format: `(tool_name, endpoint_path, http_method, artifact_type)`.

**Output:**
The script generates a comprehensive markdown report containing:
- Generated docstring templates for all "my work" tools
- Identified clarifications for each tool
- Ready-to-review documentation that can be enhanced with workflow context

**Example Output:**
```markdown
## get_my_tasks

**Endpoint:** `GET /tasks`
**Artifact Type:** `task`

### Generated Docstring
[Complete Python docstring with all sections]

### Clarifications Needed
- ⚠️ Vague description for field 'TaskId': 'The id of the task'
- ⚠️ Missing endpoint description for GET /tasks
```

**Testing:**
Run the test suite to verify functionality:
```bash
python -m pytest tests/scripts/test_generate_tool_docs.py -v
```

**See Also:**
- `docs/DOCUMENTATION_GENERATOR_SUMMARY.md` - Detailed implementation summary
- `docs/tool_documentation_report.md` - Generated documentation report
- `tests/scripts/test_generate_tool_docs.py` - Comprehensive test suite

## Development

### Adding New Scripts

When adding new scripts to this directory:

1. Make the script executable: `chmod +x scripts/your_script.py`
2. Add a shebang line: `#!/usr/bin/env python3`
3. Include comprehensive docstrings
4. Add CLI argument parsing with `argparse`
5. Create corresponding tests in `tests/scripts/`
6. Update this README with usage information

### Testing Scripts

All scripts should have corresponding test files in `tests/scripts/`:

```bash
# Run all script tests
python -m pytest tests/scripts/ -v

# Run specific script tests
python -m pytest tests/scripts/test_generate_tool_docs.py -v
```

## Requirements

Scripts in this directory require:
- Python 3.12+
- Dependencies from `requirements-dev.txt`
- Access to project root directory

## Contributing

When modifying scripts:
1. Update docstrings and comments
2. Add/update tests
3. Update this README if usage changes
4. Ensure all tests pass before committing
