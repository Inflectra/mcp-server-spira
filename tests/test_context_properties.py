# Feature: kiro-power-packaging
"""Property-based tests for mcp_server_spira.features.context module."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

import mcp_server_spira.features.context as context_module
from mcp_server_spira.features.context import (
    get_active_product_context,
    load_active_product_context,
)
from mcp_server_spira.server import active_product_resource

pytestmark = pytest.mark.unit

# Strategy: a single release dict with required fields
_release_strategy = st.fixed_dictionaries(
    {
        "ReleaseId": st.integers(),
        "Name": st.text(max_size=50),
        "VersionNumber": st.text(max_size=20),
        "Active": st.booleans(),
    }
)


def _reset_context():
    context_module._active_product_context = None


# Feature: kiro-power-packaging, Property 5: Active product context fetches both endpoints
@given(st.integers(min_value=1, max_value=100_000))
@settings(max_examples=50)
def test_context_fetches_both_endpoints(product_id):
    """For any valid product ID, load_active_product_context() calls both
    GET projects/{id} and POST projects/{id}/releases/search exactly once.

    Validates: Requirements 5.1, 5.2
    """
    _reset_context()
    mock_client = MagicMock()
    mock_client.make_spira_api_get_request.return_value = {"Name": "P", "Description": "D"}
    mock_client.make_spira_api_post_request.return_value = []

    with (
        patch("mcp_server_spira.config._default_product_id", product_id),
        patch("mcp_server_spira.features.context.get_client", return_value=mock_client),
    ):
        asyncio.run(load_active_product_context())

    mock_client.make_spira_api_get_request.assert_called_once_with(f"projects/{product_id}")
    mock_client.make_spira_api_post_request.assert_called_once_with(
        f"projects/{product_id}/releases/search", {}
    )


# Feature: kiro-power-packaging, Property 6: Active product context contains required fields
@given(
    st.integers(min_value=1, max_value=100_000),
    st.text(max_size=100),
    st.text(max_size=200),
    st.lists(_release_strategy, max_size=10),
)
@settings(max_examples=50)
def test_context_has_required_fields(product_id, name, description, releases):
    """For any successful API response, the context dict contains all four
    required keys and active_releases is a list.

    Validates: Requirements 5.3, 5.6
    """
    _reset_context()
    mock_client = MagicMock()
    mock_client.make_spira_api_get_request.return_value = {
        "Name": name,
        "Description": description,
    }
    mock_client.make_spira_api_post_request.return_value = releases

    with (
        patch("mcp_server_spira.config._default_product_id", product_id),
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
    # active_releases must only contain releases where Active=True
    active_ids = {r["ReleaseId"] for r in releases if r.get("Active", True)}
    result_ids = {r["ReleaseId"] for r in ctx["active_releases"]}
    assert result_ids == active_ids


# Feature: kiro-power-packaging, Property 7: Resource reads use cached data
@given(
    st.integers(min_value=1, max_value=100_000),
    st.integers(min_value=1, max_value=20),
)
@settings(max_examples=50)
def test_resource_reads_use_cached_data(product_id, num_reads):
    """After a successful load, any number of active_product_resource() calls
    must not trigger additional API calls — all reads use the cached value.

    Validates: Requirements 5.7
    """
    _reset_context()
    mock_client = MagicMock()
    mock_client.make_spira_api_get_request.return_value = {"Name": "P", "Description": "D"}
    mock_client.make_spira_api_post_request.return_value = []

    with (
        patch("mcp_server_spira.config._default_product_id", product_id),
        patch("mcp_server_spira.features.context.get_client", return_value=mock_client),
    ):
        asyncio.run(load_active_product_context())

    # Capture call counts after load
    get_calls_after_load = mock_client.make_spira_api_get_request.call_count
    post_calls_after_load = mock_client.make_spira_api_post_request.call_count

    # Read the resource multiple times
    for _ in range(num_reads):
        active_product_resource()

    # No additional API calls should have been made
    assert mock_client.make_spira_api_get_request.call_count == get_calls_after_load
    assert mock_client.make_spira_api_post_request.call_count == post_calls_after_load
