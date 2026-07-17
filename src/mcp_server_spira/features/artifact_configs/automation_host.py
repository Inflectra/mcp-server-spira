"""Automation Host artifact config — extracted from OpenAPI schema."""

from mcp_server_spira.models import ArtifactConfig, FieldMeta, Visibility

# Short aliases for readability in field_metadata
S = Visibility.SUMMARY
V = Visibility.VISIBLE
E = Visibility.EXCLUDED

AUTOMATION_HOST_CONFIG = ArtifactConfig(
    artifact_type="automation_host",
    workspace_type="product",
    search_endpoint="projects/{product_id}/automation-hosts/search",
    single_endpoint="projects/{product_id}/automation-hosts/{artifact_id}",
    description="Automation hosts registered in a Spira product.",
    field_metadata={
        "AutomationHostId": FieldMeta("int", "The id of the host", S),
        "Name": FieldMeta("str", "The name of the host", S),
        "Active": FieldMeta("bool", "Is this host active for the project", V),
        "Description": FieldMeta("str", "The detailed description of the host", V),
        "LastContactDate": FieldMeta("datetime", "The last time this host was contacted", V),
        "LastUpdateDate": FieldMeta("datetime", "The date/time that the host was last modified", V),
        "ProjectId": FieldMeta("int", "The id of the project that the artifact belongs to", V),
        "Tags": FieldMeta(
            "str", "The list of meta-tags that should be associated with the artifact", V
        ),
        "Token": FieldMeta("str", "The token of the host", V),
        "ArtifactTypeId": FieldMeta("int", "The type of artifact that we have", E),
        "ConcurrencyDate": FieldMeta(
            "datetime",
            "The datetime used to track optimistic concurrency to prevent edit conflicts",
            E,
        ),
        "CustomProperties": FieldMeta(
            "list", "The list of associated custom properties/fields for this artifact", E
        ),
        "Guid": FieldMeta("str", "The unique identifier for the artifact", E),
        "IsAttachments": FieldMeta("bool", "Does this artifact have any attachments?", E),
        "ProjectGuid": FieldMeta("str", "The guid of the project that the artifact belongs to", E),
    },
    status_field=None,
    owner_field=None,
    priority_field=None,
    release_field=None,
    type_field=None,
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
