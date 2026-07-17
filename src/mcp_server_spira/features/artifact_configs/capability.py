"""Capability artifact config — extracted from OpenAPI schema."""

from mcp_server_spira.models import ArtifactConfig, FieldMeta, Visibility

# Short aliases for readability in field_metadata
S = Visibility.SUMMARY
V = Visibility.VISIBLE
E = Visibility.EXCLUDED

CAPABILITY_CONFIG = ArtifactConfig(
    artifact_type="capability",
    workspace_type="program",
    search_endpoint="programs/{program_id}/capabilities/search",
    single_endpoint="programs/{program_id}/capabilities/{artifact_id}",
    description="Capabilities tracked in a Spira program.",
    field_metadata={
        "CapabilityId": FieldMeta("int", "ID of the program capability", S),
        "MilestoneName": FieldMeta(
            "str", "The name of the Program Milestone this capability belongs to", S
        ),
        "Name": FieldMeta("str", "Name of this capability", S),
        "OwnerName": FieldMeta("str", "Full name of the owner of this capability", S),
        "PercentComplete": FieldMeta("int", "Percent Completion of the capability", S),
        "PriorityName": FieldMeta("str", "Name of the capability priority this capability has", S),
        "StatusName": FieldMeta("str", "Name of the capability status this capability has", S),
        "TypeName": FieldMeta("str", "Name of the capability type this capability has", S),
        "CreationDate": FieldMeta("datetime", "The date/time the capability was created", V),
        "CreatorId": FieldMeta("int", "UserId of the creator of this capability", V),
        "CreatorName": FieldMeta("str", "Full name of the creator of this capability", V),
        "Description": FieldMeta("str", "Description of the capability", V),
        "IsSummary": FieldMeta("bool", "This Capability represents a summary in the program?", V),
        "LastUpdateDate": FieldMeta("datetime", "The date/time the capability was last updated", V),
        "MilestoneId": FieldMeta(
            "int", "The ID of the Program Milestone this capability belongs to", V
        ),
        "OwnerId": FieldMeta("int", "UserId of the owner of this capability", V),
        "PriorityId": FieldMeta("int", "ID of the capability priority this capability has", V),
        "ProjectGroupId": FieldMeta(
            "int", "ID of the project group which this capability belongs to", V
        ),
        "RequirementCount": FieldMeta(
            "int", "Number of requirements associated with this capability", V
        ),
        "StatusId": FieldMeta("int", "ID of the capability status this capability has", V),
        "StatusIsOpen": FieldMeta(
            "bool", 'Whether or not this status makes this capability "Open"', V
        ),
        "TypeId": FieldMeta("int", "ID of the capability type this capability has", V),
        "ArtifactTypeId": FieldMeta("int", "The type of artifact that we have", E),
        "ConcurrencyGuid": FieldMeta(
            "str", "The field used to track optimistic concurrency to prevent edit conflicts", E
        ),
        "CustomProperties": FieldMeta(
            "list", "The list of associated custom properties/fields for this workspace", E
        ),
        "Guid": FieldMeta("str", "Artifact guid for avoiding concurrency interactions", E),
        "IndentLevel": FieldMeta("str", "Indent level of this capability in the hierarchy", E),
    },
    status_field="StatusId",
    owner_field="OwnerId",
    priority_field="PriorityId",
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
