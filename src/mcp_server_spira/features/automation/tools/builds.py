"""
Provides operations for recording the results of CI/CD builds into Spira

This module provides MCP tools for recording the results of continuous integration / continuous deployment
pipeline builds against a matching release in Spira 
"""

import datetime

from mcp_server_spira.features.common import get_spira_client

def _create_build_url_impl(spira_client, product_id: int, release_id: int, build_status_id: int, name: str, description: str, commits: list[str]) -> str:
    """
    Creates a new CI/CD pipeline build entry in Spira

    Args:
        spira_client: The Inflectra Spira API client instance
        product_id: The numeric ID of the product. If the ID is PG:45, just use 45.
        release_id: The ID of the release/sprint/phase in Spira that the build is for, without the RL prefix (e.g. RL:12 would be 12)
        build_status_id: The status of the build (1=Failed, 2=Passed)
        name: The name of the build (usually containing the project name and the date/time of the build)
        description: The detailed description of the build (optional), what was included and why
        commits: An optional array/list of the Git hashes of the commits included in the build
                
    Returns:
        The ID of the new build that was created (with 'BL' prefix)
    """
    try:
        # Populate the revisions object from the commits
        revisions = []
        if commits:
            for commit in commits:
                revision = {
                    'RevisionKey': commit
                }
                revisions.append(revision)

        # The body we are sending
        body = {
            # 1=Failed, 2=Passed
            'ProjectId': product_id,
            'BuildStatusId': build_status_id,
            'ReleaseId': release_id,
            'Name': name,
            'Description': description,
            'Revisions': revisions            
        }

        # Record the test run using the API method
        create_build_url = "projects/" + str(product_id) + "/releases/" + str(release_id) + "/builds "
        build = spira_client.make_spira_api_post_request(create_build_url, body)

        if not build:
            return "The build was not recorded successfully."

        # Extract the new build ID
        build_id = build['BuildId']

        return "BL:" + str(build_id)
    except Exception as e:
        return f"There was a problem using this tool: {e}"
    
def register_tools(mcp) -> None:
    """
    Register tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def create_build(product_id: int, release_id: int, build_status_id: int, name: str, description: str, commits: list[str]) -> str:
        """
        Creates a new CI/CD pipeline build entry in Spira
        
        Use this tool when you need to:
        - Push the results of an automated software build into Spira
                    
        Args:
            product_id: The numeric ID of the product. If the ID is PG:45, just use 45.
            release_id: The ID of the release/sprint/phase in Spira that the build is for, without the RL prefix (e.g. RL:12 would be 12)
            build_status_id: The status of the build (1=Failed, 2=Passed)
            name: The name of the build (usually containing the project name and the date/time of the build)
            description: The detailed description of the build (optional), what was included and why
            commits: An optional array/list of the Git hashes of the commits included in the build
                
        Returns:
            The ID of the new build that was created (with 'BL' prefix)
        """
        try:
            spira_client = get_spira_client()
            return _create_build_url_impl(spira_client, product_id, release_id, build_status_id, name, description, commits)
        except Exception as e:
            return f"Error: {str(e)}"
        