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
