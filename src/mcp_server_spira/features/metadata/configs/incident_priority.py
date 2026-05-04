"""Incident priority config — from RemoteIncidentPriority schema."""

from mcp_server_spira.models import TemplateMetadataFieldConfig

INCIDENT_PRIORITY_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="PriorityId",
    endpoint="project-templates/{template_id}/incidents/priorities",
    include_fields=("Color", "Score"),
)
