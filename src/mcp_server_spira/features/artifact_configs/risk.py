"""Risk artifact config — extracted from OpenAPI schema."""

from mcp_server_spira.models import ArtifactConfig, FieldMeta, Visibility

# Short aliases for readability in field_metadata
S = Visibility.SUMMARY
V = Visibility.VISIBLE
E = Visibility.EXCLUDED

RISK_CONFIG = ArtifactConfig(
    artifact_type="risk",
    workspace_type="product",
    search_endpoint="projects/{product_id}/risks/search",
    single_endpoint="projects/{product_id}/risks/{artifact_id}",
    description="Risks tracked in a Spira product.",
    field_metadata={
        "Name": FieldMeta("str", "The name of the risk", S),
        "OwnerName": FieldMeta(
            "str", "The name of the user that the risk is assigned to currently (read-only)", S
        ),
        "RiskId": FieldMeta("int", "The id of the risk", S),
        "RiskProbabilityName": FieldMeta("str", "The name of the risk probability (read-only)", S),
        "RiskStatusName": FieldMeta("str", "The name of the risk status (read-only)", S),
        "RiskTypeName": FieldMeta("str", "The name of the risk type (read-only)", S),
        "ClosedDate": FieldMeta("datetime", "The date the risk was closed (optional) (in UTC)", V),
        "ComponentId": FieldMeta(
            "int", "The id of the component the risk is associated with (optional)", V
        ),
        "ComponentName": FieldMeta("str", "The name of the component (read-only)", V),
        "CreationDate": FieldMeta("datetime", "The date the risk was created (in UTC)", V),
        "CreatorId": FieldMeta("int", "The id of the user that created the risk", V),
        "CreatorName": FieldMeta(
            "str", "The name of the user that created the risk (read-only)", V
        ),
        "Description": FieldMeta("str", "The description of the risk", V),
        "LastUpdateDate": FieldMeta(
            "datetime", "The date/time the risk was last updated (in UTC)", V
        ),
        "OwnerId": FieldMeta(
            "int", "The id of the user that the risk is assigned to currently (optional)", V
        ),
        "ProjectGroupId": FieldMeta("int", "The id of the project group (not used)", V),
        "ProjectId": FieldMeta("int", "The id of the project that the artifact belongs to", V),
        "ReleaseId": FieldMeta(
            "int", "The id of the release that the risk is currently assigned to (optional)", V
        ),
        "ReleaseName": FieldMeta(
            "str", "The name of the release that the risk is currently assigned to (read-only)", V
        ),
        "ReleaseVersionNumber": FieldMeta(
            "str",
            "The version number of the release that the risk is currently assigned to (read-only)",
            V,
        ),
        "ReviewDate": FieldMeta(
            "datetime", "The date/time the risk needs to be reviewed (in UTC)", V
        ),
        "RiskDetectabilityId": FieldMeta("int", "The id of the risk detectability (not used)", V),
        "RiskDetectabilityName": FieldMeta(
            "str", "The name of the risk detectability (not used)", V
        ),
        "RiskExposure": FieldMeta("int", "The calculated risk exposure score (read-only)", V),
        "RiskImpactId": FieldMeta("int", "The id of the risk impact (optional)", V),
        "RiskImpactName": FieldMeta("str", "The name of the risk impact (read-only)", V),
        "RiskProbabilityId": FieldMeta("int", "The id of the risk probability (optional)", V),
        "RiskStatusId": FieldMeta("int", "The id of the risk status (default if not populated)", V),
        "RiskTypeId": FieldMeta("int", "The id of the risk type (default if not populated)", V),
        "Tags": FieldMeta(
            "str", "The list of meta-tags that should be associated with the artifact", V
        ),
        "ArtifactTypeId": FieldMeta("int", "The type of artifact that we have", E),
        "ConcurrencyDate": FieldMeta(
            "datetime",
            "The datetime used to track optimistic concurrency to prevent edit conflicts",
            E,
        ),
        "CreatorGuid": FieldMeta("str", "The guid of the creator.", E),
        "CustomProperties": FieldMeta(
            "list", "The list of associated custom properties/fields for this artifact", E
        ),
        "GoalId": FieldMeta("int", "The id of the project goal (not used)", E),
        "Guid": FieldMeta("str", "The unique identifier for the artifact", E),
        "IsAttachments": FieldMeta("bool", "Does this artifact have any attachments?", E),
        "IsDeleted": FieldMeta("bool", "Is the risk deleted", E),
        "OwnerGuid": FieldMeta("str", "The guid of the owner.", E),
        "ProjectGuid": FieldMeta("str", "The guid of the project that the artifact belongs to", E),
        "ReleaseGuid": FieldMeta("str", "The guid of the release", E),
    },
    status_field="RiskStatusId",
    owner_field="OwnerId",
    priority_field=None,
    release_field="ReleaseId",
    type_field="RiskTypeId",
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
    includes=["mitigations", "comments", "associations"],
    comments_endpoint="projects/{product_id}/risks/{artifact_id}/comments",
    create_endpoint="projects/{product_id}/risks",
    id_field="RiskId",
    id_prefix="RK",
    required_fields=["Name", "Description"],
    writable_fields=[
        "ClosedDate",
        "ComponentId",
        "CreatorId",
        "Description",
        "Name",
        "OwnerId",
        "ReleaseId",
        "ReviewDate",
        "RiskImpactId",
        "RiskProbabilityId",
        "RiskStatusId",
        "RiskTypeId",
        "Tags",
    ],
    update_endpoint="projects/{product_id}/risks",
    resolvable_fields={
        "RiskStatusId": "statuses",
        "RiskTypeId": "types",
    },
)
