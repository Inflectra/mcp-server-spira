"""Risk type config — extracted from RemoteRiskType OpenAPI schema."""

from mcp_server_spira.models import TemplateMetadataFieldConfig

RISK_TYPE_CONFIG = TemplateMetadataFieldConfig(
    active_field="IsActive",
    id_field="RiskTypeId",
    endpoint="project-templates/{template_id}/risks/types",
    include_fields=(
        "IsDefault",
        "Position",
        "WorkflowId",
    ),
)
