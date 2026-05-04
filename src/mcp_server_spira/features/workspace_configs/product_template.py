"""Product template workspace config — extracted from RemoteProjectTemplate OpenAPI schema."""

from mcp_server_spira.models import WorkspaceConfig

PRODUCT_TEMPLATE_CONFIG = WorkspaceConfig(
    workspace_type="product_template",
    description="Product templates in the Spira instance.",
    list_endpoint="project-templates",
    single_endpoint="project-templates/{workspace_id}",
    openapi_schema="RemoteProjectTemplate",
    # REVIEW: curated summary subset — adjust after human review
    summary_fields=[
        "ProjectTemplateId",
        "Name",
        "IsActive",
    ],
    # all_fields: LLM-visible fields from RemoteProjectTemplate schema
    all_fields=[
        "Description",
        "IsActive",
        "LastUpdatedDate",
        "Name",
        "ProjectTemplateId",
    ],
    # excluded_fields: valid OpenAPI fields hidden from LLM
    excluded_fields=[
        "ArtifactTypeId",
        "ConcurrencyGuid",
        "CustomProperties",
        "Guid",
        "WorkspaceTypeId",
    ],
)
