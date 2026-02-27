# Testing Guide for Spira MCP Server

This guide explains how to test the MCP server both manually and with integration tests.

## Prerequisites

1. **Spira Instance**: You need access to a Spira instance (cloud or on-premise)
2. **Credentials**: You need:
   - Base URL (e.g., `https://mycompany.spiraservice.net`)
   - Username
   - API Key (RSS Token) - Get this from your Spira user profile

## Setup

### 1. Create `.env` File

Create a `.env` file in the project root with your credentials:

```bash
# Copy the template
cp .env.template .env

# Edit .env with your actual credentials
nano .env  # or use your preferred editor
```

Your `.env` should look like:

```
INFLECTRA_SPIRA_BASE_URL=https://your-instance.spiraservice.net
INFLECTRA_SPIRA_USERNAME=your-username
INFLECTRA_SPIRA_API_KEY=your-api-key-here
```

**Important**: The `.env` file is in `.gitignore` and will not be committed.

### 2. Load Environment Variables for Tests

**Good news!** The integration tests automatically load environment variables from `.env` - no manual setup needed!

The `tests/integration/conftest.py` file handles this automatically when you run pytest.

Just run:
```bash
pytest tests/integration/test_current_server.py -v -s
```

If you see tests being skipped, check that your `.env` file exists and has the correct variables.

### 2. Verify Installation

```bash
# Check that the package is installed
pip show mcp-server-spira

# Should show:
# Name: mcp-server-spira
# Version: 1.1.1
# Location: /path/to/.venv/lib/python3.13/site-packages
# Editable project location: /path/to/mcp-server-spira
```

## Test Organization

The project uses pytest markers to organize tests:

### Available Markers

- **`@pytest.mark.unit`** - Fast unit tests with mocked dependencies
- **`@pytest.mark.integration`** - Integration tests requiring real API access
- **`@pytest.mark.slow`** - Tests that may take longer to run

### Running Different Test Types

```bash
# Run ALL tests (unit + integration)
pytest

# Run only unit tests (fast, no API needed)
pytest -m unit

# Run only integration tests (requires .env with credentials)
pytest -m integration

# Run everything except slow tests
pytest -m "not slow"

# Run integration tests but skip slow ones
pytest -m "integration and not slow"

# Run unit tests with coverage
pytest -m unit --cov

# Run specific test file
pytest tests/features/common/test_validation.py -v
```

### Test Locations

```
tests/
├── features/
│   ├── common/          # Unit tests for infrastructure (validation, pagination, etc.)
│   ├── mywork/          # Tests for "my work" tools
│   └── ...
├── integration/         # Integration tests (marked with @pytest.mark.integration)
│   ├── conftest.py      # Auto-loads .env for integration tests
│   └── test_current_server.py
└── scripts/             # Tests for documentation generator
```

---

## Testing Methods

### Method 1: MCP Inspector (Recommended for Manual Testing)

The MCP Inspector provides a web UI for testing MCP servers interactively.

```bash
# Start the MCP Inspector
mcp dev src/mcp_server_spira/server.py
```

This will:
1. Start the MCP server
2. Open a web browser with the inspector UI
3. Show all available tools
4. Let you test each tool with different parameters
5. Display responses in real-time

**What to test:**
- `get_my_tasks` - Should return markdown with your assigned tasks
- `get_my_incidents` - Should return markdown with your assigned incidents
- `get_my_requirements` - Should return markdown with your assigned requirements
- `get_products` - Should return list of products you have access to

**Expected behavior (current version):**
- ✅ Returns markdown formatted text
- ✅ Truncates at 25 items (no warning)
- ✅ No pagination parameters
- ✅ Generic error messages

### Method 2: Integration Tests

Run automated integration tests against your real Spira instance.

```bash
# Run all integration tests
pytest tests/integration/test_current_server.py -v -s

# Run only integration tests (using marker)
pytest -m integration -v -s

# Run integration tests but skip slow ones
pytest -m "integration and not slow" -v -s

# Run specific test
pytest tests/integration/test_current_server.py::TestCurrentServerIntegration::test_get_my_tasks_current -v -s

# With coverage
pytest tests/integration/test_current_server.py --cov -v -s

# Alternative: Use the shell script
./run_integration_tests.sh
```

