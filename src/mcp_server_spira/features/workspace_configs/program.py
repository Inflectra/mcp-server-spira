"""Program workspace config — extracted from RemoteProgram OpenAPI schema."""

from mcp_server_spira.models import WorkspaceConfig

PROGRAM_CONFIG = WorkspaceConfig(
    workspace_type="program",
    description="Programs (project groups) in the Spira instance.",
    list_endpoint="programs",
    single_endpoint=None,
    openapi_schema="RemoteProgram",
    # REVIEW: curated summary subset — adjust after human review
    summary_fields=[
        "ProgramId",
        "Name",
        "isActive",
        "PortfolioId",
        "ProjectTemplateId",
    ],
    # all_fields: LLM-visible fields from RemoteProgram schema
    all_fields=[
        "Description",
        "isActive",
        "isDefault",
        "LastUpdatedDate",
        "Name",
        "PortfolioId",
        "ProgramId",
        "ProjectTemplateId",
        "Website",
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
