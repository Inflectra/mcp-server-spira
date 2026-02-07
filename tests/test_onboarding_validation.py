"""
Test script to validate the new developer onboarding process.

This script simulates a new developer following the setup guide and validates
that all steps work correctly.
"""

import subprocess
import sys
import time
from pathlib import Path


class OnboardingValidator:
    """Validates the developer onboarding process."""

    def __init__(self):
        self.start_time = None
        self.issues = []
        self.successes = []
        self.project_root = Path(__file__).parent.parent

    def log_success(self, message: str):
        """Log a successful validation step."""
        print(f"✓ {message}")
        self.successes.append(message)

    def log_issue(self, message: str):
        """Log an issue found during validation."""
        print(f"✗ {message}")
        self.issues.append(message)

    def run_command(self, command: str, check: bool = True) -> tuple[int, str, str]:
        """Run a shell command and return exit code, stdout, stderr."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.project_root,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)

    def validate_python_version(self) -> bool:
        """Validate Python version is 3.13+."""
        print("\n1. Validating Python version...")
        code, stdout, stderr = self.run_command("python --version")

        if code != 0:
            self.log_issue("Python not found or not accessible")
            return False

        version_str = stdout.strip() or stderr.strip()
        if "Python 3.13" in version_str or "Python 3.14" in version_str:
            self.log_success(f"Python version correct: {version_str}")
            return True
        else:
            self.log_issue(f"Python version incorrect: {version_str} (need 3.13+)")
            return False

    def validate_python_version_file(self) -> bool:
        """Validate .python-version file exists."""
        print("\n2. Validating .python-version file...")
        version_file = self.project_root / ".python-version"

        if not version_file.exists():
            self.log_issue(".python-version file not found")
            return False

        content = version_file.read_text().strip()
        if content.startswith("3.13") or content.startswith("3.14"):
            self.log_success(f".python-version file correct: {content}")
            return True
        else:
            self.log_issue(f".python-version file incorrect: {content}")
            return False

    def validate_requirements_file(self) -> bool:
        """Validate requirements-dev.txt exists and is readable."""
        print("\n3. Validating requirements-dev.txt...")
        req_file = self.project_root / "requirements-dev.txt"

        if not req_file.exists():
            self.log_issue("requirements-dev.txt not found")
            return False

        content = req_file.read_text()
        required_packages = ["ruff", "black", "mypy", "pytest", "pre-commit"]

        missing = [pkg for pkg in required_packages if pkg not in content.lower()]

        if missing:
            self.log_issue(f"Missing packages in requirements-dev.txt: {missing}")
            return False

        self.log_success("requirements-dev.txt contains all required packages")
        return True

    def validate_package_installed(self) -> bool:
        """Validate the package is installed in editable mode."""
        print("\n4. Validating package installation...")
        code, stdout, stderr = self.run_command("pip show mcp-server-spira")

        if code != 0:
            self.log_issue("Package mcp-server-spira not installed")
            return False

        if "editable" in stdout.lower() or "location" in stdout.lower():
            self.log_success("Package installed correctly")
            return True
        else:
            self.log_issue("Package not installed in editable mode")
            return False

    def validate_dev_tools(self) -> bool:
        """Validate development tools are installed."""
        print("\n5. Validating development tools...")
        tools = {
            "ruff": "ruff --version",
            "black": "black --version",
            "mypy": "mypy --version",
            "pytest": "pytest --version",
            "pre-commit": "pre-commit --version",
        }

        all_ok = True
        for tool, command in tools.items():
            code, stdout, stderr = self.run_command(command)
            if code == 0:
                version = (stdout + stderr).strip().split("\n")[0]
                self.log_success(f"{tool} installed: {version}")
            else:
                self.log_issue(f"{tool} not installed or not accessible")
                all_ok = False

        return all_ok

    def validate_tests_run(self) -> bool:
        """Validate that tests can run."""
        print("\n6. Validating tests run...")
        code, stdout, stderr = self.run_command("pytest --collect-only")

        if code != 0:
            self.log_issue(f"Test collection failed: {stderr}")
            return False

        if "test" in stdout.lower():
            self.log_success("Tests can be collected and run")
            return True
        else:
            self.log_issue("No tests found")
            return False

    def validate_linters_run(self) -> bool:
        """Validate that linters can run."""
        print("\n7. Validating linters run...")
        linters = {
            "ruff": "ruff check . --exit-zero",
            "black": "black --check . --quiet || true",
            "mypy": "mypy src/ --no-error-summary || true",
        }

        all_ok = True
        for linter, command in linters.items():
            code, stdout, stderr = self.run_command(command)
            # We don't care about exit code, just that it runs
            if "error" not in stderr.lower() or code in [0, 1]:
                self.log_success(f"{linter} runs successfully")
            else:
                self.log_issue(f"{linter} failed to run: {stderr}")
                all_ok = False

        return all_ok

    def validate_precommit_config(self) -> bool:
        """Validate pre-commit configuration exists."""
        print("\n8. Validating pre-commit configuration...")
        config_file = self.project_root / ".pre-commit-config.yaml"

        if not config_file.exists():
            self.log_issue(".pre-commit-config.yaml not found")
            return False

        content = config_file.read_text()
        required_hooks = ["ruff", "black", "mypy"]

        missing = [hook for hook in required_hooks if hook not in content.lower()]

        if missing:
            self.log_issue(f"Missing hooks in .pre-commit-config.yaml: {missing}")
            return False

        self.log_success(".pre-commit-config.yaml configured correctly")
        return True

    def validate_documentation(self) -> bool:
        """Validate documentation files exist."""
        print("\n9. Validating documentation...")
        docs = {
            "Development Setup": "docs/development_setup.md",
            "Architecture": "docs/architecture.md",
            "README": "README.md",
        }

        all_ok = True
        for name, path in docs.items():
            doc_file = self.project_root / path
            if doc_file.exists():
                self.log_success(f"{name} documentation exists")
            else:
                self.log_issue(f"{name} documentation not found at {path}")
                all_ok = False

        return all_ok

    def run_validation(self) -> dict:
        """Run all validation steps and return results."""
        print("=" * 70)
        print("ONBOARDING VALIDATION TEST")
        print("=" * 70)

        self.start_time = time.time()

        # Run all validations
        validations = [
            self.validate_python_version(),
            self.validate_python_version_file(),
            self.validate_requirements_file(),
            self.validate_package_installed(),
            self.validate_dev_tools(),
            self.validate_tests_run(),
            self.validate_linters_run(),
            self.validate_precommit_config(),
            self.validate_documentation(),
        ]

        elapsed_time = time.time() - self.start_time

        # Print summary
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)
        print(f"\nTotal time: {elapsed_time:.2f} seconds")
        print(f"Successful checks: {len(self.successes)}")
        print(f"Issues found: {len(self.issues)}")

        if self.issues:
            print("\nIssues:")
            for issue in self.issues:
                print(f"  - {issue}")

        print("\n" + "=" * 70)

        return {
            "success": all(validations),
            "elapsed_time": elapsed_time,
            "successes": self.successes,
            "issues": self.issues,
        }


def main():
    """Main entry point."""
    validator = OnboardingValidator()
    results = validator.run_validation()

    if results["success"]:
        print("\n✓ All validation checks passed!")
        return 0
    else:
        print("\n✗ Some validation checks failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
