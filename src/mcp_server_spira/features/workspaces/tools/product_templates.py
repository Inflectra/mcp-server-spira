"""
Provides operations for working with the Spira product template workspace

This module provides MCP tools for retrieving and updating product
templates (also known as projects).
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.common.responses import (
    ErrorCodes,
    format_error_response,
    format_success_response,
)


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
        template_id: The numeric ID of the product template.
            If the ID is PT:45, just use 45.

    Returns:
        JSON string containing the product template details
    """
    try:
        # Get the product template by its ID
        product_templates_url = f"project-templates/{template_id}"
        product_template = spira_client.make_spira_api_get_request(product_templates_url)

        if not product_template:
            return format_error_response(
                error="Product template not found",
                error_code=ErrorCodes.NOT_FOUND,
                details={"template_id": template_id},
                suggestion=("Verify the template ID is correct and you have access to it"),
            )

        # Return product template as JSON
        return format_success_response(data=[product_template])
    except Exception as e:
        return format_error_response(
            error="Failed to retrieve product template",
            error_code=ErrorCodes.API_ERROR,
            details={"template_id": template_id, "message": str(e)},
            suggestion="Check API connectivity and authentication",
        )


def register_tools(mcp) -> None:
    """
    Register my work tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool(
        name="system_get_product_templates",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    )
    def get_product_templates() -> str:
        """
        Retrieves a list of the product templates that the current user
        has access to

        Maps to Spira API: GET /project-templates

        Use this to discover available templates before creating new
        products.

        Returns:
            JSON string with structure: {"data": [product template objects]}
            Full response structure documented in API.

        Related Tools:
            - get_products: Get list of products
            - get_programs: Get program-level groupings

        Error Responses:
            Returns structured JSON with error, error_code, details, and
            suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            templates_json = get_product_templates()
            templates = json.loads(templates_json)
            active_templates = [t for t in templates["data"] if t["IsActive"]]
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

    @mcp.tool(
        name="system_get_product_template",
        annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    )
    def get_product_template(template_id: int) -> str:
        """
        Retrieves a product template by its unique numeric ID
        (remove any PT prefixes)

        Maps to Spira API: GET /project-templates/{template_id}

        Use this tool when you need to:
        - View the details of a product template when you know its
          ProjectTemplateId
        - Get information about a single product template
        - Access the full description and selected fields of the
          product template

        Args:
            template_id: The numeric ID of the product template.
                If the ID is PT:45, just use 45.

        Returns:
            JSON string with structure: {"data": [product template object]}
            Full response structure documented in API.

        Related Tools:
            - get_product_templates: Get list of product templates
            - get_products: Get list of products

        Error Responses:
            Returns structured JSON with error, error_code, details, and
            suggestion.
            Common error codes: INVALID_PARAMETER, API_ERROR, NOT_FOUND

        Example Usage:
            template_json = get_product_template(template_id=1)
            template = json.loads(template_json)
            template_data = template["data"][0]
            print(f"Template: {template_data['Name']}")
        """
        try:
            spira_client = get_spira_client()
            return _get_product_template_impl(spira_client, template_id)
        except Exception as e:
            return format_error_response(
                error="Failed to retrieve product template",
                error_code=ErrorCodes.API_ERROR,
                details={"template_id": template_id, "message": str(e)},
                suggestion="Check API connectivity and authentication",
            )
