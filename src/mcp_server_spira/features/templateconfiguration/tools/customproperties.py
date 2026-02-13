"""
Provides operations for getting a list of custom properties defined in the current product template

This module provides MCP tools for retrieving artifact types, and their associated custom properties
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _get_custom_properties_impl(spira_client, template_id: int) -> str:
    """
    Implementation of retrieving the list of artifact types and custom properties in the product template

    Args:
        spira_client: The Inflectra Spira API client instance
        template_id: The numeric ID of the product template. If the ID is PT:45, just use 45.

    Returns:
        JSON string containing the list of artifact types and associated custom properties
    """
    try:
        artifact_custom_properties = []

        # Define artifact types to query
        artifact_types = [
            "Requirement",
            "Release",
            "TestCase",
            "Task",
            "Risk",
            "Incident",
            "TestSet",
            "TestStep",
            "TestRun",
            "AutomationHost",
            "Document",
        ]

        # Retrieve custom properties for each artifact type
        for artifact_type_name in artifact_types:
            custom_props = _get_custom_properties_for_artifact_type(
                spira_client, template_id, artifact_type_name
            )

            if custom_props:
                artifact_custom_properties.append(
                    {"ArtifactTypeName": artifact_type_name, "CustomProperties": custom_props}
                )

        return format_success_response(data=artifact_custom_properties)

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve custom properties",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e), "template_id": template_id},
            suggestion="Check API connectivity and verify the template_id is valid",
        )


def _get_custom_properties_for_artifact_type(
    spira_client, template_id: int, artifact_type_name: str
) -> list:
    """
    Retrieves custom properties for a specific artifact type.

    Args:
        spira_client: The Inflectra Spira API client instance
        template_id: The numeric ID of the product template
        artifact_type_name: The name of the artifact type (e.g., "Requirement", "TestCase")

    Returns:
        List of custom property dictionaries, or empty list if none found
    """
    try:
        custom_props_url = (
            "project-templates/" + str(template_id) + "/custom-properties/" + artifact_type_name
        )
        custom_props = spira_client.make_spira_api_get_request(custom_props_url)

        return custom_props if custom_props else []

    except Exception:
        return []


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
            JSON string with structure:
            {
                "data": [
                    {
                        "ArtifactTypeName": "Requirement",
                        "CustomProperties": [
                            {
                                "CustomPropertyId": 1,
                                "PropertyNumber": 1,
                                "Name": "Business Unit",
                                "CustomPropertyTypeId": 1,
                                "CustomPropertyTypeName": "Text",
                                "IsDeleted": false,
                                "IsRequired": false,
                                "IsRichText": false,
                                "Options": null
                            }
                        ]
                    },
                    {
                        "ArtifactTypeName": "TestCase",
                        "CustomProperties": [
                            {
                                "CustomPropertyId": 5,
                                "PropertyNumber": 2,
                                "Name": "Test Environment",
                                "CustomPropertyTypeId": 2,
                                "CustomPropertyTypeName": "List",
                                "IsDeleted": false,
                                "IsRequired": true,
                                "IsRichText": false,
                                "Options": [
                                    {"CustomPropertyValueId": 1, "Name": "Development"},
                                    {"CustomPropertyValueId": 2, "Name": "Staging"}
                                ]
                            }
                        ]
                    },
                    {
                        "ArtifactTypeName": "Task",
                        "CustomProperties": [...]
                    }
                ]
            }

        Key Fields:
            - ArtifactTypeName: The name of the artifact type (Requirement, Release, TestCase, Task, Risk, Incident, TestSet, TestStep, TestRun, AutomationHost, Document)
            - CustomProperties: Array of custom properties for this artifact type
            - CustomPropertyId: Unique identifier for the custom property
            - PropertyNumber: Display order number for the property
            - Name: Display name of the custom property
            - CustomPropertyTypeId/CustomPropertyTypeName: Type of the property (Text, List, Date, User, etc.)
            - IsDeleted: Whether the property has been deleted (boolean)
            - IsRequired: Whether the property is required when creating artifacts (boolean)
            - IsRichText: Whether the property supports rich text formatting (boolean)
            - Options: Array of valid values for list-type properties (null for other types)

        When to Use:
            - Discovering available custom properties in a template
            - Validating custom property IDs before creating/updating artifacts
            - Understanding which custom properties are required
            - Listing custom properties for user selection in UI
            - Determining valid values for list-type custom properties

        Related Tools:
            - get_artifact_types: Get artifact types and sub-types
            - get_product_template: Get template details

        Error Responses:
            {
                "error": "Invalid template_id parameter",
                "error_code": "INVALID_VALUE",
                "details": {
                    "parameter": "template_id",
                    "value": -1,
                    "expected": ">= 1"
                },
                "suggestion": "template_id must be >= 1"
            }

        Example Usage:
            # Get all custom properties for a template
            props_json = get_custom_properties(template_id=1)
            props = json.loads(props_json)

            # Find required custom properties for requirements
            for artifact in props["data"]:
                if artifact["ArtifactTypeName"] == "Requirement":
                    for prop in artifact["CustomProperties"]:
                        if prop["IsRequired"]:
                            print(f"Required: {prop['Name']} (ID: {prop['CustomPropertyId']})")

            # Find list-type custom properties with their options
            for artifact in props["data"]:
                for prop in artifact["CustomProperties"]:
                    if prop["CustomPropertyTypeName"] == "List" and prop["Options"]:
                        print(f"{prop['Name']} options:")
                        for option in prop["Options"]:
                            print(f"  - {option['Name']} (ID: {option['CustomPropertyValueId']})")
        """
        try:
            # Validate template_id
            validation_error = ParameterValidator.validate_positive_integer(
                template_id, "template_id"
            )
            if validation_error:
                return format_error_response(**validation_error)

            spira_client = get_spira_client()
            return _get_custom_properties_impl(spira_client, template_id)
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve custom properties",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
