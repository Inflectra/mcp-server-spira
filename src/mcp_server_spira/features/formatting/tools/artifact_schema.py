"""Artifact schema tool — returns hardcoded field schema data for Spira artifact types."""

import json

VALID_ARTIFACT_TYPES: tuple[str, ...] = (
    "task",
    "incident",
    "requirement",
    "test_case",
    "release",
    "risk",
    "test_set",
    "test_run",
    "automation_host",
    "capability",
    "milestone",
)

# Schemas transcribed from SpiraRestAPI-v7.0-OpenAPI.json components/schemas
# Type mapping: integer→int, string→str, boolean→bool, string/date-time→datetime, array→list
ARTIFACT_SCHEMAS: dict[str, dict] = {
    "task": {
        "artifact_type": "task",
        "fields": [
            {"name": "TaskId", "type": "int", "description": "The id of the task"},
            {
                "name": "TaskStatusId",
                "type": "int",
                "description": "The id of the status of the task",
            },
            {
                "name": "TaskTypeId",
                "type": "int",
                "description": "The id of the type of the task (null for default)",
            },
            {
                "name": "TaskFolderId",
                "type": "int",
                "description": "The of the folder the task is stored in (null for root)",
            },
            {
                "name": "RequirementId",
                "type": "int",
                "description": "The id of the parent requirement that the task belongs to",
            },
            {
                "name": "ReleaseId",
                "type": "int",
                "description": "The id of the release/iteration that the task is scheduled for",
            },
            {"name": "ReleaseGuid", "type": "str", "description": "The guid of the release"},
            {
                "name": "ComponentId",
                "type": "int",
                "description": "The id of the component that this task belongs to",
            },
            {
                "name": "CreatorId",
                "type": "int",
                "description": "The id of the user that originally created the task",
            },
            {
                "name": "OwnerId",
                "type": "int",
                "description": "The id of the user that the task is assigned-to",
            },
            {"name": "CreatorGuid", "type": "str", "description": "The guid of the creator."},
            {"name": "OwnerGuid", "type": "str", "description": "The guid of the owner."},
            {
                "name": "TaskPriorityId",
                "type": "int",
                "description": "The id of the priority of the task",
            },
            {"name": "Name", "type": "str", "description": "The name of the task"},
            {
                "name": "Description",
                "type": "str",
                "description": "The detailed description of the task",
            },
            {
                "name": "CreationDate",
                "type": "datetime",
                "description": "The date/time that the task was originally created",
            },
            {
                "name": "LastUpdateDate",
                "type": "datetime",
                "description": "The date/time that the task was last modified",
            },
            {
                "name": "StartDate",
                "type": "datetime",
                "description": "The scheduled start date for the task",
            },
            {
                "name": "EndDate",
                "type": "datetime",
                "description": "The scheduled end date for the task",
            },
            {
                "name": "CompletionPercent",
                "type": "int",
                "description": "The completion percentage (value = 0-100) of the task as calculated in the system from the remaining effort vs. the original estimated effort.",
            },
            {
                "name": "EstimatedEffort",
                "type": "int",
                "description": "The originally estimated effort (in minutes) of the task",
            },
            {
                "name": "ActualEffort",
                "type": "int",
                "description": "The actual effort expended so far (in minutes) for the task",
            },
            {
                "name": "RemainingEffort",
                "type": "int",
                "description": "The effort remaining as reported by the developer",
            },
            {
                "name": "ProjectedEffort",
                "type": "int",
                "description": "The projected actual effort of the task when it is completed",
            },
            {
                "name": "TaskStatusName",
                "type": "str",
                "description": "The display name of the status of the task",
            },
            {
                "name": "TaskTypeName",
                "type": "str",
                "description": "The display name of the type of the task",
            },
            {
                "name": "OwnerName",
                "type": "str",
                "description": "The display name of the user who the task is assigned-to",
            },
            {
                "name": "TaskPriorityName",
                "type": "str",
                "description": "The display name of the priority of the task",
            },
            {
                "name": "ProjectName",
                "type": "str",
                "description": "The display name of the project the task belongs to",
            },
            {
                "name": "ReleaseVersionNumber",
                "type": "str",
                "description": "The version number of the release/iteration the task is scheduled for",
            },
            {
                "name": "RequirementName",
                "type": "str",
                "description": "The name of the requirement that the task is associated with",
            },
            {
                "name": "RiskId",
                "type": "int",
                "description": "The risk that the task is associated with",
            },
            {
                "name": "ProjectId",
                "type": "int",
                "description": "The id of the project that the artifact belongs to",
            },
            {
                "name": "ProjectGuid",
                "type": "str",
                "description": "The guid of the project that the artifact belongs to",
            },
            {
                "name": "ArtifactTypeId",
                "type": "int",
                "description": "The type of artifact that we have",
            },
            {
                "name": "ConcurrencyDate",
                "type": "datetime",
                "description": "The datetime used to track optimistic concurrency to prevent edit conflicts",
            },
            {
                "name": "CustomProperties",
                "type": "list",
                "description": "The list of associated custom properties/fields for this artifact",
            },
            {
                "name": "IsAttachments",
                "type": "bool",
                "description": "Does this artifact have any attachments?",
            },
            {
                "name": "Tags",
                "type": "str",
                "description": "The list of meta-tags that should be associated with the artifact",
            },
            {
                "name": "Guid",
                "type": "str",
                "description": "The unique identifier for the artifact",
            },
        ],
    },
    "incident": {
        "artifact_type": "incident",
        "fields": [
            {
                "name": "IncidentId",
                "type": "int",
                "description": "The id of the incident (integer)",
            },
            {
                "name": "PriorityId",
                "type": "int",
                "description": "The id of the priority of the incident (integer)",
            },
            {
                "name": "SeverityId",
                "type": "int",
                "description": "The id of the severity of the incident (integer)",
            },
            {
                "name": "IncidentStatusId",
                "type": "int",
                "description": "The id of the status of the incident (integer)",
            },
            {
                "name": "IncidentTypeId",
                "type": "int",
                "description": "The id of the type of the incident (integer)",
            },
            {
                "name": "OpenerId",
                "type": "int",
                "description": "The id of the user who detected the incident (integer)",
            },
            {
                "name": "OwnerId",
                "type": "int",
                "description": "The id of the user to the incident is assigned-to (integer)",
            },
            {"name": "OpenerGuid", "type": "str", "description": "The guid of the opener."},
            {"name": "OwnerGuid", "type": "str", "description": "The guid of the owner."},
            {
                "name": "TestRunStepIds",
                "type": "list",
                "description": "The id of the test run steps that the incident relates to (integer)",
            },
            {
                "name": "DetectedReleaseId",
                "type": "int",
                "description": "The id of the release/iteration that the incident was detected in (integer)",
            },
            {
                "name": "ResolvedReleaseId",
                "type": "int",
                "description": "The id of the release/iteration that the incident will be fixed in (integer)",
            },
            {
                "name": "VerifiedReleaseId",
                "type": "int",
                "description": "The id of the release/iteration that the incident was retested in (integer)",
            },
            {
                "name": "DetectedReleaseGuid",
                "type": "str",
                "description": "The guid of the Detected release",
            },
            {
                "name": "ResolvedReleaseGuid",
                "type": "str",
                "description": "The guid of the Resolved release",
            },
            {
                "name": "VerifiedReleaseGuid",
                "type": "str",
                "description": "The guid of the Verified release",
            },
            {
                "name": "ComponentIds",
                "type": "list",
                "description": "The list of components that this incident belongs to (array of integers)",
            },
            {"name": "Name", "type": "str", "description": "The name of the incident (string)"},
            {
                "name": "Description",
                "type": "str",
                "description": "The description of the incident (string)",
            },
            {
                "name": "CreationDate",
                "type": "datetime",
                "description": "The date/time that the incident was originally created",
            },
            {
                "name": "StartDate",
                "type": "datetime",
                "description": "The date that work started on the incident (date-time)",
            },
            {
                "name": "EndDate",
                "type": "datetime",
                "description": "The date that work is scheduled to finish on the incident (date-time)",
            },
            {
                "name": "ClosedDate",
                "type": "datetime",
                "description": "The date that the incident was closed (date-time)",
            },
            {
                "name": "CompletionPercent",
                "type": "int",
                "description": "The completion percentage (value = 0-100) of the incident as calculated in the system from the remaining effort vs. the original estimated effort. (integer)",
            },
            {
                "name": "EstimatedEffort",
                "type": "int",
                "description": "The estimated effort (in minutes) to resolve the incident (integer)",
            },
            {
                "name": "ActualEffort",
                "type": "int",
                "description": "The actual effort (in minutes) it took to resolve the incident (integer)",
            },
            {
                "name": "RemainingEffort",
                "type": "int",
                "description": "The effort remaining as reported by the developer",
            },
            {
                "name": "ProjectedEffort",
                "type": "int",
                "description": "The projected actual effort of the incident when it is completed (integer)",
            },
            {
                "name": "LastUpdateDate",
                "type": "datetime",
                "description": "The date/time that the incident was last modified (date-time)",
            },
            {
                "name": "PriorityName",
                "type": "str",
                "description": "The display name of the priority of the incident (string)",
            },
            {
                "name": "SeverityName",
                "type": "str",
                "description": "The display name of the severity of the incident (string)",
            },
            {
                "name": "IncidentStatusName",
                "type": "str",
                "description": "The display name of the status of the incident (string)",
            },
            {
                "name": "IncidentTypeName",
                "type": "str",
                "description": "The display name of the type of the incident (string)",
            },
            {
                "name": "OpenerName",
                "type": "str",
                "description": "The display name of the user that detected the incident (string)",
            },
            {
                "name": "OwnerName",
                "type": "str",
                "description": "The display name of the user that the incident is assigned to (string)",
            },
            {
                "name": "ProjectName",
                "type": "str",
                "description": "The display name of the project the incident belongs to (string)",
            },
            {
                "name": "DetectedReleaseVersionNumber",
                "type": "str",
                "description": "The version number of the release/iteration that the incident was detected in (string)",
            },
            {
                "name": "ResolvedReleaseVersionNumber",
                "type": "str",
                "description": "The version number of the release/iteration that the incident will be resolved in (string)",
            },
            {
                "name": "VerifiedReleaseVersionNumber",
                "type": "str",
                "description": "The version number of the release/iteration that the incident was retested in (string)",
            },
            {
                "name": "IncidentStatusOpenStatus",
                "type": "bool",
                "description": "Is the incident in an 'open' status or not?",
            },
            {
                "name": "FixedBuildId",
                "type": "int",
                "description": "The id of the build that the incident was fixed in (integer)",
            },
            {
                "name": "FixedBuildName",
                "type": "str",
                "description": "The name of the build that the incident was fixed in (string)",
            },
            {
                "name": "DetectedBuildId",
                "type": "int",
                "description": "The id of the build that the incident was detected in (integer)",
            },
            {
                "name": "DetectedBuildName",
                "type": "str",
                "description": "The name of the build that the incident was detected in (string)",
            },
            {
                "name": "ProjectId",
                "type": "int",
                "description": "The id of the project that the artifact belongs to",
            },
            {
                "name": "ProjectGuid",
                "type": "str",
                "description": "The guid of the project that the artifact belongs to",
            },
            {
                "name": "ArtifactTypeId",
                "type": "int",
                "description": "The type of artifact that we have",
            },
            {
                "name": "ConcurrencyDate",
                "type": "datetime",
                "description": "The datetime used to track optimistic concurrency to prevent edit conflicts",
            },
            {
                "name": "CustomProperties",
                "type": "list",
                "description": "The list of associated custom properties/fields for this artifact",
            },
            {
                "name": "IsAttachments",
                "type": "bool",
                "description": "Does this artifact have any attachments?",
            },
            {
                "name": "Tags",
                "type": "str",
                "description": "The list of meta-tags that should be associated with the artifact",
            },
            {
                "name": "Guid",
                "type": "str",
                "description": "The unique identifier for the artifact",
            },
        ],
    },
    "requirement": {
        "artifact_type": "requirement",
        "fields": [
            {
                "name": "RequirementId",
                "type": "int",
                "description": "The id of the requirement (integer)",
            },
            {
                "name": "IndentLevel",
                "type": "str",
                "description": "The indentation level of the artifact (string)",
            },
            {
                "name": "StatusId",
                "type": "int",
                "description": "The id of the requirement's status (integer).",
            },
            {
                "name": "RequirementTypeId",
                "type": "int",
                "description": "The type of requirement (integer).",
            },
            {
                "name": "AuthorId",
                "type": "int",
                "description": "The id of the user that wrote the requirement (integer)",
            },
            {
                "name": "OwnerId",
                "type": "int",
                "description": "The id of the user that the requirement is assigned-to (integer)",
            },
            {"name": "AuthorGuid", "type": "str", "description": "The guid of the author."},
            {"name": "OwnerGuid", "type": "str", "description": "The guid of the owner."},
            {
                "name": "ImportanceId",
                "type": "int",
                "description": "The id of the importance of the requirement (integer)",
            },
            {
                "name": "ReleaseId",
                "type": "int",
                "description": "The id of the release the requirement is scheduled to implemented in (integer)",
            },
            {"name": "ReleaseGuid", "type": "str", "description": "The guid of the release"},
            {
                "name": "ComponentId",
                "type": "int",
                "description": "The id of the component the requirement is a part of (integer - these are created on a per project user by an administrator)",
            },
            {
                "name": "Name",
                "type": "str",
                "description": "The name of the requirement (string - required for POST)",
            },
            {
                "name": "Description",
                "type": "str",
                "description": "The description of the requirement (string)",
            },
            {
                "name": "CreationDate",
                "type": "datetime",
                "description": "The date/time the requirement was originally created (date-time)",
            },
            {
                "name": "LastUpdateDate",
                "type": "datetime",
                "description": "The date/time the requirement was last modified (date-time)",
            },
            {
                "name": "Summary",
                "type": "bool",
                "description": "Is this a summary requirement or not (boolean)",
            },
            {
                "name": "CoverageCountTotal",
                "type": "int",
                "description": "How many test cases cover this requirement (integer)",
            },
            {
                "name": "CoverageCountPassed",
                "type": "int",
                "description": "How many of the test cases that cover this requirement have passed (integer)",
            },
            {
                "name": "CoverageCountFailed",
                "type": "int",
                "description": "How many of the test cases that cover this requirement have failed (integer)",
            },
            {
                "name": "CoverageCountCaution",
                "type": "int",
                "description": "How many of the test cases that cover this requirement have been marked as caution (integer)",
            },
            {
                "name": "CoverageCountBlocked",
                "type": "int",
                "description": "How many of the test cases that cover this requirement have blocked (integer)",
            },
            {
                "name": "EstimatePoints",
                "type": "str",
                "description": "The estimate of the requirement (decimal - in story points)",
            },
            {
                "name": "EstimatedEffort",
                "type": "int",
                "description": "What was the original top-down level of effort estimated for this requirement, calculated from the points estimate (integer)",
            },
            {
                "name": "TaskEstimatedEffort",
                "type": "int",
                "description": "What is the bottom-up estimated effort for all the tasks associated with this requirement (integer)",
            },
            {
                "name": "TaskActualEffort",
                "type": "int",
                "description": "What is the bottom-up actual effort for all the tasks associated with this requirement (integer)",
            },
            {
                "name": "TaskCount",
                "type": "int",
                "description": "How many tasks are associated with this requirement (integer)",
            },
            {
                "name": "ReleaseVersionNumber",
                "type": "str",
                "description": "The version number string of the release that the requirement is scheduled for (string)",
            },
            {
                "name": "AuthorName",
                "type": "str",
                "description": "The display name of the user that wrote this requirement (string)",
            },
            {
                "name": "OwnerName",
                "type": "str",
                "description": "The display name of the user that this requirement is assigned-to (string)",
            },
            {
                "name": "StatusName",
                "type": "str",
                "description": "The display name of the status the requirement is in (string)",
            },
            {
                "name": "ImportanceName",
                "type": "str",
                "description": "The display name of the importance that the requirement is in (string)",
            },
            {
                "name": "ProjectName",
                "type": "str",
                "description": "The display name of the project that the requirement is associated with (string)",
            },
            {
                "name": "RequirementTypeName",
                "type": "str",
                "description": "The display name of the type of requirement (string)",
            },
            {
                "name": "Steps",
                "type": "list",
                "description": "The list of scenarios steps (array - only available for Use Case requirement types)",
            },
            {
                "name": "StartDate",
                "type": "datetime",
                "description": "The start date of the requirement for planning purposes",
            },
            {
                "name": "EndDate",
                "type": "datetime",
                "description": "The end date of the requirement for planning purposes",
            },
            {
                "name": "PercentComplete",
                "type": "int",
                "description": "The percentage complete of the requirement",
            },
            {
                "name": "GoalId",
                "type": "int",
                "description": "The id of the goal that the requirement belongs to",
            },
            {
                "name": "IsSuspect",
                "type": "bool",
                "description": "Is the requirement marked as suspect due to dependent item changes",
            },
            {
                "name": "ProjectId",
                "type": "int",
                "description": "The id of the project that the artifact belongs to",
            },
            {
                "name": "ProjectGuid",
                "type": "str",
                "description": "The guid of the project that the artifact belongs to",
            },
            {
                "name": "ArtifactTypeId",
                "type": "int",
                "description": "The type of artifact that we have",
            },
            {
                "name": "ConcurrencyDate",
                "type": "datetime",
                "description": "The datetime used to track optimistic concurrency to prevent edit conflicts",
            },
            {
                "name": "CustomProperties",
                "type": "list",
                "description": "The list of associated custom properties/fields for this artifact",
            },
            {
                "name": "IsAttachments",
                "type": "bool",
                "description": "Does this artifact have any attachments?",
            },
            {
                "name": "Tags",
                "type": "str",
                "description": "The list of meta-tags that should be associated with the artifact",
            },
            {
                "name": "Guid",
                "type": "str",
                "description": "The unique identifier for the artifact",
            },
        ],
    },
    "test_case": {
        "artifact_type": "test_case",
        "fields": [
            {"name": "TestCaseId", "type": "int", "description": "The id of the test case"},
            {
                "name": "ExecutionStatusId",
                "type": "int",
                "description": "The execution status id of the test case",
            },
            {
                "name": "AuthorId",
                "type": "int",
                "description": "The id of the user that wrote the test case",
            },
            {
                "name": "OwnerId",
                "type": "int",
                "description": "The id of the user that the test case is assigned-to",
            },
            {"name": "AuthorGuid", "type": "str", "description": "The guid of the author."},
            {"name": "OwnerGuid", "type": "str", "description": "The guid of the owner."},
            {
                "name": "TestCasePriorityId",
                "type": "int",
                "description": "The id of the priority of the test case",
            },
            {
                "name": "TestCaseTypeId",
                "type": "int",
                "description": "The type of test case, pass null to use the default value",
            },
            {
                "name": "TestCaseStatusId",
                "type": "int",
                "description": "The status of the test case, pass 0 to use the default value",
            },
            {
                "name": "TestCaseFolderId",
                "type": "int",
                "description": "The id of the folder the test case belongs to. Null = root folder",
            },
            {
                "name": "ComponentIds",
                "type": "list",
                "description": "The list of components that this test case belongs to",
            },
            {
                "name": "AutomationEngineId",
                "type": "int",
                "description": "The id of the automation engine the associated test script uses (null if manual only)",
            },
            {
                "name": "AutomationAttachmentId",
                "type": "int",
                "description": "The id of the attachment that is being used to store the test script (file or url)",
            },
            {"name": "Name", "type": "str", "description": "The name of the test case"},
            {
                "name": "Description",
                "type": "str",
                "description": "The description of the test case",
            },
            {
                "name": "CreationDate",
                "type": "datetime",
                "description": "The date the test case was created",
            },
            {
                "name": "LastUpdateDate",
                "type": "datetime",
                "description": "The date the test case was last updated",
            },
            {
                "name": "ExecutionDate",
                "type": "datetime",
                "description": "The date the test case was last executed",
            },
            {
                "name": "EstimatedDuration",
                "type": "int",
                "description": "The estimated time to execute the test case",
            },
            {
                "name": "AuthorName",
                "type": "str",
                "description": "The display name of the user that wrote the test case",
            },
            {
                "name": "OwnerName",
                "type": "str",
                "description": "The display name of the user that the test case is assigned-to",
            },
            {
                "name": "ProjectName",
                "type": "str",
                "description": "The display name of the project that the test case belongs to",
            },
            {
                "name": "TestCasePriorityName",
                "type": "str",
                "description": "The display name of the priority of the test case",
            },
            {
                "name": "TestCaseStatusName",
                "type": "str",
                "description": "The display name of the status of the test case",
            },
            {
                "name": "TestCaseTypeName",
                "type": "str",
                "description": "The display name of the type of the test case",
            },
            {
                "name": "ExecutionStatusName",
                "type": "str",
                "description": "The display name of the execution status",
            },
            {
                "name": "TestSteps",
                "type": "list",
                "description": "The list of test steps that comprise the test case",
            },
            {
                "name": "ActualDuration",
                "type": "int",
                "description": "The actual result from the most recent test run of the this test case",
            },
            {
                "name": "IsSuspect",
                "type": "bool",
                "description": "Have any of the requirements associated with this test case changed",
            },
            {
                "name": "IsTestSteps",
                "type": "bool",
                "description": "Does this test case have steps",
            },
            {
                "name": "ProjectId",
                "type": "int",
                "description": "The id of the project that the artifact belongs to",
            },
            {
                "name": "ProjectGuid",
                "type": "str",
                "description": "The guid of the project that the artifact belongs to",
            },
            {
                "name": "ArtifactTypeId",
                "type": "int",
                "description": "The type of artifact that we have",
            },
            {
                "name": "ConcurrencyDate",
                "type": "datetime",
                "description": "The datetime used to track optimistic concurrency to prevent edit conflicts",
            },
            {
                "name": "CustomProperties",
                "type": "list",
                "description": "The list of associated custom properties/fields for this artifact",
            },
            {
                "name": "IsAttachments",
                "type": "bool",
                "description": "Does this artifact have any attachments?",
            },
            {
                "name": "Tags",
                "type": "str",
                "description": "The list of meta-tags that should be associated with the artifact",
            },
            {
                "name": "Guid",
                "type": "str",
                "description": "The unique identifier for the artifact",
            },
        ],
    },
    "release": {
        "artifact_type": "release",
        "fields": [
            {"name": "ReleaseId", "type": "int", "description": "The id of the release"},
            {
                "name": "CreatorId",
                "type": "int",
                "description": "The id of the user that created the release",
            },
            {
                "name": "OwnerId",
                "type": "int",
                "description": "The id of the user that the release is assigned to",
            },
            {"name": "CreatorGuid", "type": "str", "description": "The guid of the creator."},
            {"name": "OwnerGuid", "type": "str", "description": "The guid of the owner."},
            {
                "name": "OwnerName",
                "type": "str",
                "description": "The name of the user that the release is assigned to",
            },
            {
                "name": "IndentLevel",
                "type": "str",
                "description": "The indentation level of the artifact",
            },
            {"name": "Name", "type": "str", "description": "The name of the release"},
            {"name": "Description", "type": "str", "description": "The description of the release"},
            {
                "name": "VersionNumber",
                "type": "str",
                "description": "The version number string of the release",
            },
            {
                "name": "CreationDate",
                "type": "datetime",
                "description": "The date the release was originally created",
            },
            {
                "name": "LastUpdateDate",
                "type": "datetime",
                "description": "The date the release was last modified",
            },
            {
                "name": "Summary",
                "type": "bool",
                "description": "Is this release a summary one (i.e. does it have child releases)",
            },
            {
                "name": "Active",
                "type": "bool",
                "description": "Is this release active for the project",
            },
            {"name": "ReleaseStatusId", "type": "int", "description": "The status of the release"},
            {"name": "ReleaseTypeId", "type": "int", "description": "The type of the release"},
            {
                "name": "StartDate",
                "type": "datetime",
                "description": "What is the start date for the release",
            },
            {
                "name": "EndDate",
                "type": "datetime",
                "description": "What is the end date for the release",
            },
            {
                "name": "ResourceCount",
                "type": "str",
                "description": "How many people are working on the release",
            },
            {
                "name": "DaysNonWorking",
                "type": "str",
                "description": "How many non-working days are associated with the release",
            },
            {
                "name": "PlannedEffort",
                "type": "int",
                "description": "What is the estimated planned effort associated with the release",
            },
            {
                "name": "AvailableEffort",
                "type": "int",
                "description": "How much effort is still available in the release for planning",
            },
            {
                "name": "TaskEstimatedEffort",
                "type": "int",
                "description": "How much effort was estimated for all the tasks scheduled for this release",
            },
            {
                "name": "TaskActualEffort",
                "type": "int",
                "description": "How much effort was actually expended for all the tasks scheduled for this release",
            },
            {
                "name": "TaskCount",
                "type": "int",
                "description": "How many tasks are scheduled for this release",
            },
            {
                "name": "CreatorName",
                "type": "str",
                "description": "What is the full display name of the person who created this release",
            },
            {
                "name": "FullName",
                "type": "str",
                "description": "The full name and version number of the release combined",
            },
            {
                "name": "ReleaseStatusName",
                "type": "str",
                "description": "The display name for the release status",
            },
            {
                "name": "ReleaseTypeName",
                "type": "str",
                "description": "The display name for the release type",
            },
            {
                "name": "CountBlocked",
                "type": "int",
                "description": "The count of blocked test cases in this release",
            },
            {
                "name": "CountCaution",
                "type": "int",
                "description": "The count of caution test cases in this release",
            },
            {
                "name": "CountFailed",
                "type": "int",
                "description": "The count of failed test cases in this release",
            },
            {
                "name": "CountNotApplicable",
                "type": "int",
                "description": "The count of N/A test cases in this release",
            },
            {
                "name": "CountNotRun",
                "type": "int",
                "description": "The count of not run test cases in this release",
            },
            {
                "name": "CountPassed",
                "type": "int",
                "description": "The count of passed test cases in this release",
            },
            {
                "name": "PercentComplete",
                "type": "int",
                "description": "The percentage complete of the project/sprint",
            },
            {
                "name": "RequirementCount",
                "type": "int",
                "description": "Number of requirements assigned to this release",
            },
            {
                "name": "RequirementPoints",
                "type": "str",
                "description": "Number of effort points assigned to the requirements of this release",
            },
            {
                "name": "ProjectId",
                "type": "int",
                "description": "The id of the project that the artifact belongs to",
            },
            {
                "name": "ProjectGuid",
                "type": "str",
                "description": "The guid of the project that the artifact belongs to",
            },
            {
                "name": "ArtifactTypeId",
                "type": "int",
                "description": "The type of artifact that we have",
            },
            {
                "name": "ConcurrencyDate",
                "type": "datetime",
                "description": "The datetime used to track optimistic concurrency to prevent edit conflicts",
            },
            {
                "name": "CustomProperties",
                "type": "list",
                "description": "The list of associated custom properties/fields for this artifact",
            },
            {
                "name": "IsAttachments",
                "type": "bool",
                "description": "Does this artifact have any attachments?",
            },
            {
                "name": "Tags",
                "type": "str",
                "description": "The list of meta-tags that should be associated with the artifact",
            },
            {
                "name": "Guid",
                "type": "str",
                "description": "The unique identifier for the artifact",
            },
        ],
    },
    "risk": {
        "artifact_type": "risk",
        "fields": [
            {"name": "RiskId", "type": "int", "description": "The id of the risk"},
            {
                "name": "ClosedDate",
                "type": "datetime",
                "description": "The date the risk was closed (optional) (in UTC)",
            },
            {
                "name": "ComponentId",
                "type": "int",
                "description": "The id of the component the risk is associated with (optional)",
            },
            {
                "name": "ComponentName",
                "type": "str",
                "description": "The name of the component (read-only)",
            },
            {
                "name": "CreationDate",
                "type": "datetime",
                "description": "The date the risk was created (in UTC)",
            },
            {
                "name": "CreatorId",
                "type": "int",
                "description": "The id of the user that created the risk",
            },
            {"name": "CreatorGuid", "type": "str", "description": "The guid of the creator."},
            {
                "name": "CreatorName",
                "type": "str",
                "description": "The name of the user that created the risk (read-only)",
            },
            {"name": "Description", "type": "str", "description": "The description of the risk"},
            {"name": "IsDeleted", "type": "bool", "description": "Is the risk deleted"},
            {
                "name": "LastUpdateDate",
                "type": "datetime",
                "description": "The date/time the risk was last updated (in UTC)",
            },
            {"name": "Name", "type": "str", "description": "The name of the risk"},
            {
                "name": "OwnerId",
                "type": "int",
                "description": "The id of the user that the risk is assigned to currently (optional)",
            },
            {"name": "OwnerGuid", "type": "str", "description": "The guid of the owner."},
            {
                "name": "OwnerName",
                "type": "str",
                "description": "The name of the user that the risk is assigned to currently (read-only)",
            },
            {
                "name": "ReleaseId",
                "type": "int",
                "description": "The id of the release that the risk is currently assigned to (optional)",
            },
            {
                "name": "ReleaseName",
                "type": "str",
                "description": "The name of the release that the risk is currently assigned to (read-only)",
            },
            {
                "name": "ReleaseVersionNumber",
                "type": "str",
                "description": "The version number of the release that the risk is currently assigned to (read-only)",
            },
            {"name": "ReleaseGuid", "type": "str", "description": "The guid of the release"},
            {
                "name": "ReviewDate",
                "type": "datetime",
                "description": "The date/time the risk needs to be reviewed (in UTC)",
            },
            {
                "name": "RiskImpactId",
                "type": "int",
                "description": "The id of the risk impact (optional)",
            },
            {
                "name": "RiskImpactName",
                "type": "str",
                "description": "The name of the risk impact (read-only)",
            },
            {
                "name": "RiskProbabilityId",
                "type": "int",
                "description": "The id of the risk probability (optional)",
            },
            {
                "name": "RiskProbabilityName",
                "type": "str",
                "description": "The name of the risk probability (read-only)",
            },
            {
                "name": "RiskStatusId",
                "type": "int",
                "description": "The id of the risk status (default if not populated)",
            },
            {
                "name": "RiskStatusName",
                "type": "str",
                "description": "The name of the risk status (read-only)",
            },
            {
                "name": "RiskTypeId",
                "type": "int",
                "description": "The id of the risk type (default if not populated)",
            },
            {
                "name": "RiskTypeName",
                "type": "str",
                "description": "The name of the risk type (read-only)",
            },
            {
                "name": "RiskExposure",
                "type": "int",
                "description": "The calculated risk exposure score (read-only)",
            },
            {
                "name": "ProjectGroupId",
                "type": "int",
                "description": "The id of the project group (not used)",
            },
            {
                "name": "RiskDetectabilityId",
                "type": "int",
                "description": "The id of the risk detectability (not used)",
            },
            {
                "name": "RiskDetectabilityName",
                "type": "str",
                "description": "The name of the risk detectability (not used)",
            },
            {
                "name": "GoalId",
                "type": "int",
                "description": "The id of the project goal (not used)",
            },
            {
                "name": "ProjectId",
                "type": "int",
                "description": "The id of the project that the artifact belongs to",
            },
            {
                "name": "ProjectGuid",
                "type": "str",
                "description": "The guid of the project that the artifact belongs to",
            },
            {
                "name": "ArtifactTypeId",
                "type": "int",
                "description": "The type of artifact that we have",
            },
            {
                "name": "ConcurrencyDate",
                "type": "datetime",
                "description": "The datetime used to track optimistic concurrency to prevent edit conflicts",
            },
            {
                "name": "CustomProperties",
                "type": "list",
                "description": "The list of associated custom properties/fields for this artifact",
            },
            {
                "name": "IsAttachments",
                "type": "bool",
                "description": "Does this artifact have any attachments?",
            },
            {
                "name": "Tags",
                "type": "str",
                "description": "The list of meta-tags that should be associated with the artifact",
            },
            {
                "name": "Guid",
                "type": "str",
                "description": "The unique identifier for the artifact",
            },
        ],
    },
    "test_set": {
        "artifact_type": "test_set",
        "fields": [
            {"name": "TestSetId", "type": "int", "description": "The id of the test set"},
            {
                "name": "IndentLevel",
                "type": "str",
                "description": "(Not used in this version of the API)",
            },
            {
                "name": "TestSetStatusId",
                "type": "int",
                "description": "The id of the test set's status",
            },
            {
                "name": "CreatorId",
                "type": "int",
                "description": "The id of the user who created the test set",
            },
            {
                "name": "OwnerId",
                "type": "int",
                "description": "The id of the user who the test set is assigned-to",
            },
            {"name": "CreatorGuid", "type": "str", "description": "The guid of the creator."},
            {"name": "OwnerGuid", "type": "str", "description": "The guid of the owner."},
            {
                "name": "ReleaseId",
                "type": "int",
                "description": "The id of the release that the test set is assigned-to",
            },
            {"name": "ReleaseGuid", "type": "str", "description": "The guid of the release"},
            {
                "name": "AutomationHostId",
                "type": "int",
                "description": "The id of the automation host the test set is assigned-to",
            },
            {
                "name": "TestRunTypeId",
                "type": "int",
                "description": "The id of the type of test set (1 = Manual, 2 = Automated)",
            },
            {
                "name": "RecurrenceId",
                "type": "int",
                "description": "The id of the recurrence pattern the test set is scheduled for",
            },
            {"name": "Name", "type": "str", "description": "The name of the test set"},
            {
                "name": "Description",
                "type": "str",
                "description": "The detailed description of the test set",
            },
            {
                "name": "CreationDate",
                "type": "datetime",
                "description": "The date the test set was originally created",
            },
            {
                "name": "LastUpdateDate",
                "type": "datetime",
                "description": "The date the test set was last modified",
            },
            {
                "name": "PlannedDate",
                "type": "datetime",
                "description": "The date that the test set needs is planned to be executed on",
            },
            {
                "name": "ExecutionDate",
                "type": "datetime",
                "description": "The date that the test set was last executed by a tester",
            },
            {
                "name": "CountPassed",
                "type": "int",
                "description": "How many passed test cases are in the set",
            },
            {
                "name": "CountFailed",
                "type": "int",
                "description": "How many failed test cases are in the set",
            },
            {
                "name": "CountCaution",
                "type": "int",
                "description": "How many cautioned test cases are in the set",
            },
            {
                "name": "CountBlocked",
                "type": "int",
                "description": "How many blocked test cases are in the set",
            },
            {
                "name": "CountNotRun",
                "type": "int",
                "description": "How many test cases in the set have not been run",
            },
            {
                "name": "CountNotApplicable",
                "type": "int",
                "description": "How many test cases in the set are not applicable",
            },
            {
                "name": "CreatorName",
                "type": "str",
                "description": "The display name of the user that created the test set",
            },
            {
                "name": "OwnerName",
                "type": "str",
                "description": "The display name of the user that the test set is assigned-to",
            },
            {
                "name": "ProjectName",
                "type": "str",
                "description": "The display name of the project that the test set belongs to",
            },
            {
                "name": "TestSetStatusName",
                "type": "str",
                "description": "The display name of the status of the test set",
            },
            {
                "name": "ReleaseVersionNumber",
                "type": "str",
                "description": "The version number of the release the test set is scheduled for",
            },
            {
                "name": "RecurrenceName",
                "type": "str",
                "description": "The display name of the recurrence pattern",
            },
            {
                "name": "TestSetFolderId",
                "type": "int",
                "description": "The ID of the test set folder this test set belongs to (NULL = root)",
            },
            {
                "name": "EstimatedDuration",
                "type": "int",
                "description": "The total estimated duration for all the test cases in this set",
            },
            {
                "name": "ActualDuration",
                "type": "int",
                "description": "The total actual duration for all the test cases in this set",
            },
            {
                "name": "IsAutoScheduled",
                "type": "bool",
                "description": "Is this test set auto-scheduled when a build associated with the release runs",
            },
            {"name": "IsDynamic", "type": "bool", "description": "Is this a dynamic test set"},
            {
                "name": "DynamicQuery",
                "type": "str",
                "description": "The underlying query if this is a dynamic test set",
            },
            {
                "name": "TestConfigurationSetId",
                "type": "int",
                "description": "The id of any test configuration set to be used with this test set",
            },
            {
                "name": "BuildExecuteTimeInterval",
                "type": "int",
                "description": "The interval between a build finishing and the test being execution (if auto-scheduled)",
            },
            {
                "name": "ProjectId",
                "type": "int",
                "description": "The id of the project that the artifact belongs to",
            },
            {
                "name": "ProjectGuid",
                "type": "str",
                "description": "The guid of the project that the artifact belongs to",
            },
            {
                "name": "ArtifactTypeId",
                "type": "int",
                "description": "The type of artifact that we have",
            },
            {
                "name": "ConcurrencyDate",
                "type": "datetime",
                "description": "The datetime used to track optimistic concurrency to prevent edit conflicts",
            },
            {
                "name": "CustomProperties",
                "type": "list",
                "description": "The list of associated custom properties/fields for this artifact",
            },
            {
                "name": "IsAttachments",
                "type": "bool",
                "description": "Does this artifact have any attachments?",
            },
            {
                "name": "Tags",
                "type": "str",
                "description": "The list of meta-tags that should be associated with the artifact",
            },
            {
                "name": "Guid",
                "type": "str",
                "description": "The unique identifier for the artifact",
            },
        ],
    },
    "test_run": {
        "artifact_type": "test_run",
        "fields": [
            {"name": "TestRunId", "type": "int", "description": "The id of the test run"},
            {
                "name": "Name",
                "type": "str",
                "description": "The name of the test run (usually the same as the test case)",
            },
            {
                "name": "TestCaseId",
                "type": "int",
                "description": "The id of the test case that the test run is an instance of",
            },
            {
                "name": "TestCaseGuid",
                "type": "str",
                "description": "The guid of the test case that the test run is an instance of",
            },
            {
                "name": "TestRunTypeId",
                "type": "int",
                "description": "The id of the type of test run (automated vs. manual)",
            },
            {
                "name": "TesterId",
                "type": "int",
                "description": "The id of the user that executed the test",
            },
            {"name": "TesterGuid", "type": "str", "description": "The guid of the tester."},
            {
                "name": "ExecutionStatusId",
                "type": "int",
                "description": "The id of overall execution status for the test run",
            },
            {
                "name": "ReleaseId",
                "type": "int",
                "description": "The id of the release that the test run should be reported against",
            },
            {"name": "ReleaseGuid", "type": "str", "description": "The guid of the release"},
            {
                "name": "TestSetId",
                "type": "int",
                "description": "The id of the test set that the test run should be reported against",
            },
            {"name": "TestSetGuid", "type": "str", "description": "The guid of the test set"},
            {
                "name": "TestSetTestCaseId",
                "type": "int",
                "description": "The id of the unique test case entry in the test set",
            },
            {
                "name": "StartDate",
                "type": "datetime",
                "description": "The date/time that the test execution was started",
            },
            {
                "name": "EndDate",
                "type": "datetime",
                "description": "The date/time that the test execution was completed",
            },
            {
                "name": "BuildId",
                "type": "int",
                "description": "The id of the build that the test was executed against",
            },
            {
                "name": "EstimatedDuration",
                "type": "int",
                "description": "The estimated duration of how long the test should take to execute (read-only)",
            },
            {
                "name": "ActualDuration",
                "type": "int",
                "description": "The actual duration of how long the test should take to execute (read-only)",
            },
            {
                "name": "TestConfigurationId",
                "type": "int",
                "description": "The id of the specific test configuration that was used",
            },
            {
                "name": "ReleaseVersionNumber",
                "type": "str",
                "description": "version number of the release this test run was run against.",
            },
            {
                "name": "ProjectId",
                "type": "int",
                "description": "The id of the project that the artifact belongs to",
            },
            {
                "name": "ProjectGuid",
                "type": "str",
                "description": "The guid of the project that the artifact belongs to",
            },
            {
                "name": "ArtifactTypeId",
                "type": "int",
                "description": "The type of artifact that we have",
            },
            {
                "name": "ConcurrencyDate",
                "type": "datetime",
                "description": "The datetime used to track optimistic concurrency to prevent edit conflicts",
            },
            {
                "name": "CustomProperties",
                "type": "list",
                "description": "The list of associated custom properties/fields for this artifact",
            },
            {
                "name": "IsAttachments",
                "type": "bool",
                "description": "Does this artifact have any attachments?",
            },
            {
                "name": "Tags",
                "type": "str",
                "description": "The list of meta-tags that should be associated with the artifact",
            },
            {
                "name": "Guid",
                "type": "str",
                "description": "The unique identifier for the artifact",
            },
        ],
    },
    "automation_host": {
        "artifact_type": "automation_host",
        "fields": [
            {"name": "AutomationHostId", "type": "int", "description": "The id of the host"},
            {"name": "Name", "type": "str", "description": "The name of the host"},
            {"name": "Token", "type": "str", "description": "The token of the host"},
            {
                "name": "Description",
                "type": "str",
                "description": "The detailed description of the host",
            },
            {
                "name": "LastUpdateDate",
                "type": "datetime",
                "description": "The date/time that the host was last modified",
            },
            {
                "name": "Active",
                "type": "bool",
                "description": "Is this host active for the project",
            },
            {
                "name": "LastContactDate",
                "type": "datetime",
                "description": "The last time this host was contacted",
            },
            {
                "name": "ProjectId",
                "type": "int",
                "description": "The id of the project that the artifact belongs to",
            },
            {
                "name": "ProjectGuid",
                "type": "str",
                "description": "The guid of the project that the artifact belongs to",
            },
            {
                "name": "ArtifactTypeId",
                "type": "int",
                "description": "The type of artifact that we have",
            },
            {
                "name": "ConcurrencyDate",
                "type": "datetime",
                "description": "The datetime used to track optimistic concurrency to prevent edit conflicts",
            },
            {
                "name": "CustomProperties",
                "type": "list",
                "description": "The list of associated custom properties/fields for this artifact",
            },
            {
                "name": "IsAttachments",
                "type": "bool",
                "description": "Does this artifact have any attachments?",
            },
            {
                "name": "Tags",
                "type": "str",
                "description": "The list of meta-tags that should be associated with the artifact",
            },
            {
                "name": "Guid",
                "type": "str",
                "description": "The unique identifier for the artifact",
            },
        ],
    },
    "capability": {
        "artifact_type": "capability",
        "fields": [
            {"name": "CapabilityId", "type": "int", "description": "ID of the program capability"},
            {
                "name": "ProjectGroupId",
                "type": "int",
                "description": "ID of the project group which this capability belongs to",
            },
            {
                "name": "MilestoneId",
                "type": "int",
                "description": "The ID of the Program Milestone this capability belongs to",
            },
            {
                "name": "MilestoneName",
                "type": "str",
                "description": "The name of the Program Milestone this capability belongs to",
            },
            {
                "name": "StatusId",
                "type": "int",
                "description": "ID of the capability status this capability has",
            },
            {
                "name": "StatusName",
                "type": "str",
                "description": "Name of the capability status this capability has",
            },
            {
                "name": "StatusIsOpen",
                "type": "bool",
                "description": 'Whether or not this status makes this capability "Open"',
            },
            {
                "name": "TypeId",
                "type": "int",
                "description": "ID of the capability type this capability has",
            },
            {
                "name": "TypeName",
                "type": "str",
                "description": "Name of the capability type this capability has",
            },
            {
                "name": "PriorityId",
                "type": "int",
                "description": "ID of the capability priority this capability has",
            },
            {
                "name": "PriorityName",
                "type": "str",
                "description": "Name of the capability priority this capability has",
            },
            {"name": "Name", "type": "str", "description": "Name of this capability"},
            {"name": "Description", "type": "str", "description": "Description of the capability"},
            {
                "name": "PercentComplete",
                "type": "int",
                "description": "Percent Completion of the capability",
            },
            {
                "name": "RequirementCount",
                "type": "int",
                "description": "Number of requirements associated with this capability",
            },
            {
                "name": "IndentLevel",
                "type": "str",
                "description": "Indent level of this capability in the hierarchy",
            },
            {
                "name": "Guid",
                "type": "str",
                "description": "Artifact guid for avoiding concurrency interactions",
            },
            {
                "name": "CreatorId",
                "type": "int",
                "description": "UserId of the creator of this capability",
            },
            {
                "name": "CreatorName",
                "type": "str",
                "description": "Full name of the creator of this capability",
            },
            {
                "name": "OwnerId",
                "type": "int",
                "description": "UserId of the owner of this capability",
            },
            {
                "name": "OwnerName",
                "type": "str",
                "description": "Full name of the owner of this capability",
            },
            {
                "name": "CreationDate",
                "type": "datetime",
                "description": "The date/time the capability was created",
            },
            {
                "name": "LastUpdateDate",
                "type": "datetime",
                "description": "The date/time the capability was last updated",
            },
            {
                "name": "IsSummary",
                "type": "bool",
                "description": "This Capability represents a summary in the program?",
            },
            {
                "name": "ArtifactTypeId",
                "type": "int",
                "description": "The type of artifact that we have",
            },
            {
                "name": "ConcurrencyGuid",
                "type": "str",
                "description": "The field used to track optimistic concurrency to prevent edit conflicts",
            },
            {
                "name": "CustomProperties",
                "type": "list",
                "description": "The list of associated custom properties/fields for this workspace",
            },
        ],
    },
    "milestone": {
        "artifact_type": "milestone",
        "fields": [
            {"name": "MilestoneId", "type": "int", "description": "ID of the program milestone"},
            {
                "name": "Guid",
                "type": "str",
                "description": "Artifact guid for unique identification of an artifact",
            },
            {
                "name": "CreatorId",
                "type": "int",
                "description": "UserId of the creator of this milestone",
            },
            {
                "name": "CreatorName",
                "type": "str",
                "description": "Full name of the creator of this milestone",
            },
            {
                "name": "OwnerId",
                "type": "int",
                "description": "UserId of the owner of this milestone",
            },
            {
                "name": "OwnerName",
                "type": "str",
                "description": "Full name of the owner of this milestone",
            },
            {
                "name": "StatusId",
                "type": "int",
                "description": "ID of the program milestone status this milestone has",
            },
            {
                "name": "StatusIsOpen",
                "type": "bool",
                "description": 'Whether or not this status makes this milestone "Open"',
            },
            {
                "name": "StatusName",
                "type": "str",
                "description": "Name of the milestone status this milestone has",
            },
            {
                "name": "TypeId",
                "type": "int",
                "description": "ID of the program milestone type this milestone has",
            },
            {
                "name": "TypeName",
                "type": "str",
                "description": "Name of the program milestone type this milestone has",
            },
            {"name": "Name", "type": "str", "description": "Name of this milestone"},
            {"name": "Description", "type": "str", "description": "Description of the milestone"},
            {
                "name": "ProjectGroupId",
                "type": "int",
                "description": "ID of the project group which this milestone belongs to",
            },
            {
                "name": "ProjectGroupName",
                "type": "str",
                "description": "Name of the project group this milestone belongs to",
            },
            {
                "name": "StartDate",
                "type": "datetime",
                "description": "Start date of this milestone",
            },
            {
                "name": "ChildrenStartDate",
                "type": "datetime",
                "description": "Earliest start date of this milestone's children releases",
            },
            {"name": "EndDate", "type": "datetime", "description": "End date of this milestone"},
            {
                "name": "ChildrenEndDate",
                "type": "datetime",
                "description": "Earliest end date of this milestone's children releases",
            },
            {
                "name": "CreationDate",
                "type": "datetime",
                "description": "The date/time the milestone was created",
            },
            {
                "name": "LastUpdateDate",
                "type": "datetime",
                "description": "The date/time the milestone was last updated",
            },
            {
                "name": "PercentComplete",
                "type": "int",
                "description": "Percent of the associated capabilities which are completed",
            },
            {
                "name": "ReleaseCount",
                "type": "int",
                "description": "Number of releases associated with this milestone",
            },
            {
                "name": "RequirementCount",
                "type": "int",
                "description": "Number of requirements which are within the child releases",
            },
            {
                "name": "ArtifactTypeId",
                "type": "int",
                "description": "The type of artifact that we have",
            },
            {
                "name": "ConcurrencyGuid",
                "type": "str",
                "description": "The field used to track optimistic concurrency to prevent edit conflicts",
            },
            {
                "name": "CustomProperties",
                "type": "list",
                "description": "The list of associated custom properties/fields for this workspace",
            },
        ],
    },
}


