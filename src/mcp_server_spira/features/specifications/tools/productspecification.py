"""
Provides operations for retrieving the product specification files that
can be used to build the functionality of the product using AI.
This is used by Agentic AI development tools such as Amazon Kiro
for building applications from a formal spec.

A product specification consists of the data in markdown format used by Kiro to generate
the following files:
    - requirements.md - Captures user stories and acceptance criteria in structured EARS notation
    - design.md - Documents technical architecture, sequence diagrams, and implementation considerations
    - tasks.md - Provides a detailed implementation plan with discrete, trackable tasks
    - test-cases.md - Includes detailed test scenarios and steps, expected results and pass/fail criteria

This module provides the following MCP tools for retrieving the entire product specifications:
    - get_specification_requirements - returns the data for populating the requirements.md file
    - get_specification_design - returns the data for populating the design.md file
    - get_specification_tasks - returns the data for populating the tasks.md file
    - get_specification_test_cases - returns the data for populating the test-cases.md file
"""

from typing import Any

from mcp.server.fastmcp.utilities.logging import get_logger

from mcp_server_spira.config import resolve_product_id
from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import ErrorCodes, format_error_response
from mcp_server_spira.features.common.validation import ParameterValidator

# Get a logger instance, typically named after the current module
logger = get_logger(__name__)


async def _get_product_by_id(spira_client, product_id: int) -> Any:
    """
    Implementation of retrieving a single Spira product by its ID

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45.

    Returns:
        The product object from Spira
    """
    try:
        # Get the product by its ID
        product_url = f"projects/{product_id}"
        product = await spira_client.make_spira_api_get_request(product_url)

        if not product:
            return "There was no product with that ID available"

        return product
    except Exception as e:
        raise e


async def _get_release_by_id(spira_client, product_id: int, release_id: int) -> Any:
    """
    Retrieves a single release in the specified product with the specified ID

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45.
        release_id: The numeric ID of the release. If the ID is RL:12, just use 12.

    Returns:
        The Spira release object
    """
    try:
        # Get the release in the product
        release_url = f"projects/{product_id}/releases/{release_id}"
        release = await spira_client.make_spira_api_get_request(release_url)

        if not release:
            return "There is no release with the specified ID."

        # Return the object
        return release
    except Exception as e:
        raise e


async def _get_specification_requirements(
    spira_client, product_id: int, release_id: int | None
) -> list[Any]:
    """
    Gets the list of requirements in the product/release

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45.
        release_id: The numeric ID of the release. If the ID is RL:12, just use 12. (optional)

    Returns:
        List of requirements
    """
    try:
        requirements = []
        starting_row = 1
        number_of_rows = 250
        more_results = True

        # See if we are filtering by release or not
        if release_id:
            while more_results:
                requirements_url = f"projects/{product_id}/requirements/search?starting_row={starting_row}&number_of_rows={number_of_rows}"
                body = [{"PropertyName": "ReleaseId", "IntValue": release_id}]
                results = await spira_client.make_spira_api_post_request(requirements_url, body)
                if not results:
                    more_results = False
                else:
                    starting_row += number_of_rows
                requirements.extend(results)
        else:
            while more_results:
                requirements_url = f"projects/{product_id}/requirements?starting_row={starting_row}&number_of_rows={number_of_rows}"
                results = await spira_client.make_spira_api_get_request(requirements_url)
                if not results:
                    more_results = False
                else:
                    starting_row += number_of_rows
                requirements.extend(results)

        return requirements
    except Exception as e:
        raise e


async def _add_requirement_scenarios(
    spira_client, product_id: int, requirement_id: int, formatted_specification: list[str]
):
    """
    Gets the list of scenarios for a requirement and adds them to the output

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45.
        requirement_id: The numeric ID of the requirement. If the ID is RQ:12, just use 12
        formatted_specification: The output text in markdown format
    """
    scenarios_url = f"projects/{product_id}/requirements/{requirement_id}/steps"
    scenarios = await spira_client.make_spira_api_get_request(scenarios_url)
    if scenarios:
        formatted_specification.append("#### Acceptance Criteria\n\n")
        for scenario in scenarios:
            position = scenario["Position"]
            description = scenario["Description"]
            text = f"{position}. {description}\n"
            formatted_specification.append(text)
        formatted_specification.append("\n")


