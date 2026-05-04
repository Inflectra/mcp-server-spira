"""Incident type config — extracted from RemoteIncidentType OpenAPI schema."""

from mcp_server_spira.models import TemplateMetadataFieldConfig

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
