"""Generic artifact formatting tool for converting JSON to markdown."""

import json
from typing import Literal

from mcp_server_spira.features.formatting.common import (
    format_incident,
    format_requirement,
    format_task,
    format_test_case,
    format_test_set,
)


def register_tools(mcp) -> None:
    """
    Register formatting tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def format_artifacts_as_markdown(
        artifact_json: str,
        artifact_type: Literal["task", "incident", "requirement", "test_case", "test_set"],
    ) -> str:
        """
        Converts artifact JSON to human-readable markdown format.

        Use for complex workflows where you've filtered or processed artifact data
        and need consistent markdown formatting. For simple display, LLMs can format
        JSON naturally without this tool.

        Args:
            artifact_json: JSON string (full response with pagination or data array)
            artifact_type: One of: "task", "incident", "requirement", "test_case", "test_set"

        Returns:
            Markdown formatted string with artifact information.
            Format varies by artifact type but includes key fields like status, priority, owner.

        When to Use:
            - After filtering or processing JSON data
            - When combining multiple artifact types in one display
            - When consistent formatting is required across operations

        When NOT to Use:
            - Simple display requests (LLM can format naturally)
            - Direct display of unmodified API results

        Related Tools:
            - get_my_tasks: Get tasks assigned to current user
            - get_my_incidents: Get incidents assigned to current user
            - get_my_requirements: Get requirements assigned to current user
            - get_my_testcases: Get test cases assigned to current user
            - get_my_testsets: Get test sets assigned to current user

        Error Responses:
            Returns error string with description.
            Common errors: Invalid JSON, unknown artifact type, missing required fields

        Example Usage:
            tasks_json = get_my_tasks(limit=100)
            tasks = json.loads(tasks_json)
            critical = [t for t in tasks["data"] if t["TaskPriorityName"] == "Critical"]
            display = format_artifacts_as_markdown(json.dumps({"data": critical}), "task")
        """
        try:
            # Parse JSON input
            data = json.loads(artifact_json)

            # Handle both full response with pagination and data array
            artifacts = data.get("data", data) if isinstance(data, dict) else data

            # Handle case where data is not a list
            if not isinstance(artifacts, list):
                return "Error: Expected artifact data to be a list"

            # Handle empty list
            if not artifacts:
                return "No artifacts to display."

            # Format based on artifact type
            formatter_map = {
                "task": format_task,
                "incident": format_incident,
                "requirement": format_requirement,
                "test_case": format_test_case,
                "test_set": format_test_set,
            }

            formatter = formatter_map.get(artifact_type)
            if not formatter:
                return f"Error: Unknown artifact type '{artifact_type}'. Valid types: task, incident, requirement, test_case, test_set"

            # Format each artifact
            formatted_artifacts = []
            for artifact in artifacts:
                try:
                    formatted = formatter(artifact)
                    formatted_artifacts.append(formatted)
                except KeyError as e:
                    return f"Error: Missing required field in artifact: {e}"
                except Exception as e:
                    return f"Error formatting artifact: {str(e)}"

            # Join all formatted artifacts with double newline separator
            return "\n\n".join(formatted_artifacts)

        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON input - {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
