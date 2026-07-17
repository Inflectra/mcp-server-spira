"""Incident artifact config — extracted from OpenAPI schema."""

from mcp_server_spira.models import ArtifactConfig, FieldMeta, Visibility

# Short aliases for readability in field_metadata
S = Visibility.SUMMARY
V = Visibility.VISIBLE
E = Visibility.EXCLUDED

INCIDENT_CONFIG = ArtifactConfig(
    artifact_type="incident",
    workspace_type="product",
    search_endpoint="projects/{product_id}/incidents/search",
    single_endpoint="projects/{product_id}/incidents/{artifact_id}",
    description="Incidents (bugs, issues, defects) tracked in a Spira product.",
    field_metadata={
        "IncidentId": FieldMeta("int", "The id of the incident (integer)", S),
        "Name": FieldMeta("str", "The name of the incident (string)", S),
        "IncidentTypeName": FieldMeta(
            "str", "The display name of the type of the incident (string)", S
        ),
        "IncidentStatusName": FieldMeta(
            "str", "The display name of the status of the incident (string)", S
        ),
        "PriorityName": FieldMeta(
            "str", "The display name of the priority of the incident (string)", S
        ),
        "SeverityName": FieldMeta(
            "str", "The display name of the severity of the incident (string)", S
        ),
        "OwnerName": FieldMeta(
            "str", "The display name of the user that the incident is assigned to (string)", S
        ),
        "ResolvedReleaseVersionNumber": FieldMeta(
            "str",
            "The version number of the release/iteration that the incident will be resolved in (string)",
            S,
        ),
        "ActualEffort": FieldMeta(
            "int", "The actual effort (in minutes) it took to resolve the incident (integer)", V
        ),
        "ClosedDate": FieldMeta("datetime", "The date that the incident was closed (date-time)", V),
        "CompletionPercent": FieldMeta(
            "int",
            "The completion percentage (value = 0-100) of the incident as calculated in the system from the remaining effort vs. the original estimated effort. (integer)",
            V,
        ),
        "ComponentIds": FieldMeta(
            "list", "The list of components that this incident belongs to (array of integers)", V
        ),
        "CreationDate": FieldMeta(
            "datetime", "The date/time that the incident was originally created", V
        ),
        "Description": FieldMeta("str", "The description of the incident (string)", V),
        "DetectedReleaseId": FieldMeta(
            "int", "The id of the release/iteration that the incident was detected in (integer)", V
        ),
        "DetectedReleaseVersionNumber": FieldMeta(
            "str",
            "The version number of the release/iteration that the incident was detected in (string)",
            V,
        ),
        "EndDate": FieldMeta(
            "datetime", "The date that work is scheduled to finish on the incident (date-time)", V
        ),
        "EstimatedEffort": FieldMeta(
            "int", "The estimated effort (in minutes) to resolve the incident (integer)", V
        ),
        "IncidentStatusId": FieldMeta("int", "The id of the status of the incident (integer)", V),
        "IncidentStatusOpenStatus": FieldMeta(
            "bool", "Is the incident in an 'open' status or not?", V
        ),
        "IncidentTypeId": FieldMeta("int", "The id of the type of the incident (integer)", V),
        "LastUpdateDate": FieldMeta(
            "datetime", "The date/time that the incident was last modified (date-time)", V
        ),
        "OpenerId": FieldMeta("int", "The id of the user who detected the incident (integer)", V),
        "OpenerName": FieldMeta(
            "str", "The display name of the user that detected the incident (string)", V
        ),
        "OwnerId": FieldMeta(
            "int", "The id of the user to the incident is assigned-to (integer)", V
        ),
        "PriorityId": FieldMeta("int", "The id of the priority of the incident (integer)", V),
        "ProjectedEffort": FieldMeta(
            "int", "The projected actual effort of the incident when it is completed (integer)", V
        ),
        "ProjectId": FieldMeta("int", "The id of the project that the artifact belongs to", V),
        "ProjectName": FieldMeta(
            "str", "The display name of the project the incident belongs to (string)", V
        ),
        "RemainingEffort": FieldMeta("int", "The effort remaining as reported by the developer", V),
        "ResolvedReleaseId": FieldMeta(
            "int", "The id of the release/iteration that the incident will be fixed in (integer)", V
        ),
        "SeverityId": FieldMeta("int", "The id of the severity of the incident (integer)", V),
        "StartDate": FieldMeta(
            "datetime", "The date that work started on the incident (date-time)", V
        ),
        "Tags": FieldMeta(
            "str", "The list of meta-tags that should be associated with the artifact", V
        ),
        "VerifiedReleaseId": FieldMeta(
            "int", "The id of the release/iteration that the incident was retested in (integer)", V
        ),
        "VerifiedReleaseVersionNumber": FieldMeta(
            "str",
            "The version number of the release/iteration that the incident was retested in (string)",
            V,
        ),
        "ArtifactTypeId": FieldMeta("int", "The type of artifact that we have", E),
        "ConcurrencyDate": FieldMeta(
            "datetime",
            "The datetime used to track optimistic concurrency to prevent edit conflicts",
            E,
        ),
        "CustomProperties": FieldMeta(
            "list", "The list of associated custom properties/fields for this artifact", E
        ),
        "DetectedBuildId": FieldMeta(
            "int", "The id of the build that the incident was detected in (integer)", E
        ),
        "DetectedBuildName": FieldMeta(
            "str", "The name of the build that the incident was detected in (string)", E
        ),
        "DetectedReleaseGuid": FieldMeta("str", "The guid of the Detected release", E),
        "FixedBuildId": FieldMeta(
            "int", "The id of the build that the incident was fixed in (integer)", E
        ),
        "FixedBuildName": FieldMeta(
            "str", "The name of the build that the incident was fixed in (string)", E
        ),
        "Guid": FieldMeta("str", "The unique identifier for the artifact", E),
        "IsAttachments": FieldMeta("bool", "Does this artifact have any attachments?", E),
        "OpenerGuid": FieldMeta("str", "The guid of the opener.", E),
        "OwnerGuid": FieldMeta("str", "The guid of the owner.", E),
        "ProjectGuid": FieldMeta("str", "The guid of the project that the artifact belongs to", E),
        "ResolvedReleaseGuid": FieldMeta("str", "The guid of the Resolved release", E),
        "TestRunStepIds": FieldMeta(
            "list", "The id of the test run steps that the incident relates to (integer)", E
        ),
        "VerifiedReleaseGuid": FieldMeta("str", "The guid of the Verified release", E),
    },
    status_field="IncidentStatusId",
    owner_field="OwnerId",
    priority_field="PriorityId",
    release_field="ResolvedReleaseId",
    type_field="IncidentTypeId",
    supports_server_search=True,
    mywork_endpoint="incidents",
    search_query_params={
        "row_start": "start_row",
        "row_count": "number_rows",
        "sort_by": "sort_by",
    },
    default_sort_field="LastUpdateDate",
    default_sort_direction="desc",
    create_endpoint="projects/{product_id}/incidents",
    id_field="IncidentId",
    id_prefix="IN",
    required_fields=["Name", "Description"],
    writable_fields=[
        "ActualEffort",
        "ClosedDate",
        "CompletionPercent",
        "ComponentIds",
        "CustomProperties",
        "Description",
        "DetectedBuildId",
        "DetectedReleaseId",
        "EndDate",
        "EstimatedEffort",
        "FixedBuildId",
        "IncidentStatusId",
        "IncidentTypeId",
        "Name",
        "OpenerId",
        "OwnerId",
        "PriorityId",
        "ProjectedEffort",
        "RemainingEffort",
        "ResolvedReleaseId",
        "SeverityId",
        "StartDate",
        "Tags",
        "VerifiedReleaseId",
    ],
    update_endpoint="projects/{product_id}/incidents/{artifact_id}",
    resolvable_fields={
        "PriorityId": "priorities",
        "IncidentStatusId": "statuses",
        "IncidentTypeId": "types",
        "SeverityId": "severities",
    },
    includes=["comments", "associations"],
    comments_endpoint="projects/{product_id}/incidents/{artifact_id}/comments",
    comments_body_is_array=True,
)
