"""Document artifact config — extracted from RemoteDocument OpenAPI schema."""

from mcp_server_spira.models import ArtifactConfig

DOCUMENT_CONFIG = ArtifactConfig(
    artifact_type="document",
    workspace_type="product",
    search_endpoint="projects/{product_id}/documents/search",
    single_endpoint="projects/{product_id}/documents/{artifact_id}",
    description="Documents and attachments tracked in a Spira product.",
    # Normalised field mappings
    status_field="DocumentStatusId",
    owner_field="AuthorId",
    priority_field=None,
    release_field=None,
    type_field="DocumentTypeId",
    summary_fields=[
        "AttachmentId",
        "FilenameOrUrl",
        "DocumentTypeName",
        "DocumentStatusName",
        "AuthorName",
    ],
    # all_fields: LLM-visible fields from RemoteDocument schema
    all_fields=[
        "AttachedArtifacts",
        "AttachmentId",
        "AttachmentTypeId",
        "AttachmentTypeName",
        "AuthorId",
        "AuthorName",
        "CurrentVersion",
        "Description",
        "DocumentStatusId",
        "DocumentStatusName",
        "DocumentTypeId",
        "DocumentTypeName",
        "EditedDate",
        "EditorId",
        "EditorName",
        "FilenameOrUrl",
        "ProjectAttachmentFolderId",
        "ProjectId",
        "Size",
        "Tags",
        "UploadDate",
        "Versions",
    ],
    # excluded_fields: valid OpenAPI fields hidden from LLM
    excluded_fields=[
        "ArtifactTypeId",
        "AuthorGuid",
        "ConcurrencyDate",
        "CustomProperties",
        "EditorGuid",
        "Guid",
        "IsAttachments",
        "ProjectGuid",
    ],
    supports_server_search=True,
    mywork_endpoint=None,
    search_query_params={
        "row_start": "start_row",
        "row_count": "number_rows",
        "sort_by": "sort_by",
    },
    default_sort_field="LastUpdateDate",
    default_sort_direction="desc",
)
