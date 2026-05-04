"""Build artifact config — extracted from RemoteBuild OpenAPI schema."""

from mcp_server_spira.models import ArtifactConfig

BUILD_CONFIG = ArtifactConfig(
    artifact_type="build",
    workspace_type="product",
    search_endpoint=("projects/{product_id}/releases/{release_id}/builds/search"),
    single_endpoint=("projects/{product_id}/releases/{release_id}/builds/{artifact_id}"),
    description=("Builds (CI/CD build records) tracked in a Spira product release."),
    # Normalised field mappings
    status_field="BuildStatusId",
    owner_field=None,
    priority_field=None,
    release_field="ReleaseId",
    type_field=None,
    summary_fields=[
        "BuildId",
        "Name",
        "BuildStatusName",
        "CreationDate",
    ],
    # all_fields: LLM-visible fields from RemoteBuild schema
    all_fields=[
        "BuildId",
        "BuildStatusId",
        "BuildStatusName",
        "CreationDate",
        "Description",
        "LastUpdateDate",
        "Name",
        "ProjectId",
        "ReleaseId",
        "Revisions",
    ],
    # excluded_fields: valid OpenAPI fields hidden from LLM
    excluded_fields=[
        "Guid",
        "ReleaseGuid",
    ],
    supports_server_search=True,
    mywork_endpoint=None,
    search_query_params={
        "row_start": "starting_row",
        "row_count": "number_of_rows",
        "sort_by": "sort_by",
    },
    default_sort_field="LastUpdateDate",
    default_sort_direction="desc",
)
