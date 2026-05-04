"""Document status config — extracted from RemoteDocumentStatus OpenAPI schema."""

from mcp_server_spira.models import TemplateMetadataFieldConfig

DOCUMENT_STATUS_CONFIG = TemplateMetadataFieldConfig(
    active_field="Active",
    id_field="DocumentStatusId",
    endpoint="project-templates/{template_id}/document-statuses",
    include_fields=(
        "Default",
        "Open",
        "Position",
        "ProjectTemplateId",
    ),
)
