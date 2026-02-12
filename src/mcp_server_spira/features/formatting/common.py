"""Common formatting utilities for converting artifacts to markdown.

This module provides helper functions for formatting individual artifact types
with consistent markdown structure.
"""

from typing import Any


def _format_description(description: str | None) -> str:
    """
    Format description field, handling None values.

    Args:
        description: The description text or None

    Returns:
        Empty string if None, otherwise the description text
    """
    return "" if description is None else description


def _format_optional_field(label: str, value: Any | None, prefix: str = "") -> str:
    """
    Format an optional field, only including it if value is not None.

    Args:
        label: The field label (e.g., "Detected in Release")
        value: The field value or None
        prefix: Optional prefix for the value (e.g., "RL:" for release IDs)

    Returns:
        Formatted markdown line or empty string if value is None
    """
    if value is None:
        return ""
    return f"- **{label}:** {prefix}{value}\n"


def _format_header(artifact_type: str, artifact_id: int, name: str, prefix: str) -> str:
    """
    Format a consistent header for artifacts.

    Args:
        artifact_type: Type of artifact (e.g., "Task", "Incident")
        artifact_id: Numeric ID of the artifact
        name: Name/title of the artifact
        prefix: ID prefix (e.g., "TK", "IN")

    Returns:
        Formatted markdown header
    """
    return f"## {artifact_type} [{prefix}:{artifact_id}] - {name}\n"


def format_task(task: dict) -> str:
    """
    Format a task artifact as markdown.

    Args:
        task: Task data dictionary

    Returns:
        Markdown formatted string
    """
    header = _format_header("Task", task["TaskId"], task["Name"], "TK")
    description = _format_description(task.get("Description"))

    # Build effort information if available
    effort_info = ""
    if task.get("EstimatedEffort"):
        actual = task.get("ActualEffort", 0)
        estimated = task["EstimatedEffort"]
        percent = task.get("CompletionPercent", 0)
        effort_info = f"- **Effort:** {actual}/{estimated} min ({percent}% complete)\n"

    task_info = f"""{header}{description}
- **Status:** {task["TaskStatusName"]}
- **Type:** {task["TaskTypeName"]}
- **Priority:** {task["TaskPriorityName"]}
{effort_info}- **Due Date:** {task.get("EndDate", "Not set")}
"""

    # Add optional fields
    if task.get("OwnerName"):
        task_info += f"- **Owner:** {task['OwnerName']}\n"
    if task.get("ReleaseVersionNumber"):
        task_info += f"- **Release:** {task['ReleaseVersionNumber']}\n"

    return task_info


def format_incident(incident: dict) -> str:
    """
    Format an incident artifact as markdown.

    Args:
        incident: Incident data dictionary

    Returns:
        Markdown formatted string
    """
    header = _format_header("Incident", incident["IncidentId"], incident["Name"], "IN")
    description = _format_description(incident.get("Description"))

    incident_info = f"""{header}{description}
- **Status:** {incident["IncidentStatusName"]}
- **Type:** {incident["IncidentTypeName"]}
- **Priority:** {incident["PriorityName"]}
- **Severity:** {incident.get("SeverityName", "Not set")}
- **Start Date:** {incident.get("StartDate", "Not set")}
"""

    # Add optional release information
    # Support both ID and version number fields for backward compatibility
    detected_release = incident.get("DetectedReleaseVersionNumber") or incident.get(
        "DetectedReleaseId"
    )
    resolved_release = incident.get("ResolvedReleaseVersionNumber") or incident.get(
        "ResolvedReleaseId"
    )
    verified_release = incident.get("VerifiedReleaseVersionNumber") or incident.get(
        "VerifiedReleaseId"
    )

    incident_info += _format_optional_field("Detected in Release", detected_release)
    incident_info += _format_optional_field("Planned for Release", resolved_release)
    incident_info += _format_optional_field("Verified in Release", verified_release)

    # Add owner if available
    if incident.get("OwnerName"):
        incident_info += f"- **Owner:** {incident['OwnerName']}\n"

    return incident_info


def format_requirement(requirement: dict) -> str:
    """
    Format a requirement artifact as markdown.

    Args:
        requirement: Requirement data dictionary

    Returns:
        Markdown formatted string
    """
    header = _format_header("Requirement", requirement["RequirementId"], requirement["Name"], "RQ")
    description = _format_description(requirement.get("Description"))

    requirement_info = f"""{header}{description}
- **Status:** {requirement["StatusName"]}
- **Type:** {requirement["RequirementTypeName"]}
- **Importance:** {requirement["ImportanceName"]}
"""

    # Add optional fields
    if requirement.get("ReleaseVersionNumber"):
        requirement_info += f"- **Release:** {requirement['ReleaseVersionNumber']}\n"
    if requirement.get("OwnerName"):
        requirement_info += f"- **Owner:** {requirement['OwnerName']}\n"

    return requirement_info


