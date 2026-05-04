"""Config aggregator — imports all artifact configs.

Validates every config at import time.
"""

from mcp_server_spira.models import ArtifactConfig

from .automation_host import AUTOMATION_HOST_CONFIG
from .build import BUILD_CONFIG
from .capability import CAPABILITY_CONFIG
from .document import DOCUMENT_CONFIG
from .incident import INCIDENT_CONFIG
from .milestone import MILESTONE_CONFIG
from .release import RELEASE_CONFIG
from .requirement import REQUIREMENT_CONFIG
from .risk import RISK_CONFIG
from .task import TASK_CONFIG
from .test_case import TEST_CASE_CONFIG
from .test_run import TEST_RUN_CONFIG
from .test_set import TEST_SET_CONFIG

ARTIFACT_CONFIG: dict[str, ArtifactConfig] = {
    cfg.artifact_type: cfg
    for cfg in [
        INCIDENT_CONFIG,
        TASK_CONFIG,
        TEST_CASE_CONFIG,
        REQUIREMENT_CONFIG,
        RISK_CONFIG,
        RELEASE_CONFIG,
        TEST_SET_CONFIG,
        TEST_RUN_CONFIG,
        AUTOMATION_HOST_CONFIG,
        BUILD_CONFIG,
        DOCUMENT_CONFIG,
        CAPABILITY_CONFIG,
        MILESTONE_CONFIG,
    ]
}

VALID_ARTIFACT_TYPES: tuple[str, ...] = tuple(ARTIFACT_CONFIG.keys())

# Import-time validation — fail at startup, not runtime.
_all_errors: list[str] = []
for _name, _cfg in ARTIFACT_CONFIG.items():
    _errs = _cfg.validate()
    if _errs:
        _all_errors.extend(f"{_name}: {e}" for e in _errs)
if _all_errors:
    raise ValueError("ArtifactConfig validation failed:\n" + "\n".join(_all_errors))
