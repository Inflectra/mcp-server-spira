"""Milestone artifact config — extracted from RemoteProgramMilestone OpenAPI schema."""

from mcp_server_spira.models import ArtifactConfig

MILESTONE_CONFIG = ArtifactConfig(
    artifact_type="milestone",
    workspace_type="program",
    search_endpoint="programs/{program_id}/milestones/search",
    single_endpoint="programs/{program_id}/milestones/{artifact_id}",
    description="Milestones tracked in a Spira program.",
    # Normalised field mappings
    status_field="StatusId",
    owner_field="OwnerId",
    priority_field=None,
    release_field=None,
    type_field="TypeId",
    summary_fields=[
        "MilestoneId",
        "Name",
        "OwnerName",
        "PercentComplete",
        "StatusName",
        "TypeName",
    ],
    # all_fields: LLM-visible fields from RemoteProgramMilestone schema
    all_fields=[
        "ChildrenEndDate",
        "ChildrenStartDate",
        "CreationDate",
        "CreatorId",
        "CreatorName",
        "Description",
        "EndDate",
        "LastUpdateDate",
        "MilestoneId",
        "Name",
        "OwnerId",
        "OwnerName",
        "PercentComplete",
        "ProjectGroupId",
        "ProjectGroupName",
        "ReleaseCount",
        "RequirementCount",
        "StartDate",
        "StatusId",
        "StatusIsOpen",
        "StatusName",
        "TypeId",
        "TypeName",
    ],
    # excluded_fields: valid OpenAPI fields hidden from LLM
    excluded_fields=[
        "ArtifactTypeId",
        "ConcurrencyGuid",
        "CustomProperties",
        "Guid",
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