def format_test_case(test_case: dict) -> str:
    """
    Format a test case artifact as markdown.

    Args:
        test_case: Test case data dictionary

    Returns:
        Markdown formatted string
    """
    header = _format_header("Test Case", test_case["TestCaseId"], test_case["Name"], "TC")
    description = _format_description(test_case.get("Description"))

    test_case_info = f"""{header}{description}
- **Status:** {test_case["TestCaseStatusName"]}
- **Type:** {test_case["TestCaseTypeName"]}
- **Priority:** {test_case["TestCasePriorityName"]}
- **Last Execution Status:** {test_case.get("ExecutionStatusName", "Not executed")}
"""

    # Add optional fields
    if test_case.get("ExecutionDate"):
        test_case_info += f"- **Last Executed:** {test_case['ExecutionDate']}\n"
    if test_case.get("OwnerName"):
        test_case_info += f"- **Owner:** {test_case['OwnerName']}\n"

    return test_case_info


def format_test_set(test_set: dict) -> str:
    """
    Format a test set artifact as markdown.

    Args:
        test_set: Test set data dictionary

    Returns:
        Markdown formatted string
    """
    header = _format_header("Test Set", test_set["TestSetId"], test_set["Name"], "TX")
    description = _format_description(test_set.get("Description"))

    test_set_info = f"""{header}{description}
- **Status:** {test_set["TestSetStatusName"]}
"""

    # Add optional fields
    if test_set.get("ReleaseVersionNumber"):
        test_set_info += f"- **Release:** {test_set['ReleaseVersionNumber']}\n"
    if test_set.get("RecurrenceName"):
        test_set_info += f"- **Recurrence:** {test_set['RecurrenceName']}\n"
    if test_set.get("PlannedDate"):
        test_set_info += f"- **Due Date:** {test_set['PlannedDate']}\n"
    if test_set.get("OwnerName"):
        test_set_info += f"- **Owner:** {test_set['OwnerName']}\n"

    return test_set_info


def format_test_case_folder(test_case_folder: dict) -> str:
    """
    Format a test case folder as markdown.

    Args:
        test_case_folder: Test case folder data dictionary

    Returns:
        Markdown formatted string
    """
    description = _format_description(test_case_folder.get("Description"))
    return f"""# Test Folder: {test_case_folder["Name"]}
{description}
"""


def format_test_set_folder(test_set_folder: dict) -> str:
    """
    Format a test set folder as markdown.

    Args:
        test_set_folder: Test set folder data dictionary

    Returns:
        Markdown formatted string
    """
    description = _format_description(test_set_folder.get("Description"))
    return f"""# Test Set Folder: {test_set_folder["Name"]}
{description}
"""


def format_product(product: dict) -> str:
    """
    Format a product artifact as markdown.

    Args:
        product: Product data dictionary

    Returns:
        Markdown formatted string
    """
    header = _format_header("Product", product["ProjectId"], product["Name"], "PR")
    description = _format_description(product.get("Description"))

    product_info = f"""{header}{description}
"""

    # Add optional fields
    if product.get("Website"):
        product_info += f"- **Website:** {product['Website']}\n"
    if product.get("ProjectTemplateId"):
        product_info += f"- **Template ID:** [PT:{product['ProjectTemplateId']}]\n"
    if product.get("ProjectGroupId"):
        product_info += f"- **Program ID:** [PG:{product['ProjectGroupId']}]\n"
    if product.get("PercentComplete") is not None:
        product_info += f"- **% Complete:** {product['PercentComplete']}%\n"
    if product.get("StartDate"):
        product_info += f"- **Start Date:** {product['StartDate']}\n"
    if product.get("EndDate"):
        product_info += f"- **End Date:** {product['EndDate']}\n"

    return product_info


def format_product_template(template: dict) -> str:
    """
    Format a product template as markdown.

    Args:
        template: Product template data dictionary

    Returns:
        Markdown formatted string
    """
    header = _format_header(
        "Product Template", template["ProjectTemplateId"], template["Name"], "PT"
    )
    description = _format_description(template.get("Description"))

    return f"""{header}{description}
"""


def format_program(program: dict) -> str:
    """
    Format a program artifact as markdown.

    Args:
        program: Program data dictionary

    Returns:
        Markdown formatted string
    """
    header = _format_header("Program", program["ProgramId"], program["Name"], "PG")
    description = _format_description(program.get("Description"))

    program_info = f"""{header}{description}
"""

    # Add optional fields
    if program.get("Website"):
        program_info += f"- **Website:** {program['Website']}\n"
    if program.get("ProjectTemplateId"):
        program_info += f"- **Product Template ID:** [PT:{program['ProjectTemplateId']}]\n"
    if program.get("PortfolioId"):
        program_info += f"- **Portfolio ID:** [PF:{program['PortfolioId']}]\n"

    return program_info


