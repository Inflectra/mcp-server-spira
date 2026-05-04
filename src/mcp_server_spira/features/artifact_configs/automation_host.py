"""Automation Host artifact config — extracted from RemoteAutomationHost OpenAPI schema."""

from mcp_server_spira.models import ArtifactConfig

AUTOMATION_HOST_CONFIG = ArtifactConfig(
    artifact_type="automation_host",
    workspace_type="product",
    search_endpoint="projects/{product_id}/automation-hosts/search",
    single_endpoint="projects/{product_id}/automation-hosts/{artifact_id}",
    description="Automation hosts registered in a Spira product.",
    # Normalised field mappings
    status_field=None,
    owner_field=None,
    priority_field=None,
    release_field=None,
    type_field=None,
    summary_fields=[
        "AutomationHostId",
        "Name",
    ],
    # all_fields: LLM-visible fields from RemoteAutomationHost schema
    all_fields=[
        "Active",
        "AutomationHostId",
        "Description",
        "LastContactDate",
        "LastUpdateDate",
        "Name",
        "ProjectId",
        "Tags",
        "Token",
    ],
    # excluded_fields: valid OpenAPI fields hidden from LLM
    excluded_fields=[
        "ArtifactTypeId",
        "ConcurrencyDate",
        "CustomProperties",
        "Guid",
        "IsAttachments",
        "ProjectGuid",
    ],
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
