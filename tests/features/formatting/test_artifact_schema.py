"""Unit and property tests for the artifact_schema tool."""

import json

import pytest
from hypothesis import given, settings
from hypothesis.strategies import sampled_from, text

from mcp_server_spira.features.formatting.tools.artifact_schema import (
    VALID_ARTIFACT_TYPES,
    _get_artifact_schema_impl,
)

# ---------------------------------------------------------------------------
# Unit tests (subtask 3.1)
# ---------------------------------------------------------------------------


def test_valid_task_returns_fields():
    """Call _impl('task'), assert fields non-empty, each entry has name/type/description."""
    result = json.loads(_get_artifact_schema_impl("task"))
    assert "fields" in result
    assert len(result["fields"]) > 0
    for field in result["fields"]:
        assert "name" in field
        assert "type" in field
        assert "description" in field


@pytest.mark.parametrize("artifact_type", list(VALID_ARTIFACT_TYPES))
def test_all_artifact_types_return_fields(artifact_type):
    """All 11 artifact types return a non-empty fields list."""
    result = json.loads(_get_artifact_schema_impl(artifact_type))
    assert "fields" in result
    assert len(result["fields"]) > 0


def test_invalid_type_returns_error():
    """Call _impl('bogus'), assert 'error' key present."""
    result = json.loads(_get_artifact_schema_impl("bogus"))
    assert "error" in result


def test_invalid_type_lists_valid_types():
    """Error response includes 'valid_types' key containing all 11 types."""
    result = json.loads(_get_artifact_schema_impl("bogus"))
    assert "valid_types" in result
    for t in VALID_ARTIFACT_TYPES:
        assert t in result["valid_types"]


def test_valid_type_echoed_in_response():
    """The artifact_type key in the response matches the input."""
    for artifact_type in VALID_ARTIFACT_TYPES:
        result = json.loads(_get_artifact_schema_impl(artifact_type))
        assert result["artifact_type"] == artifact_type


# ---------------------------------------------------------------------------
# Property test — Property 1 (subtask 3.2)
# ---------------------------------------------------------------------------


# Feature: artifact-schema-tool, Property 1: Valid artifact type returns parseable schema
@given(artifact_type=sampled_from(VALID_ARTIFACT_TYPES))
@settings(max_examples=100)
def test_valid_type_schema_round_trip(artifact_type):
    """Validates: Requirements 1.1, 1.2, 4.2"""
    result = json.loads(_get_artifact_schema_impl(artifact_type))
    assert result["artifact_type"] == artifact_type
    assert len(result["fields"]) > 0
    for field in result["fields"]:
        assert "name" in field
        assert "type" in field
        assert "description" in field


# ---------------------------------------------------------------------------
# Property test — Property 2 (subtask 3.3)
# ---------------------------------------------------------------------------


# Feature: artifact-schema-tool, Property 2: Invalid artifact type returns JSON error object
@given(artifact_type=text().filter(lambda s: s not in VALID_ARTIFACT_TYPES))
@settings(max_examples=100)
def test_invalid_type_returns_error_property(artifact_type):
    """Validates: Requirements 1.1, 1.3"""
    result = json.loads(_get_artifact_schema_impl(artifact_type))
    assert "error" in result
    assert len(result["error"]) > 0
    assert "valid_types" in result
