"""Product workspace config — extracted from RemoteProject OpenAPI schema."""

from mcp_server_spira.models import WorkspaceConfig

PRODUCT_CONFIG = WorkspaceConfig(
    workspace_type="product",
    description="Products (projects) in the Spira instance.",
    list_endpoint="projects",
    single_endpoint="projects/{workspace_id}",
    openapi_schema="RemoteProject",
    # REVIEW: curated summary subset — adjust after human review
    summary_fields=[
        "ProjectId",
        "Name",
        "Active",
        "ProjectGroupId",
        "ProjectTemplateId",
    ],
    # all_fields: LLM-visible fields from RemoteProject schema
    all_fields=[
        "Active",
        "CreationDate",
        "Description",
        "EndDate",
        "LastUpdatedDate",
        "Name",
        "NonWorkingHours",
        "PercentComplete",
        "ProjectGroupId",
        "ProjectId",
        "ProjectTemplateId",
        "RequirementCount",
        "StartDate",
        "Website",
        "WorkingDays",
        "WorkingHours",
        "WorkspaceTypeId",
    ],
    # excluded_fields: valid OpenAPI fields hidden from LLM
    excluded_fields=[
        "ArtifactTypeId",
        "ConcurrencyGuid",
        "CustomProperties",
        "Guid",
    ],
)