def _get_artifact_schema_impl(artifact_type: str) -> str:
    """Return the field schema for the given artifact type as a JSON string.

    Args:
        artifact_type: One of the values in VALID_ARTIFACT_TYPES.

    Returns:
        JSON string with {"artifact_type": ..., "fields": [...]} on success,
        or {"error": ..., "valid_types": [...]} for an unrecognised type.
    """
    if artifact_type not in VALID_ARTIFACT_TYPES:
        return json.dumps(
            {
                "error": (
                    f"Unknown artifact type '{artifact_type}'. "
                    f"Valid types are: {', '.join(sorted(VALID_ARTIFACT_TYPES))}"
                ),
                "valid_types": sorted(VALID_ARTIFACT_TYPES),
            }
        )
    return json.dumps(ARTIFACT_SCHEMAS[artifact_type], indent=2)


def register_tools(mcp) -> None:
    """Register the get_artifact_schema tool with the MCP server."""

    @mcp.tool(
        name="get_artifact_schema",
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": False,
        },
    )
    async def get_artifact_schema(artifact_type: str) -> str:
        """Returns the field schema for a Spira artifact type as JSON.

        Args:
            artifact_type: One of: task, incident, requirement, test_case,
                release, risk, test_set, test_run, automation_host,
                capability, milestone

        Returns:
            JSON: {"artifact_type": "...", "fields": [{"name", "type",
                "description"}, ...]}
            or {"error": "...", "valid_types": [...]} for unknown types.

        Call get_artifact_schema(artifact_type='task') to see fields.
        """
        try:
            return _get_artifact_schema_impl(artifact_type)
        except Exception as e:
            return json.dumps({"error": str(e)})
