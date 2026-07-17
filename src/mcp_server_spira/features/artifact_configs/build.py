"""Build artifact config — extracted from OpenAPI schema."""

from mcp_server_spira.models import ArtifactConfig, FieldMeta, Visibility

# Short aliases for readability in field_metadata
S = Visibility.SUMMARY
V = Visibility.VISIBLE
E = Visibility.EXCLUDED

BUILD_CONFIG = ArtifactConfig(
    artifact_type="build",
    workspace_type="product",
    search_endpoint="projects/{product_id}/releases/{release_id}/builds/search",
    single_endpoint="projects/{product_id}/releases/{release_id}/builds/{artifact_id}",
    description="Builds (CI/CD build records) tracked in a Spira product release.",
    field_metadata={
        "BuildId": FieldMeta("int", "The id of the build", S),
        "Name": FieldMeta("str", "The name of the build", S),
        "BuildStatusName": FieldMeta("str", "The display name of the status of the build", S),
        "CreationDate": FieldMeta("datetime", "The date the build was created", S),
        "BuildStatusId": FieldMeta(
            "int", "The id of the status of the build (1=Failed, 2=Passed)", V
        ),
        "Description": FieldMeta("str", "The detailed description of the host", V),
        "LastUpdateDate": FieldMeta(
            "datetime", "The date/time that the build was last modified", V
        ),
        "ProjectId": FieldMeta("int", "The id of the project the build belongs to", V),
        "ReleaseId": FieldMeta("int", "The id of the release or iteration the build belongs to", V),
        "Revisions": FieldMeta(
            "list", "The list of source code revisions associated with the build", V
        ),
        "Guid": FieldMeta("str", "The unique identifier for the build", E),
        "ReleaseGuid": FieldMeta(
            "str", "The guid of the release or iteration the build belongs to", E
        ),
    },
    status_field="BuildStatusId",
    owner_field=None,
    priority_field=None,
    release_field="ReleaseId",
    type_field=None,
    supports_server_search=True,
    mywork_endpoint=None,
    search_query_params={
        "row_start": "starting_row",
        "row_count": "number_of_rows",
        "sort_by": "sort_by",
    },
    default_sort_field="LastUpdateDate",
    default_sort_direction="desc",
    create_endpoint="projects/{product_id}/releases/{release_id}/builds",
    id_field="BuildId",
    id_prefix="BL",
    required_fields=["Name", "BuildStatusId"],
    url_params=["release_id"],
    writable_fields=["BuildStatusId", "Description", "Name", "ReleaseId", "Revisions"],
)
