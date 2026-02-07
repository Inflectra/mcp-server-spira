"""
Pytest configuration for integration tests.

This file automatically loads environment variables from .env file
before running integration tests.
"""

import os
from pathlib import Path


def pytest_configure(config):
    """
    Load environment variables from .env file before running tests.

    This allows integration tests to run directly with pytest without
    needing a shell script to load environment variables.
    """
    # Find the .env file in the project root
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / ".env"

    if env_file.exists():
        # Load environment variables from .env
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value

        print(f"\n✅ Loaded environment variables from {env_file}")
        print(f"   Base URL: {os.environ.get('INFLECTRA_SPIRA_BASE_URL', 'NOT SET')}")
        print(f"   Username: {os.environ.get('INFLECTRA_SPIRA_USERNAME', 'NOT SET')}")
    else:
        print(f"\n⚠️  Warning: .env file not found at {env_file}")
        print("   Integration tests will be skipped if credentials are not set.")
