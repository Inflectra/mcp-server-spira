# Tool Documentation Generation Report

This report contains generated documentation templates for MCP tools based on the Spira OpenAPI specification.

**Generated:** Auto-generated from OpenAPI spec
**Purpose:** Provide starting point for tool documentation
**Next Steps:** Review, enhance with workflow context, and resolve clarifications

---

## get_my_tasks

**Endpoint:** `GET /tasks`
**Artifact Type:** `task`

### Generated Docstring

```python
@mcp.tool()
def get_my_tasks(limit: int = 25, offset: int = 0) -> str:
"""
Retrieves all tasks owned by the currently authenticated user

Maps to Spira API: GET /tasks

**Pagination:** This endpoint uses CLIENT-SIDE pagination. The API returns
all results, and we slice them in Python. This is acceptable for 'my work'
queries which typically return < 500 items.

**For Display:** Modern LLMs can format JSON naturally for simple display.
For complex workflows where you've filtered or processed the data, use
format_artifacts_as_markdown() to ensure consistent formatting.

Args:
    limit: Maximum number of items to return (1-500, default: 25)
        Controls result set size for pagination.
    offset: Number of items to skip (>= 0, default: 0)
        Used for retrieving subsequent pages of results.

Returns:
    JSON string with structure:
    {
        "data": [
            {
                "TaskId": integer, nullable,  // The id of the task
                "TaskStatusId": integer,  // The id of the status of the task
                "TaskTypeId": integer, nullable,  // The id of the type of the task (null for default)
                "TaskFolderId": integer, nullable,  // The of the folder the task is stored in (null for root)
                "RequirementId": integer, nullable,  // The id of the parent requirement that the task belongs to
                "ReleaseId": integer, nullable,  // The id of the release/iteration that the task is scheduled for
                "ReleaseGuid": string,  // The guid of the release
                "ComponentId": integer, nullable,  // The id of the component that this task belongs to
                "CreatorId": integer, nullable,  // The id of the user that originally created the task
                "OwnerId": integer, nullable,  // The id of the user that the task is assigned-to
                // ... additional fields ...
            }
        ],
        "pagination": {
            "limit": 25,
            "offset": 0,
            "returned_count": 25,
            "total_count": 150,
            "has_more": true,
            "pagination_type": "client-side"
        }
    }

Key Fields:
    - TaskId: The id of the task
    - TaskStatusId: The id of the status of the task
    - TaskTypeId: The id of the type of the task (null for default)
    - TaskFolderId: The of the folder the task is stored in (null for root)
    - RequirementId: The id of the parent requirement that the task belongs to
    - ReleaseId: The id of the release/iteration that the task is scheduled for
    - ReleaseGuid: The guid of the release
    - ComponentId: The id of the component that this task belongs to

When to Use:
    [TO BE FILLED: Describe use cases and scenarios]

Related Tools:
    - format_artifacts_as_markdown: Format filtered/processed results
    [TO BE FILLED: List other related tools]

Error Responses:
    {
        "error": "Invalid pagination parameters",
        "error_code": "INVALID_PARAMETER",
        "details": {
            "parameter": "limit",
            "value": 1000,
            "expected": "1-500"
        },
        "suggestion": "Use limit between 1 and 500"
    }

Example Usage:
    # Simple display - LLM formats naturally
    result_json = get_my_tasks()
    # LLM can format this JSON for display without additional tools

    # Complex workflow - Use formatting tool for filtered results
    result_json = get_my_tasks(limit=100)
    result = json.loads(result_json)
    filtered = [item for item in result["data"] if meets_criteria(item)]
    filtered_json = json.dumps({"data": filtered})
    readable = format_artifacts_as_markdown(filtered_json, "artifact_type")
"""
```

### Clarifications Needed

**Total Issues:** 31

#### 🔴 High Priority

**Missing Description**
- **Issue:** Missing endpoint description for GET /tasks
- **Question:** What is the purpose of this endpoint? What does it return and when should it be used?
- **Context:** `OpenAPI: paths./tasks.get.description`

**Business Logic**
- **Issue:** Multiple similar fields found: EstimatedEffort, ActualEffort, RemainingEffort, ProjectedEffort
- **Question:** What's the difference between EstimatedEffort vs ActualEffort vs RemainingEffort vs ProjectedEffort? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTask - Fields: EstimatedEffort, ActualEffort, RemainingEffort, ProjectedEffort`

**Business Logic**
- **Issue:** Multiple similar fields found: CreationDate, LastUpdateDate, StartDate, EndDate, ConcurrencyDate
- **Question:** What's the difference between CreationDate vs LastUpdateDate vs StartDate vs EndDate vs ConcurrencyDate? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTask - Fields: CreationDate, LastUpdateDate, StartDate, EndDate, ConcurrencyDate`

**Business Logic**
- **Issue:** Multiple similar fields found: TaskId, TaskStatusId, TaskTypeId, TaskFolderId, RequirementId, ReleaseId, ComponentId, CreatorId, OwnerId, TaskPriorityId, RiskId, ProjectId, ArtifactTypeId
- **Question:** What's the difference between TaskId vs TaskStatusId vs TaskTypeId vs TaskFolderId vs RequirementId vs ReleaseId vs ComponentId vs CreatorId vs OwnerId vs TaskPriorityId vs RiskId vs ProjectId vs ArtifactTypeId? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTask - Fields: TaskId, TaskStatusId, TaskTypeId, TaskFolderId, RequirementId, ReleaseId, ComponentId, CreatorId, OwnerId, TaskPriorityId, RiskId, ProjectId, ArtifactTypeId`

**Business Logic**
- **Issue:** Multiple similar fields found: Name, TaskStatusName, TaskTypeName, OwnerName, TaskPriorityName, ProjectName, RequirementName
- **Question:** What's the difference between Name vs TaskStatusName vs TaskTypeName vs OwnerName vs TaskPriorityName vs ProjectName vs RequirementName? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTask - Fields: Name, TaskStatusName, TaskTypeName, OwnerName, TaskPriorityName, ProjectName, RequirementName`

**Business Logic**
- **Issue:** Multiple similar fields found: TaskStatusId, TaskStatusName
- **Question:** What's the difference between TaskStatusId vs TaskStatusName? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTask - Fields: TaskStatusId, TaskStatusName`

**Business Logic**
- **Issue:** Multiple similar fields found: TaskTypeId, TaskTypeName, ArtifactTypeId
- **Question:** What's the difference between TaskTypeId vs TaskTypeName vs ArtifactTypeId? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTask - Fields: TaskTypeId, TaskTypeName, ArtifactTypeId`

**Business Logic**
- **Issue:** Multiple similar fields found: TaskPriorityId, TaskPriorityName
- **Question:** What's the difference between TaskPriorityId vs TaskPriorityName? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTask - Fields: TaskPriorityId, TaskPriorityName`

**Business Logic**
- **Issue:** Multiple similar fields found: OwnerId, OwnerGuid, OwnerName
- **Question:** What's the difference between OwnerId vs OwnerGuid vs OwnerName? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTask - Fields: OwnerId, OwnerGuid, OwnerName`

**Workflow Context**
- **Issue:** Missing workflow context
- **Question:** When should an LLM use this tool (GET /tasks)? What are the typical use cases? Are there related tools that should be used instead?
- **Context:** `This requires human knowledge of the overall system workflow`

#### 🟡 Medium Priority

**Vague Field Description**
- **Issue:** Vague description for field 'TaskId': 'The id of the task'
- **Question:** Can you provide more context about 'TaskId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTask.properties.TaskId`

**Vague Field Description**
- **Issue:** Vague description for field 'TaskStatusId': 'The id of the status of the task'
- **Question:** Can you provide more context about 'TaskStatusId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTask.properties.TaskStatusId`

**Vague Field Description**
- **Issue:** Vague description for field 'TaskTypeId': 'The id of the type of the task (null for default)'
- **Question:** Can you provide more context about 'TaskTypeId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTask.properties.TaskTypeId`

**Vague Field Description**
- **Issue:** Vague description for field 'RequirementId': 'The id of the parent requirement that the task belongs to'
- **Question:** Can you provide more context about 'RequirementId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTask.properties.RequirementId`

