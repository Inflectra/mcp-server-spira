"""
Inflectra Spira MCP Server

A simple MCP server that exposes Inflectra Spira capabilities.

Prerequisites: You need to have the following environment variables defined:

- INFLECTRA_SPIRA_BASE_URL: The base URL to your Spira instance (e.g. https://mycompany.spiraservice.net)
- INFLECTRA_SPIRA_USERNAME: The login to your Spira instance
- INFLECTRA_SPIRA_API_KEY: The API Key (RSS Token) for your Spira instance

"""

import argparse

from mcp.server.fastmcp import FastMCP

from mcp_server_spira.features import register_all
from mcp_server_spira.utils import register_all_prompts

# Create a FastMCP server instance with a name
mcp = FastMCP(
    "inflectra-spira",
    description=(
        "Inflectra Spira MCP Server — project management, testing, and requirements tools. "
        "Tools are prefixed by scope: "
        "my_ (current user's work items), "
        "product_ (product-scoped artifacts), "
        "program_ (program-scoped artifacts), "
        "template_ (product template configuration), "
        "system_ (instance-wide operations), "
        "spec_ (specification document structures), "
        "format_ (data display transformations). "
        "32 tools available."
    ),
)

# Register all features
register_all(mcp)
register_all_prompts(mcp)


def main():
    """Entry point for the command-line script."""
    parser = argparse.ArgumentParser(description="Run the Inflectra Spira MCP server")
    # Add more command-line arguments as needed

    parser.parse_args()  # Store args if needed later

    # Start the server
    mcp.run()


if __name__ == "__main__":
    main()
