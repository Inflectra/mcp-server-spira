"""
Provides operations for getting a list of artifact types and sub-types in the current product template

This module provides MCP tools for retrieving artifact types, and their assoicated sub types
"""

from mcp_server_spira.features.formatting import format_milestone
from mcp_server_spira.features.common import get_spira_client

def _get_artifact_types_impl(spira_client, template_id: int) -> str:
    """
    Implementation of retrieving the list of artifact types and sub-types in the product template

    Args:
        spira_client: The Inflectra Spira API client instance
        template_id: The numeric ID of the product template. If the ID is PT:45, just use 45. 
                
    Returns:
        Formatted string containing the list of artifact types and sub-types
    """

    formatted_results = "# Artifact Types\n\n"


    # --- Requirements ---
    formatted_results += "## Requirement"
        
    types_url = "project-templates/" + str(template_id) + "/requirements/types"
    types = spira_client.make_spira_api_get_request(types_url)

    if not types:
        return "Unable to fetch requirement types for the product template."

    # Format the types into human readable data
    type_results = []
    for type in types:
        milestone_info = f"""   - {type['Name']} (ID={type['RequirementTypeId']})"""
        type_results.append(milestone_info)

    formatted_results += "\n".join(type_results)    
    formatted_results += "\n\n------------------------------\n\n"


    # --- Test Cases ---
    formatted_results += "## Test Case"
        
    types_url = "project-templates/" + str(template_id) + "/test-cases/types"
    types = spira_client.make_spira_api_get_request(types_url)

    if not types:
        return "Unable to fetch test case types for the product template."

    # Format the types into human readable data
    type_results = []
    for type in types:
        milestone_info = f"""   - {type['Name']} (ID={type['TestCaseTypeId']})"""
        type_results.append(milestone_info)

    formatted_results += "\n".join(type_results)    
    formatted_results += "\n\n------------------------------\n\n"

    # --- Tasks ---
    formatted_results += "## Task"
        
    types_url = "project-templates/" + str(template_id) + "/tasks/types"
    types = spira_client.make_spira_api_get_request(types_url)

    if not types:
        return "Unable to fetch task types for the product template."

    # Format the types into human readable data
    type_results = []
    for type in types:
        milestone_info = f"""   - {type['Name']} (ID={type['TaskTypeId']})"""
        type_results.append(milestone_info)

    formatted_results += "\n".join(type_results)
    formatted_results += "\n\n------------------------------\n\n"

    # --- Risks ---
    formatted_results += "## Risk"
        
    types_url = "project-templates/" + str(template_id) + "/risks/types"
    types = spira_client.make_spira_api_get_request(types_url)

    if not types:
        return "Unable to fetch risk types for the product template."

    # Format the types into human readable data
    type_results = []
    for type in types:
        milestone_info = f"""   - {type['Name']} (ID={type['RiskTypeId']})"""
        type_results.append(milestone_info)

    formatted_results += "\n".join(type_results)
    formatted_results += "\n\n------------------------------\n\n"


    # --- Incidents ---
    formatted_results += "## Incident"
        
    types_url = "project-templates/" + str(template_id) + "/incidents/types"
    types = spira_client.make_spira_api_get_request(types_url)

    if not types:
        return "Unable to fetch incident types for the product template."

    # Format the types into human readable data
    type_results = []
    for type in types:
        milestone_info = f"""   - {type['Name']} (ID={type['IncidentTypeId']})"""
        type_results.append(milestone_info)

    formatted_results += "\n".join(type_results)
    formatted_results += "\n\n------------------------------\n\n"


    # --- Documents ---
    formatted_results += "## Document"
        
    types_url = "project-templates/" + str(template_id) + "/document-types"
    types = spira_client.make_spira_api_get_request(types_url)

    if not types:
        return "Unable to fetch document types for the product template."

    # Format the types into human readable data
    type_results = []
    for type in types:
        milestone_info = f"""   - {type['Name']} (ID={type['DocumentTypeId']})"""
        type_results.append(milestone_info)

    formatted_results += "\n".join(type_results)
    formatted_results += "\n\n------------------------------\n\n"

    return formatted_results

def register_tools(mcp) -> None:
    """
    Register artifact type tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_artifact_types(template_id: int) -> str:
        """
        Retrieves a list of the artifact types and associated sub-types for the current product template
        
        Use this tool when you need to:
        - View the list of artifact types in the product template
        - For each artifact type (e.g. test case), get the list of sub-types (e.g. test case types)
        - Access the name and ID of each type

        Args:
            template_id: The numeric ID of the product template. If the ID is PT:45, just use 45. 
        
        Returns:
            Formatted string containing comprehensive information for the
            requested list of artifact types and corresponding sub-types
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_artifact_types_impl(spira_client, template_id)
        except Exception as e:
            return f"Error: {str(e)}"
        