**Vague Field Description**
- **Issue:** Vague description for field 'ReleaseId': 'The id of the release/iteration that the task is scheduled for'
- **Question:** Can you provide more context about 'ReleaseId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTask.properties.ReleaseId`

**Vague Field Description**
- **Issue:** Vague description for field 'ComponentId': 'The id of the component that this task belongs to'
- **Question:** Can you provide more context about 'ComponentId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTask.properties.ComponentId`

**Vague Field Description**
- **Issue:** Vague description for field 'CreatorId': 'The id of the user that originally created the task'
- **Question:** Can you provide more context about 'CreatorId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTask.properties.CreatorId`

**Vague Field Description**
- **Issue:** Vague description for field 'OwnerId': 'The id of the user that the task is assigned-to'
- **Question:** Can you provide more context about 'OwnerId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTask.properties.OwnerId`

**Vague Field Description**
- **Issue:** Vague description for field 'TaskPriorityId': 'The id of the priority of the task'
- **Question:** Can you provide more context about 'TaskPriorityId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTask.properties.TaskPriorityId`

**Vague Field Description**
- **Issue:** Vague description for field 'Name': 'The name of the task'
- **Question:** Can you provide more context about 'Name'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTask.properties.Name`

**Vague Field Description**
- **Issue:** Vague description for field 'TaskStatusName': 'The display name of the status of the task'
- **Question:** Can you provide more context about 'TaskStatusName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTask.properties.TaskStatusName`

**Vague Field Description**
- **Issue:** Vague description for field 'TaskTypeName': 'The display name of the type of the task'
- **Question:** Can you provide more context about 'TaskTypeName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTask.properties.TaskTypeName`

**Vague Field Description**
- **Issue:** Vague description for field 'OwnerName': 'The display name of the user who the task is assigned-to'
- **Question:** Can you provide more context about 'OwnerName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTask.properties.OwnerName`

**Vague Field Description**
- **Issue:** Vague description for field 'TaskPriorityName': 'The display name of the priority of the task'
- **Question:** Can you provide more context about 'TaskPriorityName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTask.properties.TaskPriorityName`

**Vague Field Description**
- **Issue:** Vague description for field 'ProjectName': 'The display name of the project the task belongs to'
- **Question:** Can you provide more context about 'ProjectName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTask.properties.ProjectName`

**Vague Field Description**
- **Issue:** Vague description for field 'RequirementName': 'The name of the requirement that the task is associated with'
- **Question:** Can you provide more context about 'RequirementName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTask.properties.RequirementName`

**Vague Field Description**
- **Issue:** Vague description for field 'ProjectId': 'The id of the project that the artifact belongs to'
- **Question:** Can you provide more context about 'ProjectId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTask.properties.ProjectId`

**Vague Field Description**
- **Issue:** Vague description for field 'ArtifactTypeId': 'The type of artifact that we have'
- **Question:** Can you provide more context about 'ArtifactTypeId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTask.properties.ArtifactTypeId`

**Business Logic**
- **Issue:** Found ID/Name pairs: TaskStatusId/TaskStatusName, TaskTypeId/TaskTypeName, RequirementId/RequirementName, OwnerId/OwnerName, TaskPriorityId/TaskPriorityName, ProjectId/ProjectName
- **Question:** Should LLMs filter/search by ID or Name? What's the recommended approach for each pair?
- **Context:** `OpenAPI: components.schemas.RemoteTask`

**Performance**
- **Issue:** Potential performance concern for 'my work' endpoint
- **Question:** What's a typical result set size for this endpoint? Are there performance issues with large result sets? Should we recommend a maximum limit?
- **Context:** `This endpoint uses client-side pagination - all results are retrieved from API`

#### 🟢 Low Priority

**Edge Cases**
- **Issue:** Many nullable fields: 16 fields can be null
- **Question:** Under what conditions are these fields null? Are there common scenarios where multiple fields are null?
- **Context:** `OpenAPI: components.schemas.RemoteTask - Nullable fields: TaskId, TaskTypeId, TaskFolderId, RequirementId, ReleaseId...`

---

## get_my_incidents

**Endpoint:** `GET /incidents`
**Artifact Type:** `incident`

### Generated Docstring

```python
@mcp.tool()
def get_my_incidents(limit: int = 25, offset: int = 0) -> str:
"""
Retrieves all incidents owned by the currently authenticated user

Maps to Spira API: GET /incidents

**Pagination:** This endpoint uses CLIENT-SIDE pagination. The API returns
all results, and we slice them in Python. This is acceptable for 'my work'
queries which typically return < 500 items.

**For Display:** Modern LLMs can format JSON naturally for simple display.
For complex workflows where you've filtered or processed the data, use
format_artifacts_as_markdown() to ensure consistent formatting.

Args:
    limit: Maximum number of items to return (1-500, default: 25)
        Controls result set size for pagination.
    offset: Number of items to skip (>= 0, default: 0)
        Used for retrieving subsequent pages of results.

Returns:
    JSON string with structure:
    {
        "data": [
            {
                "IncidentId": integer, nullable,  // The id of the incident (integer)
                "PriorityId": integer, nullable,  // The id of the priority of the incident (integer)
                "SeverityId": integer, nullable,  // The id of the severity of the incident (integer)
                "IncidentStatusId": integer, nullable,  // The id of the status of the incident (integer)
                "IncidentTypeId": integer, nullable,  // The id of the type of the incident (integer)
                "OpenerId": integer, nullable,  // The id of the user who detected the incident (integer)
                "OwnerId": integer, nullable,  // The id of the user to the incident is assigned-to (integer)
                "OpenerGuid": string,  // The guid of the opener.
                "OwnerGuid": string,  // The guid of the owner.
                "TestRunStepIds": array,  // The id of the test run steps that the incident relates to (integer)
                // ... additional fields ...
            }
        ],
        "pagination": {
            "limit": 25,
            "offset": 0,
            "returned_count": 25,
            "total_count": 150,
            "has_more": true,
            "pagination_type": "client-side"
        }
    }

Key Fields:
    - IncidentId: The id of the incident (integer)
    - PriorityId: The id of the priority of the incident (integer)
    - SeverityId: The id of the severity of the incident (integer)
    - IncidentStatusId: The id of the status of the incident (integer)
    - IncidentTypeId: The id of the type of the incident (integer)
    - OpenerId: The id of the user who detected the incident (integer)
    - OwnerId: The id of the user to the incident is assigned-to (integer)
    - OpenerGuid: The guid of the opener.

When to Use:
    [TO BE FILLED: Describe use cases and scenarios]

Related Tools:
    - format_artifacts_as_markdown: Format filtered/processed results
    [TO BE FILLED: List other related tools]

Error Responses:
    {
        "error": "Invalid pagination parameters",
        "error_code": "INVALID_PARAMETER",
        "details": {
            "parameter": "limit",
            "value": 1000,
            "expected": "1-500"
        },
        "suggestion": "Use limit between 1 and 500"
    }

Example Usage:
    # Simple display - LLM formats naturally
    result_json = get_my_incidents()
    # LLM can format this JSON for display without additional tools

    # Complex workflow - Use formatting tool for filtered results
    result_json = get_my_incidents(limit=100)
    result = json.loads(result_json)
    filtered = [item for item in result["data"] if meets_criteria(item)]
    filtered_json = json.dumps({"data": filtered})
    readable = format_artifacts_as_markdown(filtered_json, "artifact_type")
"""
```

### Clarifications Needed

**Total Issues:** 39

#### 🔴 High Priority

**Missing Description**
- **Issue:** Missing endpoint description for GET /incidents
- **Question:** What is the purpose of this endpoint? What does it return and when should it be used?
- **Context:** `OpenAPI: paths./incidents.get.description`

**Business Logic**
- **Issue:** Multiple similar fields found: EstimatedEffort, ActualEffort, RemainingEffort, ProjectedEffort
- **Question:** What's the difference between EstimatedEffort vs ActualEffort vs RemainingEffort vs ProjectedEffort? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteIncident - Fields: EstimatedEffort, ActualEffort, RemainingEffort, ProjectedEffort`

