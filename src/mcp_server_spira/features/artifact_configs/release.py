"""Release artifact config — extracted from OpenAPI schema."""

from mcp_server_spira.models import ArtifactConfig, FieldMeta, Visibility

# Short aliases for readability in field_metadata
S = Visibility.SUMMARY
V = Visibility.VISIBLE
E = Visibility.EXCLUDED

RELEASE_CONFIG = ArtifactConfig(
    artifact_type="release",
    workspace_type="product",
    search_endpoint="projects/{product_id}/releases/search",
    single_endpoint="projects/{product_id}/releases/{artifact_id}",
    description="Releases and iterations tracked in a Spira product.",
    field_metadata={
        "Name": FieldMeta("str", "The name of the release", S),
        "OwnerName": FieldMeta("str", "The name of the user that the release is assigned to", S),
        "PercentComplete": FieldMeta("int", "The percentage complete of the project/sprint", S),
        "ReleaseId": FieldMeta("int", "The id of the release", S),
        "ReleaseStatusName": FieldMeta("str", "The display name for the release status", S),
        "ReleaseTypeName": FieldMeta("str", "The display name for the release type", S),
        "VersionNumber": FieldMeta("str", "The version number string of the release", S),
        "Active": FieldMeta("bool", "Is this release active for the project", V),
        "AvailableEffort": FieldMeta(
            "int", "How much effort is still available in the release for planning", V
        ),
        "CountBlocked": FieldMeta("int", "The count of blocked test cases in this release", V),
        "CountCaution": FieldMeta("int", "The count of caution test cases in this release", V),
        "CountFailed": FieldMeta("int", "The count of failed test cases in this release", V),
        "CountNotApplicable": FieldMeta("int", "The count of N/A test cases in this release", V),
        "CountNotRun": FieldMeta("int", "The count of not run test cases in this release", V),
        "CountPassed": FieldMeta("int", "The count of passed test cases in this release", V),
        "CreationDate": FieldMeta("datetime", "The date the release was originally created", V),
        "CreatorId": FieldMeta("int", "The id of the user that created the release", V),
        "CreatorName": FieldMeta(
            "str", "What is the full display name of the person who created this release", V
        ),
        "DaysNonWorking": FieldMeta(
            "str", "How many non-working days are associated with the release", V
        ),
        "Description": FieldMeta("str", "The description of the release", V),
        "EndDate": FieldMeta("datetime", "What is the end date for the release", V),
        "IndentLevel": FieldMeta("str", "The indentation level of the artifact", V),
        "LastUpdateDate": FieldMeta("datetime", "The date the release was last modified", V),
        "OwnerId": FieldMeta("int", "The id of the user that the release is assigned to", V),
        "PlannedEffort": FieldMeta(
            "int", "What is the estimated planned effort associated with the release", V
        ),
        "ProjectId": FieldMeta("int", "The id of the project that the artifact belongs to", V),
        "ReleaseStatusId": FieldMeta("int", "The status of the release", V),
        "ReleaseTypeId": FieldMeta("int", "The type of the release", V),
        "RequirementCount": FieldMeta("int", "Number of requirements assigned to this release", V),
        "RequirementPoints": FieldMeta(
            "str", "Number of effort points assigned to the requirements of this release", V
        ),
        "ResourceCount": FieldMeta("str", "How many people are working on the release", V),
        "StartDate": FieldMeta("datetime", "What is the start date for the release", V),
        "Summary": FieldMeta(
            "bool", "Is this release a summary one (i.e. does it have child releases)", V
        ),
        "Tags": FieldMeta(
            "str", "The list of meta-tags that should be associated with the artifact", V
        ),
        "TaskActualEffort": FieldMeta(
            "int",
            "How much effort was actually expended for all the tasks scheduled for this release",
            V,
        ),
        "TaskCount": FieldMeta("int", "How many tasks are scheduled for this release", V),
        "TaskEstimatedEffort": FieldMeta(
            "int", "How much effort was estimated for all the tasks scheduled for this release", V
        ),
        "ArtifactTypeId": FieldMeta("int", "The type of artifact that we have", E),
        "ConcurrencyDate": FieldMeta(
            "datetime",
            "The datetime used to track optimistic concurrency to prevent edit conflicts",
            E,
        ),
        "CreatorGuid": FieldMeta("str", "The guid of the creator.", E),
        "CustomProperties": FieldMeta(
            "list", "The list of associated custom properties/fields for this artifact", E
        ),
        "FullName": FieldMeta("str", "The full name and version number of the release combined", E),
        "Guid": FieldMeta("str", "The unique identifier for the artifact", E),
        "IsAttachments": FieldMeta("bool", "Does this artifact have any attachments?", E),
        "OwnerGuid": FieldMeta("str", "The guid of the owner.", E),
        "ProjectGuid": FieldMeta("str", "The guid of the project that the artifact belongs to", E),
    },
    status_field="ReleaseStatusId",
    owner_field="OwnerId",
    priority_field=None,
    release_field=None,
    type_field="ReleaseTypeId",
    supports_server_search=True,
    mywork_endpoint=None,
    search_query_params={
        "row_start": "start_row",
        "row_count": "number_rows",
    },
    default_sort_field="LastUpdateDate",
    default_sort_direction="desc",
    create_endpoint="projects/{product_id}/releases",
    id_field="ReleaseId",
    id_prefix="RL",
    required_fields=["Name", "Description"],
    inject_defaults={"ReleaseTypeId": 3, "ReleaseStatusId": 1},
    writable_fields=[
        "Active",
        "CreatorId",
        "CustomProperties",
        "DaysNonWorking",
        "Description",
        "EndDate",
        "Name",
        "OwnerId",
        "ReleaseStatusId",
        "ReleaseTypeId",
        "StartDate",
        "Tags",
        "VersionNumber",
    ],
    update_endpoint="projects/{product_id}/releases",
    resolvable_fields={
        "ReleaseStatusId": "statuses",
        "ReleaseTypeId": "types",
    },
    includes=["comments", "coverage", "associations"],
    comments_endpoint="projects/{product_id}/releases/{artifact_id}/comments",
)
