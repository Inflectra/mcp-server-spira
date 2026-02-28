# Feature: kiro-power-packaging
"""Property-based tests for mcp_server_spira.config module."""

import os
from unittest.mock import patch

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from mcp_server_spira.config import (
    get_default_product_id,
    load_config,
    resolve_product_id,
)

pytestmark = pytest.mark.unit

# Strategy: strings that cannot be parsed as int (no surrogates, no null bytes)
_non_integer_text = st.text(
    alphabet=st.characters(
        blacklist_categories=["Cs"],
        blacklist_characters="\x00",
    )
).filter(lambda s: not s.lstrip("-").isdigit())


# Feature: kiro-power-packaging, Property 2: Config loads valid integer SPIRA_PROJECT_ID
@given(st.integers())
@settings(max_examples=100)
def test_load_config_valid_integer(n):
    """For any valid decimal integer string, load_config() stores the int.

    Validates: Requirements 4.1
    """
    with patch.dict(os.environ, {"SPIRA_PROJECT_ID": str(n)}, clear=False):
        load_config()
        assert get_default_product_id() == n


# Feature: kiro-power-packaging, Property 3: Config ignores non-integer SPIRA_PROJECT_ID
@given(_non_integer_text)
@settings(max_examples=100)
def test_load_config_non_integer(s):
    """For any non-integer string, load_config() leaves default as None.

    Validates: Requirements 4.5
    """
    with patch.dict(os.environ, {"SPIRA_PROJECT_ID": s}, clear=False):
        load_config()
        assert get_default_product_id() is None


# Feature: kiro-power-packaging, Property 4: resolve_product_id precedence — explicit wins
@given(st.integers(), st.integers() | st.none())
@settings(max_examples=100)
def test_resolve_product_id_explicit_wins(explicit, default):
    """When explicit is not None, it is returned regardless of the default.

    Validates: Requirements 4.2, 4.3
    """
    with patch("mcp_server_spira.config._default_product_id", default):
        assert resolve_product_id(explicit) == explicit


# Feature: kiro-power-packaging, Property 4: resolve_product_id precedence — fallback
@given(st.integers() | st.none())
@settings(max_examples=100)
def test_resolve_product_id_falls_back_to_default(default):
    """When explicit is None, resolve_product_id returns the default.

    Validates: Requirements 4.2, 4.3
    """
    with patch("mcp_server_spira.config._default_product_id", default):
        assert resolve_product_id(None) == default
