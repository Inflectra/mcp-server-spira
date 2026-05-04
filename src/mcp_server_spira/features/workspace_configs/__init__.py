"""Workspace configs — central registry keyed by workspace_type."""

from mcp_server_spira.models import WorkspaceConfig

from .product import PRODUCT_CONFIG
from .product_template import PRODUCT_TEMPLATE_CONFIG
from .program import PROGRAM_CONFIG

WORKSPACE_CONFIG: dict[str, WorkspaceConfig] = {
    PRODUCT_CONFIG.workspace_type: PRODUCT_CONFIG,
    PROGRAM_CONFIG.workspace_type: PROGRAM_CONFIG,
    PRODUCT_TEMPLATE_CONFIG.workspace_type: PRODUCT_TEMPLATE_CONFIG,
}

WORKSPACE_TYPES: tuple[str, ...] = tuple(WORKSPACE_CONFIG.keys())

# Validate all configs at import time
for _wtype, _cfg in WORKSPACE_CONFIG.items():
    _errors = _cfg.validate()
    if _errors:
        msg = f"WorkspaceConfig '{_wtype}' failed validation: "
        msg += "; ".join(_errors)
        raise ValueError(msg)