async def _add_requirement_test_cases(
    spira_client, product_id: int, requirement_id: int, formatted_specification: list[str]
):
    """
    Gets the list of test cases for a requirement and adds them to the output

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45.
        requirement_id: The numeric ID of the requirement. If the ID is RQ:12, just use 12
        formatted_specification: The output text in markdown format
    """
    req_test_cases_url = f"projects/{product_id}/requirements/{requirement_id}/test-cases"
    req_test_cases = await spira_client.make_spira_api_get_request(req_test_cases_url)
    if req_test_cases:
        formatted_specification.append("#### Test Cases\n\n")
        for req_test_case in req_test_cases:
            test_case_id = req_test_case["TestCaseId"]

            # Get the full details of the test case
            test_case_url = f"projects/{product_id}/test-cases/{test_case_id}"
            test_case = await spira_client.make_spira_api_get_request(test_case_url)

            if test_case:
                formatted_specification.append(
                    f"##### Test Case TC:{test_case_id}: {test_case['Name']}\n"
                )
                if test_case["Description"]:
                    description = (
                        f"**{test_case['TestCaseTypeName']}:** {test_case['Description']}\n"
                    )
                    formatted_specification.append(description)
                formatted_specification.append("\n")

                # Get the test case steps
                test_steps_url = f"projects/{product_id}/test-cases/{test_case_id}/test-steps"
                test_steps = await spira_client.make_spira_api_get_request(test_steps_url)

                # Format the test steps as a table
                if test_steps:
                    formatted_specification.append("##### Steps\n\n")
                    formatted_specification.append("<table>")
                    formatted_specification.append(
                        "<tr><th>Step #</th><th>Description</th><th>Expected Result</th><th>Sample Data</th></tr>"
                    )
                    for test_step in test_steps:
                        position = test_step["Position"]
                        description = test_step["Description"]
                        expected_result = test_step["ExpectedResult"]
                        sample_data = test_step["SampleData"]
                        formatted_specification.append("<tr>")
                        formatted_specification.append(f"<td>{position}.</td>")
                        formatted_specification.append(f"<td>{description}.</td>")
                        formatted_specification.append(f"<td>{expected_result}.</td>")
                        formatted_specification.append(f"<td>{sample_data}.</td>")
                        formatted_specification.append("</tr>")
                    formatted_specification.append("</table>")

        formatted_specification.append("\n")


async def _add_requirement_tasks(
    spira_client, product_id: int, requirement_id: int, formatted_specification: list[str]
):
    """
    Gets the list of tasks for a requirement and adds them to the output

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45.
        requirement_id: The numeric ID of the requirement. If the ID is RQ:12, just use 12
        formatted_specification: The output text in markdown format
    """

    # First, get the count of the number of total matching tasks
    body = [{"PropertyName": "RequirementId", "IntValue": requirement_id}]
    tasks_url = f"projects/{product_id}/tasks/count "
    task_count = await spira_client.make_spira_api_post_request(tasks_url, body)

    # Next, get all of the tasks using pagination
    tasks = []
    starting_row = 1
    number_of_rows = 250
    while starting_row < task_count:
        tasks_url = f"projects/{product_id}/tasks?starting_row={starting_row}&number_of_rows={number_of_rows}&sort_field=StartDate&sort_direction=ASC"
        results = await spira_client.make_spira_api_post_request(tasks_url, body)
        starting_row += number_of_rows
        tasks.extend(results)

    if tasks:
        formatted_specification.append("#### Tasks\n\n")
        for task in tasks:
            task_id = task["TaskId"]
            formatted_specification.append(f"##### Task TK:{task_id}: {task['Name']}\n")
            if task["Description"]:
                description = f"**{task['TaskTypeName']}:** {task['Description']}\n"
                formatted_specification.append(description)
            formatted_specification.append("\n")

        formatted_specification.append("\n")


