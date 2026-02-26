"""
Provides operations for getting a list of custom properties defined
in the current product template

This module provides MCP tools for retrieving artifact types, and their
associated custom properties
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
    Implementation of retrieving the list of artifact types and
    custom properties in the product template

    Args:
        spira_client: The Inflectra Spira API client instance
        template_id: The numeric ID of the product template.
            If the ID is PT:45, just use 45.

    Returns:
        JSON string containing the list of artifact types and
        associated custom properties
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
                    {
                        "ArtifactTypeName": artifact_type_name,
                        "CustomProperties": custom_props,
                    }
                )

        return format_success_response(data=artifact_custom_properties)

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve custom properties",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e), "template_id": template_id},
            suggestion=("Check API connectivity and verify the template_id is valid"),
        )


def _get_custom_properties_for_artifact_type(
    spira_client, template_id: int, artifact_type_name: str
) -> list:
    """
    Retrieves custom properties for a specific artifact type.

    Args:
        spira_client: The Inflectra Spira API client instance
        template_id: The numeric ID of the product template
        artifact_type_name: The name of the artifact type
            (e.g., "Requirement", "TestCase")

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

    @mcp.tool(
        name="template_get_custom_properties",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    )
    def get_custom_properties(template_id: int) -> str:
        """
        Retrieves artifact types and custom properties for the template

        Use this tool to discover available custom properties in a template,
        validate custom property IDs before creating/updating artifacts,
        or determine valid values for list-type custom properties.

        Args:
            template_id: The numeric ID of the product template.
                If the ID is PT:45, just use 45.

        Returns:
            JSON string with structure: {"data": [custom property objects]}
            Each object contains ArtifactTypeName and CustomProperties array.

        Key Fields:
            - ArtifactTypeName: Name (Requirement, Release, TestCase, etc.)
            - CustomProperties: Array of custom properties
            - CustomPropertyId: Unique identifier for the custom property
            - PropertyNumber: Display order number for the property
            - Name: Display name of the custom property
            - CustomPropertyTypeId/CustomPropertyTypeName: Property type
            - IsRequired: Whether required when creating artifacts
            - Options: Valid values for list-type properties (null for other)

            Additional fields available: IsDeleted, IsRichText

        Related Tools:
            - get_artifact_types: Get artifact types and sub-types
            - get_product_template: Get template details

        Error Responses:
            Returns structured JSON with error, error_code, details,
            and suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            props_json = get_custom_properties(template_id=1)
            props = json.loads(props_json)
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
