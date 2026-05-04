"""Test Step sub-artifact config — extracted from RemoteTestStep OpenAPI schema."""

from mcp_server_spira.models import SubArtifactConfig

TEST_STEP_CONFIG = SubArtifactConfig(
    sub_artifact_type="test_steps",
    endpoint_template="projects/{product_id}/test-cases/{artifact_id}/test-steps",
    parent_id_field="TestCaseId",
    openapi_schema="RemoteTestStep",
    embedded_field="TestSteps",
    summary_fields=[
        "TestStepId",
        "Position",
        "Description",
        "ExpectedResult",
        "SampleData",
    ],
    all_fields=[
        "Description",
        "ExecutionStatusId",
        "ExpectedResult",
        "LastUpdateDate",
        "LinkedTestCaseId",
        "Position",
        "Precondition",
        "ProjectId",
        "SampleData",
        "Tags",
        "TestCaseId",
        "TestStepId",
    ],
    excluded_fields=[
        "ArtifactTypeId",
        "ConcurrencyDate",
        "CustomProperties",
        "Guid",
        "IsAttachments",
        "ProjectGuid",
        "TestCaseGuid",
    ],
)
