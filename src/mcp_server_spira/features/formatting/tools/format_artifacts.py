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

        This tool is designed for complex workflows where you've filtered, sorted,
        or processed artifact data and need consistent markdown formatting. For simple
        display of unmodified results, modern LLMs can format JSON naturally.

        Args:
            artifact_json: JSON string containing artifact data
                Can be full response with pagination or just data array.
                Can be filtered/modified JSON from processing.
            artifact_type: Type of artifact to format
                One of: "task", "incident", "requirement", "test_case", "test_set"

        Returns:
            Markdown formatted string with artifact information, suitable for
            displaying to users.

        When to Use:
            - After filtering or processing JSON data
            - When you need consistent formatting across multiple operations
            - When combining multiple artifact types in one display
            - When LLM's natural formatting isn't sufficient

        When NOT to Use:
            - Simple "show me my tasks" requests (LLM can format naturally)
            - Direct display of unmodified API results
            - When LLM's natural formatting quality is acceptable

        Example Output (for tasks):
            ## Task [TK:123] - Fix login bug
            Users cannot log in with special characters
            - **Status:** In Progress
            - **Type:** Development
            - **Priority:** Critical
            - **Owner:** John Doe
            - **Effort:** 60/120 min (50% complete)
            - **Due Date:** 2024-01-16
            - **Release:** 1.5.0

            ## Task [TK:124] - Update documentation
            ...

        Example Usage:
            # Filter then format
            tasks_json = get_my_tasks(limit=100)
            tasks = json.loads(tasks_json)
            critical = [t for t in tasks["data"] if t["TaskPriorityName"] == "Critical"]
            critical_json = json.dumps({"data": critical})
            display = format_artifacts_as_markdown(critical_json, "task")

            # Combine multiple artifact types
            tasks = get_my_tasks()
            incidents = get_my_incidents()
            combined = format_artifacts_as_markdown(tasks, "task") + "\\n\\n" + \\
                       format_artifacts_as_markdown(incidents, "incident")

        Error Responses:
            Returns error message string if:
            - Invalid JSON input
            - Unknown artifact type
            - Missing required fields in artifact data
            - Empty artifact list
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