async def _get_specification_risks(
    spira_client, product_id: int, release_id: int | None
) -> list[Any]:
    """
    Gets the list of risks in the product/release

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45.
        release_id: The numeric ID of the release. If the ID is RL:12, just use 12. (optional)

    Returns:
        List of risks
    """
    try:
        risks = []
        starting_row = 1
        number_of_rows = 250
        more_results = True
        body = []

        # See if we are filtering by release or not
        if release_id:
            body = [{"PropertyName": "ReleaseId", "IntValue": release_id}]

        while more_results:
            risks_url = f"projects/{product_id}/risks?starting_row={starting_row}&number_of_rows={number_of_rows}&sort_field=RiskExposure&sort_direction=DESC"
            results = await spira_client.make_spira_api_post_request(risks_url, body)
            if not results:
                more_results = False
            else:
                starting_row += number_of_rows
            risks.extend(results)

        return risks
    except Exception as e:
        raise e


async def _add_risk_mitigations(
    spira_client, product_id: int, risk_id: int, formatted_specification: list[str]
):
    """
    Gets the list of mitigations for a risk and adds them to the output

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45.
        risk_id: The numeric ID of the risk. If the ID is RK:12, just use 12
        formatted_specification: The output text in markdown format
    """
    mitigations_url = f"projects/{product_id}/risks/{risk_id}/mitigations"
    mitigations = await spira_client.make_spira_api_get_request(mitigations_url)
    if mitigations:
        formatted_specification.append("#### Mitigations\n\n")
        for mitigation in mitigations:
            position = mitigation["Position"]
            description = mitigation["Description"]
            text = f"{position}. {description}\n"
            formatted_specification.append(text)
        formatted_specification.append("\n")


async def _get_specification_requirements_impl(
    spira_client, product_id: int, release_id: int | None
) -> str:
    """
    Implementation of retrieving the requirements markdown specification for the specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45.
        release_id: The numeric ID of the release. If the ID is RL:12, just use 12.
                    If no release is specified, then the specification for the entire
                    project is returned

    Returns:
        Formatted string containing the product requirements specification
    """
    try:
        formatted_specification = []

        # Get the product information
        logger.info("Getting the product overview")
        product = await _get_product_by_id(spira_client, product_id)
        product_name = product["Name"]

        # Create the header
        if release_id:
            # Get the release information
            release = await _get_release_by_id(spira_client, product_id, release_id)
            release_version_number = release["VersionNumber"]
            formatted_specification.append(
                f"# Specification for {product_name} [PR:{product_id}], Release {release_version_number} [RL:{release_id}]"
            )
        else:
            formatted_specification.append(f"# Specification for {product_name} [PR:{product_id}]")
        formatted_specification.append("\n")

        # Populate the product overview
        if product["Description"]:
            formatted_specification.append("## Product Overview")
            formatted_specification.append(product["Description"])
            formatted_specification.append("\n")

        # Create the sub-header for the Requirements.md section
        formatted_specification.append("\n")
        formatted_specification.append("## Requirements Document")

        # Get the list of requirements in the product, or just the release
        requirements = await _get_specification_requirements(spira_client, product_id, release_id)

        if requirements:
            # Format the requirements into human readable data
            for requirement in requirements:
                requirement_id = requirement["RequirementId"]
                formatted_specification.append(
                    f"### Requirement RQ:{requirement_id}: {requirement['Name']}\n"
                )
                if requirement["Description"]:
                    description = (
                        f"**{requirement['RequirementTypeName']}:** {requirement['Description']}\n"
                    )
                    formatted_specification.append(description)
                formatted_specification.append("\n")

                # See if we have any scenarios for this requirement
                await _add_requirement_scenarios(
                    spira_client, product_id, requirement_id, formatted_specification
                )

                # See if we have any defined test cases for this requirement
                # We disabled this and instead now return the test cases in a separate call
                # as it was taking too long and exceeding the MCP Server timeout in Kiro
                # _add_requirement_test_cases(spira_client, product_id, requirement_id, formatted_specification)

        return "\n".join(formatted_specification)

    except Exception as e:
        return f"There was a problem using this tool: {e}"


