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
## Task [IN:{incident['IncidentId']}] - {incident['Name']}
{'' if incident['Description'] is None else incident['Description']}
- **Status:** {incident['IncidentStatusName']}
- **Type:** {incident['IncidentTypeName']}
- **Priority:** {incident['PriorityName']}
- **Due Date:** {incident['StartDate']}
"""
    return incident_info