**Business Logic**
- **Issue:** Multiple similar fields found: CreationDate, StartDate, EndDate, ClosedDate, LastUpdateDate, ConcurrencyDate
- **Question:** What's the difference between CreationDate vs StartDate vs EndDate vs ClosedDate vs LastUpdateDate vs ConcurrencyDate? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteIncident - Fields: CreationDate, StartDate, EndDate, ClosedDate, LastUpdateDate, ConcurrencyDate`

**Business Logic**
- **Issue:** Multiple similar fields found: IncidentId, PriorityId, SeverityId, IncidentStatusId, IncidentTypeId, OpenerId, OwnerId, TestRunStepIds, DetectedReleaseId, ResolvedReleaseId, VerifiedReleaseId, ComponentIds, FixedBuildId, DetectedBuildId, ProjectId, ArtifactTypeId
- **Question:** What's the difference between IncidentId vs PriorityId vs SeverityId vs IncidentStatusId vs IncidentTypeId vs OpenerId vs OwnerId vs TestRunStepIds vs DetectedReleaseId vs ResolvedReleaseId vs VerifiedReleaseId vs ComponentIds vs FixedBuildId vs DetectedBuildId vs ProjectId vs ArtifactTypeId? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteIncident - Fields: IncidentId, PriorityId, SeverityId, IncidentStatusId, IncidentTypeId, OpenerId, OwnerId, TestRunStepIds, DetectedReleaseId, ResolvedReleaseId, VerifiedReleaseId, ComponentIds, FixedBuildId, DetectedBuildId, ProjectId, ArtifactTypeId`

**Business Logic**
- **Issue:** Multiple similar fields found: Name, PriorityName, SeverityName, IncidentStatusName, IncidentTypeName, OpenerName, OwnerName, ProjectName, FixedBuildName, DetectedBuildName
- **Question:** What's the difference between Name vs PriorityName vs SeverityName vs IncidentStatusName vs IncidentTypeName vs OpenerName vs OwnerName vs ProjectName vs FixedBuildName vs DetectedBuildName? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteIncident - Fields: Name, PriorityName, SeverityName, IncidentStatusName, IncidentTypeName, OpenerName, OwnerName, ProjectName, FixedBuildName, DetectedBuildName`

**Business Logic**
- **Issue:** Multiple similar fields found: IncidentStatusId, IncidentStatusName, IncidentStatusOpenStatus
- **Question:** What's the difference between IncidentStatusId vs IncidentStatusName vs IncidentStatusOpenStatus? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteIncident - Fields: IncidentStatusId, IncidentStatusName, IncidentStatusOpenStatus`

**Business Logic**
- **Issue:** Multiple similar fields found: IncidentTypeId, IncidentTypeName, ArtifactTypeId
- **Question:** What's the difference between IncidentTypeId vs IncidentTypeName vs ArtifactTypeId? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteIncident - Fields: IncidentTypeId, IncidentTypeName, ArtifactTypeId`

**Business Logic**
- **Issue:** Multiple similar fields found: PriorityId, PriorityName
- **Question:** What's the difference between PriorityId vs PriorityName? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteIncident - Fields: PriorityId, PriorityName`

**Business Logic**
- **Issue:** Multiple similar fields found: OwnerId, OwnerGuid, OwnerName
- **Question:** What's the difference between OwnerId vs OwnerGuid vs OwnerName? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteIncident - Fields: OwnerId, OwnerGuid, OwnerName`

**Workflow Context**
- **Issue:** Missing workflow context
- **Question:** When should an LLM use this tool (GET /incidents)? What are the typical use cases? Are there related tools that should be used instead?
- **Context:** `This requires human knowledge of the overall system workflow`

#### 🟡 Medium Priority

**Vague Field Description**
- **Issue:** Vague description for field 'IncidentId': 'The id of the incident (integer)'
- **Question:** Can you provide more context about 'IncidentId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.IncidentId`

**Vague Field Description**
- **Issue:** Vague description for field 'PriorityId': 'The id of the priority of the incident (integer)'
- **Question:** Can you provide more context about 'PriorityId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.PriorityId`

**Vague Field Description**
- **Issue:** Vague description for field 'SeverityId': 'The id of the severity of the incident (integer)'
- **Question:** Can you provide more context about 'SeverityId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.SeverityId`

**Vague Field Description**
- **Issue:** Vague description for field 'IncidentStatusId': 'The id of the status of the incident (integer)'
- **Question:** Can you provide more context about 'IncidentStatusId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.IncidentStatusId`

**Vague Field Description**
- **Issue:** Vague description for field 'IncidentTypeId': 'The id of the type of the incident (integer)'
- **Question:** Can you provide more context about 'IncidentTypeId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.IncidentTypeId`

**Vague Field Description**
- **Issue:** Vague description for field 'OpenerId': 'The id of the user who detected the incident (integer)'
- **Question:** Can you provide more context about 'OpenerId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.OpenerId`

**Vague Field Description**
- **Issue:** Vague description for field 'OwnerId': 'The id of the user to the incident is assigned-to (integer)'
- **Question:** Can you provide more context about 'OwnerId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.OwnerId`

**Vague Field Description**
- **Issue:** Vague description for field 'TestRunStepIds': 'The id of the test run steps that the incident relates to (integer)'
- **Question:** Can you provide more context about 'TestRunStepIds'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.TestRunStepIds`

**Vague Field Description**
- **Issue:** Vague description for field 'DetectedReleaseId': 'The id of the release/iteration that the incident was detected in (integer)'
- **Question:** Can you provide more context about 'DetectedReleaseId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.DetectedReleaseId`

**Vague Field Description**
- **Issue:** Vague description for field 'ResolvedReleaseId': 'The id of the release/iteration that the incident will be fixed in (integer)'
- **Question:** Can you provide more context about 'ResolvedReleaseId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.ResolvedReleaseId`

**Vague Field Description**
- **Issue:** Vague description for field 'VerifiedReleaseId': 'The id of the release/iteration that the incident was retested in (integer)'
- **Question:** Can you provide more context about 'VerifiedReleaseId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.VerifiedReleaseId`

**Vague Field Description**
- **Issue:** Vague description for field 'Name': 'The name of the incident (string)'
- **Question:** Can you provide more context about 'Name'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.Name`

**Vague Field Description**
- **Issue:** Vague description for field 'PriorityName': 'The display name of the priority of the incident (string)'
- **Question:** Can you provide more context about 'PriorityName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.PriorityName`

**Vague Field Description**
- **Issue:** Vague description for field 'SeverityName': 'The display name of the severity of the incident (string)'
- **Question:** Can you provide more context about 'SeverityName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.SeverityName`

**Vague Field Description**
- **Issue:** Vague description for field 'IncidentStatusName': 'The display name of the status of the incident (string)'
- **Question:** Can you provide more context about 'IncidentStatusName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.IncidentStatusName`

**Vague Field Description**
- **Issue:** Vague description for field 'IncidentTypeName': 'The display name of the type of the incident (string)'
- **Question:** Can you provide more context about 'IncidentTypeName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.IncidentTypeName`

**Vague Field Description**
- **Issue:** Vague description for field 'OpenerName': 'The display name of the user that detected the incident (string)'
- **Question:** Can you provide more context about 'OpenerName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.OpenerName`

**Vague Field Description**
- **Issue:** Vague description for field 'OwnerName': 'The display name of the user that the incident is assigned to (string)'
- **Question:** Can you provide more context about 'OwnerName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.OwnerName`

**Vague Field Description**
- **Issue:** Vague description for field 'ProjectName': 'The display name of the project the incident belongs to (string)'
- **Question:** Can you provide more context about 'ProjectName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.ProjectName`

**Vague Field Description**
- **Issue:** Vague description for field 'FixedBuildId': 'The id of the build that the incident was fixed in (integer)'
- **Question:** Can you provide more context about 'FixedBuildId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.FixedBuildId`

**Vague Field Description**
- **Issue:** Vague description for field 'FixedBuildName': 'The name of the build that the incident was fixed in (string)'
- **Question:** Can you provide more context about 'FixedBuildName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.FixedBuildName`

