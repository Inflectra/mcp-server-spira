"""
Provides operations for working with the Spira product template workspace

This module provides MCP tools for retrieving and updating product templates (also known as projects).
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)
from mcp_server_spira.features.formatting import format_product_template


def _get_product_templates_impl(spira_client) -> str:
    """
    Implementation of retrieving the list of Spira product templates
    the current user has access to

    Args:
        spira_client: The Inflectra Spira API client instance

    Returns:
        JSON string containing the list of available product templates
    """
    try:
        # Get the list of available product templates for the current user
        product_templates_url = "project-templates"
        product_templates = spira_client.make_spira_api_get_request(product_templates_url)

        if not product_templates:
            # Return empty data array if no product templates
            return format_success_response(data=[])

        # Return all product templates as JSON (no truncation)
        return format_success_response(data=product_templates)
    except Exception as e:
        return format_error_response(
            error="Failed to retrieve product templates",
            error_code=ErrorCodes.API_ERROR,
            details={"message": str(e)},
            suggestion="Check API connectivity and authentication",
        )


def _get_product_template_impl(spira_client, template_id: int) -> str:
    """
    Implementation of retrieving a single Spira product template

    Args:
        spira_client: The Inflectra Spira API client instance
        template_id: The numeric ID of the product template. If the ID is PT:45, just use 45.

    Returns:
        Formatted string containing the details of the requested product template
    """
    try:
        # Get the product template by its ID
        product_templates_url = "project-templates/" + str(template_id)
        product_template = spira_client.make_spira_api_get_request(product_templates_url)

        if not product_template:
            return "Unable to fetch product template details for ID " + str(template_id) + "."

        # Format the product template into human readable data
        product_template_info = format_product_template(product_template)
        return product_template_info
    except Exception as e:
        return f"There was a problem using this tool: {e}"


def register_tools(mcp) -> None:
    """
    Register my work tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_product_templates() -> str:
        """
        Retrieves a list of the product templates that the current
        user has access to

        Use this tool when you need to:
        - View the list of product templates that a user has access to
        - Get information about multiple product templates at once
        - Access the full description and selected fields of product
            templates

        Returns:
            JSON string with structure:
            {
                "data": [
                    {
                        "ProjectTemplateId": 1,
                        "Name": "Scrum Template",
                        "Description": "Agile Scrum project template",
                        "IsActive": true,
                        "WorkspaceTypeId": 1,
                        "Guid": "abc-123-def-456",
                        "LastUpdatedDate": "2024-01-15T10:00:00Z",
                        "ArtifactTypeId": 1,
                        "ConcurrencyGuid": "xyz-789",
                        "CustomProperties": []
                    }
                ]
            }

        Key Fields:
            - ProjectTemplateId: Unique identifier for the product
                template (use this when creating products)
            - Name: Display name of the product template
            - Description: Detailed description of the product template
            - IsActive: Whether the template is currently active
                (boolean)
            - WorkspaceTypeId: Type of workspace (integer)
            - Guid: Unique global identifier (string)
            - LastUpdatedDate: Last modification timestamp
                (ISO 8601 datetime, nullable)
            - ArtifactTypeId: Type of artifact (integer)
            - ConcurrencyGuid: Used for optimistic concurrency control
                (string)
            - CustomProperties: Array of custom fields for this template

        When to Use:
            - Discovering available product templates
            - Listing templates for product creation
            - Validating template IDs before creating products
            - Getting template metadata for configuration

        Related Tools:
            - get_product_template: Get detailed information for a
                single template
            - get_products: Get list of products
            - get_programs: Get program-level groupings

        Error Responses:
            {
                "error": "Failed to retrieve product templates",
                "error_code": "API_ERROR",
                "details": {
                    "message": "Connection timeout"
                },
                "suggestion": "Check API connectivity and authentication"
            }

        Example Usage:
            # Get all product templates
            templates_json = get_product_templates()
            templates = json.loads(templates_json)

            # Filter active templates
            active_templates = [t for t in templates["data"]
                                if t["IsActive"]]

            # Find template by name
            scrum_template = next((t for t in templates["data"]
                                   if "Scrum" in t["Name"]), None)
        """
        try:
            spira_client = get_spira_client()
            return _get_product_templates_impl(spira_client)
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve product templates",
                error_code=ErrorCodes.API_ERROR,
                details={"message": str(e)},
                suggestion="Check API connectivity and authentication",
            )

    @mcp.tool()
    def get_product_template(template_id: int) -> str:
        """
        Retrieves a product template by its unique numeric ID (remove any PT prefixes)

        Use this tool when you need to:
        - View the details of a product template when you know its ProjectTemplateId
        - Get information about a single product template
        - Access the full description and selected fields of the product template

        Args:
            template_id: The numeric ID of the product template. If the ID is PT:45, just use 45.

        Returns:
            Formatted string containing comprehensive information for the
            requested product template, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_product_template_impl(spira_client, template_id)
        except Exception as e:
            return f"Error: {str(e)}"
