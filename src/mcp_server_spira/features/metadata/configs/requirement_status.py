"""Requirement status config — extracted from RemoteRequirementStatus OpenAPI schema."""

from mcp_server_spira.models import TemplateMetadataFieldConfig

REQUIREMENT_STATUS_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="RequirementStatusId",
    endpoint="project-templates/{template_id}/requirements/statuses",
    include_fields=("Position",),
)