**Vague Field Description**
- **Issue:** Vague description for field 'DetectedBuildId': 'The id of the build that the incident was detected in (integer)'
- **Question:** Can you provide more context about 'DetectedBuildId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.DetectedBuildId`

**Vague Field Description**
- **Issue:** Vague description for field 'DetectedBuildName': 'The name of the build that the incident was detected in (string)'
- **Question:** Can you provide more context about 'DetectedBuildName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.DetectedBuildName`

**Vague Field Description**
- **Issue:** Vague description for field 'ProjectId': 'The id of the project that the artifact belongs to'
- **Question:** Can you provide more context about 'ProjectId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.ProjectId`

**Vague Field Description**
- **Issue:** Vague description for field 'ArtifactTypeId': 'The type of artifact that we have'
- **Question:** Can you provide more context about 'ArtifactTypeId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteIncident.properties.ArtifactTypeId`

**Business Logic**
- **Issue:** Found ID/Name pairs: PriorityId/PriorityName, SeverityId/SeverityName, IncidentStatusId/IncidentStatusName, IncidentTypeId/IncidentTypeName, OpenerId/OpenerName, OwnerId/OwnerName, FixedBuildId/FixedBuildName, DetectedBuildId/DetectedBuildName, ProjectId/ProjectName
- **Question:** Should LLMs filter/search by ID or Name? What's the recommended approach for each pair?
- **Context:** `OpenAPI: components.schemas.RemoteIncident`

**Performance**
- **Issue:** Potential performance concern for 'my work' endpoint
- **Question:** What's a typical result set size for this endpoint? Are there performance issues with large result sets? Should we recommend a maximum limit?
- **Context:** `This endpoint uses client-side pagination - all results are retrieved from API`

#### 🟢 Low Priority

**Complex Nested Schema**
- **Issue:** Schema contains multiple array fields: TestRunStepIds, ComponentIds, CustomProperties
- **Question:** Are all these arrays (TestRunStepIds, ComponentIds, CustomProperties) typically populated? Should any be excluded for performance?
- **Context:** `OpenAPI: components.schemas.RemoteIncident`

**Edge Cases**
- **Issue:** Many nullable fields: 21 fields can be null
- **Question:** Under what conditions are these fields null? Are there common scenarios where multiple fields are null?
- **Context:** `OpenAPI: components.schemas.RemoteIncident - Nullable fields: IncidentId, PriorityId, SeverityId, IncidentStatusId, IncidentTypeId...`

---

## get_my_requirements

**Endpoint:** `GET /requirements`
**Artifact Type:** `requirement`

### Generated Docstring

```python
@mcp.tool()
def get_my_requirements(limit: int = 25, offset: int = 0) -> str:
"""
Retrieves all requirements owned by the currently authenticated user

Maps to Spira API: GET /requirements

**Pagination:** This endpoint uses CLIENT-SIDE pagination. The API returns
all results, and we slice them in Python. This is acceptable for 'my work'
queries which typically return < 500 items.

**For Display:** Modern LLMs can format JSON naturally for simple display.
For complex workflows where you've filtered or processed the data, use
format_artifacts_as_markdown() to ensure consistent formatting.

Args:
    limit: Maximum number of items to return (1-500, default: 25)
        Controls result set size for pagination.
    offset: Number of items to skip (>= 0, default: 0)
        Used for retrieving subsequent pages of results.

Returns:
    JSON string with structure:
    {
        "data": [
            {
                "RequirementId": integer, nullable,  // The id of the requirement (integer)
                "IndentLevel": string,  // The indentation level of the artifact (string)
                "StatusId": integer, nullable,  // The id of the requirement's status (integer).
                "RequirementTypeId": integer, nullable,  // The type of requirement (integer).
                "AuthorId": integer, nullable,  // The id of the user that wrote the requirement (integer)
                "OwnerId": integer, nullable,  // The id of the user that the requirement is assigned-to (integer)
                "AuthorGuid": string,  // The guid of the author.
                "OwnerGuid": string,  // The guid of the owner.
                "ImportanceId": integer, nullable,  // The id of the importance of the requirement (integer)
                "ReleaseId": integer, nullable,  // The id of the release the requirement is scheduled to implemented in (integer)
                // ... additional fields ...
            }
        ],
        "pagination": {
            "limit": 25,
            "offset": 0,
            "returned_count": 25,
            "total_count": 150,
            "has_more": true,
            "pagination_type": "client-side"
        }
    }

Key Fields:
    - RequirementId: The id of the requirement (integer)
    - IndentLevel: The indentation level of the artifact (string)
    - StatusId: The id of the requirement's status (integer).
    - RequirementTypeId: The type of requirement (integer).
    - AuthorId: The id of the user that wrote the requirement (integer)
    - OwnerId: The id of the user that the requirement is assigned-to (integer)
    - AuthorGuid: The guid of the author.
    - OwnerGuid: The guid of the owner.

When to Use:
    [TO BE FILLED: Describe use cases and scenarios]

Related Tools:
    - format_artifacts_as_markdown: Format filtered/processed results
    [TO BE FILLED: List other related tools]

Error Responses:
    {
        "error": "Invalid pagination parameters",
        "error_code": "INVALID_PARAMETER",
        "details": {
            "parameter": "limit",
            "value": 1000,
            "expected": "1-500"
        },
        "suggestion": "Use limit between 1 and 500"
    }

Example Usage:
    # Simple display - LLM formats naturally
    result_json = get_my_requirements()
    # LLM can format this JSON for display without additional tools

    # Complex workflow - Use formatting tool for filtered results
    result_json = get_my_requirements(limit=100)
    result = json.loads(result_json)
    filtered = [item for item in result["data"] if meets_criteria(item)]
    filtered_json = json.dumps({"data": filtered})
    readable = format_artifacts_as_markdown(filtered_json, "artifact_type")
"""
```

### Clarifications Needed

**Total Issues:** 31

#### 🔴 High Priority

**Missing Description**
- **Issue:** Missing endpoint description for GET /requirements
- **Question:** What is the purpose of this endpoint? What does it return and when should it be used?
- **Context:** `OpenAPI: paths./requirements.get.description`

**Business Logic**
- **Issue:** Multiple similar fields found: EstimatedEffort, TaskEstimatedEffort, TaskActualEffort
- **Question:** What's the difference between EstimatedEffort vs TaskEstimatedEffort vs TaskActualEffort? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement - Fields: EstimatedEffort, TaskEstimatedEffort, TaskActualEffort`

**Business Logic**
- **Issue:** Multiple similar fields found: CreationDate, LastUpdateDate, StartDate, EndDate, ConcurrencyDate
- **Question:** What's the difference between CreationDate vs LastUpdateDate vs StartDate vs EndDate vs ConcurrencyDate? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement - Fields: CreationDate, LastUpdateDate, StartDate, EndDate, ConcurrencyDate`

**Business Logic**
- **Issue:** Multiple similar fields found: RequirementId, StatusId, RequirementTypeId, AuthorId, OwnerId, ImportanceId, ReleaseId, ComponentId, GoalId, ProjectId, ArtifactTypeId
- **Question:** What's the difference between RequirementId vs StatusId vs RequirementTypeId vs AuthorId vs OwnerId vs ImportanceId vs ReleaseId vs ComponentId vs GoalId vs ProjectId vs ArtifactTypeId? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement - Fields: RequirementId, StatusId, RequirementTypeId, AuthorId, OwnerId, ImportanceId, ReleaseId, ComponentId, GoalId, ProjectId, ArtifactTypeId`

**Business Logic**
- **Issue:** Multiple similar fields found: Name, AuthorName, OwnerName, StatusName, ImportanceName, ProjectName, RequirementTypeName
- **Question:** What's the difference between Name vs AuthorName vs OwnerName vs StatusName vs ImportanceName vs ProjectName vs RequirementTypeName? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement - Fields: Name, AuthorName, OwnerName, StatusName, ImportanceName, ProjectName, RequirementTypeName`

**Business Logic**
- **Issue:** Multiple similar fields found: StatusId, StatusName
- **Question:** What's the difference between StatusId vs StatusName? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement - Fields: StatusId, StatusName`

