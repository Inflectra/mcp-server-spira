"""Unified search tools for Spira artifacts."""

from . import mywork, product, program


def register_tools(mcp) -> None:
    mywork.register_tools(mcp)
    product.register_tools(mcp)
    program.register_tools(mcp)
