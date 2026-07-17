"""Requirement artifact config — extracted from OpenAPI schema."""

from mcp_server_spira.models import ArtifactConfig, FieldMeta, Visibility

# Short aliases for readability in field_metadata
S = Visibility.SUMMARY
V = Visibility.VISIBLE
E = Visibility.EXCLUDED

REQUIREMENT_CONFIG = ArtifactConfig(
    artifact_type="requirement",
    workspace_type="product",
    search_endpoint="projects/{product_id}/requirements/search",
    single_endpoint="projects/{product_id}/requirements/{artifact_id}",
    description="Requirements tracked in a Spira product.",
    field_metadata={
        "ImportanceName": FieldMeta(
            "str", "The display name of the importance that the requirement is in (string)", S
        ),
        "Name": FieldMeta("str", "The name of the requirement (string - required for POST)", S),
        "OwnerName": FieldMeta(
            "str", "The display name of the user that this requirement is assigned-to (string)", S
        ),
        "PercentComplete": FieldMeta("int", "The percentage complete of the requirement", S),
        "ReleaseVersionNumber": FieldMeta(
            "str",
            "The version number string of the release that the requirement is scheduled for (string)",
            S,
        ),
        "RequirementId": FieldMeta("int", "The id of the requirement (integer)", S),
        "RequirementTypeName": FieldMeta(
            "str", "The display name of the type of requirement (string)", S
        ),
        "StatusName": FieldMeta(
            "str", "The display name of the status the requirement is in (string)", S
        ),
        "AuthorId": FieldMeta("int", "The id of the user that wrote the requirement (integer)", V),
        "AuthorName": FieldMeta(
            "str", "The display name of the user that wrote this requirement (string)", V
        ),
        "ComponentId": FieldMeta(
            "int",
            "The id of the component the requirement is a part of (integer - these are created on a per project user by an administrator)",
            V,
        ),
        "CoverageCountBlocked": FieldMeta(
            "int",
            "How many of the test cases that cover this requirement have blocked (integer)",
            V,
        ),
        "CoverageCountCaution": FieldMeta(
            "int",
            "How many of the test cases that cover this requirement have been marked as caution (integer)",
            V,
        ),
        "CoverageCountFailed": FieldMeta(
            "int", "How many of the test cases that cover this requirement have failed (integer)", V
        ),
        "CoverageCountPassed": FieldMeta(
            "int", "How many of the test cases that cover this requirement have passed (integer)", V
        ),
        "CoverageCountTotal": FieldMeta(
            "int", "How many test cases cover this requirement (integer)", V
        ),
        "CreationDate": FieldMeta(
            "datetime", "The date/time the requirement was originally created (date-time)", V
        ),
        "Description": FieldMeta("str", "The description of the requirement (string)", V),
        "EndDate": FieldMeta(
            "datetime", "The end date of the requirement for planning purposes", V
        ),
        "EstimatePoints": FieldMeta(
            "str", "The estimate of the requirement (decimal - in story points)", V
        ),
        "EstimatedEffort": FieldMeta(
            "int",
            "What was the original top-down level of effort estimated for this requirement, calculated from the points estimate (integer)",
            V,
        ),
        "ImportanceId": FieldMeta(
            "int", "The id of the importance of the requirement (integer)", V
        ),
        "IsSuspect": FieldMeta(
            "bool", "Is the requirement marked as suspect due to dependent item changes", V
        ),
        "LastUpdateDate": FieldMeta(
            "datetime", "The date/time the requirement was last modified (date-time)", V
        ),
        "OwnerId": FieldMeta(
            "int", "The id of the user that the requirement is assigned-to (integer)", V
        ),
        "ProjectId": FieldMeta("int", "The id of the project that the artifact belongs to", V),
        "ProjectName": FieldMeta(
            "str",
            "The display name of the project that the requirement is associated with (string)",
            V,
        ),
        "ReleaseId": FieldMeta(
            "int",
            "The id of the release the requirement is scheduled to implemented in (integer)",
            V,
        ),
        "RequirementStatusId": FieldMeta(
            "int",
            "The id of the requirement status (integer). Alias for StatusId in the API response.",
            V,
        ),
        "RequirementTypeId": FieldMeta("int", "The type of requirement (integer).", V),
        "StartDate": FieldMeta(
            "datetime", "The start date of the requirement for planning purposes", V
        ),
        "StatusId": FieldMeta("int", "The id of the requirement's status (integer).", V),
        "Summary": FieldMeta("bool", "Is this a summary requirement or not (boolean)", V),
        "Tags": FieldMeta(
            "str", "The list of meta-tags that should be associated with the artifact", V
        ),
        "TaskActualEffort": FieldMeta(
            "int",
            "What is the bottom-up actual effort for all the tasks associated with this requirement (integer)",
            V,
        ),
        "TaskCount": FieldMeta(
            "int", "How many tasks are associated with this requirement (integer)", V
        ),
        "TaskEstimatedEffort": FieldMeta(
            "int",
            "What is the bottom-up estimated effort for all the tasks associated with this requirement (integer)",
            V,
        ),
        "ArtifactTypeId": FieldMeta("int", "The type of artifact that we have", E),
        "AuthorGuid": FieldMeta("str", "The guid of the author.", E),
        "ConcurrencyDate": FieldMeta(
            "datetime",
            "The datetime used to track optimistic concurrency to prevent edit conflicts",
            E,
        ),
        "CustomProperties": FieldMeta(
            "list", "The list of associated custom properties/fields for this artifact", E
        ),
        "GoalId": FieldMeta("int", "The id of the goal that the requirement belongs to", E),
        "Guid": FieldMeta("str", "The unique identifier for the artifact", E),
        "IsAttachments": FieldMeta("bool", "Does this artifact have any attachments?", E),
        "IndentLevel": FieldMeta("str", "The indentation level of the artifact (string)", E),
        "OwnerGuid": FieldMeta("str", "The guid of the owner.", E),
        "ProjectGuid": FieldMeta("str", "The guid of the project that the artifact belongs to", E),
        "ReleaseGuid": FieldMeta("str", "The guid of the release", E),
        "Steps": FieldMeta(
            "list",
            "The list of scenarios steps (array - only available for Use Case requirement types)",
            E,
        ),
    },
    status_field="RequirementStatusId",
    owner_field="OwnerId",
    priority_field="ImportanceId",
    release_field="ReleaseId",
    type_field="RequirementTypeId",
    supports_server_search=True,
    mywork_endpoint="requirements",
    search_query_params={
        "row_start": "starting_row",
        "row_count": "number_of_rows",
    },
    default_sort_field="LastUpdateDate",
    default_sort_direction="desc",
    includes=["steps", "comments", "coverage", "associations"],
    comments_endpoint="projects/{product_id}/requirements/{artifact_id}/comments",
    create_endpoint="projects/{product_id}/requirements",
    id_field="RequirementId",
    id_prefix="RQ",
    required_fields=["Name", "Description"],
    writable_fields=[
        "AuthorId",
        "ComponentId",
        "Description",
        "EndDate",
        "EstimatePoints",
        "ImportanceId",
        "Name",
        "OwnerId",
        "ReleaseId",
        "RequirementTypeId",
        "StartDate",
        "StatusId",
        "Tags",
    ],
    update_endpoint="projects/{product_id}/requirements",
    resolvable_fields={
        "ImportanceId": "priorities",
        "StatusId": "statuses",
        "RequirementTypeId": "types",
    },
)
