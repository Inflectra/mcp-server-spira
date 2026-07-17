"""Association tools for Spira artifacts.

Provides create_association tool for linking artifacts via general
associations (related-to, depends-on) or coverage mappings.
"""

from typing import Annotated

from pydantic import WithJsonSchema

from mcp_server_spira.constants import VALID_ASSOCIATION_PAIRS

__all__ = [
    "ASSOCIABLE_ARTIFACT_TYPES",
    "AssociableArtifactType",
    "SourceArtifactType",
    "DestArtifactType",
    "SOURCE_ARTIFACT_TYPES",
    "DEST_ARTIFACT_TYPES",
    "VALID_ASSOCIATION_TYPES",
    "VALID_COVERAGE_PAIRS",
    "register_tools",
]

# Valid association_type values for the create_association tool.
VALID_ASSOCIATION_TYPES: tuple[str, ...] = ("related-to", "depends-on", "coverage")

# Valid coverage pairs: (source_type, dest_type) -> dispatch key.
# Used by _create_association_impl to route coverage creation to the correct endpoint.
VALID_COVERAGE_PAIRS: dict[tuple[str, str], str] = {
    ("requirement", "test_case"): "req_tc",
    ("requirement", "test_step"): "req_ts",
    ("release", "test_case"): "rel_tc",
    ("test_case", "requirement"): "tc_req",  # reversed internally to req_tc
}

# Union of all artifact types appearing in VALID_ASSOCIATION_PAIRS (keys + all
# frozenset values). Kept for backward compatibility.
_all_pair_types: set[str] = set(VALID_ASSOCIATION_PAIRS.keys())
for _dests in VALID_ASSOCIATION_PAIRS.values():
    _all_pair_types.update(_dests)

ASSOCIABLE_ARTIFACT_TYPES: tuple[str, ...] = tuple(sorted(_all_pair_types))

# Separate source and dest types for accurate schema enums.
# Sources: types that can appear as the "from" side of an association or coverage.
_source_types: set[str] = set(VALID_ASSOCIATION_PAIRS.keys())
_source_types.update(s for s, _d in VALID_COVERAGE_PAIRS)

# Dests: types that can appear as the "to" side of an association or coverage.
_dest_types: set[str] = set()
for _d in VALID_ASSOCIATION_PAIRS.values():
    _dest_types.update(_d)
_dest_types.update(d for _s, d in VALID_COVERAGE_PAIRS)

SOURCE_ARTIFACT_TYPES: tuple[str, ...] = tuple(sorted(_source_types))
DEST_ARTIFACT_TYPES: tuple[str, ...] = tuple(sorted(_dest_types))

# Type hint for tool signatures -- advertises valid values in the JSON schema
# (so the LLM sees them in tools/list) but accepts any string at Pydantic
# validation time. Actual validation happens in _impl.
AssociableArtifactType = Annotated[
    str,
    WithJsonSchema({"type": "string", "enum": list(ASSOCIABLE_ARTIFACT_TYPES)}),
]

# Separate annotated types for source vs dest -- gives accurate schema enums
SourceArtifactType = Annotated[
    str,
    WithJsonSchema({"type": "string", "enum": list(SOURCE_ARTIFACT_TYPES)}),
]

DestArtifactType = Annotated[
    str,
    WithJsonSchema({"type": "string", "enum": list(DEST_ARTIFACT_TYPES)}),
]


def register_tools(mcp) -> None:
    """Register all association tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    from mcp_server_spira.features.associations.tools import create

    create.register_tools(mcp)