async def _get_specification_design_impl(
    spira_client, product_id: int, release_id: int | None
) -> str:
    """
    Implementation of retrieving the design markdown specification for the specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45.
        release_id: The numeric ID of the release. If the ID is RL:12, just use 12.
                    If no release is specified, then the specification for the entire
                    project is returned

    Returns:
        Formatted string containing the product design specification
    """
    try:
        formatted_specification = []

        # Get the product information
        logger.info("Getting the product overview")
        product = await _get_product_by_id(spira_client, product_id)
        product_name = product["Name"]

        # Create the header
        if release_id:
            # Get the release information
            release = await _get_release_by_id(spira_client, product_id, release_id)
            release_version_number = release["VersionNumber"]
            formatted_specification.append(
                f"# Specification for {product_name} [PR:{product_id}], Release {release_version_number} [RL:{release_id}]"
            )
        else:
            formatted_specification.append(f"# Specification for {product_name} [PR:{product_id}]")
        formatted_specification.append("\n")

        # Populate the product overview
        if product["Description"]:
            formatted_specification.append("## Product Overview")
            formatted_specification.append(product["Description"])
            formatted_specification.append("\n")

        # Create the sub-header for the Design.md section
        formatted_specification.append("\n")
        formatted_specification.append("## Design Document")

        # Get the list of risks in the product, or just the release
        risks = await _get_specification_risks(spira_client, product_id, release_id)

        if risks:
            # Format the risks into human readable data
            for risk in risks:
                risk_id = risk["RiskId"]
                formatted_specification.append(f"### Risk RK:{risk_id}: {risk['Name']}\n")
                if risk["Description"]:
                    description = f"**{risk['RiskTypeName']}:** {risk['Description']}\n"
                    formatted_specification.append(description)
                formatted_specification.append("\n")

                # See if we have any mitigations for this risk
                await _add_risk_mitigations(
                    spira_client, product_id, risk_id, formatted_specification
                )

        return "\n".join(formatted_specification)

    except Exception as e:
        return f"There was a problem using this tool: {e}"


async def _get_specification_tasks_impl(
    spira_client, product_id: int, release_id: int | None
) -> str:
    """
    Implementation of retrieving the tasks markdown specification for the specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45.
        release_id: The numeric ID of the release. If the ID is RL:12, just use 12.
                    If no release is specified, then the specification for the entire
                    project is returned

    Returns:
        Formatted string containing the product tasks specification
    """
    try:
        formatted_specification = []

        # Get the product information
        logger.info("Getting the product overview")
        product = await _get_product_by_id(spira_client, product_id)
        product_name = product["Name"]

        # Create the header
        if release_id:
            # Get the release information
            release = await _get_release_by_id(spira_client, product_id, release_id)
            release_version_number = release["VersionNumber"]
            formatted_specification.append(
                f"# Specification for {product_name} [PR:{product_id}], Release {release_version_number} [RL:{release_id}]"
            )
        else:
            formatted_specification.append(f"# Specification for {product_name} [PR:{product_id}]")
        formatted_specification.append("\n")

        # Populate the product overview
        if product["Description"]:
            formatted_specification.append("## Product Overview")
            formatted_specification.append(product["Description"])
            formatted_specification.append("\n")

        # Get the list of requirements in the product, or just the release
        requirements = await _get_specification_requirements(spira_client, product_id, release_id)

        # Create the sub-header for the Tasks.md section
        formatted_specification.append("\n")
        formatted_specification.append("## Implementation Plan")

        # Loop through the requirements and add the tasks
        if requirements:
            # Format the requirements into human readable data
            for requirement in requirements:
                requirement_id = requirement["RequirementId"]
                formatted_specification.append(
                    f"### Requirement RQ:{requirement_id}: {requirement['Name']}\n"
                )

                # See if we have any defined tasks for this requirement
                await _add_requirement_tasks(
                    spira_client, product_id, requirement_id, formatted_specification
                )

        return "\n".join(formatted_specification)

    except Exception as e:
        return f"There was a problem using this tool: {e}"


