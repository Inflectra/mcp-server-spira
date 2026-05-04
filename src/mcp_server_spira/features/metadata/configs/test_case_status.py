"""Test case status config — extracted from RemoteTestCaseStatus OpenAPI schema."""

from mcp_server_spira.models import TemplateMetadataFieldConfig

TEST_CASE_STATUS_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="TestCaseStatusId",
    endpoint="project-templates/{template_id}/test-cases/statuses",
    include_fields=("Position",),
)
