"""Document type config — extracted from RemoteDocumentType OpenAPI schema."""

from mcp_server_spira.models import TemplateMetadataFieldConfig

DOCUMENT_TYPE_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="DocumentTypeId",
    endpoint="project-templates/{template_id}/document-types?active_only=true",
    include_fields=(
        "Default",
        "Description",
        "ProjectTemplateId",
    ),
)
