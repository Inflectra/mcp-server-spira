"""Requirement type config — extracted from RemoteRequirementType OpenAPI schema."""

from mcp_server_spira.models import TemplateMetadataFieldConfig

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
