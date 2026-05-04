"""Risk probability config — from RemoteRiskProbability schema."""

from mcp_server_spira.models import TemplateMetadataFieldConfig

RISK_PROBABILITY_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="RiskProbabilityId",
    endpoint="project-templates/{template_id}/risks/probabilities",
    include_fields=("Position", "Color", "Score"),
)
