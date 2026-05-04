"""Incident severity config — from RemoteIncidentSeverity schema."""

from mcp_server_spira.models import TemplateMetadataFieldConfig

INCIDENT_SEVERITY_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="SeverityId",
    endpoint="project-templates/{template_id}/incidents/severities",
    include_fields=("Color", "Score"),
)