**Test Markers:**
- `@pytest.mark.integration` - All integration tests (require real API)
- `@pytest.mark.slow` - Tests that may take longer (e.g., truncation test with many items)

**How it works:** The `tests/integration/conftest.py` file automatically loads environment variables from `.env` before running tests. No manual setup needed!

**What the tests verify:**
- ✅ Connection to Spira works
- ✅ Tools return markdown strings
- ✅ Truncation happens at 25 items
- ✅ No pagination parameters exist
- ✅ Error handling is graceful
- ✅ Raw API responses are JSON-serializable

**Sample output:**
```
tests/integration/test_current_server.py::TestCurrentServerIntegration::test_connection_to_spira
✅ Connected to Spira successfully
   Found 5 products
PASSED

tests/integration/test_current_server.py::TestCurrentServerIntegration::test_get_my_tasks_current
📋 get_my_tasks result:
   Type: <class 'str'>
   Length: 1234 characters
   Format: Markdown ✓
   First 200 chars: ## Task [TK:40] - Fix login bug...
PASSED

tests/integration/test_current_server.py::TestCurrentServerIntegration::test_truncation_behavior
✂️  Truncation test:
   Total tasks from API: 47
   Tasks in formatted result: 25
   ⚠️  Truncation confirmed: 47 tasks → 25 shown
PASSED
```

### Method 3: Direct Python Testing

You can also test directly in Python:

```python
# Start Python REPL
python

# Import and test
from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.mywork.tools.mytasks import _get_my_tasks_impl

# Get client
client = get_spira_client()

# Test a tool
result = _get_my_tasks_impl(client)
print(result)

# Check raw API response
tasks = client.make_spira_api_get_request("tasks")
print(f"Total tasks: {len(tasks)}")
print(f"First task: {tasks[0]}")
```

### Method 4: Install in Kiro

To test the MCP server within Kiro:

1. Create/edit `~/.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "inflectra-spira": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/simonbor/git/mcp-server-spira",
        "run",
        "main.py"
      ],
      "env": {
        "INFLECTRA_SPIRA_BASE_URL": "https://your-instance.spiraservice.net",
        "INFLECTRA_SPIRA_USERNAME": "your-username",
        "INFLECTRA_SPIRA_API_KEY": "your-api-key"
      },
      "disabled": false,
      "autoApprove": [
        "get_my_tasks",
        "get_my_incidents",
        "get_products"
      ]
    }
  }
}
```

2. Restart Kiro

3. Test with prompts like:
   - "Get my assigned tasks from Spira"
   - "Show me my incidents"
   - "List all products"

## Troubleshooting

### Connection Issues

```bash
# Test connection manually
python -c "
from mcp_server_spira.features.common import get_spira_client
client = get_spira_client()
products = client.make_spira_api_get_request('projects')
print(f'Connected! Found {len(products)} products')
"
```

### Common Errors

**Error: "Unable to read file '.env'"**
- Solution: Create the `.env` file with your credentials

**Error: "Authentication failed"**
- Check your API key is active in Spira user profile
- Verify the base URL is correct (no trailing slash)
- Ensure username is correct

**Error: "Module not found"**
- Solution: Install in editable mode: `pip install -e .`

**Tests skipped with "Requires Spira credentials"**
- Solution: Create `.env` file with valid credentials

## What to Look For

When testing the **current** implementation (before Task 4):

### Expected Behavior ✅
- Returns markdown formatted strings
- Truncates at 25 items without warning
- No pagination parameters
- Generic error messages like "There was a problem using this tool"

### After Task 4 (Future) ✅
- Returns JSON strings
- Has `limit` and `offset` parameters
- Includes pagination metadata
- Structured error responses with error codes

## Next Steps

After verifying the current implementation works:

1. **Proceed with Task 4**: Convert tools to JSON with pagination
2. **Test incrementally**: After each tool is converted, test it
3. **Compare behavior**: Use these same tests to verify the new implementation

## Questions?

If you encounter issues:
1. Check the `.env` file is correct
2. Verify you can access Spira in a browser
3. Check the API key is active
4. Review the error messages in the test output
