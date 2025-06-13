# MCP Inflectra Spira Server Guide

This guide helps AI assistants implement and modify the MCP Inflectra Spira server codebase effectively.

## 1. Purpose & Overview

This MCP server enables AI assistants to interact with Inflectra Spira by:
- Connecting to the Inflectra Spira platform via its v7.0 REST API
- Exposing Inflectra Spira data (programs, products, releases, artifacts)
- Providing tools to create and modify Spira artifacts
- Including prompts for common workflows
- Using API Key authentication for secure interactions

## 2. Project Structure

```
mcp-server-spira/
├── docs/                      # API documentation
├── src/                       # Source code
│   └── mcp_server_spira/      # Main package
│       ├── features/          # Feature modules
│       │   ├── formatting.py  # Formatting helpers
│       │   ├── projects/      # Project management features
│       │   ├── programs/      # Program management features 
│       │   └── mywork/        # My assigned work features
│       │       ├── tools/     # My assigned work tools
│       │       └── common.py  # Common utilities for my assigned work
│       ├── utils/             # Shared utilities
│       ├── __init__.py        # Package initialization
│       └── server.py          # Main MCP server
├── tests/                     # Test suite
├── .env                       # Environment variables (not in repo)
├── CLAUDE.md                  # AI assistant guide
├── LICENSE                    # MIT License
├── pyproject.toml             # Project configuration
├── README.md                  # Project documentation
└── uv.lock                    # Package dependency locks
```

## 3. Core Concepts

### Inflectra Spira & MCP Integration

This project bridges two systems:

1. **Spira Objects**:
   - Workspaces (products, programs, portfolios)
   - Product artifacts
     - Requirements
     - Releases (including sprints, phases)
     - Test Cases
     - Test Steps
     - Test Sets
     - Test Runs
     - Tasks
     - Incidents
     - Risks
     - Risk mitigations
     - Documents
     - Code
     - Commits
   - Program artifacts
     - Capabilities
     - Milestones
   - Users

2. **MCP Components**:
   - **Tools**: Action performers that modify data (like POST/PUT/DELETE endpoints)
   - **Prompts**: Templates for guiding interactions

### Authentication

The project requires these environment variables:
- `INFLECTRA_SPIRA_BASE_URL`: The base URL for your instance of Spira
- `INFLECTRA_SPIRA_USERNAME`: The login name you use to access Spira
- `INFLECTRA_SPIRA_API_KEY`: The API Key (RSS Token) you use to access the Spira REST API

## 4. Implementation Guidelines

### Feature Structure

Each feature in the `features/` directory follows this pattern:
- `__init__.py`: Contains `register()` function to add the feature to the MCP server
- `common.py`: Shared utilities, exceptions, and helper functions
- `tools.py` or `tools/`: Functions or classes for operations (GET, POST, PUT, DELETE)

### Tool Implementation Pattern

When implementing a new tool:

1. Define a private implementation function with `_name_impl` that takes explicit client objects:
```python
def _get_data_impl(client, param1, param2):
    # Implementation
    return formatted_result
```

2. Create a public MCP tool function that handles client initialization and error handling:
```python
@mcp.tool()
def get_data(param1, param2):
    """
    Docstring following the standard pattern.
    
    Use this tool when you need to:
    - First use case
    - Second use case
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        Description of the return value format
    """
    try:
        client = get_client()
        return _get_data_impl(client, param1, param2)
    except Exception as e:
        return f"Error: {str(e)}"
```

3. Register the tool in the feature's `__init__.py` or `register_tools()` function

### Function Docstring Pattern

All public tools must have detailed docstrings following this pattern:

```python
"""
Brief description of what the tool does.

Use this tool when you need to:
- First use case with specific example
- Second use case with specific example
- Third use case with specific example

IMPORTANT: Any special considerations or warnings.

Args:
    param1: Description of first parameter
    param2: Description of second parameter
    
Returns:
    Detailed description of what is returned and in what format
"""
```

### Error Handling

The standard error handling pattern is:

```python
try:
    # Implementation code
except Exception as e:
    return f"Error doing operation: {str(e)}"
```

For specific errors, create custom exception classes in the feature's `common.py` file.

## 5. Common Code Patterns

### Client Initialization

```python
from mcp_server_spira.utils.spira_client import SpiraClient, get_client

def get_spira_client() -> SpiraClient:
    """
    Get the Spira API client.
    
    Returns:
        SpiraClient instance
        
    """
    # Get Spira client
    spira_client = get_client()        
    return spira_client
```

### Response Formatting

```python
def format_task(task) -> str:
    task_info = f"""
## Task [TK:{task['TaskId']}] - {task['Name']}
{'' if task['Description'] is None else task['Description']}
- **Status:** {task['TaskStatusName']}
- **Type:** {task['TaskTypeName']}
- **Priority:** {task['TaskPriorityName']}
- **Due Date:** {task['EndDate']}
"""
    return task_info
```


## 6. Adding New Features

To add a new feature:

1. Create a new directory under `features/` with the appropriate structure
2. Implement feature-specific client initialization in `common.py`
3. Create tools in `tools.py` or a `tools/` directory with specific operations
4. Register the feature with the server by updating `features/__init__.py`
5. Write tests for the new feature in the `tests/` directory

## 7. Technical Requirements

### Code Style
- PEP 8 conventions
- Type hints for all functions
- Google-style docstrings
- Small, focused functions
- Line length: 79 characters
- Import sorting: standard library → third-party → local

### Development Tools
- Install: `uv pip install -e ".[dev]"`
- Run server: `mcp dev src/mcp_server_spira/server.py`
- Run tests: `uv run pytest tests/`
- Format: `uv run ruff format .`
- Type check: `uv run pyright`

### Testing
- Write tests for all new functionality
- Test both successful and error cases
- Mock Inflectra Spira API responses for deterministic testing
- Place tests in the `tests/` directory with corresponding structure

## 8. Examples

### Example: Creating a New Tool

```python
# In src/mcp_server_spira/features/mywork/tools/mytasks.py

def _get_my_tasks_impl(spira_client) -> str:
    """
    Implementation of retrieving my assigned Spira tasks.

    Args:
        spira_client: The Inflectra Spira API client instance
                
    Returns:
        Formatted string containing the list of assigned tasks
    """
    # Get the list of open tasks for the current user
    tasks_url = "tasks"
    tasks = spira_client.make_spira_api_get_request(tasks_url)

    if not tasks:
        return "Unable to fetch task data for the current user."

    # Format the tasks into human readable data
    formatted_results = []
    for task in tasks[:25]:  # Only show first 25 tasks
        task_info = format_task(task)
        formatted_results.append(task_info)

    return "\n\n".join(formatted_results)

def register_tools(mcp) -> None:
    """
    Register my work tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_my_tasks() -> str:
        """
        Retrieves a list of the open tasks that are assigned to me
        
        Use this tool when you need to:
        - View the complete details of a specific task
        - Examine the current state, assigned user, and other properties
        - Get information about multiple tasks at once
        - Access the full description and selected fields of tasks
                    
        Returns:
            Formatted string containing comprehensive information for the
            requested list of tasks, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_my_tasks_impl(spira_client)
        except Exception as e:
            return f"Error: {str(e)}"
        
```

### Example: Registering a New Feature

```python
# In src/mcp_server_spira/features/mywork/tools/__init__.py

from mcp_server_spira.features.mywork.tools import (
    mytasks,myincidents,myrequirements,mytestcases,mytestsets
)

def register_tools(mcp) -> None:
    """
    Register all work item tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    mytasks.register_tools(mcp)  # Add the new tool
    myincidents.register_tools(mcp)
    myrequirements.register_tools(mcp)
    mytestcases.register_tools(mcp)
    mytestsets.register_tools(mcp)

# In src/mcp_server_spira/features/__init__.py

from mcp_server_spira.features import mywork


def register_all(mcp):
    """
    Register all features with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """
    mywork.register(mcp)   # Add the new feature

```