**Business Logic**
- **Issue:** Multiple similar fields found: RequirementTypeId, RequirementTypeName, ArtifactTypeId
- **Question:** What's the difference between RequirementTypeId vs RequirementTypeName vs ArtifactTypeId? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement - Fields: RequirementTypeId, RequirementTypeName, ArtifactTypeId`

**Business Logic**
- **Issue:** Multiple similar fields found: OwnerId, OwnerGuid, OwnerName
- **Question:** What's the difference between OwnerId vs OwnerGuid vs OwnerName? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement - Fields: OwnerId, OwnerGuid, OwnerName`

**Business Logic**
- **Issue:** Multiple similar fields found: CoverageCountTotal, CoverageCountPassed, CoverageCountFailed, CoverageCountCaution, CoverageCountBlocked, TaskCount
- **Question:** What's the difference between CoverageCountTotal vs CoverageCountPassed vs CoverageCountFailed vs CoverageCountCaution vs CoverageCountBlocked vs TaskCount? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement - Fields: CoverageCountTotal, CoverageCountPassed, CoverageCountFailed, CoverageCountCaution, CoverageCountBlocked, TaskCount`

**Workflow Context**
- **Issue:** Missing workflow context
- **Question:** When should an LLM use this tool (GET /requirements)? What are the typical use cases? Are there related tools that should be used instead?
- **Context:** `This requires human knowledge of the overall system workflow`

#### 🟡 Medium Priority

**Vague Field Description**
- **Issue:** Vague description for field 'RequirementId': 'The id of the requirement (integer)'
- **Question:** Can you provide more context about 'RequirementId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement.properties.RequirementId`

**Vague Field Description**
- **Issue:** Vague description for field 'StatusId': 'The id of the requirement's status (integer).'
- **Question:** Can you provide more context about 'StatusId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement.properties.StatusId`

**Vague Field Description**
- **Issue:** Vague description for field 'RequirementTypeId': 'The type of requirement (integer).'
- **Question:** Can you provide more context about 'RequirementTypeId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement.properties.RequirementTypeId`

**Vague Field Description**
- **Issue:** Vague description for field 'AuthorId': 'The id of the user that wrote the requirement (integer)'
- **Question:** Can you provide more context about 'AuthorId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement.properties.AuthorId`

**Vague Field Description**
- **Issue:** Vague description for field 'OwnerId': 'The id of the user that the requirement is assigned-to (integer)'
- **Question:** Can you provide more context about 'OwnerId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement.properties.OwnerId`

**Vague Field Description**
- **Issue:** Vague description for field 'ImportanceId': 'The id of the importance of the requirement (integer)'
- **Question:** Can you provide more context about 'ImportanceId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement.properties.ImportanceId`

**Vague Field Description**
- **Issue:** Vague description for field 'ReleaseId': 'The id of the release the requirement is scheduled to implemented in (integer)'
- **Question:** Can you provide more context about 'ReleaseId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement.properties.ReleaseId`

**Vague Field Description**
- **Issue:** Vague description for field 'ComponentId': 'The id of the component the requirement is a part of (integer - these are created on a per project user by an administrator)'
- **Question:** Can you provide more context about 'ComponentId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement.properties.ComponentId`

**Vague Field Description**
- **Issue:** Vague description for field 'Name': 'The name of the requirement (string - required for POST)'
- **Question:** Can you provide more context about 'Name'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement.properties.Name`

**Vague Field Description**
- **Issue:** Vague description for field 'AuthorName': 'The display name of the user that wrote this requirement (string)'
- **Question:** Can you provide more context about 'AuthorName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement.properties.AuthorName`

**Vague Field Description**
- **Issue:** Vague description for field 'OwnerName': 'The display name of the user that this requirement is assigned-to (string)'
- **Question:** Can you provide more context about 'OwnerName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement.properties.OwnerName`

**Vague Field Description**
- **Issue:** Vague description for field 'StatusName': 'The display name of the status the requirement is in (string)'
- **Question:** Can you provide more context about 'StatusName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement.properties.StatusName`

**Vague Field Description**
- **Issue:** Vague description for field 'ImportanceName': 'The display name of the importance that the requirement is in (string)'
- **Question:** Can you provide more context about 'ImportanceName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement.properties.ImportanceName`

**Vague Field Description**
- **Issue:** Vague description for field 'ProjectName': 'The display name of the project that the requirement is associated with (string)'
- **Question:** Can you provide more context about 'ProjectName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement.properties.ProjectName`

**Vague Field Description**
- **Issue:** Vague description for field 'RequirementTypeName': 'The display name of the type of requirement (string)'
- **Question:** Can you provide more context about 'RequirementTypeName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement.properties.RequirementTypeName`

**Vague Field Description**
- **Issue:** Vague description for field 'GoalId': 'The id of the goal that the requirement belongs to'
- **Question:** Can you provide more context about 'GoalId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement.properties.GoalId`

**Vague Field Description**
- **Issue:** Vague description for field 'ProjectId': 'The id of the project that the artifact belongs to'
- **Question:** Can you provide more context about 'ProjectId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement.properties.ProjectId`

**Vague Field Description**
- **Issue:** Vague description for field 'ArtifactTypeId': 'The type of artifact that we have'
- **Question:** Can you provide more context about 'ArtifactTypeId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement.properties.ArtifactTypeId`

**Business Logic**
- **Issue:** Found ID/Name pairs: StatusId/StatusName, RequirementTypeId/RequirementTypeName, AuthorId/AuthorName, OwnerId/OwnerName, ImportanceId/ImportanceName, ProjectId/ProjectName
- **Question:** Should LLMs filter/search by ID or Name? What's the recommended approach for each pair?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement`

**Performance**
- **Issue:** Potential performance concern for 'my work' endpoint
- **Question:** What's a typical result set size for this endpoint? Are there performance issues with large result sets? Should we recommend a maximum limit?
- **Context:** `This endpoint uses client-side pagination - all results are retrieved from API`

#### 🟢 Low Priority

**Edge Cases**
- **Issue:** Many nullable fields: 22 fields can be null
- **Question:** Under what conditions are these fields null? Are there common scenarios where multiple fields are null?
- **Context:** `OpenAPI: components.schemas.RemoteRequirement - Nullable fields: RequirementId, StatusId, RequirementTypeId, AuthorId, OwnerId...`

---

## get_my_test_cases

**Endpoint:** `GET /test-cases`
**Artifact Type:** `test_case`

### Generated Docstring

