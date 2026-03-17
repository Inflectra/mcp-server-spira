"""
Root pytest configuration.

Loads environment variables from .env before test collection,
so that skipif conditions referencing env vars are evaluated correctly.
"""

import os
from pathlib import Path


def pytest_configure(config):  # noqa: ARG001
    """Load .env at configure time so skipif decorators see the credentials."""
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"

    if env_file.exists():
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if key not in os.environ:
                        os.environ[key] = value
