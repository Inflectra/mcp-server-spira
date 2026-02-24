"""
Provides operations for getting a list of artifact types and sub-types
in the current product template

This module provides MCP tools for retrieving artifact types, and their
associated sub types
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.common.validation import ParameterValidator


def _get_artifact_types_impl(spira_client, template_id: int) -> str:
    """
    Implementation of retrieving the list of artifact types and sub-types
    in the product template

    Args:
        spira_client: The Inflectra Spira API client instance
        template_id: The numeric ID of the product template.
            If the ID is PT:45, just use 45.

    Returns:
        JSON string containing the list of artifact types and sub-types
    """
    try:
        artifact_types = []

        # --- Requirements ---
        types_url = f"project-templates/{template_id}/requirements/types"
        requirement_types = spira_client.make_spira_api_get_request(types_url)

        if requirement_types:
            artifact_types.append(
                {
                    "ArtifactTypeName": "Requirement",
                    "Types": requirement_types,
                }
            )

        # --- Test Cases ---
        types_url = f"project-templates/{template_id}/test-cases/types"
        test_case_types = spira_client.make_spira_api_get_request(types_url)

        if test_case_types:
            artifact_types.append({"ArtifactTypeName": "Test Case", "Types": test_case_types})

        # --- Tasks ---
        types_url = f"project-templates/{template_id}/tasks/types"
        task_types = spira_client.make_spira_api_get_request(types_url)

        if task_types:
            artifact_types.append({"ArtifactTypeName": "Task", "Types": task_types})

        # --- Risks ---
        types_url = f"project-templates/{template_id}/risks/types"
        risk_types = spira_client.make_spira_api_get_request(types_url)

        if risk_types:
            artifact_types.append({"ArtifactTypeName": "Risk", "Types": risk_types})

        # --- Incidents ---
        types_url = f"project-templates/{template_id}/incidents/types"
        incident_types = spira_client.make_spira_api_get_request(types_url)

        if incident_types:
            artifact_types.append({"ArtifactTypeName": "Incident", "Types": incident_types})

        # --- Documents ---
        types_url = f"project-templates/{template_id}/document-types?active_only=true"
        document_types = spira_client.make_spira_api_get_request(types_url)

        if document_types:
            artifact_types.append({"ArtifactTypeName": "Document", "Types": document_types})

        return format_success_response(data=artifact_types)

    except Exception as e:
        return format_error_response(
            error="Failed to retrieve artifact types",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e), "template_id": template_id},
            suggestion=("Check API connectivity and verify the template_id is valid"),
        )


def register_tools(mcp) -> None:
    """
    Register artifact type tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_artifact_types(template_id: int) -> str:
        """
        Retrieves artifact types and sub-types for the product template

        Use this tool to view artifact types in the product template,
        get sub-types for each artifact type, or validate type IDs
        before creating artifacts.

        Args:
            template_id: The numeric ID of the product template.
                If the ID is PT:45, just use 45.

        Returns:
            JSON string with structure: {"data": [artifact type objects]}
            Each object contains ArtifactTypeName and Types array.

        Key Fields:
            - ArtifactTypeName: Name (Requirement, Test Case, Task, etc.)
            - Types: Array of sub-types for this artifact type
            - RequirementTypeId/TestCaseTypeId/etc: Unique type ID
            - Name: Display name of the type
            - WorkflowId: Workflow ID (null if none)
            - Active: Whether the type is currently active
            - IsDefault: Whether this is the default type

        Related Tools:
            - get_custom_properties: Get custom fields for artifact types
            - get_product_template: Get template details

        Error Responses:
            Returns structured JSON with error, error_code, details,
            and suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            types_json = get_artifact_types(template_id=1)
            types = json.loads(types_json)
        """
        try:
            # Validate template_id
            validation_error = ParameterValidator.validate_positive_integer(
                template_id, "template_id"
            )
            if validation_error:
                return format_error_response(**validation_error)

            spira_client = get_spira_client()
            return _get_artifact_types_impl(spira_client, template_id)
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve artifact types",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
