# Feature: kiro-power-packaging
"""Unit tests for mcp_server_spira.config module."""

import os
from unittest.mock import patch

import pytest

from mcp_server_spira.config import (
    get_default_product_id,
    load_config,
    resolve_product_id,
)

pytestmark = pytest.mark.unit


class TestLoadConfig:
    """Tests for load_config() reading SPIRA_PROJECT_ID from the environment."""

    def test_valid_integer_env_var(self):
        """Valid integer string sets the default product ID."""
        with patch.dict(os.environ, {"SPIRA_PROJECT_ID": "42"}, clear=False):
            load_config()
            assert get_default_product_id() == 42

    def test_valid_negative_integer_env_var(self):
        """Negative integer strings are also valid."""
        with patch.dict(os.environ, {"SPIRA_PROJECT_ID": "-7"}, clear=False):
            load_config()
            assert get_default_product_id() == -7

    def test_non_integer_env_var(self):
        """Non-integer string leaves default as None."""
        with patch.dict(os.environ, {"SPIRA_PROJECT_ID": "abc"}, clear=False):
            load_config()
            assert get_default_product_id() is None

    def test_float_string_env_var(self):
        """Float string is not a valid integer, so default is None."""
        with patch.dict(os.environ, {"SPIRA_PROJECT_ID": "1.5"}, clear=False):
            load_config()
            assert get_default_product_id() is None

    def test_empty_string_env_var(self):
        """Empty string is not a valid integer, so default is None."""
        with patch.dict(os.environ, {"SPIRA_PROJECT_ID": ""}, clear=False):
            load_config()
            assert get_default_product_id() is None

    def test_absent_env_var(self):
        """When SPIRA_PROJECT_ID is not set, default is None."""
        env = {k: v for k, v in os.environ.items() if k != "SPIRA_PROJECT_ID"}
        with patch.dict(os.environ, env, clear=True):
            load_config()
            assert get_default_product_id() is None

    def test_non_integer_logs_warning(self, caplog):
        """Non-integer value triggers a warning log."""
        import logging

        with (
            patch.dict(os.environ, {"SPIRA_PROJECT_ID": "bad"}, clear=False),
            caplog.at_level(logging.WARNING),
        ):
            load_config()
        assert "bad" in caplog.text

    def test_load_config_resets_previous_value(self):
        """load_config() resets the default before reading env."""
        with patch.dict(os.environ, {"SPIRA_PROJECT_ID": "10"}, clear=False):
            load_config()
            assert get_default_product_id() == 10

        env = {k: v for k, v in os.environ.items() if k != "SPIRA_PROJECT_ID"}
        with patch.dict(os.environ, env, clear=True):
            load_config()
            assert get_default_product_id() is None


class TestResolveProductId:
    """Tests for resolve_product_id()."""

    def test_explicit_value_wins_over_default(self):
        """Explicit value is returned regardless of the default."""
        with patch("mcp_server_spira.config._default_product_id", 10):
            assert resolve_product_id(5) == 5

    def test_explicit_zero_wins_over_default(self):
        """0 is a valid explicit value and is not treated as falsy."""
        with patch("mcp_server_spira.config._default_product_id", 99):
            assert resolve_product_id(0) == 0

    def test_none_explicit_falls_back_to_default(self):
        """When explicit is None and a default is set, the default is returned."""
        with patch("mcp_server_spira.config._default_product_id", 10):
            assert resolve_product_id(None) == 10

    def test_none_explicit_with_no_default_returns_none(self):
        """When explicit is None and no default is set, None is returned."""
        with patch("mcp_server_spira.config._default_product_id", None):
            assert resolve_product_id(None) is None
