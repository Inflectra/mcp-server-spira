"""
Provides operations for getting a list of custom properties defined in the current product template

This module provides MCP tools for retrieving artifact types, and their associated custom properties
"""

from mcp_server_spira.features.formatting import format_milestone
from mcp_server_spira.features.common import get_spira_client

def _get_custom_properties_impl(spira_client, template_id: int) -> str:
    """
    Implementation of retrieving the list of artifact types and custom properties in the product template

    Args:
        spira_client: The Inflectra Spira API client instance
        template_id: The numeric ID of the product template. If the ID is PT:45, just use 45. 
                
    Returns:
        Formatted string containing the list of artifact types and associated custom properties
    """

    formatted_results = "# Artifact Types\n\n"

    # --- Requirements ---
    formatted_results += "## Requirement"
    custom_prop_results = _get_custom_properties_for_artifact_type(spira_client, template_id, 'Requirement')
    formatted_results += custom_prop_results

    # --- Releases ---
    formatted_results += "## Release"
    custom_prop_results = _get_custom_properties_for_artifact_type(spira_client, template_id, 'Release')
    formatted_results += custom_prop_results

    # --- Test Cases ---
    formatted_results += "## Test Case"
    custom_prop_results = _get_custom_properties_for_artifact_type(spira_client, template_id, 'TestCase')
    formatted_results += custom_prop_results

    # --- Tasks ---
    formatted_results += "## Task"
    custom_prop_results = _get_custom_properties_for_artifact_type(spira_client, template_id, 'Task')
    formatted_results += custom_prop_results

    # --- Risks ---
    formatted_results += "## Risk"
    custom_prop_results = _get_custom_properties_for_artifact_type(spira_client, template_id, 'Risk')
    formatted_results += custom_prop_results

    # --- Incidents ---
    formatted_results += "## Incident"
    custom_prop_results = _get_custom_properties_for_artifact_type(spira_client, template_id, 'Incident')
    formatted_results += custom_prop_results

    # --- Test Sets ---
    formatted_results += "## Test Set"
    custom_prop_results = _get_custom_properties_for_artifact_type(spira_client, template_id, 'TestSet')
    formatted_results += custom_prop_results

    # --- Test Steps ---
    formatted_results += "## Test Step"
    custom_prop_results = _get_custom_properties_for_artifact_type(spira_client, template_id, 'TestStep')
    formatted_results += custom_prop_results

    # --- Test Runs ---
    formatted_results += "## Test Run"
    custom_prop_results = _get_custom_properties_for_artifact_type(spira_client, template_id, 'TestRun')
    formatted_results += custom_prop_results

    # --- Automation Hosts ---
    formatted_results += "## Automation Host"
    custom_prop_results = _get_custom_properties_for_artifact_type(spira_client, template_id, 'AutomationHost')
    formatted_results += custom_prop_results

    # --- Documents ---
    formatted_results += "## Documents"
    custom_prop_results = _get_custom_properties_for_artifact_type(spira_client, template_id, 'Document')
    formatted_results += custom_prop_results

    return formatted_results

def _get_custom_properties_for_artifact_type(spira_client, template_id: int, artifact_type_name: str) -> str:

    try:
        custom_props_url = "project-templates/" + str(template_id) + "/custom-properties/" + artifact_type_name
        custom_props = spira_client.make_spira_api_get_request(custom_props_url)

        if not custom_props:
            return ""

        # Format the custom prop into human readable data
        custom_prop_results = []
        for custom_prop in custom_props:
            custom_prop_info = f"""   {custom_prop['PropertyNumber']}. {custom_prop['Name']} (ID={custom_prop['CustomPropertyId']})"""
            custom_prop_results.append(custom_prop_info)

        formatted_results = "\n".join(custom_prop_results)    
        formatted_results += "\n\n------------------------------\n\n"

        return formatted_results
    
    except Exception as e:
        return ""

def register_tools(mcp) -> None:
    """
    Register custom property tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_custom_properties(template_id: int) -> str:
        """
        Retrieves a list of the artifact types and associated custom properties for the current product template
        
        Use this tool when you need to:
        - View the list of artifact types in the product template
        - For each artifact type (e.g. test case), get the list of custom properties
        - Access the name and ID of each type

        Args:
            template_id: The numeric ID of the product template. If the ID is PT:45, just use 45. 
        
        Returns:
            Formatted string containing comprehensive information for the
            requested list of artifact types and corresponding custom properties
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_custom_properties_impl(spira_client, template_id)
        except Exception as e:
            return f"Error: {str(e)}"
        