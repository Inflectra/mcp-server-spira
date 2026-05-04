"""
Inflectra Spira MCP Server

A simple MCP server that exposes Inflectra Spira capabilities.

Prerequisites: You need to have the following environment variables defined:

- INFLECTRA_SPIRA_BASE_URL: The base URL to your Spira instance (e.g. https://mycompany.spiraservice.net)
- INFLECTRA_SPIRA_USERNAME: The login to your Spira instance
- INFLECTRA_SPIRA_API_KEY: The API Key (RSS Token) for your Spira instance

"""

import argparse
import json
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from mcp_server_spira.config import load_config
from mcp_server_spira.features import register_all
from mcp_server_spira.features.context import (
    get_active_product_context,
    load_active_product_context,
)
from mcp_server_spira.utils import register_all_prompts


@asynccontextmanager
async def lifespan(server):
    load_config()
    await load_active_product_context()
    yield
    # shutdown: nothing needed


# Create a FastMCP server instance with a name
mcp = FastMCP(
    "inflectra-spira",
    lifespan=lifespan,
    instructions=(
        "Inflectra Spira MCP Server — project management, testing, and requirements tools.\n"
        "Hierarchy: Programs contain Products (projects). Products contain artifacts.\n"
        "\n"
        "TOOL SCOPES (prefix_action):\n"
        "  mywork_     — user's items via mywork_search_artifacts (task, incident, requirement, test_case, test_set)\n"
        "  product_    — product_search_artifacts (11 types), product_get_artifact, create_build, create_automated_test_run\n"
        "  program_    — requires program_id: program_search_artifacts (capability, milestone)\n"
        "  workspace_  — workspace_search, workspace_get for products, programs, product templates\n"
        "  template_   — template_get_metadata (types, custom_properties, statuses, priorities, severities, importances, probabilities, impacts)\n"
        "  get_artifact_schema — local-only field schema introspection\n"
        "\n"
        "10 tools total. "
        "If user asks for artifacts without context: use my_ for their own items, "
        "or call workspace_search(workspace_type='product') first to find a product_id."
    ),
)

# Register all features
register_all(mcp)
register_all_prompts(mcp)


@mcp.resource("spira://active-product")
def active_product_resource() -> str:
    ctx = get_active_product_context()
    if ctx is None:
        return json.dumps({"error": "No active product context available"})
    return json.dumps(ctx, indent=2)


def main():
    """Entry point for the command-line script."""
    parser = argparse.ArgumentParser(description="Run the Inflectra Spira MCP server")
    # Add more command-line arguments as needed

    parser.parse_args()  # Store args if needed later

    # Start the server
    mcp.run()


if __name__ == "__main__":
    main()