async def _get_specification_test_cases_impl(
    spira_client, product_id: int, release_id: int | None
) -> str:
    """
    Implementation of retrieving the test cases markdown specification for the specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45.
        release_id: The numeric ID of the release. If the ID is RL:12, just use 12.
                    If no release is specified, then the specification for the entire
                    project is returned

    Returns:
        Formatted string containing the product test cases specification
    """
    try:
        formatted_specification = []

        # Get the product information
        logger.info("Getting the product overview")
        product = await _get_product_by_id(spira_client, product_id)
        product_name = product["Name"]

        # Create the header
        if release_id:
            # Get the release information
            release = await _get_release_by_id(spira_client, product_id, release_id)
            release_version_number = release["VersionNumber"]
            formatted_specification.append(
                f"# Specification for {product_name} [PR:{product_id}], Release {release_version_number} [RL:{release_id}]"
            )
        else:
            formatted_specification.append(f"# Specification for {product_name} [PR:{product_id}]")
        formatted_specification.append("\n")

        # Populate the product overview
        if product["Description"]:
            formatted_specification.append("## Product Overview")
            formatted_specification.append(product["Description"])
            formatted_specification.append("\n")

        # Create the sub-header for the test-cases.md section
        formatted_specification.append("\n")
        formatted_specification.append("## Test Cases")

        # Get the list of test cases in the product, or just the release
        test_cases = []
        starting_row = 1
        number_of_rows = 250
        more_results = True
        sort_field = "TestCaseId"
        sort_direction = "ASC"
        while more_results:
            test_cases_url = f"projects/{product_id}/test-cases?starting_row={starting_row}&number_of_rows={number_of_rows}&sort_field={sort_field}&sort_direction={sort_direction}"
            if release_id is not None:
                test_cases_url += f"&release_id={release_id}"
            results = await spira_client.make_spira_api_get_request(test_cases_url)
            if not results:
                more_results = False
            else:
                starting_row += number_of_rows
            test_cases.extend(results)

        if test_cases:
            # Format the test cases into human readable data
            for test_case_item in test_cases:
                # Get the full details of the test case (with steps)
                test_case_id = test_case_item["TestCaseId"]
                test_case_url = f"projects/{product_id}/test-cases/{test_case_id}"
                test_case = await spira_client.make_spira_api_get_request(test_case_url)

                if test_case:
                    formatted_specification.append(
                        f"##### Test Case TC:{test_case_id}: {test_case['Name']}\n"
                    )
                    if test_case["Description"]:
                        description = (
                            f"**{test_case['TestCaseTypeName']}:** {test_case['Description']}\n"
                        )
                        formatted_specification.append(description)
                    formatted_specification.append("\n")

                    # Get the test case steps
                    test_steps_url = f"projects/{product_id}/test-cases/{test_case_id}/test-steps"
                    test_steps = await spira_client.make_spira_api_get_request(test_steps_url)

                    # Format the test steps as a table
                    if test_steps:
                        formatted_specification.append("##### Steps\n\n")
                        formatted_specification.append("<table>")
                        formatted_specification.append(
                            "<tr><th>Step #</th><th>Description</th><th>Expected Result</th><th>Sample Data</th></tr>"
                        )
                        for test_step in test_steps:
                            position = test_step["Position"]
                            description = test_step["Description"]
                            expected_result = test_step["ExpectedResult"]
                            sample_data = test_step["SampleData"]
                            formatted_specification.append("<tr>")
                            formatted_specification.append(f"<td>{position}.</td>")
                            formatted_specification.append(f"<td>{description}.</td>")
                            formatted_specification.append(f"<td>{expected_result}.</td>")
                            formatted_specification.append(f"<td>{sample_data}.</td>")
                            formatted_specification.append("</tr>")
                        formatted_specification.append("</table>")

        return "\n".join(formatted_specification)

    except Exception as e:
        return f"There was a problem using this tool: {e}"


