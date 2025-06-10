# General artifact formatting features
def format_task(task) -> str:
    task_info = f"""
## Task [TK:{task['TaskId']}] - {task['Name']}
{'' if task['Description'] is None else task['Description']}
- **Status:** {task['TaskStatusName']}
- **Type:** {task['TaskTypeName']}
- **Priority:** {task['TaskPriorityName']}
- **Due Date:** {task['EndDate']}
"""
    return task_info

def format_incident(incident) -> str:
    incident_info = f"""
## Incident [IN:{incident['IncidentId']}] - {incident['Name']}
{'' if incident['Description'] is None else incident['Description']}
- **Status:** {incident['IncidentStatusName']}
- **Type:** {incident['IncidentTypeName']}
- **Priority:** {incident['PriorityName']}
- **Due Date:** {incident['StartDate']}
"""
    return incident_info

def format_requirement(requirement) -> str:
    requirement_info = f"""
## Requirement [RQ:{requirement['RequirementId']}] - {requirement['Name']}
{'' if requirement['Description'] is None else requirement['Description']}
- **Status:** {requirement['RequirementStatusName']}
- **Type:** {requirement['RequirementTypeName']}
- **Importance:** {requirement['ImportanceName']}
- **Release:** {requirement['ReleaseVersionNumber']}
"""
    return requirement_info

def format_test_case(test_case) -> str:
    test_case_info = f"""
## Test Case [TC:{test_case['TestCaseId']}] - {test_case['Name']}
{'' if test_case['Description'] is None else test_case['Description']}
- **Status:** {test_case['TestCaseStatusName']}
- **Type:** {test_case['TestCaseTypeName']}
- **Priority:** {test_case['TestCasePriorityName']}
- **Last Execution Status:** {test_case['ExecutionStatusName']}
- **Last Executed:** {test_case['ExecutionDate']}
"""
    return test_case_info

def format_test_set(test_set) -> str:
    test_set_info = f"""
## Test Set [TX:{test_set['TestSetId']}] - {test_set['Name']}
{'' if test_set['Description'] is None else test_set['Description']}
- **Status:** {test_set['TestSetStatusName']}
- **Type:** {test_set['TestCaseTypeName']}
- **Release:** {test_set['ReleaseVersionNumber']}
- **Recurrence:** {test_set['RecurrenceName']}
- **Due Date:** {test_set['PlannedDate']}
"""
    return test_set_info