"""
Provides operations for getting a list of artifact types and sub-types in the current product template

This module provides MCP tools for retrieving artifact types, and their assoicated sub types
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
    Implementation of retrieving the list of artifact types and sub-types in the product template

    Args:
        spira_client: The Inflectra Spira API client instance
        template_id: The numeric ID of the product template. If the ID is PT:45, just use 45.

    Returns:
        JSON string containing the list of artifact types and sub-types
    """
    try:
        artifact_types = []

        # --- Requirements ---
        types_url = f"project-templates/{template_id}/requirements/types"
        requirement_types = spira_client.make_spira_api_get_request(types_url)

        if requirement_types:
            artifact_types.append({"ArtifactTypeName": "Requirement", "Types": requirement_types})

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
            suggestion="Check API connectivity and verify the template_id is valid",
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
        Retrieves a list of the artifact types and associated sub-types for the current product template

        Use this tool when you need to:
        - View the list of artifact types in the product template
        - For each artifact type (e.g. test case), get the list of sub-types (e.g. test case types)
        - Access the name and ID of each type

        Args:
            template_id: The numeric ID of the product template. If the ID is PT:45, just use 45.

        Returns:
            JSON string with structure:
            {
                "data": [
                    {
                        "ArtifactTypeName": "Requirement",
                        "Types": [
                            {
                                "RequirementTypeId": 1,
                                "Name": "User Story",
                                "WorkflowId": 5,
                                "Active": true,
                                "IsDefault": false
                            }
                        ]
                    },
                    {
                        "ArtifactTypeName": "Test Case",
                        "Types": [
                            {
                                "TestCaseTypeId": 1,
                                "Name": "Functional",
                                "WorkflowId": 3,
                                "Active": true,
                                "IsDefault": true
                            }
                        ]
                    },
                    {
                        "ArtifactTypeName": "Task",
                        "Types": [
                            {
                                "TaskTypeId": 1,
                                "Name": "Development",
                                "WorkflowId": 2,
                                "Active": true,
                                "IsDefault": false
                            }
                        ]
                    },
                    {
                        "ArtifactTypeName": "Risk",
                        "Types": [...]
                    },
                    {
                        "ArtifactTypeName": "Incident",
                        "Types": [
                            {
                                "IncidentTypeId": 1,
                                "Name": "Bug",
                                "WorkflowId": 4,
                                "Active": true,
                                "IsDefault": true
                            }
                        ]
                    },
                    {
                        "ArtifactTypeName": "Document",
                        "Types": [
                            {
                                "DocumentTypeId": 1,
                                "Name": "Specification",
                                "Active": true,
                                "IsDefault": false
                            }
                        ]
                    }
                ]
            }

        Key Fields:
            - ArtifactTypeName: The name of the artifact type (Requirement, Test Case, Task, Risk, Incident, Document)
            - Types: Array of sub-types for this artifact type
            - RequirementTypeId/TestCaseTypeId/TaskTypeId/etc: Unique identifier for the type
            - Name: Display name of the type
            - WorkflowId: ID of the workflow associated with this type (null if none)
            - Active: Whether the type is currently active (boolean)
            - IsDefault: Whether this is the default type for new artifacts (boolean)

        When to Use:
            - Discovering available artifact types in a template
            - Validating type IDs before creating artifacts
            - Understanding workflow associations for artifact types
            - Listing types for user selection in UI

        Related Tools:
            - get_custom_properties: Get custom fields for artifact types
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
            # Get all artifact types for a template
            types_json = get_artifact_types(template_id=1)
            types = json.loads(types_json)

            # Find requirement types
            for artifact in types["data"]:
                if artifact["ArtifactTypeName"] == "Requirement":
                    for req_type in artifact["Types"]:
                        print(f"{req_type['Name']} (ID: {req_type['RequirementTypeId']})")
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
