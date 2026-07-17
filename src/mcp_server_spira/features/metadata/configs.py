"""Template metadata field configs — all sections in one file.

Each config defines how to fetch and parse one metadata section from the
Spira REST API.  Grouped by section type (types, statuses, priorities, etc.).

Validates every config at import time — fail at startup, not runtime.
"""

from mcp_server_spira.models import TemplateMetadataFieldConfig

# ─── Types ────────────────────────────────────────────────────────────────────

REQUIREMENT_TYPE_CONFIG = TemplateMetadataFieldConfig(
    active_field="IsActive",
    id_field="RequirementTypeId",
    endpoint="project-templates/{template_id}/requirements/types",
    include_fields=(
        "IsDefault",
        "IsSteps",
        "WorkflowId",
    ),
)

TEST_CASE_TYPE_CONFIG = TemplateMetadataFieldConfig(
    active_field="IsActive",
    id_field="TestCaseTypeId",
    endpoint="project-templates/{template_id}/test-cases/types",
    include_fields=(
        "IsBdd",
        "IsDefault",
        "IsExploratory",
        "Position",
        "WorkflowId",
    ),
)

TASK_TYPE_CONFIG = TemplateMetadataFieldConfig(
    active_field="IsActive",
    id_field="TaskTypeId",
    endpoint="project-templates/{template_id}/tasks/types",
    include_fields=(
        "IsCodeReview",
        "IsDefault",
        "IsPullRequest",
        "Position",
        "WorkflowId",
    ),
)

RISK_TYPE_CONFIG = TemplateMetadataFieldConfig(
    active_field="IsActive",
    id_field="RiskTypeId",
    endpoint="project-templates/{template_id}/risks/types",
    include_fields=(
        "IsDefault",
        "Position",
        "WorkflowId",
    ),
)

INCIDENT_TYPE_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="IncidentTypeId",
    endpoint="project-templates/{template_id}/incidents/types",
    include_fields=(
        "Default",
        "Issue",
        "Risk",
        "WorkflowId",
    ),
)

DOCUMENT_TYPE_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="DocumentTypeId",
    endpoint="project-templates/{template_id}/document-types?active_only=true",
    include_fields=(
        "Default",
        "Description",
        "ProjectTemplateId",
    ),
)

RELEASE_TYPE_CONFIG = TemplateMetadataFieldConfig(
    endpoint="project-templates/{template_id}/releases/types",
    id_field="ReleaseTypeId",
    active_field="Active",
    include_fields=("WorkflowId", "Position"),
)

# ─── Statuses ─────────────────────────────────────────────────────────────────

REQUIREMENT_STATUS_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="RequirementStatusId",
    endpoint="project-templates/{template_id}/requirements/statuses",
    include_fields=("Position",),
)

INCIDENT_STATUS_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="IncidentStatusId",
    endpoint="project-templates/{template_id}/incidents/statuses",
    include_fields=("Open",),
)

TASK_STATUS_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="TaskStatusId",
    endpoint="project-templates/{template_id}/tasks/statuses",
    include_fields=("Position",),
)

RISK_STATUS_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="RiskStatusId",
    endpoint="project-templates/{template_id}/risks/statuses",
    include_fields=(
        "Position",
        "Open",
        "Default",
    ),
)

RELEASE_STATUS_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="ReleaseStatusId",
    endpoint="project-templates/{template_id}/releases/statuses",
    include_fields=("Position",),
)

TEST_CASE_STATUS_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="TestCaseStatusId",
    endpoint="project-templates/{template_id}/test-cases/statuses",
    include_fields=("Position",),
)

DOCUMENT_STATUS_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="DocumentStatusId",
    endpoint="project-templates/{template_id}/document-statuses",
    include_fields=(
        "Default",
        "Open",
        "Position",
        "ProjectTemplateId",
    ),
)

# ─── Priorities ───────────────────────────────────────────────────────────────

INCIDENT_PRIORITY_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="PriorityId",
    endpoint="project-templates/{template_id}/incidents/priorities",
    include_fields=("Color", "Score"),
)

TASK_PRIORITY_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="PriorityId",
    endpoint="project-templates/{template_id}/tasks/priorities",
    include_fields=("Color", "Score"),
)

TEST_CASE_PRIORITY_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="PriorityId",
    endpoint="project-templates/{template_id}/test-cases/priorities",
    include_fields=("Color", "Score"),
)

# ─── Severity ─────────────────────────────────────────────────────────────────

INCIDENT_SEVERITY_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="SeverityId",
    endpoint="project-templates/{template_id}/incidents/severities",
    include_fields=("Color", "Score"),
)

# ─── Importance ───────────────────────────────────────────────────────────────

REQUIREMENT_IMPORTANCE_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="ImportanceId",
    endpoint="project-templates/{template_id}/requirements/importances",
    include_fields=("Color", "Score"),
)

# ─── Probability ──────────────────────────────────────────────────────────────

RISK_PROBABILITY_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="RiskProbabilityId",
    endpoint="project-templates/{template_id}/risks/probabilities",
    include_fields=("Position", "Color", "Score"),
)

# ─── Impact ───────────────────────────────────────────────────────────────────

RISK_IMPACT_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="RiskImpactId",
    endpoint="project-templates/{template_id}/risks/impacts",
    include_fields=("Position", "Color", "Score"),
)

# ─── Aggregator dicts ─────────────────────────────────────────────────────────

TYPE_FIELD_CONFIGS: dict[str, TemplateMetadataFieldConfig] = {
    "Requirement": REQUIREMENT_TYPE_CONFIG,
    "Test Case": TEST_CASE_TYPE_CONFIG,
    "Task": TASK_TYPE_CONFIG,
    "Risk": RISK_TYPE_CONFIG,
    "Incident": INCIDENT_TYPE_CONFIG,
    "Document": DOCUMENT_TYPE_CONFIG,
    "Release": RELEASE_TYPE_CONFIG,
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

# ─── Import-time validation ───────────────────────────────────────────────────

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
