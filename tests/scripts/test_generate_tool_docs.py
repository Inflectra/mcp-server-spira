"""Unit tests for OpenAPI documentation generator."""

import json
import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from generate_tool_docs import OpenAPIDocGenerator  # noqa: E402


@pytest.fixture
def sample_openapi_spec(tmp_path):
    """Create a sample OpenAPI spec for testing."""
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0"},
        "paths": {
            "/tasks": {
                "get": {
                    "operationId": "Task_RetrieveForOwner",
                    "summary": "Retrieves all tasks owned by the currently authenticated user",
                    "description": "Returns a list of tasks where the current user is the owner",
                    "parameters": [
                        {
                            "name": "include_completed",
                            "in": "query",
                            "description": "Whether to include completed tasks",
                            "required": False,
                            "schema": {"type": "boolean"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/RemoteTask"},
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/incidents": {
                "get": {
                    "operationId": "Incident_RetrieveForOwner",
                    "summary": "Retrieves all incidents",
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/RemoteIncident"},
                                    }
                                }
                            },
                        }
                    },
                }
            },
        },
        "components": {
            "schemas": {
                "RemoteTask": {
                    "type": "object",
                    "properties": {
                        "TaskId": {
                            "type": "integer",
                            "nullable": True,
                            "description": "The id of the task",
                        },
                        "Name": {"type": "string", "description": "The name of the task"},
                        "Description": {
                            "type": "string",
                            "description": "The detailed description of the task",
                        },
                        "TaskStatusId": {
                            "type": "integer",
                            "description": "The id of the status of the task",
                        },
                        "TaskStatusName": {
                            "type": "string",
                            "description": "The display name of the status",
                        },
                        "EstimatedEffort": {
                            "type": "integer",
                            "nullable": True,
                            "description": "The originally estimated effort (in minutes) of the task",
                        },
                        "ActualEffort": {
                            "type": "integer",
                            "nullable": True,
                            "description": "The actual effort expended so far (in minutes)",
                        },
                        "OwnerId": {
                            "type": "integer",
                            "nullable": True,
                            "description": "The id of the user that the task is assigned-to",
                        },
                        "OwnerName": {
                            "type": "string",
                            "description": "The display name of the owner",
                        },
                    },
                    "required": ["TaskId", "Name"],
                },
                "RemoteIncident": {
                    "type": "object",
                    "properties": {
                        "IncidentId": {"type": "integer", "description": "Unique identifier"},
                        "Name": {"type": "string"},
                    },
                },
            }
        },
    }

    spec_file = tmp_path / "test_spec.json"
    with open(spec_file, "w") as f:
        json.dump(spec, f)

    return str(spec_file)


