"""Task artifact config — extracted from OpenAPI schema."""

from mcp_server_spira.models import ArtifactConfig, FieldMeta, Visibility

# Short aliases for readability in field_metadata
S = Visibility.SUMMARY
V = Visibility.VISIBLE
E = Visibility.EXCLUDED

TASK_CONFIG = ArtifactConfig(
    artifact_type="task",
    workspace_type="product",
    search_endpoint="projects/{product_id}/tasks/search",
    single_endpoint="projects/{product_id}/tasks/{artifact_id}",
    description="Tasks (work items, to-dos) tracked in a Spira product.",
    field_metadata={
        "TaskId": FieldMeta("int", "The id of the task", S),
        "Name": FieldMeta("str", "The name of the task", S),
        "TaskTypeName": FieldMeta("str", "The display name of the type of the task", S),
        "TaskStatusName": FieldMeta("str", "The display name of the status of the task", S),
        "TaskPriorityName": FieldMeta("str", "The display name of the priority of the task", S),
        "OwnerName": FieldMeta(
            "str", "The display name of the user who the task is assigned-to", S
        ),
        "CompletionPercent": FieldMeta(
            "int",
            "The completion percentage (value = 0-100) of the task as calculated in the system from the remaining effort vs. the original estimated effort.",
            S,
        ),
        "ReleaseVersionNumber": FieldMeta(
            "str", "The version number of the release/iteration the task is scheduled for", S
        ),
        "ActualEffort": FieldMeta(
            "int", "The actual effort expended so far (in minutes) for the task", V
        ),
        "ComponentId": FieldMeta("int", "The id of the component that this task belongs to", V),
        "CreationDate": FieldMeta(
            "datetime", "The date/time that the task was originally created", V
        ),
        "CreatorId": FieldMeta("int", "The id of the user that originally created the task", V),
        "Description": FieldMeta("str", "The detailed description of the task", V),
        "EndDate": FieldMeta("datetime", "The scheduled end date for the task", V),
        "EstimatedEffort": FieldMeta(
            "int", "The originally estimated effort (in minutes) of the task", V
        ),
        "LastUpdateDate": FieldMeta("datetime", "The date/time that the task was last modified", V),
        "OwnerId": FieldMeta("int", "The id of the user that the task is assigned-to", V),
        "ProjectId": FieldMeta("int", "The id of the project that the artifact belongs to", V),
        "ProjectName": FieldMeta("str", "The display name of the project the task belongs to", V),
        "ProjectedEffort": FieldMeta(
            "int", "The projected actual effort of the task when it is completed", V
        ),
        "ReleaseId": FieldMeta(
            "int", "The id of the release/iteration that the task is scheduled for", V
        ),
        "RemainingEffort": FieldMeta("int", "The effort remaining as reported by the developer", V),
        "RequirementId": FieldMeta(
            "int", "The id of the parent requirement that the task belongs to", V
        ),
        "RequirementName": FieldMeta(
            "str", "The name of the requirement that the task is associated with", V
        ),
        "StartDate": FieldMeta("datetime", "The scheduled start date for the task", V),
        "Tags": FieldMeta(
            "str", "The list of meta-tags that should be associated with the artifact", V
        ),
        "TaskFolderId": FieldMeta(
            "int", "The of the folder the task is stored in (null for root)", V
        ),
        "TaskPriorityId": FieldMeta("int", "The id of the priority of the task", V),
        "TaskStatusId": FieldMeta("int", "The id of the status of the task", V),
        "TaskTypeId": FieldMeta("int", "The id of the type of the task (null for default)", V),
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
        "Guid": FieldMeta("str", "The unique identifier for the artifact", E),
        "IsAttachments": FieldMeta("bool", "Does this artifact have any attachments?", E),
        "OwnerGuid": FieldMeta("str", "The guid of the owner.", E),
        "ProjectGuid": FieldMeta("str", "The guid of the project that the artifact belongs to", E),
        "ReleaseGuid": FieldMeta("str", "The guid of the release", E),
        "RiskId": FieldMeta("int", "The risk that the task is associated with", E),
    },
    status_field="TaskStatusId",
    owner_field="OwnerId",
    priority_field="TaskPriorityId",
    release_field="ReleaseId",
    type_field="TaskTypeId",
    supports_server_search=True,
    mywork_endpoint="tasks",
    search_query_params={
        "row_start": "starting_row",
        "row_count": "number_of_rows",
        "sort_field": "sort_field",
        "sort_direction": "sort_direction",
    },
    default_sort_field="LastUpdateDate",
    default_sort_direction="desc",
    create_endpoint="projects/{product_id}/tasks",
    id_field="TaskId",
    id_prefix="TK",
    required_fields=["Name", "Description"],
    inject_defaults={"TaskStatusId": 1},
    writable_fields=[
        "ActualEffort",
        "CompletionPercent",
        "CreatorId",
        "Description",
        "EndDate",
        "EstimatedEffort",
        "Name",
        "OwnerId",
        "ProjectedEffort",
        "ReleaseId",
        "RemainingEffort",
        "RequirementId",
        "StartDate",
        "Tags",
        "TaskFolderId",
        "TaskPriorityId",
        "TaskStatusId",
        "TaskTypeId",
    ],
    update_endpoint="projects/{product_id}/tasks",
    resolvable_fields={
        "TaskPriorityId": "priorities",
        "TaskStatusId": "statuses",
        "TaskTypeId": "types",
    },
    includes=["comments", "associations"],
    comments_endpoint="projects/{product_id}/tasks/{artifact_id}/comments",
)
