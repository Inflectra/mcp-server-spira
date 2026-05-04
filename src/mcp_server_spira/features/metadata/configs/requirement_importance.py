"""Requirement importance config — from RemoteRequirementImportance schema."""

from mcp_server_spira.models import TemplateMetadataFieldConfig

REQUIREMENT_IMPORTANCE_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="ImportanceId",
    endpoint="project-templates/{template_id}/requirements/importances",
    include_fields=("Color", "Score"),
)
