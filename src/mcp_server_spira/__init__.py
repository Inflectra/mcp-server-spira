"""
MCP Inflectra Spira Server - A Model Context Protocol server for Spira (SpiraTest, SpiraTeam and SpiraPlan)
integration.
"""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("mcp-server-spira")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"