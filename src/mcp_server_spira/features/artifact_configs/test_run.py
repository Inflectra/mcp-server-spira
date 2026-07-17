"""Test Run artifact config — extracted from OpenAPI schema."""

from mcp_server_spira.models import ArtifactConfig, FieldMeta, Visibility

# Short aliases for readability in field_metadata
S = Visibility.SUMMARY
V = Visibility.VISIBLE
E = Visibility.EXCLUDED

TEST_RUN_CONFIG = ArtifactConfig(
    artifact_type="test_run",
    workspace_type="product",
    search_endpoint="projects/{product_id}/test-runs/search",
    single_endpoint="projects/{product_id}/test-runs/{artifact_id}",
    description="Test runs (execution records) tracked in a Spira product.",
    field_metadata={
        "ExecutionStatusId": FieldMeta(
            "int", "The id of overall execution status for the test run", S
        ),
        "Name": FieldMeta("str", "The name of the test run (usually the same as the test case)", S),
        "StartDate": FieldMeta("datetime", "The date/time that the test execution was started", S),
        "TestRunId": FieldMeta("int", "The id of the test run", S),
        "TesterId": FieldMeta("int", "The id of the user that executed the test", S),
        "ActualDuration": FieldMeta(
            "int", "The actual duration of how long the test should take to execute (read-only)", V
        ),
        "BuildId": FieldMeta("int", "The id of the build that the test was executed against", V),
        "EndDate": FieldMeta("datetime", "The date/time that the test execution was completed", V),
        "EstimatedDuration": FieldMeta(
            "int",
            "The estimated duration of how long the test should take to execute (read-only)",
            V,
        ),
        "ProjectId": FieldMeta("int", "The id of the project that the artifact belongs to", V),
        "ReleaseId": FieldMeta(
            "int", "The id of the release that the test run should be reported against", V
        ),
        "ReleaseVersionNumber": FieldMeta(
            "str", "version number of the release this test run was run against.", V
        ),
        "Tags": FieldMeta(
            "str", "The list of meta-tags that should be associated with the artifact", V
        ),
        "TestCaseId": FieldMeta(
            "int", "The id of the test case that the test run is an instance of", V
        ),
        "TestConfigurationId": FieldMeta(
            "int", "The id of the specific test configuration that was used", V
        ),
        "TestRunTypeId": FieldMeta(
            "int", "The id of the type of test run (automated vs. manual)", V
        ),
        "TestSetId": FieldMeta(
            "int", "The id of the test set that the test run should be reported against", V
        ),
        "TestSetTestCaseId": FieldMeta(
            "int", "The id of the unique test case entry in the test set", V
        ),
        "ArtifactTypeId": FieldMeta("int", "The type of artifact that we have", E),
        "ConcurrencyDate": FieldMeta(
            "datetime",
            "The datetime used to track optimistic concurrency to prevent edit conflicts",
            E,
        ),
        "CustomProperties": FieldMeta(
            "list", "The list of associated custom properties/fields for this artifact", E
        ),
        "Guid": FieldMeta("str", "The unique identifier for the artifact", E),
        "IsAttachments": FieldMeta("bool", "Does this artifact have any attachments?", E),
        "ProjectGuid": FieldMeta("str", "The guid of the project that the artifact belongs to", E),
        "ReleaseGuid": FieldMeta("str", "The guid of the release", E),
        "TestCaseGuid": FieldMeta(
            "str", "The guid of the test case that the test run is an instance of", E
        ),
        "TestSetGuid": FieldMeta("str", "The guid of the test set", E),
        "TesterGuid": FieldMeta("str", "The guid of the tester.", E),
    },
    status_field="ExecutionStatusId",
    owner_field="TesterId",
    priority_field=None,
    release_field="ReleaseId",
    type_field="TestRunTypeId",
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