class TestOpenAPIDocGenerator:
    """Test suite for OpenAPIDocGenerator class."""

    def test_init_loads_spec(self, sample_openapi_spec):
        """Test that generator loads OpenAPI spec correctly."""
        generator = OpenAPIDocGenerator(sample_openapi_spec)

        assert generator.spec is not None
        assert "openapi" in generator.spec
        assert generator.spec["openapi"] == "3.0.0"

    def test_init_file_not_found(self):
        """Test error handling when spec file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            OpenAPIDocGenerator("/nonexistent/path/spec.json")

    def test_extract_endpoint_info_success(self, sample_openapi_spec):
        """Test extracting endpoint information."""
        generator = OpenAPIDocGenerator(sample_openapi_spec)

        endpoint_info = generator.extract_endpoint_info("/tasks", "get")

        assert endpoint_info["operation_id"] == "Task_RetrieveForOwner"
        assert (
            endpoint_info["summary"]
            == "Retrieves all tasks owned by the currently authenticated user"
        )
        assert (
            endpoint_info["description"]
            == "Returns a list of tasks where the current user is the owner"
        )
        assert len(endpoint_info["parameters"]) == 1
        assert endpoint_info["parameters"][0]["name"] == "include_completed"
        assert "200" in endpoint_info["responses"]

    def test_extract_endpoint_info_path_not_found(self, sample_openapi_spec):
        """Test error when path doesn't exist."""
        generator = OpenAPIDocGenerator(sample_openapi_spec)

        with pytest.raises(ValueError, match="Path '/nonexistent' not found"):
            generator.extract_endpoint_info("/nonexistent", "get")

    def test_extract_endpoint_info_method_not_found(self, sample_openapi_spec):
        """Test error when method doesn't exist for path."""
        generator = OpenAPIDocGenerator(sample_openapi_spec)

        with pytest.raises(ValueError, match="Method 'post' not found"):
            generator.extract_endpoint_info("/tasks", "post")

    def test_extract_schema_info_success(self, sample_openapi_spec):
        """Test extracting schema information."""
        generator = OpenAPIDocGenerator(sample_openapi_spec)

        schema_info = generator.extract_schema_info("#/components/schemas/RemoteTask")

        assert schema_info["name"] == "RemoteTask"
        assert "TaskId" in schema_info["properties"]
        assert "Name" in schema_info["properties"]
        assert schema_info["properties"]["TaskId"]["type"] == "integer"
        assert schema_info["properties"]["TaskId"]["nullable"] is True
        assert schema_info["required"] == ["TaskId", "Name"]

    def test_extract_schema_info_invalid_reference(self, sample_openapi_spec):
        """Test error with invalid schema reference."""
        generator = OpenAPIDocGenerator(sample_openapi_spec)

        with pytest.raises(ValueError, match="Invalid schema reference"):
            generator.extract_schema_info("invalid/reference")

    def test_extract_schema_info_schema_not_found(self, sample_openapi_spec):
        """Test error when schema doesn't exist."""
        generator = OpenAPIDocGenerator(sample_openapi_spec)

        with pytest.raises(ValueError, match="Schema 'NonexistentSchema' not found"):
            generator.extract_schema_info("#/components/schemas/NonexistentSchema")

    def test_generate_docstring_template_basic(self, sample_openapi_spec):
        """Test generating basic docstring template."""
        generator = OpenAPIDocGenerator(sample_openapi_spec)

        docstring = generator.generate_docstring_template("get_my_tasks", "/tasks", "get")

        # Check key sections are present
        assert "Retrieves all tasks owned by the currently authenticated user" in docstring
        assert "Maps to Spira API: GET /tasks" in docstring
        assert "CLIENT-SIDE pagination" in docstring
        assert "Args:" in docstring
        assert "limit: Maximum number of items to return" in docstring
        assert "offset: Number of items to skip" in docstring
        assert "Returns:" in docstring
        assert '"data": [' in docstring
        assert '"pagination": {' in docstring
        assert "Key Fields:" in docstring
        assert "When to Use:" in docstring
        assert "[TO BE FILLED:" in docstring
        assert "Related Tools:" in docstring
        assert "Error Responses:" in docstring
        assert "Example Usage:" in docstring

    def test_generate_docstring_template_includes_schema_fields(self, sample_openapi_spec):
        """Test that docstring includes fields from schema."""
        generator = OpenAPIDocGenerator(sample_openapi_spec)

        docstring = generator.generate_docstring_template("get_my_tasks", "/tasks", "get")

        # Check that schema fields are included
        assert "TaskId" in docstring
        assert "Name" in docstring
        assert "EstimatedEffort" in docstring
        assert "ActualEffort" in docstring
        assert "The id of the task" in docstring
        assert "The originally estimated effort (in minutes)" in docstring

    def test_generate_docstring_template_includes_parameters(self, sample_openapi_spec):
        """Test that docstring includes endpoint parameters."""
        generator = OpenAPIDocGenerator(sample_openapi_spec)

        docstring = generator.generate_docstring_template("get_my_tasks", "/tasks", "get")

        # Check that endpoint parameters are included
        assert "include_completed" in docstring
        assert "Whether to include completed tasks" in docstring

    def test_identify_clarifications_needed_missing_description(self, sample_openapi_spec):
        """Test identification of missing endpoint description."""
        generator = OpenAPIDocGenerator(sample_openapi_spec)

        # /incidents has no description
        clarifications = generator.identify_clarifications_needed("/incidents", "get")

        assert len(clarifications) > 0
        # Check for structured clarification
        missing_desc = [c for c in clarifications if c["category"] == "missing_description"]
        assert len(missing_desc) > 0
        assert missing_desc[0]["severity"] == "high"
        assert "Missing endpoint description" in missing_desc[0]["issue"]
        assert "What is the purpose of this endpoint" in missing_desc[0]["question"]
        assert "OpenAPI:" in missing_desc[0]["context"]

    def test_identify_clarifications_needed_vague_descriptions(self, sample_openapi_spec):
        """Test identification of vague field descriptions."""
        generator = OpenAPIDocGenerator(sample_openapi_spec)

        clarifications = generator.identify_clarifications_needed("/tasks", "get")

        # Should identify vague descriptions like "The id of..."
        vague_clarifications = [
            c for c in clarifications if c["category"] == "vague_field_description"
        ]
        assert len(vague_clarifications) > 0
        # Check that TaskId and TaskStatusId are flagged
        vague_fields = [c["issue"] for c in vague_clarifications]
        assert any("TaskId" in issue for issue in vague_fields)
        assert any("TaskStatusId" in issue for issue in vague_fields)

    def test_identify_clarifications_needed_missing_field_description(self, sample_openapi_spec):
        """Test identification of missing field descriptions."""
        generator = OpenAPIDocGenerator(sample_openapi_spec)

        # RemoteIncident has Name field without description
        clarifications = generator.identify_clarifications_needed("/incidents", "get")

        missing_clarifications = [
            c for c in clarifications if c["category"] == "missing_field_description"
        ]
        assert len(missing_clarifications) > 0
        assert any("Name" in c["issue"] for c in missing_clarifications)

    def test_identify_clarifications_needed_business_logic(self, sample_openapi_spec):
        """Test identification of business logic questions (similar fields)."""
        generator = OpenAPIDocGenerator(sample_openapi_spec)

        clarifications = generator.identify_clarifications_needed("/tasks", "get")

        # Should identify similar fields like EstimatedEffort and ActualEffort
        business_logic = [c for c in clarifications if c["category"] == "business_logic"]
        assert len(business_logic) > 0
        # Check for effort-related fields
        effort_clarifications = [c for c in business_logic if "effort" in c["issue"].lower()]
        assert len(effort_clarifications) > 0

    def test_identify_clarifications_needed_id_name_pairs(self, sample_openapi_spec):
        """Test identification of ID/Name field pairs."""
        generator = OpenAPIDocGenerator(sample_openapi_spec)

        clarifications = generator.identify_clarifications_needed("/tasks", "get")

        # Should identify ID/Name pairs like TaskStatusId/TaskStatusName
        id_name_pairs = [
            c
            for c in clarifications
            if c["category"] == "business_logic" and "ID/Name pairs" in c["issue"]
        ]
        assert len(id_name_pairs) > 0
        assert any("TaskStatusId" in c["issue"] for c in id_name_pairs)

    def test_identify_clarifications_needed_workflow_context(self, sample_openapi_spec):
        """Test that workflow context questions are always added."""
        generator = OpenAPIDocGenerator(sample_openapi_spec)

        clarifications = generator.identify_clarifications_needed("/tasks", "get")

        # Should always have workflow context question
        workflow = [c for c in clarifications if c["category"] == "workflow_context"]
        assert len(workflow) > 0
        assert workflow[0]["severity"] == "high"
        assert "When should an LLM use this tool" in workflow[0]["question"]

    def test_identify_clarifications_needed_performance(self, sample_openapi_spec):
        """Test identification of performance concerns."""
        generator = OpenAPIDocGenerator(sample_openapi_spec)

        clarifications = generator.identify_clarifications_needed("/tasks", "get")

        # Should have performance question for 'my work' endpoints
        performance = [c for c in clarifications if c["category"] == "performance"]
        assert len(performance) > 0
        assert performance[0]["severity"] == "medium"
        assert "result set size" in performance[0]["question"]

    def test_identify_clarifications_needed_no_vague_issues(self, tmp_path):
        """Test when no vague descriptions exist."""
        # Create spec with complete descriptions
        spec = {
            "openapi": "3.0.0",
            "paths": {
                "/complete": {
                    "get": {
                        "operationId": "Complete_Get",
                        "summary": "Complete endpoint",
                        "description": "This endpoint has complete documentation with sufficient detail",
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {
                                                "$ref": "#/components/schemas/CompleteSchema"
                                            },
                                        }
                                    }
                                },
                            }
                        },
                    }
                }
            },
            "components": {
                "schemas": {
                    "CompleteSchema": {
                        "type": "object",
                        "properties": {
                            "Id": {
                                "type": "integer",
                                "description": "Unique identifier for the resource",
                            },
                            "Title": {
                                "type": "string",
                                "description": "Human-readable title of the resource",
                            },
                        },
                    }
                }
            },
        }

        spec_file = tmp_path / "complete_spec.json"
        with open(spec_file, "w") as f:
            json.dump(spec, f)

        generator = OpenAPIDocGenerator(str(spec_file))
        clarifications = generator.identify_clarifications_needed("/complete", "get")

        # Should have no vague descriptions (only checking for patterns like "the id")
        vague_clarifications = [
            c for c in clarifications if c["category"] == "vague_field_description"
        ]
        assert len(vague_clarifications) == 0

        # But should still have workflow and performance questions
        workflow = [c for c in clarifications if c["category"] == "workflow_context"]
        assert len(workflow) > 0

    def test_generate_documentation_report(self, sample_openapi_spec, tmp_path):
        """Test generating complete documentation report."""
        generator = OpenAPIDocGenerator(sample_openapi_spec)

        output_file = tmp_path / "test_report.md"
        generator.generate_documentation_report(str(output_file))

        # Check that file was created
        assert output_file.exists()

        # Read and verify content
        content = output_file.read_text()

        # Check report structure
        assert "# Tool Documentation Generation Report" in content
        assert "## get_my_tasks" in content
        assert "## get_my_incidents" in content
        assert "### Generated Docstring" in content
        assert "### Clarifications Needed" in content
        assert "```python" in content
        assert "@mcp.tool()" in content

        # Check for structured clarifications
        assert "🔴 High Priority" in content or "🟡 Medium Priority" in content
        assert "**Issue:**" in content
        assert "**Question:**" in content
        assert "**Context:**" in content

        # Check for examples section
        assert "## Examples of Good Clarification Requests" in content
        assert "### Example 1: Ambiguous Field Description" in content
        assert "### Example 2: Business Logic Question" in content

    def test_generate_documentation_report_creates_directory(self, sample_openapi_spec, tmp_path):
        """Test that report generation creates output directory if needed."""
        generator = OpenAPIDocGenerator(sample_openapi_spec)

        # Use nested path that doesn't exist
        output_file = tmp_path / "nested" / "dir" / "report.md"
        generator.generate_documentation_report(str(output_file))

        # Check that file and directories were created
        assert output_file.exists()
        assert output_file.parent.exists()


class TestDocGeneratorEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_parameters_list(self, tmp_path):
        """Test handling endpoint with no parameters."""
        spec = {
            "openapi": "3.0.0",
            "paths": {
                "/simple": {
                    "get": {
                        "operationId": "Simple_Get",
                        "summary": "Simple endpoint",
                        "parameters": [],
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/SimpleSchema"},
                                        }
                                    }
                                },
                            }
                        },
                    }
                }
            },
            "components": {
                "schemas": {
                    "SimpleSchema": {"type": "object", "properties": {"Id": {"type": "integer"}}}
                }
            },
        }

        spec_file = tmp_path / "simple_spec.json"
        with open(spec_file, "w") as f:
            json.dump(spec, f)

        generator = OpenAPIDocGenerator(str(spec_file))
        docstring = generator.generate_docstring_template("simple_tool", "/simple", "get")

        # Should still generate valid docstring
        assert "Args:" in docstring
        assert "limit:" in docstring  # Standard pagination params
        assert "offset:" in docstring

    def test_schema_with_many_fields(self, tmp_path):
        """Test handling schema with many fields (should limit output)."""
        # Create schema with 20 fields
        properties = {
            f"Field{i}": {"type": "string", "description": f"Field {i}"} for i in range(20)
        }

        spec = {
            "openapi": "3.0.0",
            "paths": {
                "/large": {
                    "get": {
                        "operationId": "Large_Get",
                        "summary": "Large schema endpoint",
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/LargeSchema"},
                                        }
                                    }
                                },
                            }
                        },
                    }
                }
            },
            "components": {
                "schemas": {"LargeSchema": {"type": "object", "properties": properties}}
            },
        }

        spec_file = tmp_path / "large_spec.json"
        with open(spec_file, "w") as f:
            json.dump(spec, f)

        generator = OpenAPIDocGenerator(str(spec_file))
        docstring = generator.generate_docstring_template("large_tool", "/large", "get")

        # Should limit fields in output
        assert "// ... additional fields ..." in docstring
        # Should show exactly 10 fields in JSON structure (limited) + 8 in Key Fields
        # Count field definitions in the JSON structure section
        json_section = docstring.split("Key Fields:")[0]
        field_count_in_json = json_section.count('"Field')
        assert field_count_in_json == 10  # Limited to 10 fields in JSON structure
