"""
Provides operations for working with the Spira product releases

This module provides MCP tools for retrieving and updating product releases
"""

from mcp_server_spira.features.common import get_spira_client
from mcp_server_spira.features.formatting import format_release


def _get_releases_impl(spira_client, product_id: int) -> str:
    """
    Implementation of retrieving the list of releases in the specified product

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45.

    Returns:
        Formatted string containing the list of releases
    """
    try:
        # Get the list of releases in the product
        releases_url = "projects/" + str(product_id) + "/releases?active_only=true"
        releases = spira_client.make_spira_api_get_request(releases_url)

        if not releases:
            return "There are no releases for the product."

        # Format the releases into human readable data
        formatted_results = []
        for release in releases:
            release_info = format_release(release)
            formatted_results.append(release_info)

        return "\n\n".join(formatted_results)

    except Exception as e:
        return f"There was a problem using this tool: {e}"


def _get_release_by_id_impl(spira_client, product_id: int, release_id: int) -> str:
    """
    Implementation of retrieving a single release in the specified product with the specified ID

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PR:45, just use 45.
        release_id: The numeric ID of the release. If the ID is RL:12, just use 12.

    Returns:
        Formatted string containing the details of the release
    """
    try:
        # Get the release in the product
        release_url = f"projects/{product_id}/releases/{release_id}"
        release = spira_client.make_spira_api_get_request(release_url)

        if not release:
            return "There is no release with the specified ID."

        # Format the release into human readable data
        release_info = format_release(release)
        return release_info

    except Exception as e:
        return f"There was a problem using this tool: {e}"


def register_tools(mcp) -> None:
    """
    Register my work tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_releases(product_id: int) -> str:
        """
        Retrieves a list of the releases in the specified product

        Use this tool when you need to:
        - View the list of releases in the specified product
        - Get information about multiple releases at once
        - Access the full description and selected fields of releases

        Args:
            product_id: The numeric ID of the product. If the ID is PR:45, just use 45.

        Returns:
            Formatted string containing comprehensive information for the
            requested list of releases, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_releases_impl(spira_client, product_id)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def get_release_by_id(product_id: int, release_id: int) -> str:
        """
        Retrieves the details of a single release in the specified product

        Use this tool when you need to:
        - View the details of a single release in the specified product
        - Access the full description and selected fields of the release

        Args:
            product_id: The numeric ID of the product. If the ID is PR:45, just use 45.
            release_id: The numeric ID of the release. If the ID is RL:12, just use 12.

        Returns:
            Formatted string containing comprehensive information for the
            requested release, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_release_by_id_impl(spira_client, product_id, release_id)
        except Exception as e:
            return f"Error: {str(e)}"