def register_tools(mcp) -> None:
    """
    Register product specification tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool(
        name="spec_get_requirements",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    )
    async def get_specification_requirements(
        release_id: int | None, product_id: int | None = None
    ) -> str:
        """
        Retrieves the requirements specification file for the requested Spira product.

        Use this for downloading the requirements part of a product specification
        for agentic development environments such as Amazon Kiro.

        Args:
            release_id: The numeric ID of the release (e.g., 12 for RL:12) or None for entire project
            product_id: The numeric ID of the product (e.g., 45 for PR:45). If omitted, uses SPIRA_PROJECT_ID from environment.

        Returns:
            Formatted markdown string containing the specification.
            Includes: product overview, requirements with descriptions, acceptance criteria.

        Error Responses:
            Returns structured JSON with error, error_code, details, and suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            # Get requirements for entire product
            spec = get_specification_requirements(product_id=55, release_id=None)

            # Get requirements for specific release
            spec = get_specification_requirements(product_id=55, release_id=12)
        """
        try:
            # Resolve product_id from explicit arg or SPIRA_PROJECT_ID env var
            resolved_id = resolve_product_id(product_id)
            if resolved_id is None:
                return format_error_response(
                    error="product_id is required",
                    error_code=ErrorCodes.INVALID_PARAMETER,
                    details={"parameter": "product_id"},
                    suggestion="Pass product_id explicitly or set SPIRA_PROJECT_ID in your environment",
                )
            product_id = resolved_id

            # Validate product_id
            validator = ParameterValidator()
            error = validator.validate_positive_integer(product_id, "product_id")
            if error:
                return format_error_response(
                    error=error["error"],
                    error_code=error["error_code"],
                    details=error["details"],
                    suggestion=error["suggestion"],
                )

            # Validate release_id if provided
            if release_id is not None:
                error = validator.validate_positive_integer(release_id, "release_id")
                if error:
                    return format_error_response(
                        error=error["error"],
                        error_code=error["error_code"],
                        details=error["details"],
                        suggestion=error["suggestion"],
                    )

            spira_client = get_spira_client()
            return await _get_specification_requirements_impl(spira_client, product_id, release_id)
        except Exception as e:
            return format_error_response(
                error=f"Failed to retrieve requirements specification: {str(e)}",
                error_code="API_ERROR",
                suggestion="Check API connectivity and authentication",
            )

    @mcp.tool(
        name="spec_get_design",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    )
    async def get_specification_design(
        release_id: int | None, product_id: int | None = None
    ) -> str:
        """
        Retrieves the design specification file for the requested Spira product.

        Use this for downloading the design part of a product specification
        for agentic development environments such as Amazon Kiro.

        Args:
            release_id: The numeric ID of the release (e.g., 12 for RL:12) or None for entire project
            product_id: The numeric ID of the product (e.g., 45 for PR:45). If omitted, uses SPIRA_PROJECT_ID from environment.

        Returns:
            Formatted markdown string containing the specification.
            Includes: product overview, risks with descriptions, mitigations.

        Error Responses:
            Returns structured JSON with error, error_code, details, and suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            # Get design for entire product
            spec = get_specification_design(product_id=55, release_id=None)

            # Get design for specific release
            spec = get_specification_design(product_id=55, release_id=12)
        """
        try:
            # Resolve product_id from explicit arg or SPIRA_PROJECT_ID env var
            resolved_id = resolve_product_id(product_id)
            if resolved_id is None:
                return format_error_response(
                    error="product_id is required",
                    error_code=ErrorCodes.INVALID_PARAMETER,
                    details={"parameter": "product_id"},
                    suggestion="Pass product_id explicitly or set SPIRA_PROJECT_ID in your environment",
                )
            product_id = resolved_id

            # Validate product_id
            validator = ParameterValidator()
            error = validator.validate_positive_integer(product_id, "product_id")
            if error:
                return format_error_response(
                    error=error["error"],
                    error_code=error["error_code"],
                    details=error["details"],
                    suggestion=error["suggestion"],
                )

            # Validate release_id if provided
            if release_id is not None:
                error = validator.validate_positive_integer(release_id, "release_id")
                if error:
                    return format_error_response(
                        error=error["error"],
                        error_code=error["error_code"],
                        details=error["details"],
                        suggestion=error["suggestion"],
                    )

            spira_client = get_spira_client()
            return await _get_specification_design_impl(spira_client, product_id, release_id)
        except Exception as e:
            return format_error_response(
                error=f"Failed to retrieve design specification: {str(e)}",
                error_code="API_ERROR",
                suggestion="Check API connectivity and authentication",
            )

    @mcp.tool(
        name="spec_get_tasks",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    )
    async def get_specification_tasks(release_id: int | None, product_id: int | None = None) -> str:
        """
        Retrieves the tasks specification file for the requested Spira product.

        Use this for downloading the tasks part of a product specification
        for agentic development environments such as Amazon Kiro.

        Args:
            release_id: The numeric ID of the release (e.g., 12 for RL:12) or None for entire project
            product_id: The numeric ID of the product (e.g., 45 for PR:45). If omitted, uses SPIRA_PROJECT_ID from environment.

        Returns:
            Formatted markdown string containing the specification.
            Includes: product overview, implementation plan with tasks grouped by requirement.

        Error Responses:
            Returns structured JSON with error, error_code, details, and suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            # Get tasks for entire product
            spec = get_specification_tasks(product_id=55, release_id=None)

            # Get tasks for specific release
            spec = get_specification_tasks(product_id=55, release_id=12)
        """
        try:
            # Resolve product_id from explicit arg or SPIRA_PROJECT_ID env var
            resolved_id = resolve_product_id(product_id)
            if resolved_id is None:
                return format_error_response(
                    error="product_id is required",
                    error_code=ErrorCodes.INVALID_PARAMETER,
                    details={"parameter": "product_id"},
                    suggestion="Pass product_id explicitly or set SPIRA_PROJECT_ID in your environment",
                )
            product_id = resolved_id

            # Validate product_id
            validator = ParameterValidator()
            error = validator.validate_positive_integer(product_id, "product_id")
            if error:
                return format_error_response(
                    error=error["error"],
                    error_code=error["error_code"],
                    details=error["details"],
                    suggestion=error["suggestion"],
                )

            # Validate release_id if provided
            if release_id is not None:
                error = validator.validate_positive_integer(release_id, "release_id")
                if error:
                    return format_error_response(
                        error=error["error"],
                        error_code=error["error_code"],
                        details=error["details"],
                        suggestion=error["suggestion"],
                    )

            spira_client = get_spira_client()
            return await _get_specification_tasks_impl(spira_client, product_id, release_id)
        except Exception as e:
            return format_error_response(
                error=f"Failed to retrieve tasks specification: {str(e)}",
                error_code="API_ERROR",
                suggestion="Check API connectivity and authentication",
            )

    @mcp.tool(
        name="spec_get_test_cases",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    )
    async def get_specification_test_cases(
        release_id: int | None, product_id: int | None = None
    ) -> str:
        """
        Retrieves the test cases specification file for the requested Spira product.

        Use this for downloading the test cases part of a product specification
        for agentic development environments such as Amazon Kiro.

        Args:
            release_id: The numeric ID of the release (e.g., 12 for RL:12) or None for entire project
            product_id: The numeric ID of the product (e.g., 45 for PR:45). If omitted, uses SPIRA_PROJECT_ID from environment.

        Returns:
            Formatted markdown string containing the specification.
            Includes: product overview, test cases with steps, expected results, sample data.

        Error Responses:
            Returns structured JSON with error, error_code, details, and suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            # Get test cases for entire product
            spec = get_specification_test_cases(product_id=55, release_id=None)

            # Get test cases for specific release
            spec = get_specification_test_cases(product_id=55, release_id=12)
        """
        try:
            # Resolve product_id from explicit arg or SPIRA_PROJECT_ID env var
            resolved_id = resolve_product_id(product_id)
            if resolved_id is None:
                return format_error_response(
                    error="product_id is required",
                    error_code=ErrorCodes.INVALID_PARAMETER,
                    details={"parameter": "product_id"},
                    suggestion="Pass product_id explicitly or set SPIRA_PROJECT_ID in your environment",
                )
            product_id = resolved_id

            # Validate product_id
            validator = ParameterValidator()
            error = validator.validate_positive_integer(product_id, "product_id")
            if error:
                return format_error_response(
                    error=error["error"],
                    error_code=error["error_code"],
                    details=error["details"],
                    suggestion=error["suggestion"],
                )

            # Validate release_id if provided
            if release_id is not None:
                error = validator.validate_positive_integer(release_id, "release_id")
                if error:
                    return format_error_response(
                        error=error["error"],
                        error_code=error["error_code"],
                        details=error["details"],
                        suggestion=error["suggestion"],
                    )

            spira_client = get_spira_client()
            return await _get_specification_test_cases_impl(spira_client, product_id, release_id)
        except Exception as e:
            return format_error_response(
                error=f"Failed to retrieve test cases specification: {str(e)}",
                error_code="API_ERROR",
                suggestion="Check API connectivity and authentication",
            )
