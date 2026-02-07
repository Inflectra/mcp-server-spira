"""
Quick style check tests for common issues.

Run with: pytest tests/test_style_issues.py -v --no-cov

Note: This test suite uses Ruff for both linting and formatting.
Ruff is a drop-in replacement for Black, flake8, isort, and more.
"""

import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.precommit


class TestQuickStyleChecks:
    """Quick style checks that can be auto-fixed."""

    @pytest.fixture(scope="class")
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent

    def test_ruff_format(self, project_root: Path) -> None:
        """Check ruff formatting (can be auto-fixed with 'ruff format .')."""
        result = subprocess.run(
            ["ruff", "format", "--check", "."],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            pytest.fail(
                f"Ruff formatting issues found:\n{result.stdout}\n\nFix with: ruff format ."
            )

    def test_ruff_lint(self, project_root: Path) -> None:
        """Check ruff linting (many issues can be auto-fixed with 'ruff check . --fix')."""
        result = subprocess.run(
            ["ruff", "check", ".", "--output-format=concise"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            pytest.fail(
                f"Ruff linting issues found:\n{result.stdout}\n\nFix with: ruff check . --fix"
            )
