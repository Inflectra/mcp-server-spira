"""Task status config — extracted from RemoteTaskStatus OpenAPI schema."""

from mcp_server_spira.models import TemplateMetadataFieldConfig

TASK_STATUS_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="TaskStatusId",
    endpoint="project-templates/{template_id}/tasks/statuses",
    include_fields=("Position",),
)
