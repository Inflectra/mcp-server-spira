"""Incident status config — extracted from RemoteIncidentStatus OpenAPI schema."""

from mcp_server_spira.models import TemplateMetadataFieldConfig

INCIDENT_STATUS_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="IncidentStatusId",
    endpoint="project-templates/{template_id}/incidents/statuses",
    include_fields=("Open",),
)
