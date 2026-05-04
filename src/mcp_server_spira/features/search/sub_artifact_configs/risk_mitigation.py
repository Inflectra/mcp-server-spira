"""Risk Mitigation sub-artifact config — extracted from RemoteRiskMitigation OpenAPI schema."""

from mcp_server_spira.models import SubArtifactConfig

RISK_MITIGATION_CONFIG = SubArtifactConfig(
    sub_artifact_type="mitigations",
    endpoint_template="projects/{product_id}/risks/{artifact_id}/mitigations",
    parent_id_field="RiskId",
    openapi_schema="RemoteRiskMitigation",
    summary_fields=[
        "RiskMitigationId",
        "Position",
        "Description",
    ],
    all_fields=[
        "CreationDate",
        "Description",
        "LastUpdateDate",
        "Position",
        "ReviewDate",
        "RiskId",
        "RiskMitigationId",
    ],
    excluded_fields=[
        "ConcurrencyDate",
        "IsActive",
        "IsDeleted",
        "RiskGuid",
        "RiskMitigationGuid",
    ],
)
