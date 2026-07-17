"""Milestone artifact config — extracted from OpenAPI schema."""

from mcp_server_spira.models import ArtifactConfig, FieldMeta, Visibility

# Short aliases for readability in field_metadata
S = Visibility.SUMMARY
V = Visibility.VISIBLE
E = Visibility.EXCLUDED

MILESTONE_CONFIG = ArtifactConfig(
    artifact_type="milestone",
    workspace_type="program",
    search_endpoint="programs/{program_id}/milestones/search",
    single_endpoint="programs/{program_id}/milestones/{artifact_id}",
    description="Milestones tracked in a Spira program.",
    field_metadata={
        "MilestoneId": FieldMeta("int", "ID of the program milestone", S),
        "Name": FieldMeta("str", "Name of this milestone", S),
        "OwnerName": FieldMeta("str", "Full name of the owner of this milestone", S),
        "PercentComplete": FieldMeta(
            "int", "Percent of the associated capabilities which are completed", S
        ),
        "StatusName": FieldMeta("str", "Name of the milestone status this milestone has", S),
        "TypeName": FieldMeta("str", "Name of the program milestone type this milestone has", S),
        "ChildrenEndDate": FieldMeta(
            "datetime", "Earliest end date of this milestone's children releases", V
        ),
        "ChildrenStartDate": FieldMeta(
            "datetime", "Earliest start date of this milestone's children releases", V
        ),
        "CreationDate": FieldMeta("datetime", "The date/time the milestone was created", V),
        "CreatorId": FieldMeta("int", "UserId of the creator of this milestone", V),
        "CreatorName": FieldMeta("str", "Full name of the creator of this milestone", V),
        "Description": FieldMeta("str", "Description of the milestone", V),
        "EndDate": FieldMeta("datetime", "End date of this milestone", V),
        "LastUpdateDate": FieldMeta("datetime", "The date/time the milestone was last updated", V),
        "OwnerId": FieldMeta("int", "UserId of the owner of this milestone", V),
        "ProjectGroupId": FieldMeta(
            "int", "ID of the project group which this milestone belongs to", V
        ),
        "ProjectGroupName": FieldMeta(
            "str", "Name of the project group this milestone belongs to", V
        ),
        "ReleaseCount": FieldMeta("int", "Number of releases associated with this milestone", V),
        "RequirementCount": FieldMeta(
            "int", "Number of requirements which are within the child releases", V
        ),
        "StartDate": FieldMeta("datetime", "Start date of this milestone", V),
        "StatusId": FieldMeta("int", "ID of the program milestone status this milestone has", V),
        "StatusIsOpen": FieldMeta(
            "bool", 'Whether or not this status makes this milestone "Open"', V
        ),
        "TypeId": FieldMeta("int", "ID of the program milestone type this milestone has", V),
        "ArtifactTypeId": FieldMeta("int", "The type of artifact that we have", E),
        "ConcurrencyGuid": FieldMeta(
            "str", "The field used to track optimistic concurrency to prevent edit conflicts", E
        ),
        "CustomProperties": FieldMeta(
            "list", "The list of associated custom properties/fields for this workspace", E
        ),
        "Guid": FieldMeta("str", "Artifact guid for unique identification of an artifact", E),
    },
    status_field="StatusId",
    owner_field="OwnerId",
    priority_field=None,
    release_field=None,
    type_field="TypeId",
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
