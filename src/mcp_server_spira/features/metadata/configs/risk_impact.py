"""Risk impact config — from RemoteRiskImpact schema."""

from mcp_server_spira.models import TemplateMetadataFieldConfig

RISK_IMPACT_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="RiskImpactId",
    endpoint="project-templates/{template_id}/risks/impacts",
    include_fields=("Position", "Color", "Score"),
)
