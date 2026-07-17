"""Sub-artifact config aggregator — imports all sub-artifact configs.

Validates every config at import time.
"""

from mcp_server_spira.models import SubArtifactConfig

from .requirement_step import REQUIREMENT_STEP_CONFIG
from .risk_mitigation import RISK_MITIGATION_CONFIG
from .test_step import TEST_STEP_CONFIG

SUB_ARTIFACT_CONFIG: dict[str, SubArtifactConfig] = {
    cfg.sub_artifact_type: cfg
    for cfg in [
        TEST_STEP_CONFIG,
        RISK_MITIGATION_CONFIG,
        REQUIREMENT_STEP_CONFIG,
    ]
}

# Import-time validation — fail at startup, not runtime.
_all_errors: list[str] = []
for _name, _cfg in SUB_ARTIFACT_CONFIG.items():
    _errs = _cfg.validate()
    if _errs:
        _all_errors.extend(f"{_name}: {e}" for e in _errs)
if _all_errors:
    raise ValueError("SubArtifactConfig validation failed:\n" + "\n".join(_all_errors))

# --- Shared constants for create/update validation ---
# Tool-facing singular names for sub-artifact types.
SUB_ARTIFACT_TYPES: tuple[str, ...] = (
    "test_step",
    "mitigation",
    "requirement_step",
)

# Mapping from tool-facing singular names to SUB_ARTIFACT_CONFIG dict keys.
SUB_ARTIFACT_TYPE_TO_CONFIG_KEY: dict[str, str] = {
    "test_step": "test_steps",
    "mitigation": "mitigations",
    "requirement_step": "steps",
}
