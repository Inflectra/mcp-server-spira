"""
Inflectra Spira general utilities.

This module provides helper functions for working with data in Spira
"""

def get_execution_status_name(execution_status_id: int) -> str:
    """
    Gets the name of a Spira test execution status from its ID

    Args:
        execution_status_id: The ID of the execution status
                
    Returns:
        The name of the matching execution status or an empty string, if no match
    """

    if execution_status_id == None:
        return ""
    
    # Find the matching status id
    # 1 = Failed, 2 = Passed, 3 = Not Run, 4 = N/A, 5 = Blocked and 6 = Caution
    match execution_status_id:
        case 1:
            return "Failed"
        case 2:
            return "Passed"
        case 3:
            return "Not Run"
        case 4:
            return "N/A"
        case 5:
            return "Blocked"
        case 6:
            return "Caution"

    return "(Unknown)"