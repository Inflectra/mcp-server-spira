"""Requirement Step sub-artifact config — extracted from RemoteRequirementStep OpenAPI schema."""

from mcp_server_spira.models import SubArtifactConfig

REQUIREMENT_STEP_CONFIG = SubArtifactConfig(
    sub_artifact_type="steps",
    endpoint_template="projects/{product_id}/requirements/{artifact_id}/steps",
    parent_id_field="RequirementId",
    openapi_schema="RemoteRequirementStep",
    embedded_field="Steps",
    create_endpoint=(
        "projects/{product_id}/requirements/{parent_id}/steps"
        "?existing_requirement_step_id=null&creator_id={creator_id}"
    ),
    id_field="RequirementStepId",
    id_prefix="RS",
    required_fields=["Description"],
    writable_fields=[
        "Description",
        "Position",
    ],
    single_endpoint=("projects/{product_id}/requirements/{parent_id}/steps/{artifact_id}"),
    update_endpoint=("projects/{product_id}/requirements/{parent_id}/steps"),
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
