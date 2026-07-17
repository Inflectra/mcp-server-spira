"""Document artifact config — extracted from OpenAPI schema."""

from mcp_server_spira.models import ArtifactConfig, FieldMeta, Visibility

# Short aliases for readability in field_metadata
S = Visibility.SUMMARY
V = Visibility.VISIBLE
E = Visibility.EXCLUDED

DOCUMENT_CONFIG = ArtifactConfig(
    artifact_type="document",
    workspace_type="product",
    search_endpoint="projects/{product_id}/documents/search",
    single_endpoint="projects/{product_id}/documents/{artifact_id}",
    description="Documents and attachments tracked in a Spira product.",
    field_metadata={
        "AttachmentId": FieldMeta("int", "The id of the attachment", S),
        "FilenameOrUrl": FieldMeta(
            "str",
            "The filename of the file (if a file attachment) or the full URL if a URL attachment",
            S,
        ),
        "DocumentTypeName": FieldMeta(
            "str",
            "The display name of the attachment type relative to the current project template",
            S,
        ),
        "DocumentStatusName": FieldMeta(
            "str",
            "The display name of the document status relative to the current project template",
            S,
        ),
        "AuthorName": FieldMeta(
            "str", "The display name of the user that uploaded the attachment", S
        ),
        "AttachedArtifacts": FieldMeta(
            "list", "The list of artifacts the document is attached to", V
        ),
        "AttachmentTypeId": FieldMeta("int", "The id of the attachment type", V),
        "AttachmentTypeName": FieldMeta(
            "str",
            "The display name of the attachment type (i.e. whether it's a file or url)",
            V,
        ),
        "AuthorId": FieldMeta("int", "The id of the user that uploaded the attachment", V),
        "CurrentVersion": FieldMeta("str", "The version name of the current attachment", V),
        "Description": FieldMeta("str", "The description of the attachment", V),
        "DocumentStatusId": FieldMeta(
            "int",
            "The id of the document status relative to the current project template",
            V,
        ),
        "DocumentTypeId": FieldMeta(
            "int",
            "The id of the document type relative to the current project template",
            V,
        ),
        "EditedDate": FieldMeta("datetime", "The date/time the attachment was last edited", V),
        "EditorId": FieldMeta("int", "The id of the user that edited the document", V),
        "EditorName": FieldMeta("str", "The display name of the user that edited the document", V),
        "ProjectAttachmentFolderId": FieldMeta(
            "int", "The id of the attachment folder id for the current project", V
        ),
        "ProjectId": FieldMeta("int", "The id of the project that the artifact belongs to", V),
        "Size": FieldMeta("int", "The size of the attachment in bytes", V),
        "Tags": FieldMeta(
            "str", "The list of meta-tags that should be associated with the artifact", V
        ),
        "UploadDate": FieldMeta("datetime", "The date/time the attachment was uploaded", V),
        "Versions": FieldMeta("list", "The list of document versions", V),
        "ArtifactTypeId": FieldMeta("int", "The type of artifact that we have", E),
        "AuthorGuid": FieldMeta("str", "The guid of the author.", E),
        "ConcurrencyDate": FieldMeta(
            "datetime",
            "The datetime used to track optimistic concurrency to prevent edit conflicts",
            E,
        ),
        "CustomProperties": FieldMeta(
            "list", "The list of associated custom properties/fields for this artifact", E
        ),
        "EditorGuid": FieldMeta("str", "The guid of the editor.", E),
        "Guid": FieldMeta("str", "The unique identifier for the artifact", E),
        "IsAttachments": FieldMeta("bool", "Does this artifact have any attachments?", E),
        "ProjectGuid": FieldMeta("str", "The guid of the project that the artifact belongs to", E),
    },
    status_field="DocumentStatusId",
    owner_field="AuthorId",
    priority_field=None,
    release_field=None,
    type_field="DocumentTypeId",
    supports_server_search=True,
    mywork_endpoint=None,
    search_query_params={
        "row_start": "start_row",
        "row_count": "number_rows",
        "sort_by": "sort_by",
    },
    default_sort_field="LastUpdateDate",
    default_sort_direction="desc",
    id_field="AttachmentId",
    includes=["associations"],
)
