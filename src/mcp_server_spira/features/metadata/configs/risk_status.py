"""Risk status config — extracted from RemoteRiskStatus OpenAPI schema."""

from mcp_server_spira.models import TemplateMetadataFieldConfig

RISK_STATUS_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="RiskStatusId",
    endpoint="project-templates/{template_id}/risks/statuses",
    include_fields=(
        "Position",
        "Open",
        "Default",
    ),
)
