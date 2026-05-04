"""Test case priority config — from RemoteTestCasePriority schema."""

from mcp_server_spira.models import TemplateMetadataFieldConfig

TEST_CASE_PRIORITY_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="PriorityId",
    endpoint="project-templates/{template_id}/test-cases/priorities",
    include_fields=("Color", "Score"),
)
