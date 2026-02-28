# Feature: kiro-power-packaging
"""Unit tests for mcp_server_spira.features.context module."""

import asyncio
import json
from unittest.mock import MagicMock, patch

import pytest

import mcp_server_spira.features.context as context_module
from mcp_server_spira.features.context import (
    get_active_product_context,
    load_active_product_context,
)
from mcp_server_spira.server import active_product_resource

pytestmark = pytest.mark.unit


def _reset_context():
    """Reset module-level context state between tests."""
    context_module._active_product_context = None


def _make_mock_client(product=None, releases=None, raise_exc=None):
    """Build a mock Spira client."""
    client = MagicMock()
    if raise_exc is not None:
        client.make_spira_api_get_request.side_effect = raise_exc
        client.make_spira_api_post_request.side_effect = raise_exc
    else:
        client.make_spira_api_get_request.return_value = product or {}
        client.make_spira_api_post_request.return_value = releases or []
    return client


class TestLoadActiveProductContext:
    """Tests for load_active_product_context()."""

    def setup_method(self):
        _reset_context()

    def test_no_default_product_id_makes_no_api_call(self):
        """When no default product ID is set, no API call is made and context stays None."""
        mock_client = _make_mock_client()
        with (
            patch("mcp_server_spira.config._default_product_id", None),
            patch("mcp_server_spira.features.context.get_client", return_value=mock_client),
        ):
            asyncio.run(load_active_product_context())

        mock_client.make_spira_api_get_request.assert_not_called()
        mock_client.make_spira_api_post_request.assert_not_called()
        assert get_active_product_context() is None

    def test_api_failure_does_not_raise(self):
        """When the API call fails, no exception is raised and context remains None."""
        mock_client = _make_mock_client(raise_exc=RuntimeError("network error"))
        with (
            patch("mcp_server_spira.config._default_product_id", 42),
            patch("mcp_server_spira.features.context.get_client", return_value=mock_client),
        ):
            # Must not raise
            asyncio.run(load_active_product_context())

        assert get_active_product_context() is None

    def test_successful_load_context_has_required_keys(self):
        """Successful load stores a dict with all four required keys."""
        product = {"Name": "My Project", "Description": "A test project"}
        releases = [
            {"ReleaseId": 1, "Name": "Sprint 1", "VersionNumber": "1.0.0", "Active": True},
            {"ReleaseId": 2, "Name": "Sprint 2", "VersionNumber": "1.0.1", "Active": False},
        ]
        mock_client = _make_mock_client(product=product, releases=releases)

        with (
            patch("mcp_server_spira.config._default_product_id", 55),
            patch("mcp_server_spira.features.context.get_client", return_value=mock_client),
        ):
            asyncio.run(load_active_product_context())

        ctx = get_active_product_context()
        assert ctx is not None
        assert "product_id" in ctx
        assert "name" in ctx
        assert "description" in ctx
        assert "active_releases" in ctx
        assert isinstance(ctx["active_releases"], list)

    def test_successful_load_context_values(self):
        """Loaded context contains the correct values from the API response."""
        product = {"Name": "My Project", "Description": "A test project"}
        releases = [
            {"ReleaseId": 1, "Name": "Sprint 1", "VersionNumber": "1.0.0", "Active": True},
            {"ReleaseId": 2, "Name": "Sprint 2", "VersionNumber": "1.0.1", "Active": False},
        ]
        mock_client = _make_mock_client(product=product, releases=releases)

        with (
            patch("mcp_server_spira.config._default_product_id", 55),
            patch("mcp_server_spira.features.context.get_client", return_value=mock_client),
        ):
            asyncio.run(load_active_product_context())

        ctx = get_active_product_context()
        assert ctx is not None
        assert ctx["product_id"] == 55
        assert ctx["name"] == "My Project"
        assert ctx["description"] == "A test project"
        # Only the active release should be included
        assert len(ctx["active_releases"]) == 1
        assert ctx["active_releases"][0]["ReleaseId"] == 1

    def test_inactive_releases_are_filtered_out(self):
        """Releases with Active=False are excluded from active_releases."""
        product = {"Name": "P", "Description": "D"}
        releases = [
            {"ReleaseId": 10, "Name": "Old", "VersionNumber": "0.9", "Active": False},
            {"ReleaseId": 11, "Name": "Current", "VersionNumber": "1.0", "Active": True},
        ]
        mock_client = _make_mock_client(product=product, releases=releases)

        with (
            patch("mcp_server_spira.config._default_product_id", 1),
            patch("mcp_server_spira.features.context.get_client", return_value=mock_client),
        ):
            asyncio.run(load_active_product_context())

        ctx = get_active_product_context()
        assert ctx is not None
        assert len(ctx["active_releases"]) == 1
        assert ctx["active_releases"][0]["ReleaseId"] == 11


class TestActiveProductResource:
    """Tests for active_product_resource() in server.py."""

    def setup_method(self):
        _reset_context()

    def test_none_context_returns_error_json(self):
        """When context is None, resource returns a JSON error object."""
        with patch("mcp_server_spira.features.context._active_product_context", None):
            result = active_product_resource()

        data = json.loads(result)
        assert "error" in data
        assert data["error"] == "No active product context available"

    def test_populated_context_returns_context_json(self):
        """When context is populated, resource returns it as JSON."""
        ctx = {
            "product_id": 55,
            "name": "My Project",
            "description": "A project",
            "active_releases": [{"ReleaseId": 1, "Name": "Sprint 1", "VersionNumber": "1.0"}],
        }
        with patch("mcp_server_spira.features.context._active_product_context", ctx):
            result = active_product_resource()

        data = json.loads(result)
        assert data["product_id"] == 55
        assert data["name"] == "My Project"
        assert data["description"] == "A project"
        assert isinstance(data["active_releases"], list)
        assert len(data["active_releases"]) == 1
