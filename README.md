# MCP Inflectra Spira Server
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

## Getting Started

### Prerequisites

- Python 3.10+
- Inflectra Spira cloud account with appropriate permissions
- Username and active API Key (RSS Token) for this instance

### Installation

```bash
# Clone the repository
git clone https://github.com/Inflectra/mcp-server-spira.git
cd mcp-server-spira

# Install in development mode
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

### Running the Server

```bash
# Development mode with the MCP Inspector
mcp dev src/mcp_server_spira/server.py

# Production mode using shell / command line
python -m mcp_server_spira

# Install in Claude Desktop
mcp install src/mcp_server_spira/server.py --name "Inflectra Spira Server"
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

## Development

The project is structured into feature modules, each implementing specific Inflectra Spira capabilities:

- `features/mywork`: Accessing a user's assigned artifacts and updating their status/progress
- `features/projects`: Project management capabilities
- `features/programs`: Program management features
- `utils`: Common utilities and client initialization

For more information on development, see the [CLAUDE.md](CLAUDE.md) file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- Uses [Inflectra Spira v7.0 REST API](https://spiradoc.inflectra.com/Developers/API-Overview/)