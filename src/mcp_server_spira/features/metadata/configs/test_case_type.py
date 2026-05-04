"""Test Case type config — extracted from RemoteTestCaseType OpenAPI schema."""

from mcp_server_spira.models import TemplateMetadataFieldConfig

TEST_CASE_TYPE_CONFIG = TemplateMetadataFieldConfig(
    active_field="IsActive",
    id_field="TestCaseTypeId",
    endpoint="project-templates/{template_id}/test-cases/types",
    include_fields=(
        "IsBdd",
        "IsDefault",
        "IsExploratory",
        "Position",
        "WorkflowId",
    ),
)