```python
@mcp.tool()
def get_my_test_cases(limit: int = 25, offset: int = 0) -> str:
"""
Retrieves all testCases owned by the currently authenticated user

Maps to Spira API: GET /test-cases

**Pagination:** This endpoint uses CLIENT-SIDE pagination. The API returns
all results, and we slice them in Python. This is acceptable for 'my work'
queries which typically return < 500 items.

**For Display:** Modern LLMs can format JSON naturally for simple display.
For complex workflows where you've filtered or processed the data, use
format_artifacts_as_markdown() to ensure consistent formatting.

Args:
    limit: Maximum number of items to return (1-500, default: 25)
        Controls result set size for pagination.
    offset: Number of items to skip (>= 0, default: 0)
        Used for retrieving subsequent pages of results.

Returns:
    JSON string with structure:
    {
        "data": [
            {
                "TestCaseId": integer, nullable,  // The id of the test case
                "ExecutionStatusId": integer, nullable,  // The execution status id of the test case
                "AuthorId": integer, nullable,  // The id of the user that wrote the test case
                "OwnerId": integer, nullable,  // The id of the user that the test case is assigned-to
                "AuthorGuid": string,  // The guid of the author.
                "OwnerGuid": string,  // The guid of the owner.
                "TestCasePriorityId": integer, nullable,  // The id of the priority of the test case
                "TestCaseTypeId": integer, nullable,  // The type of test case, pass null to use the default value
                "TestCaseStatusId": integer,  // The status of the test case, pass 0 to use the default value
                "TestCaseFolderId": integer, nullable,  // The id of the folder the test case belongs to. Null = root folder
                // ... additional fields ...
            }
        ],
        "pagination": {
            "limit": 25,
            "offset": 0,
            "returned_count": 25,
            "total_count": 150,
            "has_more": true,
            "pagination_type": "client-side"
        }
    }

Key Fields:
    - TestCaseId: The id of the test case
    - ExecutionStatusId: The execution status id of the test case
    - AuthorId: The id of the user that wrote the test case
    - OwnerId: The id of the user that the test case is assigned-to
    - AuthorGuid: The guid of the author.
    - OwnerGuid: The guid of the owner.
    - TestCasePriorityId: The id of the priority of the test case
    - TestCaseTypeId: The type of test case, pass null to use the default value

When to Use:
    [TO BE FILLED: Describe use cases and scenarios]

Related Tools:
    - format_artifacts_as_markdown: Format filtered/processed results
    [TO BE FILLED: List other related tools]

Error Responses:
    {
        "error": "Invalid pagination parameters",
        "error_code": "INVALID_PARAMETER",
        "details": {
            "parameter": "limit",
            "value": 1000,
            "expected": "1-500"
        },
        "suggestion": "Use limit between 1 and 500"
    }

Example Usage:
    # Simple display - LLM formats naturally
    result_json = get_my_test_cases()
    # LLM can format this JSON for display without additional tools

    # Complex workflow - Use formatting tool for filtered results
    result_json = get_my_test_cases(limit=100)
    result = json.loads(result_json)
    filtered = [item for item in result["data"] if meets_criteria(item)]
    filtered_json = json.dumps({"data": filtered})
    readable = format_artifacts_as_markdown(filtered_json, "artifact_type")
"""
```

### Clarifications Needed

**Total Issues:** 31

#### 🔴 High Priority

**Missing Description**
- **Issue:** Missing endpoint description for GET /test-cases
- **Question:** What is the purpose of this endpoint? What does it return and when should it be used?
- **Context:** `OpenAPI: paths./test-cases.get.description`

**Business Logic**
- **Issue:** Multiple similar fields found: CreationDate, LastUpdateDate, ExecutionDate, ConcurrencyDate
- **Question:** What's the difference between CreationDate vs LastUpdateDate vs ExecutionDate vs ConcurrencyDate? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase - Fields: CreationDate, LastUpdateDate, ExecutionDate, ConcurrencyDate`

**Business Logic**
- **Issue:** Multiple similar fields found: TestCaseId, ExecutionStatusId, AuthorId, OwnerId, TestCasePriorityId, TestCaseTypeId, TestCaseStatusId, TestCaseFolderId, ComponentIds, AutomationEngineId, AutomationAttachmentId, ProjectId, ArtifactTypeId
- **Question:** What's the difference between TestCaseId vs ExecutionStatusId vs AuthorId vs OwnerId vs TestCasePriorityId vs TestCaseTypeId vs TestCaseStatusId vs TestCaseFolderId vs ComponentIds vs AutomationEngineId vs AutomationAttachmentId vs ProjectId vs ArtifactTypeId? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase - Fields: TestCaseId, ExecutionStatusId, AuthorId, OwnerId, TestCasePriorityId, TestCaseTypeId, TestCaseStatusId, TestCaseFolderId, ComponentIds, AutomationEngineId, AutomationAttachmentId, ProjectId, ArtifactTypeId`

**Business Logic**
- **Issue:** Multiple similar fields found: Name, AuthorName, OwnerName, ProjectName, TestCasePriorityName, TestCaseStatusName, TestCaseTypeName, ExecutionStatusName
- **Question:** What's the difference between Name vs AuthorName vs OwnerName vs ProjectName vs TestCasePriorityName vs TestCaseStatusName vs TestCaseTypeName vs ExecutionStatusName? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase - Fields: Name, AuthorName, OwnerName, ProjectName, TestCasePriorityName, TestCaseStatusName, TestCaseTypeName, ExecutionStatusName`

**Business Logic**
- **Issue:** Multiple similar fields found: ExecutionStatusId, TestCaseStatusId, TestCaseStatusName, ExecutionStatusName
- **Question:** What's the difference between ExecutionStatusId vs TestCaseStatusId vs TestCaseStatusName vs ExecutionStatusName? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase - Fields: ExecutionStatusId, TestCaseStatusId, TestCaseStatusName, ExecutionStatusName`

**Business Logic**
- **Issue:** Multiple similar fields found: TestCaseTypeId, TestCaseTypeName, ArtifactTypeId
- **Question:** What's the difference between TestCaseTypeId vs TestCaseTypeName vs ArtifactTypeId? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase - Fields: TestCaseTypeId, TestCaseTypeName, ArtifactTypeId`

**Business Logic**
- **Issue:** Multiple similar fields found: TestCasePriorityId, TestCasePriorityName
- **Question:** What's the difference between TestCasePriorityId vs TestCasePriorityName? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase - Fields: TestCasePriorityId, TestCasePriorityName`

**Business Logic**
- **Issue:** Multiple similar fields found: OwnerId, OwnerGuid, OwnerName
- **Question:** What's the difference between OwnerId vs OwnerGuid vs OwnerName? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase - Fields: OwnerId, OwnerGuid, OwnerName`

**Workflow Context**
- **Issue:** Missing workflow context
- **Question:** When should an LLM use this tool (GET /test-cases)? What are the typical use cases? Are there related tools that should be used instead?
- **Context:** `This requires human knowledge of the overall system workflow`

#### 🟡 Medium Priority

**Vague Field Description**
- **Issue:** Vague description for field 'TestCaseId': 'The id of the test case'
- **Question:** Can you provide more context about 'TestCaseId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase.properties.TestCaseId`

**Vague Field Description**
- **Issue:** Vague description for field 'AuthorId': 'The id of the user that wrote the test case'
- **Question:** Can you provide more context about 'AuthorId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase.properties.AuthorId`

**Vague Field Description**
- **Issue:** Vague description for field 'OwnerId': 'The id of the user that the test case is assigned-to'
- **Question:** Can you provide more context about 'OwnerId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase.properties.OwnerId`

**Vague Field Description**
- **Issue:** Vague description for field 'TestCasePriorityId': 'The id of the priority of the test case'
- **Question:** Can you provide more context about 'TestCasePriorityId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase.properties.TestCasePriorityId`

**Vague Field Description**
- **Issue:** Vague description for field 'TestCaseTypeId': 'The type of test case, pass null to use the default value'
- **Question:** Can you provide more context about 'TestCaseTypeId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase.properties.TestCaseTypeId`

**Vague Field Description**
- **Issue:** Vague description for field 'TestCaseFolderId': 'The id of the folder the test case belongs to. Null = root folder'
- **Question:** Can you provide more context about 'TestCaseFolderId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase.properties.TestCaseFolderId`

**Vague Field Description**
- **Issue:** Vague description for field 'AutomationEngineId': 'The id of the automation engine the associated test script uses (null if manual only)'
- **Question:** Can you provide more context about 'AutomationEngineId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase.properties.AutomationEngineId`

**Vague Field Description**
- **Issue:** Vague description for field 'AutomationAttachmentId': 'The id of the attachment that is being used to store the test script (file or url)'
- **Question:** Can you provide more context about 'AutomationAttachmentId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase.properties.AutomationAttachmentId`

**Vague Field Description**
- **Issue:** Vague description for field 'Name': 'The name of the test case'
- **Question:** Can you provide more context about 'Name'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase.properties.Name`

**Vague Field Description**
- **Issue:** Vague description for field 'AuthorName': 'The display name of the user that wrote the test case'
- **Question:** Can you provide more context about 'AuthorName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase.properties.AuthorName`

**Vague Field Description**
- **Issue:** Vague description for field 'OwnerName': 'The display name of the user that the test case is assigned-to'
- **Question:** Can you provide more context about 'OwnerName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase.properties.OwnerName`

**Vague Field Description**
- **Issue:** Vague description for field 'ProjectName': 'The display name of the project that the test case belongs to'
- **Question:** Can you provide more context about 'ProjectName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase.properties.ProjectName`

