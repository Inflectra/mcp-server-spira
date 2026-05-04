"""Task type config — extracted from RemoteTaskType OpenAPI schema."""

from mcp_server_spira.models import TemplateMetadataFieldConfig

TASK_TYPE_CONFIG = TemplateMetadataFieldConfig(
    active_field="IsActive",
    id_field="TaskTypeId",
    endpoint="project-templates/{template_id}/tasks/types",
    include_fields=(
        "IsCodeReview",
        "IsDefault",
        "IsPullRequest",
        "Position",
        "WorkflowId",
    ),
)
