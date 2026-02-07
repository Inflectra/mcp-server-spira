"""
Test suite that mirrors pre-commit hooks for faster iteration.

This test class replicates all pre-commit hook checks so developers can
quickly identify and fix issues without waiting for pre-commit to run.

Run with: pytest tests/test_precommit_validation.py -v -m precommit
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

# Mark all tests in this module with 'precommit' marker
pytestmark = pytest.mark.precommit


class TestPreCommitValidation:
    """Test class that mirrors all pre-commit hook checks."""

    @pytest.fixture(scope="class")
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent

    @pytest.fixture(scope="class")
    def python_files(self, project_root: Path) -> list[Path]:
        """Get all Python files in the project (excluding venv and cache)."""
        exclude_dirs = {
            ".venv",
            ".mypy_cache",
            ".pytest_cache",
            ".ruff_cache",
            "__pycache__",
            ".git",
        }
        python_files = []

        for path in project_root.rglob("*.py"):
            # Skip if any parent directory is in exclude list
            if any(excluded in path.parts for excluded in exclude_dirs):
                continue
            python_files.append(path)

        return python_files

    @pytest.fixture(scope="class")
    def yaml_files(self, project_root: Path) -> list[Path]:
        """Get all YAML files in the project."""
        exclude_dirs = {".venv", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".git"}
        yaml_files = []

        for pattern in ["*.yaml", "*.yml"]:
            for path in project_root.rglob(pattern):
                if any(excluded in path.parts for excluded in exclude_dirs):
                    continue
                yaml_files.append(path)

        return yaml_files

    @pytest.fixture(scope="class")
    def json_files(self, project_root: Path) -> list[Path]:
        """Get all JSON files in the project."""
        exclude_dirs = {".venv", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".git"}
        json_files = []

        for path in project_root.rglob("*.json"):
            if any(excluded in path.parts for excluded in exclude_dirs):
                continue
            json_files.append(path)

        return json_files

    # =========================================================================
    # Standard Pre-commit Hooks
    # =========================================================================

    def test_no_trailing_whitespace(self, python_files: list[Path]) -> None:
        """Check for trailing whitespace in Python files."""
        files_with_trailing_ws = []

        for file_path in python_files:
            with open(file_path, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    # Check if line has trailing whitespace (but not empty lines)
                    if line.rstrip("\n\r") != line.rstrip():
                        files_with_trailing_ws.append((file_path, line_num))

        if files_with_trailing_ws:
            error_msg = "Files with trailing whitespace:\n"
            for file_path, line_num in files_with_trailing_ws:
                error_msg += f"  {file_path}:{line_num}\n"
            pytest.fail(error_msg)

    def test_files_end_with_newline(self, python_files: list[Path]) -> None:
        """Check that all Python files end with a newline."""
        files_without_newline = []

        for file_path in python_files:
            with open(file_path, "rb") as f:
                content = f.read()
                if content and not content.endswith(b"\n"):
                    files_without_newline.append(file_path)

        if files_without_newline:
            error_msg = "Files not ending with newline:\n"
            for file_path in files_without_newline:
                error_msg += f"  {file_path}\n"
            pytest.fail(error_msg)

    def test_yaml_files_valid(self, yaml_files: list[Path]) -> None:
        """Check that all YAML files are valid."""
        invalid_yaml_files = []

        for file_path in yaml_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    yaml.safe_load(f)
            except yaml.YAMLError as e:
                invalid_yaml_files.append((file_path, str(e)))

        if invalid_yaml_files:
            error_msg = "Invalid YAML files:\n"
            for file_path, error in invalid_yaml_files:
                error_msg += f"  {file_path}: {error}\n"
            pytest.fail(error_msg)

    def test_json_files_valid(self, json_files: list[Path]) -> None:
        """Check that all JSON files are valid."""
        invalid_json_files = []

        for file_path in json_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                invalid_json_files.append((file_path, str(e)))

        if invalid_json_files:
            error_msg = "Invalid JSON files:\n"
            for file_path, error in invalid_json_files:
                error_msg += f"  {file_path}: {error}\n"
            pytest.fail(error_msg)

    def test_no_large_files(self, project_root: Path) -> None:
        """Check for files larger than 1MB (excluding known large files)."""
        max_size_kb = 1000
        exclude_dirs = {".venv", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".git", "htmlcov"}
        exclude_files = {"SpiraRestAPI-v7.0-OpenAPI.json", "uv.lock"}  # Known large files

        large_files = []

        for path in project_root.rglob("*"):
            if not path.is_file():
                continue
            if any(excluded in path.parts for excluded in exclude_dirs):
                continue
            if path.name in exclude_files:
                continue

            size_kb = path.stat().st_size / 1024
            if size_kb > max_size_kb:
                large_files.append((path, size_kb))

        if large_files:
            error_msg = f"Files larger than {max_size_kb}KB:\n"
            for file_path, size_kb in large_files:
                error_msg += f"  {file_path}: {size_kb:.1f}KB\n"
            pytest.fail(error_msg)

    def test_no_merge_conflicts(self, python_files: list[Path]) -> None:
        """Check for merge conflict markers in Python files."""
        conflict_markers = ["<<<<<<<", "=======", ">>>>>>>"]
        files_with_conflicts = []

        for file_path in python_files:
            with open(file_path, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    stripped = line.strip()
                    # Skip lines that are just comment dividers (e.g., "# ========")
                    if stripped.startswith("#") and all(c in "# =" for c in stripped):
                        continue
                    # Skip string literals containing conflict markers (e.g., in test code)
                    if any(quote in line for quote in ['"', "'"]):
                        continue
                    if any(marker in line for marker in conflict_markers):
                        files_with_conflicts.append((file_path, line_num, line.strip()))

        if files_with_conflicts:
            error_msg = "Files with merge conflict markers:\n"
            for file_path, line_num, line in files_with_conflicts:
                error_msg += f"  {file_path}:{line_num}: {line}\n"
            pytest.fail(error_msg)

    # =========================================================================
    # Ruff Linting
    # =========================================================================

    def test_ruff_check(self, project_root: Path) -> None:
        """Run ruff linter on the codebase."""
        try:
            result = subprocess.run(
                ["ruff", "check", ".", "--output-format=concise"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                error_msg = "Ruff linting failed:\n"
                error_msg += result.stdout
                if result.stderr:
                    error_msg += "\nStderr:\n" + result.stderr
                pytest.fail(error_msg)
        except FileNotFoundError:
            pytest.skip("Ruff not installed")
        except subprocess.TimeoutExpired:
            pytest.fail("Ruff check timed out after 30 seconds")

    def test_ruff_format_check(self, project_root: Path) -> None:
        """Check if code is formatted according to ruff."""
        try:
            result = subprocess.run(
                ["ruff", "format", "--check", "."],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                error_msg = "Ruff formatting check failed:\n"
                error_msg += result.stdout
                if result.stderr:
                    error_msg += "\nStderr:\n" + result.stderr
                error_msg += "\n\nRun 'ruff format .' to fix formatting issues."
                pytest.fail(error_msg)
        except FileNotFoundError:
            pytest.skip("Ruff not installed")
        except subprocess.TimeoutExpired:
            pytest.fail("Ruff format check timed out after 30 seconds")

    # =========================================================================
    # Mypy Type Checking
    # =========================================================================

    def test_mypy_type_check(self, project_root: Path) -> None:
        """Run mypy type checker on the codebase."""
        try:
            result = subprocess.run(
                ["mypy", "src/", "tests/"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                error_msg = "Mypy type checking failed:\n"
                error_msg += result.stdout
                if result.stderr:
                    error_msg += "\nStderr:\n" + result.stderr
                pytest.fail(error_msg)
        except FileNotFoundError:
            pytest.skip("Mypy not installed")
        except subprocess.TimeoutExpired:
            pytest.fail("Mypy check timed out after 60 seconds")


# =========================================================================
# Convenience Functions
# =========================================================================


def run_precommit_tests() -> int:
    """
    Convenience function to run all pre-commit validation tests.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    result: Any = pytest.main(
        [
            __file__,
            "-v",
            "-m",
            "precommit",
            "--tb=short",
        ]
    )
    return int(result)


if __name__ == "__main__":
    sys.exit(run_precommit_tests())