**Vague Field Description**
- **Issue:** Vague description for field 'TestCasePriorityName': 'The display name of the priority of the test case'
- **Question:** Can you provide more context about 'TestCasePriorityName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase.properties.TestCasePriorityName`

**Vague Field Description**
- **Issue:** Vague description for field 'TestCaseStatusName': 'The display name of the status of the test case'
- **Question:** Can you provide more context about 'TestCaseStatusName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase.properties.TestCaseStatusName`

**Vague Field Description**
- **Issue:** Vague description for field 'TestCaseTypeName': 'The display name of the type of the test case'
- **Question:** Can you provide more context about 'TestCaseTypeName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase.properties.TestCaseTypeName`

**Vague Field Description**
- **Issue:** Vague description for field 'ExecutionStatusName': 'The display name of the execution status'
- **Question:** Can you provide more context about 'ExecutionStatusName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase.properties.ExecutionStatusName`

**Vague Field Description**
- **Issue:** Vague description for field 'ProjectId': 'The id of the project that the artifact belongs to'
- **Question:** Can you provide more context about 'ProjectId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase.properties.ProjectId`

**Vague Field Description**
- **Issue:** Vague description for field 'ArtifactTypeId': 'The type of artifact that we have'
- **Question:** Can you provide more context about 'ArtifactTypeId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase.properties.ArtifactTypeId`

**Business Logic**
- **Issue:** Found ID/Name pairs: ExecutionStatusId/ExecutionStatusName, AuthorId/AuthorName, OwnerId/OwnerName, TestCasePriorityId/TestCasePriorityName, TestCaseTypeId/TestCaseTypeName, TestCaseStatusId/TestCaseStatusName, ProjectId/ProjectName
- **Question:** Should LLMs filter/search by ID or Name? What's the recommended approach for each pair?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase`

**Performance**
- **Issue:** Potential performance concern for 'my work' endpoint
- **Question:** What's a typical result set size for this endpoint? Are there performance issues with large result sets? Should we recommend a maximum limit?
- **Context:** `This endpoint uses client-side pagination - all results are retrieved from API`

#### 🟢 Low Priority

**Complex Nested Schema**
- **Issue:** Schema contains multiple array fields: ComponentIds, TestSteps, CustomProperties
- **Question:** Are all these arrays (ComponentIds, TestSteps, CustomProperties) typically populated? Should any be excluded for performance?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase`

**Edge Cases**
- **Issue:** Many nullable fields: 12 fields can be null
- **Question:** Under what conditions are these fields null? Are there common scenarios where multiple fields are null?
- **Context:** `OpenAPI: components.schemas.RemoteTestCase - Nullable fields: TestCaseId, ExecutionStatusId, AuthorId, OwnerId, TestCasePriorityId...`

---

## get_my_test_sets

**Endpoint:** `GET /test-sets`
**Artifact Type:** `test_set`

### Generated Docstring

```python
@mcp.tool()
def get_my_test_sets(limit: int = 25, offset: int = 0) -> str:
"""
Retrieves all testSets owned by the currently authenticated user

Maps to Spira API: GET /test-sets

**Pagination:** This endpoint uses CLIENT-SIDE pagination. The API returns
all results, and we slice them in Python. This is acceptable for 'my work'
queries which typically return < 500 items.

**For Display:** Modern LLMs can format JSON naturally for simple display.
For complex workflows where you've filtered or processed the data, use
format_artifacts_as_markdown() to ensure consistent formatting.

Args:
    limit: Maximum number of items to return (1-500, default: 25)
        Controls result set size for pagination.
    offset: Number of items to skip (>= 0, default: 0)
        Used for retrieving subsequent pages of results.

Returns:
    JSON string with structure:
    {
        "data": [
            {
                "TestSetId": integer, nullable,  // The id of the test set
                "IndentLevel": string,  // (Not used in this version of the API)
                "TestSetStatusId": integer,  // The id of the test set's status
                "CreatorId": integer, nullable,  // The id of the user who created the test set
                "OwnerId": integer, nullable,  // The id of the user who the test set is assigned-to
                "CreatorGuid": string,  // The guid of the creator.
                "OwnerGuid": string,  // The guid of the owner.
                "ReleaseId": integer, nullable,  // The id of the release that the test set is assigned-to
                "ReleaseGuid": string,  // The guid of the release
                "AutomationHostId": integer, nullable,  // The id of the automation host the test set is assigned-to
                // ... additional fields ...
            }
        ],
        "pagination": {
            "limit": 25,
            "offset": 0,
            "returned_count": 25,
            "total_count": 150,
            "has_more": true,
            "pagination_type": "client-side"
        }
    }

Key Fields:
    - TestSetId: The id of the test set
    - IndentLevel: (Not used in this version of the API)
    - TestSetStatusId: The id of the test set's status
    - CreatorId: The id of the user who created the test set
    - OwnerId: The id of the user who the test set is assigned-to
    - CreatorGuid: The guid of the creator.
    - OwnerGuid: The guid of the owner.
    - ReleaseId: The id of the release that the test set is assigned-to

When to Use:
    [TO BE FILLED: Describe use cases and scenarios]

Related Tools:
    - format_artifacts_as_markdown: Format filtered/processed results
    [TO BE FILLED: List other related tools]

Error Responses:
    {
        "error": "Invalid pagination parameters",
        "error_code": "INVALID_PARAMETER",
        "details": {
            "parameter": "limit",
            "value": 1000,
            "expected": "1-500"
        },
        "suggestion": "Use limit between 1 and 500"
    }

Example Usage:
    # Simple display - LLM formats naturally
    result_json = get_my_test_sets()
    # LLM can format this JSON for display without additional tools

    # Complex workflow - Use formatting tool for filtered results
    result_json = get_my_test_sets(limit=100)
    result = json.loads(result_json)
    filtered = [item for item in result["data"] if meets_criteria(item)]
    filtered_json = json.dumps({"data": filtered})
    readable = format_artifacts_as_markdown(filtered_json, "artifact_type")
"""
```

### Clarifications Needed

**Total Issues:** 30

#### 🔴 High Priority

**Missing Description**
- **Issue:** Missing endpoint description for GET /test-sets
- **Question:** What is the purpose of this endpoint? What does it return and when should it be used?
- **Context:** `OpenAPI: paths./test-sets.get.description`

**Business Logic**
- **Issue:** Multiple similar fields found: CreationDate, LastUpdateDate, PlannedDate, ExecutionDate, ConcurrencyDate
- **Question:** What's the difference between CreationDate vs LastUpdateDate vs PlannedDate vs ExecutionDate vs ConcurrencyDate? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet - Fields: CreationDate, LastUpdateDate, PlannedDate, ExecutionDate, ConcurrencyDate`

**Business Logic**
- **Issue:** Multiple similar fields found: TestSetId, TestSetStatusId, CreatorId, OwnerId, ReleaseId, AutomationHostId, TestRunTypeId, RecurrenceId, TestSetFolderId, TestConfigurationSetId, ProjectId, ArtifactTypeId
- **Question:** What's the difference between TestSetId vs TestSetStatusId vs CreatorId vs OwnerId vs ReleaseId vs AutomationHostId vs TestRunTypeId vs RecurrenceId vs TestSetFolderId vs TestConfigurationSetId vs ProjectId vs ArtifactTypeId? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet - Fields: TestSetId, TestSetStatusId, CreatorId, OwnerId, ReleaseId, AutomationHostId, TestRunTypeId, RecurrenceId, TestSetFolderId, TestConfigurationSetId, ProjectId, ArtifactTypeId`

**Business Logic**
- **Issue:** Multiple similar fields found: Name, CreatorName, OwnerName, ProjectName, TestSetStatusName, RecurrenceName
- **Question:** What's the difference between Name vs CreatorName vs OwnerName vs ProjectName vs TestSetStatusName vs RecurrenceName? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet - Fields: Name, CreatorName, OwnerName, ProjectName, TestSetStatusName, RecurrenceName`

