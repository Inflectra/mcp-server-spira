"""Test Run artifact config — extracted from RemoteTestRun OpenAPI schema."""

from mcp_server_spira.models import ArtifactConfig

TEST_RUN_CONFIG = ArtifactConfig(
    artifact_type="test_run",
    workspace_type="product",
    search_endpoint="projects/{product_id}/test-runs/search",
    single_endpoint="projects/{product_id}/test-runs/{artifact_id}",
    description="Test runs (execution records) tracked in a Spira product.",
    # Normalised field mappings
    status_field="ExecutionStatusId",
    owner_field="TesterId",
    priority_field=None,
    release_field="ReleaseId",
    type_field="TestRunTypeId",
    summary_fields=[
        "ExecutionStatusId",
        "Name",
        "StartDate",
        "TestRunId",
        "TesterId",
    ],
    # all_fields: LLM-visible fields from RemoteTestRun schema
    all_fields=[
        "ActualDuration",
        "BuildId",
        "EndDate",
        "EstimatedDuration",
        "ExecutionStatusId",
        "Name",
        "ProjectId",
        "ReleaseId",
        "ReleaseVersionNumber",
        "StartDate",
        "Tags",
        "TestCaseId",
        "TestConfigurationId",
        "TestRunId",
        "TestRunTypeId",
        "TestSetId",
        "TestSetTestCaseId",
        "TesterId",
    ],
    # excluded_fields: valid OpenAPI fields hidden from LLM
    excluded_fields=[
        "ArtifactTypeId",
        "ConcurrencyDate",
        "CustomProperties",
        "Guid",
        "IsAttachments",
        "ProjectGuid",
        "ReleaseGuid",
        "TestCaseGuid",
        "TestSetGuid",
        "TesterGuid",
    ],
    supports_server_search=True,
    mywork_endpoint=None,
    search_query_params={
        "row_start": "starting_row",
        "row_count": "number_of_rows",
        "sort_field": "sort_field",
        "sort_direction": "sort_direction",
    },
    default_sort_field="LastUpdateDate",
    default_sort_direction="desc",
)
