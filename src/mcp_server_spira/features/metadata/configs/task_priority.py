"""Task priority config — extracted from RemoteTaskPriority OpenAPI schema."""

from mcp_server_spira.models import TemplateMetadataFieldConfig

TASK_PRIORITY_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="PriorityId",
    endpoint="project-templates/{template_id}/tasks/priorities",
    include_fields=("Color", "Score"),
)
