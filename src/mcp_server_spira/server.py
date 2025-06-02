"""
Inflectra Spira MCP Server

A simple MCP server that exposes Inflectra Spira capabilities.
"""
import argparse

from mcp.server.fastmcp import FastMCP

from mcp_server_spira.features import register_all
from mcp_server_spira.utils import register_all_prompts

# Create a FastMCP server instance with a name
mcp = FastMCP("Inflectra Spira")

# Register all features
register_all(mcp)
register_all_prompts(mcp)

def main():
    """Entry point for the command-line script."""
    parser = argparse.ArgumentParser(
        description="Run the Inflectra Spira MCP server")
    # Add more command-line arguments as needed
    
    parser.parse_args()  # Store args if needed later
    
    # Start the server
    mcp.run()

if __name__ == "__main__":
    main()