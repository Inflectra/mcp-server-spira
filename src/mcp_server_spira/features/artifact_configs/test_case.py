"""Test Case artifact config — extracted from OpenAPI schema."""

from mcp_server_spira.models import ArtifactConfig, FieldMeta, Visibility

# Short aliases for readability in field_metadata
S = Visibility.SUMMARY
V = Visibility.VISIBLE
E = Visibility.EXCLUDED

TEST_CASE_CONFIG = ArtifactConfig(
    artifact_type="test_case",
    workspace_type="product",
    search_endpoint="projects/{product_id}/test-cases/search",
    single_endpoint="projects/{product_id}/test-cases/{artifact_id}",
    description="Test cases tracked in a Spira product.",
    field_metadata={
        "ExecutionStatusName": FieldMeta("str", "The display name of the execution status", S),
        "Name": FieldMeta("str", "The name of the test case", S),
        "OwnerName": FieldMeta(
            "str", "The display name of the user that the test case is assigned-to", S
        ),
        "TestCaseId": FieldMeta("int", "The id of the test case", S),
        "TestCasePriorityName": FieldMeta(
            "str", "The display name of the priority of the test case", S
        ),
        "TestCaseStatusName": FieldMeta(
            "str", "The display name of the status of the test case", S
        ),
        "TestCaseTypeName": FieldMeta("str", "The display name of the type of the test case", S),
        "ActualDuration": FieldMeta(
            "int", "The actual result from the most recent test run of the this test case", V
        ),
        "AuthorId": FieldMeta("int", "The id of the user that wrote the test case", V),
        "AuthorName": FieldMeta("str", "The display name of the user that wrote the test case", V),
        "AutomationEngineId": FieldMeta(
            "int",
            "The id of the automation engine the associated test script uses (null if manual only)",
            V,
        ),
        "ComponentIds": FieldMeta(
            "list", "The list of components that this test case belongs to", V
        ),
        "CreationDate": FieldMeta("datetime", "The date the test case was created", V),
        "Description": FieldMeta("str", "The description of the test case", V),
        "EstimatedDuration": FieldMeta("int", "The estimated time to execute the test case", V),
        "ExecutionDate": FieldMeta("datetime", "The date the test case was last executed", V),
        "ExecutionStatusId": FieldMeta("int", "The execution status id of the test case", V),
        "IsSuspect": FieldMeta(
            "bool", "Have any of the requirements associated with this test case changed", V
        ),
        "IsTestSteps": FieldMeta("bool", "Does this test case have steps", V),
        "LastUpdateDate": FieldMeta("datetime", "The date the test case was last updated", V),
        "OwnerId": FieldMeta("int", "The id of the user that the test case is assigned-to", V),
        "ProjectId": FieldMeta("int", "The id of the project that the artifact belongs to", V),
        "ProjectName": FieldMeta(
            "str", "The display name of the project that the test case belongs to", V
        ),
        "Tags": FieldMeta(
            "str", "The list of meta-tags that should be associated with the artifact", V
        ),
        "TestCaseFolderId": FieldMeta(
            "int", "The id of the folder the test case belongs to. Null = root folder", V
        ),
        "TestCasePriorityId": FieldMeta("int", "The id of the priority of the test case", V),
        "TestCaseStatusId": FieldMeta(
            "int", "The status of the test case, pass 0 to use the default value", V
        ),
        "TestCaseTypeId": FieldMeta(
            "int", "The type of test case, pass null to use the default value", V
        ),
        "ArtifactTypeId": FieldMeta("int", "The type of artifact that we have", E),
        "AuthorGuid": FieldMeta("str", "The guid of the author.", E),
        "AutomationAttachmentId": FieldMeta(
            "int",
            "The id of the attachment that is being used to store the test script (file or url)",
            E,
        ),
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
        "OwnerGuid": FieldMeta("str", "The guid of the owner.", E),
        "ProjectGuid": FieldMeta("str", "The guid of the project that the artifact belongs to", E),
        "TestSteps": FieldMeta("list", "The list of test steps that comprise the test case", E),
    },
    status_field="TestCaseStatusId",
    owner_field="OwnerId",
    priority_field="TestCasePriorityId",
    release_field=None,
    type_field="TestCaseTypeId",
    supports_server_search=True,
    mywork_endpoint="test-cases",
    search_query_params={
        "row_start": "starting_row",
        "row_count": "number_of_rows",
        "sort_field": "sort_field",
        "sort_direction": "sort_direction",
        "release_id": "release_id",
    },
    default_sort_field="LastUpdateDate",
    default_sort_direction="desc",
    includes=["test_steps", "comments", "coverage", "associations"],
    comments_endpoint="projects/{product_id}/test-cases/{artifact_id}/comments",
    create_endpoint="projects/{product_id}/test-cases",
    id_field="TestCaseId",
    id_prefix="TC",
    required_fields=["Name", "Description"],
    writable_fields=[
        "AuthorId",
        "AutomationEngineId",
        "ComponentIds",
        "CustomProperties",
        "Description",
        "EstimatedDuration",
        "Name",
        "OwnerId",
        "Tags",
        "TestCaseFolderId",
        "TestCasePriorityId",
        "TestCaseStatusId",
        "TestCaseTypeId",
    ],
    update_endpoint="projects/{product_id}/test-cases",
    resolvable_fields={
        "TestCasePriorityId": "priorities",
        "TestCaseStatusId": "statuses",
        "TestCaseTypeId": "types",
    },
)
