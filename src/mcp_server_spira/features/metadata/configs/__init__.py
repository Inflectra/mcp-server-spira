"""Config aggregator — imports all type field configs.

Validates every config at import time.
"""

from mcp_server_spira.models import TemplateMetadataFieldConfig

from .document_status import DOCUMENT_STATUS_CONFIG
from .document_type import DOCUMENT_TYPE_CONFIG
from .incident_priority import INCIDENT_PRIORITY_CONFIG
from .incident_severity import INCIDENT_SEVERITY_CONFIG
from .incident_status import INCIDENT_STATUS_CONFIG
from .incident_type import INCIDENT_TYPE_CONFIG
from .release_status import RELEASE_STATUS_CONFIG
from .requirement_importance import REQUIREMENT_IMPORTANCE_CONFIG
from .requirement_status import REQUIREMENT_STATUS_CONFIG
from .requirement_type import REQUIREMENT_TYPE_CONFIG
from .risk_impact import RISK_IMPACT_CONFIG
from .risk_probability import RISK_PROBABILITY_CONFIG
from .risk_status import RISK_STATUS_CONFIG
from .risk_type import RISK_TYPE_CONFIG
from .task_priority import TASK_PRIORITY_CONFIG
from .task_status import TASK_STATUS_CONFIG
from .task_type import TASK_TYPE_CONFIG
from .test_case_priority import TEST_CASE_PRIORITY_CONFIG
from .test_case_status import TEST_CASE_STATUS_CONFIG
from .test_case_type import TEST_CASE_TYPE_CONFIG

TYPE_FIELD_CONFIGS: dict[str, TemplateMetadataFieldConfig] = {
    "Requirement": REQUIREMENT_TYPE_CONFIG,
    "Test Case": TEST_CASE_TYPE_CONFIG,
    "Task": TASK_TYPE_CONFIG,
    "Risk": RISK_TYPE_CONFIG,
    "Incident": INCIDENT_TYPE_CONFIG,
    "Document": DOCUMENT_TYPE_CONFIG,
}

STATUS_FIELD_CONFIGS: dict[str, TemplateMetadataFieldConfig] = {
    "Requirement": REQUIREMENT_STATUS_CONFIG,
    "Incident": INCIDENT_STATUS_CONFIG,
    "Task": TASK_STATUS_CONFIG,
    "Risk": RISK_STATUS_CONFIG,
    "Release": RELEASE_STATUS_CONFIG,
    "Test Case": TEST_CASE_STATUS_CONFIG,
    "Document": DOCUMENT_STATUS_CONFIG,
}

PRIORITY_FIELD_CONFIGS: dict[str, TemplateMetadataFieldConfig] = {
    "Incident": INCIDENT_PRIORITY_CONFIG,
    "Task": TASK_PRIORITY_CONFIG,
    "Test Case": TEST_CASE_PRIORITY_CONFIG,
    "Requirement": REQUIREMENT_IMPORTANCE_CONFIG,
}

SEVERITY_FIELD_CONFIGS: dict[str, TemplateMetadataFieldConfig] = {
    "Incident": INCIDENT_SEVERITY_CONFIG,
}

IMPORTANCE_FIELD_CONFIGS: dict[str, TemplateMetadataFieldConfig] = {
    "Requirement": REQUIREMENT_IMPORTANCE_CONFIG,
}

PROBABILITY_FIELD_CONFIGS: dict[str, TemplateMetadataFieldConfig] = {
    "Risk": RISK_PROBABILITY_CONFIG,
}

IMPACT_FIELD_CONFIGS: dict[str, TemplateMetadataFieldConfig] = {
    "Risk": RISK_IMPACT_CONFIG,
}

# Import-time validation — fail at startup, not runtime.
_ALL_AGGREGATOR_DICTS: dict[str, dict[str, TemplateMetadataFieldConfig]] = {
    "TYPE_FIELD_CONFIGS": TYPE_FIELD_CONFIGS,
    "STATUS_FIELD_CONFIGS": STATUS_FIELD_CONFIGS,
    "PRIORITY_FIELD_CONFIGS": PRIORITY_FIELD_CONFIGS,
    "SEVERITY_FIELD_CONFIGS": SEVERITY_FIELD_CONFIGS,
    "IMPORTANCE_FIELD_CONFIGS": IMPORTANCE_FIELD_CONFIGS,
    "PROBABILITY_FIELD_CONFIGS": PROBABILITY_FIELD_CONFIGS,
    "IMPACT_FIELD_CONFIGS": IMPACT_FIELD_CONFIGS,
}

_all_errors: list[str] = []
for _dict_name, _configs in _ALL_AGGREGATOR_DICTS.items():
    for _name, _cfg in _configs.items():
        _errs = _cfg.validate()
        if _errs:
            _all_errors.extend(f"{_dict_name}[{_name}]: {e}" for e in _errs)
if _all_errors:
    raise ValueError("TemplateMetadataFieldConfig validation failed:\n" + "\n".join(_all_errors))
