#!/usr/bin/env python3
"""
Generates tool documentation from OpenAPI specification.

This script automates the creation of tool docstrings by extracting
information from the Spira OpenAPI spec. It generates templates that
developers can review and enhance with workflow context.

Usage:
    python scripts/generate_tool_docs.py --spec SpiraRestAPI-v7.0-OpenAPI.json --output docs/tool_documentation_report.md
"""

import json
from pathlib import Path
from typing import Any


class OpenAPIDocGenerator:
    """Generates tool documentation from OpenAPI spec."""

    def __init__(self, openapi_spec_path: str):
        """
        Initialize generator with OpenAPI spec.

        Args:
            openapi_spec_path: Path to OpenAPI JSON file
        """
        with open(openapi_spec_path) as f:
            self.spec = json.load(f)

    def extract_endpoint_info(self, path: str, method: str) -> dict[str, Any]:
        """
        Extract endpoint information from OpenAPI spec.

        Args:
            path: API path (e.g., "/tasks")
            method: HTTP method (e.g., "get")

        Returns:
            Dictionary with endpoint details:
            - operation_id: OpenAPI operation ID
            - summary: Brief description
            - description: Detailed description
            - parameters: List of parameter definitions
            - responses: Response schema information
        """
        if path not in self.spec["paths"]:
            raise ValueError(f"Path '{path}' not found in OpenAPI spec")

        if method not in self.spec["paths"][path]:
            raise ValueError(f"Method '{method}' not found for path '{path}'")

        endpoint = self.spec["paths"][path][method]

        return {
            "operation_id": endpoint.get("operationId", ""),
            "summary": endpoint.get("summary", ""),
            "description": endpoint.get("description", ""),
            "parameters": endpoint.get("parameters", []),
            "responses": endpoint.get("responses", {}),
        }

    def extract_schema_info(self, schema_ref: str) -> dict[str, Any]:
        """
        Extract schema information from OpenAPI spec.

        Args:
            schema_ref: Schema reference (e.g., "#/components/schemas/RemoteTask")

        Returns:
            Dictionary with schema details:
            - name: Schema name
            - properties: Field definitions
            - required: List of required fields
            - description: Schema description
        """
        # Parse schema reference
        if not schema_ref.startswith("#/components/schemas/"):
            raise ValueError(f"Invalid schema reference: {schema_ref}")

        schema_name = schema_ref.split("/")[-1]

        if "components" not in self.spec or "schemas" not in self.spec["components"]:
            raise ValueError("No schemas found in OpenAPI spec")

        if schema_name not in self.spec["components"]["schemas"]:
            raise ValueError(f"Schema '{schema_name}' not found in OpenAPI spec")

        schema = self.spec["components"]["schemas"][schema_name]

        return {
            "name": schema_name,
            "properties": schema.get("properties", {}),
            "required": schema.get("required", []),
            "description": schema.get("description", ""),
        }

    def generate_docstring_template(self, tool_name: str, endpoint_path: str, method: str) -> str:
        """
        Generate docstring template for a tool.

        Args:
            tool_name: Name of the MCP tool
            endpoint_path: API endpoint path
            method: HTTP method

        Returns:
            Formatted docstring template as string
        """
        endpoint_info = self.extract_endpoint_info(endpoint_path, method)

        # Extract response schema
        response_schema = None
        if "200" in endpoint_info["responses"]:
            response_content = endpoint_info["responses"]["200"].get("content", {})
            if "application/json" in response_content:
                schema_def = response_content["application/json"].get("schema", {})

                # Handle array responses
                if schema_def.get("type") == "array" and "items" in schema_def:
                    if "$ref" in schema_def["items"]:
                        response_schema = self.extract_schema_info(schema_def["items"]["$ref"])
                # Handle direct schema references
                elif "$ref" in schema_def:
                    response_schema = self.extract_schema_info(schema_def["$ref"])

        # Build docstring
        docstring_parts = []
        docstring_parts.append('"""')
        docstring_parts.append(endpoint_info["summary"])
        docstring_parts.append("")
        docstring_parts.append(f"Maps to Spira API: {method.upper()} {endpoint_path}")
        docstring_parts.append("")

        if endpoint_info["description"]:
            docstring_parts.append(endpoint_info["description"])
            docstring_parts.append("")

        # Add pagination note for list endpoints
        docstring_parts.append(
            "**Pagination:** This endpoint uses CLIENT-SIDE pagination. The API returns"
        )
        docstring_parts.append(
            "all results, and we slice them in Python. This is acceptable for 'my work'"
        )
        docstring_parts.append("queries which typically return < 500 items.")
        docstring_parts.append("")
        docstring_parts.append(
            "**For Display:** Modern LLMs can format JSON naturally for simple display."
        )
        docstring_parts.append(
            "For complex workflows where you've filtered or processed the data, use"
        )
        docstring_parts.append("format_artifacts_as_markdown() to ensure consistent formatting.")
        docstring_parts.append("")

        # Add parameters section
        docstring_parts.append("Args:")

        # Add pagination parameters (standard for all list tools)
        docstring_parts.append("    limit: Maximum number of items to return (1-500, default: 25)")
        docstring_parts.append("        Controls result set size for pagination.")
        docstring_parts.append("    offset: Number of items to skip (>= 0, default: 0)")
        docstring_parts.append("        Used for retrieving subsequent pages of results.")

        # Add any additional parameters from OpenAPI
        for param in endpoint_info["parameters"]:
            param_name = param.get("name", "unknown")
            param_desc = param.get("description", "No description")
            required = "required" if param.get("required") else "optional"
            docstring_parts.append(f"    {param_name}: {param_desc} ({required})")

        docstring_parts.append("")

        # Add return value documentation
        docstring_parts.append("Returns:")
        docstring_parts.append("    JSON string with structure:")
        docstring_parts.append("    {")
        docstring_parts.append('        "data": [')
        docstring_parts.append("            {")

        # Add key fields from schema (limit to first 10 for readability)
        if response_schema:
            for field_count, (field_name, field_info) in enumerate(
                response_schema["properties"].items()
            ):
                if field_count >= 10:
                    docstring_parts.append("                // ... additional fields ...")
                    break

                field_type = field_info.get("type", "unknown")
                field_desc = field_info.get("description", "")
                nullable = ", nullable" if field_info.get("nullable") else ""

                # Format the field line
                if field_desc:
                    docstring_parts.append(
                        f'                "{field_name}": {field_type}{nullable},  // {field_desc}'
                    )
                else:
                    docstring_parts.append(
                        f'                "{field_name}": {field_type}{nullable}'
                    )

        docstring_parts.append("            }")
        docstring_parts.append("        ],")
        docstring_parts.append('        "pagination": {')
        docstring_parts.append('            "limit": 25,')
        docstring_parts.append('            "offset": 0,')
        docstring_parts.append('            "returned_count": 25,')
        docstring_parts.append('            "total_count": 150,')
        docstring_parts.append('            "has_more": true,')
        docstring_parts.append('            "pagination_type": "client-side"')
        docstring_parts.append("        }")
        docstring_parts.append("    }")
        docstring_parts.append("")

        # Add key fields section with descriptions
        docstring_parts.append("Key Fields:")
        if response_schema:
            field_count = 0
            for field_name, field_info in response_schema["properties"].items():
                if field_count >= 8:  # Limit to most important fields
                    break

                field_desc = field_info.get("description", "No description available")
                docstring_parts.append(f"    - {field_name}: {field_desc}")
                field_count += 1
        docstring_parts.append("")

        # Add placeholders for manual completion
        docstring_parts.append("When to Use:")
        docstring_parts.append("    [TO BE FILLED: Describe use cases and scenarios]")
        docstring_parts.append("")
        docstring_parts.append("Related Tools:")
        docstring_parts.append(
            "    - format_artifacts_as_markdown: Format filtered/processed results"
        )
        docstring_parts.append("    [TO BE FILLED: List other related tools]")
        docstring_parts.append("")
        docstring_parts.append("Error Responses:")
        docstring_parts.append("    {")
        docstring_parts.append('        "error": "Invalid pagination parameters",')
        docstring_parts.append('        "error_code": "INVALID_PARAMETER",')
        docstring_parts.append('        "details": {')
        docstring_parts.append('            "parameter": "limit",')
        docstring_parts.append('            "value": 1000,')
        docstring_parts.append('            "expected": "1-500"')
        docstring_parts.append("        },")
        docstring_parts.append('        "suggestion": "Use limit between 1 and 500"')
        docstring_parts.append("    }")
        docstring_parts.append("")
        docstring_parts.append("Example Usage:")
        docstring_parts.append("    # Simple display - LLM formats naturally")
        docstring_parts.append(f"    result_json = {tool_name}()")
        docstring_parts.append(
            "    # LLM can format this JSON for display without additional tools"
        )
        docstring_parts.append("")
        docstring_parts.append("    # Complex workflow - Use formatting tool for filtered results")
        docstring_parts.append(f"    result_json = {tool_name}(limit=100)")
        docstring_parts.append("    result = json.loads(result_json)")
        docstring_parts.append(
            '    filtered = [item for item in result["data"] if meets_criteria(item)]'
        )
        docstring_parts.append('    filtered_json = json.dumps({"data": filtered})')
        docstring_parts.append(
            '    readable = format_artifacts_as_markdown(filtered_json, "artifact_type")'
        )
        docstring_parts.append('"""')

        return "\n".join(docstring_parts)

    def identify_clarifications_needed(
        self, endpoint_path: str, method: str
    ) -> list[dict[str, Any]]:
        """
        Identify areas that need human clarification.

        This method implements comprehensive clarification detection covering:
        - Ambiguous or missing descriptions (AC-1.7.2, AC-1.7.3)
        - Complex nested schemas (AC-1.7.4)
        - Business logic questions (AC-1.7.5)
        - Workflow context (AC-1.7.6)
        - Specific questions with context (AC-1.7.7, AC-1.7.8)

        Args:
            endpoint_path: API endpoint path
            method: HTTP method

        Returns:
            List of clarification dictionaries with:
            - category: Type of clarification needed
            - severity: "high", "medium", or "low"
            - issue: Description of the issue
            - question: Specific question for human
            - context: OpenAPI spec reference or additional context
        """
        clarifications = []

        try:
            endpoint_info = self.extract_endpoint_info(endpoint_path, method)

            # 1. Check for missing or ambiguous endpoint description (AC-1.7.2)
            if not endpoint_info["description"]:
                clarifications.append(
                    {
                        "category": "missing_description",
                        "severity": "high",
                        "issue": f"Missing endpoint description for {method.upper()} {endpoint_path}",
                        "question": "What is the purpose of this endpoint? What does it return and when should it be used?",
                        "context": f"OpenAPI: paths.{endpoint_path}.{method}.description",
                    }
                )
            elif len(endpoint_info["description"]) < 20:
                clarifications.append(
                    {
                        "category": "ambiguous_description",
                        "severity": "medium",
                        "issue": f"Very brief endpoint description: '{endpoint_info['description']}'",
                        "question": "Can you provide more detail about what this endpoint does and when to use it?",
                        "context": f"OpenAPI: paths.{endpoint_path}.{method}.description",
                    }
                )

            # 2. Check for missing parameter descriptions (AC-1.7.3)
            for param in endpoint_info["parameters"]:
                param_name = param.get("name", "unknown")
                if not param.get("description"):
                    clarifications.append(
                        {
                            "category": "missing_parameter_description",
                            "severity": "high",
                            "issue": f"Missing description for parameter '{param_name}'",
                            "question": f"What is the purpose of the '{param_name}' parameter? What values are valid?",
                            "context": f"OpenAPI: paths.{endpoint_path}.{method}.parameters[name={param_name}]",
                        }
                    )

            # 3. Check response schema for issues
            if "200" in endpoint_info["responses"]:
                response_content = endpoint_info["responses"]["200"].get("content", {})
                if "application/json" in response_content:
                    schema_def = response_content["application/json"].get("schema", {})

                    # Get schema reference
                    schema_ref = None
                    if schema_def.get("type") == "array" and "items" in schema_def:
                        if "$ref" in schema_def["items"]:
                            schema_ref = schema_def["items"]["$ref"]
                    elif "$ref" in schema_def:
                        schema_ref = schema_def["$ref"]

                    if schema_ref:
                        try:
                            schema = self.extract_schema_info(schema_ref)

                            # 4. Check for vague or missing field descriptions (AC-1.7.2)
                            vague_patterns = [
                                "the id",
                                "the name",
                                "the display name",
                                "the value",
                                "the type",
                            ]
                            for field_name, field_info in schema["properties"].items():
                                desc = field_info.get("description", "").lower().strip()

                                if not desc:
                                    clarifications.append(
                                        {
                                            "category": "missing_field_description",
                                            "severity": "medium",
                                            "issue": f"Missing description for field '{field_name}' in {schema['name']}",
                                            "question": f"What is the purpose of the '{field_name}' field? When is it null? What values are typical?",
                                            "context": f"OpenAPI: components.schemas.{schema['name']}.properties.{field_name}",
                                        }
                                    )
                                elif any(pattern in desc for pattern in vague_patterns):
                                    clarifications.append(
                                        {
                                            "category": "vague_field_description",
                                            "severity": "medium",
                                            "issue": f"Vague description for field '{field_name}': '{field_info.get('description')}'",
                                            "question": f"Can you provide more context about '{field_name}'? What does it represent in business terms?",
                                            "context": f"OpenAPI: components.schemas.{schema['name']}.properties.{field_name}",
                                        }
                                    )

                            # 5. Check for complex nested schemas (AC-1.7.4)
                            nested_objects = []
                            nested_arrays = []
                            for field_name, field_info in schema["properties"].items():
                                if field_info.get("type") == "object":
                                    nested_objects.append(field_name)
                                elif field_info.get("type") == "array":
                                    nested_arrays.append(field_name)

                            if nested_objects:
                                clarifications.append(
                                    {
                                        "category": "complex_nested_schema",
                                        "severity": "medium",
                                        "issue": f"Schema contains nested objects: {', '.join(nested_objects)}",
                                        "question": f"Should these nested objects ({', '.join(nested_objects)}) be included in the response or retrieved separately? What's the performance impact?",
                                        "context": f"OpenAPI: components.schemas.{schema['name']}",
                                    }
                                )

                            if len(nested_arrays) > 2:
                                clarifications.append(
                                    {
                                        "category": "complex_nested_schema",
                                        "severity": "low",
                                        "issue": f"Schema contains multiple array fields: {', '.join(nested_arrays)}",
                                        "question": f"Are all these arrays ({', '.join(nested_arrays)}) typically populated? Should any be excluded for performance?",
                                        "context": f"OpenAPI: components.schemas.{schema['name']}",
                                    }
                                )

                            # 6. Detect similar field names that suggest business logic questions (AC-1.7.5)
                            field_groups = self._detect_similar_fields(schema["properties"])
                            for fields in field_groups.values():
                                if len(fields) > 1:
                                    clarifications.append(
                                        {
                                            "category": "business_logic",
                                            "severity": "high",
                                            "issue": f"Multiple similar fields found: {', '.join(fields)}",
                                            "question": f"What's the difference between {' vs '.join(fields)}? When should each be used? Which is recommended for LLM filtering?",
                                            "context": f"OpenAPI: components.schemas.{schema['name']} - Fields: {', '.join(fields)}",
                                        }
                                    )

                            # 7. Check for ID/Name pairs (AC-1.7.5)
                            id_name_pairs = self._detect_id_name_pairs(schema["properties"])
                            if id_name_pairs:
                                clarifications.append(
                                    {
                                        "category": "business_logic",
                                        "severity": "medium",
                                        "issue": f"Found ID/Name pairs: {', '.join([f'{id_field}/{name_field}' for id_field, name_field in id_name_pairs])}",
                                        "question": "Should LLMs filter/search by ID or Name? What's the recommended approach for each pair?",
                                        "context": f"OpenAPI: components.schemas.{schema['name']}",
                                    }
                                )

                            # 8. Check for nullable fields that might indicate edge cases (AC-1.7.5)
                            nullable_fields = [
                                field_name
                                for field_name, field_info in schema["properties"].items()
                                if field_info.get("nullable", False)
                            ]
                            if len(nullable_fields) > 5:
                                clarifications.append(
                                    {
                                        "category": "edge_cases",
                                        "severity": "low",
                                        "issue": f"Many nullable fields: {len(nullable_fields)} fields can be null",
                                        "question": "Under what conditions are these fields null? Are there common scenarios where multiple fields are null?",
                                        "context": f"OpenAPI: components.schemas.{schema['name']} - Nullable fields: {', '.join(nullable_fields[:5])}...",
                                    }
                                )

                        except ValueError:
                            pass  # Schema not found, skip

            # 9. Workflow context questions (AC-1.7.6)
            # These are always added as they require human knowledge
            clarifications.append(
                {
                    "category": "workflow_context",
                    "severity": "high",
                    "issue": "Missing workflow context",
                    "question": f"When should an LLM use this tool ({method.upper()} {endpoint_path})? What are the typical use cases? Are there related tools that should be used instead?",
                    "context": "This requires human knowledge of the overall system workflow",
                }
            )

            # 10. Performance implications (AC-1.7.5)
            if endpoint_path in [
                "/tasks",
                "/incidents",
                "/requirements",
                "/test-cases",
                "/test-sets",
            ]:
                clarifications.append(
                    {
                        "category": "performance",
                        "severity": "medium",
                        "issue": "Potential performance concern for 'my work' endpoint",
                        "question": "What's a typical result set size for this endpoint? Are there performance issues with large result sets? Should we recommend a maximum limit?",
                        "context": "This endpoint uses client-side pagination - all results are retrieved from API",
                    }
                )

        except (ValueError, KeyError) as e:
            clarifications.append(
                {
                    "category": "error",
                    "severity": "high",
                    "issue": f"Error analyzing endpoint: {str(e)}",
                    "question": "Unable to analyze this endpoint. Is the OpenAPI spec correct?",
                    "context": f"Error occurred while processing {method.upper()} {endpoint_path}",
                }
            )

        return clarifications

    def _detect_similar_fields(self, properties: dict[str, Any]) -> dict[str, list[str]]:
        """
        Detect groups of similar field names that might indicate business logic questions.

        For example: EstimatedEffort, ActualEffort, RemainingEffort, ProjectedEffort

        Args:
            properties: Schema properties dictionary

        Returns:
            Dictionary mapping base names to lists of similar fields
        """
        # Common suffixes/prefixes that indicate related fields
        patterns = {
            "effort": ["Effort"],
            "date": ["Date"],
            "id": ["Id"],
            "name": ["Name"],
            "status": ["Status"],
            "type": ["Type"],
            "priority": ["Priority"],
            "owner": ["Owner"],
            "count": ["Count"],
        }

        groups = {}
        for pattern_name, pattern_suffixes in patterns.items():
            matching_fields = []
            for field_name in properties:
                if any(suffix in field_name for suffix in pattern_suffixes):
                    matching_fields.append(field_name)

            if len(matching_fields) > 1:
                groups[pattern_name] = matching_fields

        return groups

    def _detect_id_name_pairs(self, properties: dict[str, Any]) -> list[tuple]:
        """
        Detect ID/Name field pairs (e.g., TaskStatusId and TaskStatusName).

        Args:
            properties: Schema properties dictionary

        Returns:
            List of (id_field, name_field) tuples
        """
        pairs = []
        field_names = list(properties.keys())

        for field_name in field_names:
            if field_name.endswith("Id"):
                # Look for corresponding Name field
                base_name = field_name[:-2]  # Remove "Id"
                name_field = base_name + "Name"
                if name_field in field_names:
                    pairs.append((field_name, name_field))

        return pairs

    def generate_documentation_report(self, output_path: str) -> None:
        """
        Generate complete documentation report for all tools.

        Args:
            output_path: Path to save markdown report
        """
        report_lines = []
        report_lines.append("# Tool Documentation Generation Report")
        report_lines.append("")
        report_lines.append(
            "This report contains generated documentation templates for MCP tools based on the Spira OpenAPI specification."
        )
        report_lines.append("")
        report_lines.append("**Generated:** Auto-generated from OpenAPI spec")
        report_lines.append("**Purpose:** Provide starting point for tool documentation")
        report_lines.append(
            "**Next Steps:** Review, enhance with workflow context, and resolve clarifications"
        )
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")

        # Define tools to document (my work tools)
        tools = [
            ("get_my_tasks", "/tasks", "get", "task"),
            ("get_my_incidents", "/incidents", "get", "incident"),
            ("get_my_requirements", "/requirements", "get", "requirement"),
            ("get_my_test_cases", "/test-cases", "get", "test_case"),
            ("get_my_test_sets", "/test-sets", "get", "test_set"),
        ]

        for tool_name, path, method, artifact_type in tools:
            report_lines.append(f"## {tool_name}")
            report_lines.append("")
            report_lines.append(f"**Endpoint:** `{method.upper()} {path}`")
            report_lines.append(f"**Artifact Type:** `{artifact_type}`")
            report_lines.append("")

            # Generate docstring
            try:
                docstring = self.generate_docstring_template(tool_name, path, method)
                report_lines.append("### Generated Docstring")
                report_lines.append("")
                report_lines.append("```python")
                report_lines.append("@mcp.tool()")
                report_lines.append(f"def {tool_name}(limit: int = 25, offset: int = 0) -> str:")
                report_lines.append(docstring)
                report_lines.append("```")
                report_lines.append("")
            except Exception as e:
                report_lines.append(f"❌ **Error generating docstring:** {str(e)}")
                report_lines.append("")

            # Identify clarifications (AC-1.7.9: generates clarification checklist)
            clarifications = self.identify_clarifications_needed(path, method)
            if clarifications:
                report_lines.append("### Clarifications Needed")
                report_lines.append("")
                report_lines.append(f"**Total Issues:** {len(clarifications)}")
                report_lines.append("")

                # Group by severity
                high_priority = [c for c in clarifications if c["severity"] == "high"]
                medium_priority = [c for c in clarifications if c["severity"] == "medium"]
                low_priority = [c for c in clarifications if c["severity"] == "low"]

                if high_priority:
                    report_lines.append("#### 🔴 High Priority")
                    report_lines.append("")
                    for clarification in high_priority:
                        report_lines.append(
                            f"**{clarification['category'].replace('_', ' ').title()}**"
                        )
                        report_lines.append(f"- **Issue:** {clarification['issue']}")
                        report_lines.append(f"- **Question:** {clarification['question']}")
                        report_lines.append(f"- **Context:** `{clarification['context']}`")
                        report_lines.append("")

                if medium_priority:
                    report_lines.append("#### 🟡 Medium Priority")
                    report_lines.append("")
                    for clarification in medium_priority:
                        report_lines.append(
                            f"**{clarification['category'].replace('_', ' ').title()}**"
                        )
                        report_lines.append(f"- **Issue:** {clarification['issue']}")
                        report_lines.append(f"- **Question:** {clarification['question']}")
                        report_lines.append(f"- **Context:** `{clarification['context']}`")
                        report_lines.append("")

                if low_priority:
                    report_lines.append("#### 🟢 Low Priority")
                    report_lines.append("")
                    for clarification in low_priority:
                        report_lines.append(
                            f"**{clarification['category'].replace('_', ' ').title()}**"
                        )
                        report_lines.append(f"- **Issue:** {clarification['issue']}")
                        report_lines.append(f"- **Question:** {clarification['question']}")
                        report_lines.append(f"- **Context:** `{clarification['context']}`")
                        report_lines.append("")
            else:
                report_lines.append("### Clarifications Needed")
                report_lines.append("")
                report_lines.append("✅ No clarifications needed - documentation appears complete")
                report_lines.append("")

            report_lines.append("---")
            report_lines.append("")

        # Add examples of good clarification requests (AC-1.7.10)
        report_lines.append("## Examples of Good Clarification Requests")
        report_lines.append("")
        report_lines.append("### Example 1: Ambiguous Field Description")
        report_lines.append(
            "**Issue:** Field 'EstimatedEffort' has vague description: 'The estimated effort'"
        )
        report_lines.append("")
        report_lines.append("**Good Question:**")
        report_lines.append(
            "> What is the purpose of the 'EstimatedEffort' field? Is this the original estimate set at task creation, or can it be updated? What unit is it measured in (hours, minutes, story points)? When would it be null?"
        )
        report_lines.append("")
        report_lines.append(
            "**Context:** `OpenAPI: components.schemas.RemoteTask.properties.EstimatedEffort`"
        )
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("### Example 2: Business Logic Question")
        report_lines.append(
            "**Issue:** Multiple similar fields: EstimatedEffort, ActualEffort, RemainingEffort, ProjectedEffort"
        )
        report_lines.append("")
        report_lines.append("**Good Question:**")
        report_lines.append(
            "> What's the difference between EstimatedEffort, ActualEffort, RemainingEffort, and ProjectedEffort? When should each be used? Is ProjectedEffort calculated (ActualEffort + RemainingEffort) or manually set? Which field should LLMs use for filtering 'tasks that will take more than 2 hours'?"
        )
        report_lines.append("")
        report_lines.append(
            "**Context:** `OpenAPI: components.schemas.RemoteTask - Fields: EstimatedEffort, ActualEffort, RemainingEffort, ProjectedEffort`"
        )
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("### Example 3: Workflow Context")
        report_lines.append("**Issue:** Missing workflow context for get_my_tasks")
        report_lines.append("")
        report_lines.append("**Good Question:**")
        report_lines.append(
            "> When should an LLM use get_my_tasks vs get_task_by_id (future tool) vs search_tasks (future tool)? What are typical use cases for this tool? Should it be used for daily standup reports, workload analysis, or both?"
        )
        report_lines.append("")
        report_lines.append(
            "**Context:** This requires human knowledge of the overall system workflow"
        )
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("### Example 4: Edge Cases")
        report_lines.append("**Issue:** Behavior when user has no assigned tasks is unclear")
        report_lines.append("")
        report_lines.append("**Good Question:**")
        report_lines.append(
            "> What should this tool return when the user has no assigned tasks? Should it return an empty array with pagination metadata, or should it return a specific message? Are there any error conditions that should be documented?"
        )
        report_lines.append("")
        report_lines.append("**Context:** `OpenAPI: paths./tasks.get.responses.200`")
        report_lines.append("")

        # Write report
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            f.write("\n".join(report_lines))

        print(f"✅ Documentation report generated: {output_path}")
        print(f"📄 Generated documentation for {len(tools)} tools")

        # Count total clarifications
        total_clarifications = sum(
            len(self.identify_clarifications_needed(path, method)) for _, path, method, _ in tools
        )
        print(f"⚠️  Total clarifications needed: {total_clarifications}")


def main():
    """CLI interface for documentation generator."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate tool documentation from OpenAPI spec",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate documentation report
  python scripts/generate_tool_docs.py --spec SpiraRestAPI-v7.0-OpenAPI.json --output docs/tool_documentation_report.md

  # Use custom paths
  python scripts/generate_tool_docs.py --spec /path/to/spec.json --output /path/to/output.md
        """,
    )

    parser.add_argument("--spec", required=True, help="Path to OpenAPI JSON file")
    parser.add_argument("--output", required=True, help="Path to output markdown file")

    args = parser.parse_args()

    try:
        generator = OpenAPIDocGenerator(args.spec)
        generator.generate_documentation_report(args.output)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print(f"   Make sure the OpenAPI spec file exists at: {args.spec}")
        exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