**Business Logic**
- **Issue:** Multiple similar fields found: TestSetStatusId, TestSetStatusName
- **Question:** What's the difference between TestSetStatusId vs TestSetStatusName? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet - Fields: TestSetStatusId, TestSetStatusName`

**Business Logic**
- **Issue:** Multiple similar fields found: TestRunTypeId, ArtifactTypeId
- **Question:** What's the difference between TestRunTypeId vs ArtifactTypeId? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet - Fields: TestRunTypeId, ArtifactTypeId`

**Business Logic**
- **Issue:** Multiple similar fields found: OwnerId, OwnerGuid, OwnerName
- **Question:** What's the difference between OwnerId vs OwnerGuid vs OwnerName? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet - Fields: OwnerId, OwnerGuid, OwnerName`

**Business Logic**
- **Issue:** Multiple similar fields found: CountPassed, CountFailed, CountCaution, CountBlocked, CountNotRun, CountNotApplicable
- **Question:** What's the difference between CountPassed vs CountFailed vs CountCaution vs CountBlocked vs CountNotRun vs CountNotApplicable? When should each be used? Which is recommended for LLM filtering?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet - Fields: CountPassed, CountFailed, CountCaution, CountBlocked, CountNotRun, CountNotApplicable`

**Workflow Context**
- **Issue:** Missing workflow context
- **Question:** When should an LLM use this tool (GET /test-sets)? What are the typical use cases? Are there related tools that should be used instead?
- **Context:** `This requires human knowledge of the overall system workflow`

#### 🟡 Medium Priority

**Vague Field Description**
- **Issue:** Vague description for field 'TestSetId': 'The id of the test set'
- **Question:** Can you provide more context about 'TestSetId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet.properties.TestSetId`

**Vague Field Description**
- **Issue:** Vague description for field 'TestSetStatusId': 'The id of the test set's status'
- **Question:** Can you provide more context about 'TestSetStatusId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet.properties.TestSetStatusId`

**Vague Field Description**
- **Issue:** Vague description for field 'CreatorId': 'The id of the user who created the test set'
- **Question:** Can you provide more context about 'CreatorId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet.properties.CreatorId`

**Vague Field Description**
- **Issue:** Vague description for field 'OwnerId': 'The id of the user who the test set is assigned-to'
- **Question:** Can you provide more context about 'OwnerId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet.properties.OwnerId`

**Vague Field Description**
- **Issue:** Vague description for field 'ReleaseId': 'The id of the release that the test set is assigned-to'
- **Question:** Can you provide more context about 'ReleaseId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet.properties.ReleaseId`

**Vague Field Description**
- **Issue:** Vague description for field 'AutomationHostId': 'The id of the automation host the test set is assigned-to'
- **Question:** Can you provide more context about 'AutomationHostId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet.properties.AutomationHostId`

**Vague Field Description**
- **Issue:** Vague description for field 'TestRunTypeId': 'The id of the type of test set (1 = Manual, 2 = Automated)'
- **Question:** Can you provide more context about 'TestRunTypeId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet.properties.TestRunTypeId`

**Vague Field Description**
- **Issue:** Vague description for field 'RecurrenceId': 'The id of the recurrence pattern the test set is scheduled for'
- **Question:** Can you provide more context about 'RecurrenceId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet.properties.RecurrenceId`

**Vague Field Description**
- **Issue:** Vague description for field 'Name': 'The name of the test set'
- **Question:** Can you provide more context about 'Name'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet.properties.Name`

**Vague Field Description**
- **Issue:** Vague description for field 'CreatorName': 'The display name of the user that created the test set'
- **Question:** Can you provide more context about 'CreatorName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet.properties.CreatorName`

**Vague Field Description**
- **Issue:** Vague description for field 'OwnerName': 'The display name of the user that the test set is assigned-to'
- **Question:** Can you provide more context about 'OwnerName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet.properties.OwnerName`

**Vague Field Description**
- **Issue:** Vague description for field 'ProjectName': 'The display name of the project that the test set belongs to'
- **Question:** Can you provide more context about 'ProjectName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet.properties.ProjectName`

**Vague Field Description**
- **Issue:** Vague description for field 'TestSetStatusName': 'The display name of the status of the test set'
- **Question:** Can you provide more context about 'TestSetStatusName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet.properties.TestSetStatusName`

**Vague Field Description**
- **Issue:** Vague description for field 'RecurrenceName': 'The display name of the recurrence pattern'
- **Question:** Can you provide more context about 'RecurrenceName'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet.properties.RecurrenceName`

**Vague Field Description**
- **Issue:** Vague description for field 'TestSetFolderId': 'The ID of the test set folder this test set belongs to (NULL = root)'
- **Question:** Can you provide more context about 'TestSetFolderId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet.properties.TestSetFolderId`

**Vague Field Description**
- **Issue:** Vague description for field 'TestConfigurationSetId': 'The id of any test configuration set to be used with this test set'
- **Question:** Can you provide more context about 'TestConfigurationSetId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet.properties.TestConfigurationSetId`

**Vague Field Description**
- **Issue:** Vague description for field 'ProjectId': 'The id of the project that the artifact belongs to'
- **Question:** Can you provide more context about 'ProjectId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet.properties.ProjectId`

**Vague Field Description**
- **Issue:** Vague description for field 'ArtifactTypeId': 'The type of artifact that we have'
- **Question:** Can you provide more context about 'ArtifactTypeId'? What does it represent in business terms?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet.properties.ArtifactTypeId`

**Business Logic**
- **Issue:** Found ID/Name pairs: TestSetStatusId/TestSetStatusName, CreatorId/CreatorName, OwnerId/OwnerName, RecurrenceId/RecurrenceName, ProjectId/ProjectName
- **Question:** Should LLMs filter/search by ID or Name? What's the recommended approach for each pair?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet`

**Performance**
- **Issue:** Potential performance concern for 'my work' endpoint
- **Question:** What's a typical result set size for this endpoint? Are there performance issues with large result sets? Should we recommend a maximum limit?
- **Context:** `This endpoint uses client-side pagination - all results are retrieved from API`

#### 🟢 Low Priority

**Edge Cases**
- **Issue:** Many nullable fields: 20 fields can be null
- **Question:** Under what conditions are these fields null? Are there common scenarios where multiple fields are null?
- **Context:** `OpenAPI: components.schemas.RemoteTestSet - Nullable fields: TestSetId, CreatorId, OwnerId, ReleaseId, AutomationHostId...`

---

## Examples of Good Clarification Requests

### Example 1: Ambiguous Field Description
**Issue:** Field 'EstimatedEffort' has vague description: 'The estimated effort'

**Good Question:**
> What is the purpose of the 'EstimatedEffort' field? Is this the original estimate set at task creation, or can it be updated? What unit is it measured in (hours, minutes, story points)? When would it be null?

**Context:** `OpenAPI: components.schemas.RemoteTask.properties.EstimatedEffort`

---

### Example 2: Business Logic Question
**Issue:** Multiple similar fields: EstimatedEffort, ActualEffort, RemainingEffort, ProjectedEffort

**Good Question:**
> What's the difference between EstimatedEffort, ActualEffort, RemainingEffort, and ProjectedEffort? When should each be used? Is ProjectedEffort calculated (ActualEffort + RemainingEffort) or manually set? Which field should LLMs use for filtering 'tasks that will take more than 2 hours'?

**Context:** `OpenAPI: components.schemas.RemoteTask - Fields: EstimatedEffort, ActualEffort, RemainingEffort, ProjectedEffort`

---

### Example 3: Workflow Context
**Issue:** Missing workflow context for get_my_tasks

**Good Question:**
> When should an LLM use get_my_tasks vs get_task_by_id (future tool) vs search_tasks (future tool)? What are typical use cases for this tool? Should it be used for daily standup reports, workload analysis, or both?

**Context:** This requires human knowledge of the overall system workflow

---

### Example 4: Edge Cases
**Issue:** Behavior when user has no assigned tasks is unclear

**Good Question:**
> What should this tool return when the user has no assigned tasks? Should it return an empty array with pagination metadata, or should it return a specific message? Are there any error conditions that should be documented?

**Context:** `OpenAPI: paths./tasks.get.responses.200`
