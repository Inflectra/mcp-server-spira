"""Requirement Step sub-artifact config — extracted from RemoteRequirementStep OpenAPI schema."""

from mcp_server_spira.models import SubArtifactConfig

REQUIREMENT_STEP_CONFIG = SubArtifactConfig(
    sub_artifact_type="steps",
    endpoint_template="projects/{product_id}/requirements/{artifact_id}/steps",
    parent_id_field="RequirementId",
    openapi_schema="RemoteRequirementStep",
    embedded_field="Steps",
    summary_fields=[
        "RequirementStepId",
        "Position",
        "Description",
    ],
    all_fields=[
        "CreationDate",
        "Description",
        "LastUpdateDate",
        "Position",
        "RequirementId",
        "RequirementStepId",
    ],
    excluded_fields=[
        "ConcurrencyDate",
        "Guid",
        "RequirementGuid",
    ],
)
