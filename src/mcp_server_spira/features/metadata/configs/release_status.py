"""Release status config — extracted from RemoteReleaseStatus OpenAPI schema."""

from mcp_server_spira.models import TemplateMetadataFieldConfig

RELEASE_STATUS_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="ReleaseStatusId",
    endpoint="project-templates/{template_id}/releases/statuses",
    include_fields=("Position",),
)
