"""Test Set artifact config — extracted from OpenAPI schema."""

from mcp_server_spira.models import ArtifactConfig, FieldMeta, Visibility

# Short aliases for readability in field_metadata
S = Visibility.SUMMARY
V = Visibility.VISIBLE
E = Visibility.EXCLUDED

TEST_SET_CONFIG = ArtifactConfig(
    artifact_type="test_set",
    workspace_type="product",
    search_endpoint="projects/{product_id}/test-sets/search",
    single_endpoint="projects/{product_id}/test-sets/{artifact_id}",
    description="Test sets (collections of test cases) tracked in a Spira product.",
    field_metadata={
        "Name": FieldMeta("str", "The name of the test set", S),
        "OwnerName": FieldMeta(
            "str", "The display name of the user that the test set is assigned-to", S
        ),
        "TestSetId": FieldMeta("int", "The id of the test set", S),
        "TestSetStatusName": FieldMeta("str", "The display name of the status of the test set", S),
        "ActualDuration": FieldMeta(
            "int", "The total actual duration for all the test cases in this set", V
        ),
        "AutomationHostId": FieldMeta(
            "int", "The id of the automation host the test set is assigned-to", V
        ),
        "CountBlocked": FieldMeta("int", "How many blocked test cases are in the set", V),
        "CountCaution": FieldMeta("int", "How many cautioned test cases are in the set", V),
        "CountFailed": FieldMeta("int", "How many failed test cases are in the set", V),
        "CountNotApplicable": FieldMeta(
            "int", "How many test cases in the set are not applicable", V
        ),
        "CountNotRun": FieldMeta("int", "How many test cases in the set have not been run", V),
        "CountPassed": FieldMeta("int", "How many passed test cases are in the set", V),
        "CreationDate": FieldMeta("datetime", "The date the test set was originally created", V),
        "CreatorId": FieldMeta("int", "The id of the user who created the test set", V),
        "CreatorName": FieldMeta(
            "str", "The display name of the user that created the test set", V
        ),
        "Description": FieldMeta("str", "The detailed description of the test set", V),
        "EstimatedDuration": FieldMeta(
            "int", "The total estimated duration for all the test cases in this set", V
        ),
        "ExecutionDate": FieldMeta(
            "datetime", "The date that the test set was last executed by a tester", V
        ),
        "LastUpdateDate": FieldMeta("datetime", "The date the test set was last modified", V),
        "OwnerId": FieldMeta("int", "The id of the user who the test set is assigned-to", V),
        "PlannedDate": FieldMeta(
            "datetime", "The date that the test set needs is planned to be executed on", V
        ),
        "ProjectId": FieldMeta("int", "The id of the project that the artifact belongs to", V),
        "ProjectName": FieldMeta(
            "str", "The display name of the project that the test set belongs to", V
        ),
        "RecurrenceId": FieldMeta(
            "int", "The id of the recurrence pattern the test set is scheduled for", V
        ),
        "RecurrenceName": FieldMeta("str", "The display name of the recurrence pattern", V),
        "ReleaseId": FieldMeta("int", "The id of the release that the test set is assigned-to", V),
        "ReleaseVersionNumber": FieldMeta(
            "str", "The version number of the release the test set is scheduled for", V
        ),
        "Tags": FieldMeta(
            "str", "The list of meta-tags that should be associated with the artifact", V
        ),
        "TestConfigurationSetId": FieldMeta(
            "int", "The id of any test configuration set to be used with this test set", V
        ),
        "TestRunTypeId": FieldMeta(
            "int", "The id of the type of test set (1 = Manual, 2 = Automated)", V
        ),
        "TestSetFolderId": FieldMeta(
            "int", "The ID of the test set folder this test set belongs to (NULL = root)", V
        ),
        "TestSetStatusId": FieldMeta("int", "The id of the test set's status", V),
        "ArtifactTypeId": FieldMeta("int", "The type of artifact that we have", E),
        "BuildExecuteTimeInterval": FieldMeta(
            "int",
            "The interval between a build finishing and the test being execution (if auto-scheduled)",
            E,
        ),
        "ConcurrencyDate": FieldMeta(
            "datetime",
            "The datetime used to track optimistic concurrency to prevent edit conflicts",
            E,
        ),
        "CreatorGuid": FieldMeta("str", "The guid of the creator.", E),
        "CustomProperties": FieldMeta(
            "list", "The list of associated custom properties/fields for this artifact", E
        ),
        "DynamicQuery": FieldMeta("str", "The underlying query if this is a dynamic test set", E),
        "Guid": FieldMeta("str", "The unique identifier for the artifact", E),
        "IndentLevel": FieldMeta("str", "(Not used in this version of the API)", E),
        "IsAttachments": FieldMeta("bool", "Does this artifact have any attachments?", E),
        "IsAutoScheduled": FieldMeta(
            "bool",
            "Is this test set auto-scheduled when a build associated with the release runs",
            E,
        ),
        "IsDynamic": FieldMeta("bool", "Is this a dynamic test set", E),
        "OwnerGuid": FieldMeta("str", "The guid of the owner.", E),
        "ProjectGuid": FieldMeta("str", "The guid of the project that the artifact belongs to", E),
        "ReleaseGuid": FieldMeta("str", "The guid of the release", E),
    },
    status_field="TestSetStatusId",
    owner_field="OwnerId",
    priority_field=None,
    release_field="ReleaseId",
    type_field=None,
    supports_server_search=True,
    mywork_endpoint="test-sets",
    search_query_params={
        "row_start": "starting_row",
        "row_count": "number_of_rows",
        "release_id": "release_id",
        "sort_field": "sort_field",
        "sort_direction": "sort_direction",
    },
    default_sort_field="LastUpdateDate",
    default_sort_direction="desc",
    create_endpoint="projects/{product_id}/test-sets",
    id_field="TestSetId",
    id_prefix="TX",
    required_fields=["Name", "Description"],
    writable_fields=[
        "AutomationHostId",
        "BuildExecuteTimeInterval",
        "CustomProperties",
        "Description",
        "IsAutoScheduled",
        "Name",
        "OwnerId",
        "PlannedDate",
        "RecurrenceId",
        "ReleaseId",
        "Tags",
        "TestRunTypeId",
        "TestSetFolderId",
        "TestSetStatusId",
    ],
    update_endpoint="projects/{product_id}/test-sets",
    resolvable_fields={
        "TestSetStatusId": "statuses",
    },
    includes=["comments", "associations"],
    comments_endpoint="projects/{product_id}/test-sets/{artifact_id}/comments",
)