def format_milestone(milestone: dict) -> str:
    """
    Format a milestone artifact as markdown.

    Args:
        milestone: Milestone data dictionary

    Returns:
        Markdown formatted string
    """
    header = _format_header("Milestone", milestone["MilestoneId"], milestone["Name"], "GM")
    description = _format_description(milestone.get("Description"))

    milestone_info = f"""{header}{description}
- **Status:** {milestone["StatusName"]}
- **Type:** {milestone["TypeName"]}
"""

    # Add optional fields
    if milestone.get("PercentComplete") is not None:
        milestone_info += f"- **% Complete:** {milestone['PercentComplete']}%\n"
    if milestone.get("StartDate"):
        milestone_info += f"- **Start Date:** {milestone['StartDate']}\n"
    if milestone.get("EndDate"):
        milestone_info += f"- **End Date:** {milestone['EndDate']}\n"

    return milestone_info


def format_release(release: dict) -> str:
    """
    Format a release artifact as markdown.

    Args:
        release: Release data dictionary

    Returns:
        Markdown formatted string
    """
    header = _format_header("Release", release["ReleaseId"], release["Name"], "RL")
    description = _format_description(release.get("Description"))

    release_info = f"""{header}{description}
- **Version #:** {release["VersionNumber"]}
- **Status:** {release["ReleaseStatusName"]}
- **Type:** {release["ReleaseTypeName"]}
"""

    # Add optional fields
    if release.get("PercentComplete") is not None:
        release_info += f"- **% Complete:** {release['PercentComplete']}%\n"
    if release.get("StartDate"):
        release_info += f"- **Start Date:** {release['StartDate']}\n"
    if release.get("EndDate"):
        release_info += f"- **End Date:** {release['EndDate']}\n"

    return release_info


def format_risk(risk: dict) -> str:
    """
    Format a risk artifact as markdown.

    Args:
        risk: Risk data dictionary

    Returns:
        Markdown formatted string
    """
    header = _format_header("Risk", risk["RiskId"], risk["Name"], "RK")
    description = _format_description(risk.get("Description"))

    risk_info = f"""{header}{description}
- **Status:** {risk["RiskStatusName"]}
- **Type:** {risk["RiskTypeName"]}
- **Probability:** {risk["RiskProbabilityName"]}
- **Impact:** {risk["RiskImpactName"]}
"""

    # Add optional fields
    if risk.get("RiskExposure") is not None:
        risk_info += f"- **Exposure:** {risk['RiskExposure']}\n"
    if risk.get("ReviewDate"):
        risk_info += f"- **Review Date:** {risk['ReviewDate']}\n"

    return risk_info


def format_test_run(test_run: dict) -> str:
    """
    Format a test run artifact as markdown.

    Args:
        test_run: Test run data dictionary

    Returns:
        Markdown formatted string
    """
    from mcp_server_spira.utils.general import get_execution_status_name

    header = _format_header("Test Run", test_run["TestRunId"], test_run["Name"], "TR")

    # Get execution status name
    status_name = get_execution_status_name(test_run["ExecutionStatusId"])

    test_run_info = f"""{header}- **Status:** {status_name}
"""

    # Add optional fields
    if test_run.get("TestCaseId"):
        test_run_info += f"- **Test Case:** TC:{test_run['TestCaseId']}\n"
    if test_run.get("TestSetId"):
        test_run_info += f"- **Test Set:** TX:{test_run['TestSetId']}\n"
    if test_run.get("ReleaseVersionNumber"):
        test_run_info += f"- **Release:** {test_run['ReleaseVersionNumber']}\n"
    if test_run.get("StartDate"):
        test_run_info += f"- **Start Date:** {test_run['StartDate']}\n"
    if test_run.get("EndDate"):
        test_run_info += f"- **End Date:** {test_run['EndDate']}\n"

    return test_run_info


def format_automation_host(host: dict) -> str:
    """
    Format an automation host as markdown.

    Args:
        host: Automation host data dictionary

    Returns:
        Markdown formatted string
    """
    header = _format_header("Automation Host", host["AutomationHostId"], host["Name"], "AH")
    description = _format_description(host.get("Description"))

    host_info = f"""{header}{description}
"""

    # Add optional fields
    if host.get("Token"):
        host_info += f"- **Token:** {host['Token']}\n"
    if host.get("Active") is not None:
        host_info += f"- **Active:** {host['Active']}\n"
    if host.get("LastContactDate"):
        host_info += f"- **Last Contact:** {host['LastContactDate']}\n"

    return host_info


def format_capability(capability: dict) -> str:
    """
    Format a program capability as markdown.

    Args:
        capability: Capability data dictionary

    Returns:
        Markdown formatted string
    """
    header = _format_header("Capability", capability["CapabilityId"], capability["Name"], "CP")
    description = _format_description(capability.get("Description"))

    capability_info = f"""{header}{description}
- **Status:** {capability["StatusName"]}
- **Type:** {capability["TypeName"]}
- **Priority:** {capability["PriorityName"]}
"""

    # Add optional fields
    if capability.get("PercentComplete") is not None:
        capability_info += f"- **% Complete:** {capability['PercentComplete']}%\n"
    if capability.get("MilestoneName"):
        capability_info += f"- **Milestone:** {capability['MilestoneName']}\n"
    if capability.get("RequirementCount") is not None:
        capability_info += f"- **# Requirements:** {capability['RequirementCount']}\n"

    return capability_info
