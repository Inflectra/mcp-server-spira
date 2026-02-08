#!/usr/bin/env python3
"""
Validate Spira pytest integration configuration.

This script:
1. Discovers all pytest test classes in the project
2. Checks which ones have Spira test case mappings in spira.cfg
3. Reports coverage and missing mappings
4. Validates spira.cfg format

Usage:
    python scripts/validate_spira_integration.py
    python scripts/validate_spira_integration.py --strict  # Exit 1 if not 100%
    python scripts/validate_spira_integration.py --mode module  # Check modules
    python scripts/validate_spira_integration.py --mode marker  # Check markers
    python scripts/validate_spira_integration.py --mode all  # Check all
"""

import argparse
import ast
import configparser
import sys
import tomllib
from pathlib import Path


class TestClassDiscoverer(ast.NodeVisitor):
    """AST visitor to discover test classes and markers in Python files."""

    def __init__(self):
        self.test_classes: list[str] = []
        self.markers: set[str] = set()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        """Visit class definitions and collect test classes and their markers."""
        # Check if class name starts with Test
        if node.name.startswith("Test"):
            self.test_classes.append(node.name)

            # Extract markers from class decorators
            for decorator in node.decorator_list:
                marker_name = self._extract_marker_name(decorator)
                if marker_name:
                    self.markers.add(marker_name)

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        """Visit function definitions to find markers on test methods."""
        # Extract markers from function decorators
        for decorator in node.decorator_list:
            marker_name = self._extract_marker_name(decorator)
            if marker_name:
                self.markers.add(marker_name)

        self.generic_visit(node)

    def _extract_marker_name(self, decorator: ast.expr) -> str | None:
        """Extract marker name from a decorator node."""
        # Handle @pytest.mark.xxx (Attribute node)
        if isinstance(decorator, ast.Attribute) and (
            isinstance(decorator.value, ast.Attribute)
            and isinstance(decorator.value.value, ast.Name)
            and decorator.value.value.id == "pytest"
            and decorator.value.attr == "mark"
        ):
            marker_name = decorator.attr
            # Skip built-in markers
            if marker_name not in ["skipif", "parametrize", "skip", "xfail", "usefixtures"]:
                return marker_name

        # Handle @pytest.mark.xxx(...) (Call node)
        elif (
            isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Attribute)
            and (
                isinstance(decorator.func.value, ast.Attribute)
                and isinstance(decorator.func.value.value, ast.Name)
                and decorator.func.value.value.id == "pytest"
                and decorator.func.value.attr == "mark"
            )
        ):
            marker_name = decorator.func.attr
            # Skip built-in markers
            if marker_name not in ["skipif", "parametrize", "skip", "xfail", "usefixtures"]:
                return marker_name

        return None


def discover_test_classes(test_dir: Path) -> dict[str, list[str]]:
    """
    Discover all test classes in the test directory.

    Returns:
        Dict mapping file paths to list of test class names
    """
    test_classes_by_file = {}

    for test_file in test_dir.rglob("test_*.py"):
        try:
            content = test_file.read_text()
            tree = ast.parse(content)
            discoverer = TestClassDiscoverer()
            discoverer.visit(tree)

            if discoverer.test_classes:
                relative_path = test_file.relative_to(test_dir.parent)
                test_classes_by_file[str(relative_path)] = discoverer.test_classes
        except Exception as e:
            print(f"⚠️  Error parsing {test_file}: {e}", file=sys.stderr)

    return test_classes_by_file


def discover_test_modules(test_dir: Path) -> list[str]:
    """
    Discover all test modules in the test directory.

    Returns:
        List of test module names as full Python paths (e.g., tests.features.mywork.test_mytasks)
    """
    modules = []
    project_root = test_dir.parent

    for test_file in test_dir.rglob("test_*.py"):
        # Get relative path from project root
        relative_path = test_file.relative_to(project_root)
        # Convert path to Python module notation (replace / with . and remove .py)
        module_path = str(relative_path.with_suffix("")).replace("/", ".")
        modules.append(module_path)

    return sorted(modules)


def discover_markers(test_dir: Path) -> set[str]:
    """
    Discover all pytest markers from pyproject.toml.

    Returns:
        Set of marker names defined in pyproject.toml
    """
    project_root = test_dir.parent
    pyproject_path = project_root / "pyproject.toml"

    if not pyproject_path.exists():
        print("⚠️  pyproject.toml not found, cannot discover markers", file=sys.stderr)
        return set()

    try:
        with open(pyproject_path, "rb") as f:
            pyproject = tomllib.load(f)

        # Extract markers from [tool.pytest.ini_options]
        markers_list = (
            pyproject.get("tool", {}).get("pytest", {}).get("ini_options", {}).get("markers", [])
        )

        # Parse marker definitions (format: "name: description")
        markers = set()
        for marker_def in markers_list:
            if isinstance(marker_def, str) and ":" in marker_def:
                marker_name = marker_def.split(":")[0].strip()
                markers.add(marker_name)

        return markers
    except Exception as e:
        print(f"⚠️  Error reading pyproject.toml: {e}", file=sys.stderr)
        return set()


def load_spira_config(config_path: Path) -> dict[str, str]:
    """
    Load Spira configuration and extract test case mappings.

    Returns:
        Dict mapping test class names to test case IDs
    """
    if not config_path.exists():
        return {}

    # Load environment variables from .env.spira if it exists
    env_spira_path = config_path.parent / ".env.spira"
    if env_spira_path.exists():
        import os

        with open(env_spira_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

    # Use RawConfigParser with case-sensitive keys
    config = configparser.RawConfigParser()
    # Preserve case in option names
    config.optionxform = str  # type: ignore
    config.read(config_path)

    if "test_cases" not in config:
        return {}

    # Filter out empty values and comments
    return {
        key: value
        for key, value in config.items("test_cases")
        if value.strip() and not key.startswith("#")
    }


def validate_config_format(config_path: Path) -> list[str]:
    """
    Validate spira.cfg format and return list of issues.

    Returns:
        List of validation error messages
    """
    issues = []

    if not config_path.exists():
        issues.append("spira.cfg not found")
        return issues

    # Check for .env.spira
    env_spira_path = config_path.parent / ".env.spira"
    if not env_spira_path.exists():
        issues.append(".env.spira not found (copy from .env.spira.template)")

    config = configparser.RawConfigParser()
    # Preserve case in option names
    config.optionxform = str  # type: ignore
    try:
        config.read(config_path)
    except Exception as e:
        issues.append(f"Failed to parse spira.cfg: {e}")
        return issues

    # Check for [spira] section (optional but recommended)
    if "spira" not in config:
        issues.append("Missing [spira] section (optional but recommended)")

    if "test_cases" not in config:
        issues.append("Missing [test_cases] section")

    return issues


def validate_mode(mode: str, test_dir: Path, spira_mappings: dict[str, str], strict: bool) -> None:
    """Validate mappings for a specific mode (class, module, or marker)."""
    if mode == "class":
        validate_class_mappings(test_dir, spira_mappings, strict)
    elif mode == "module":
        validate_module_mappings(test_dir, spira_mappings, strict)
    elif mode == "marker":
        validate_marker_mappings(test_dir, spira_mappings, strict)


def validate_class_mappings(test_dir: Path, spira_mappings: dict[str, str], strict: bool) -> None:
    """Validate class-level mappings."""
    print("\n🔎 Discovering test classes...")
    test_classes_by_file = discover_test_classes(test_dir)

    all_test_classes: set[str] = set()
    for file_path, classes in sorted(test_classes_by_file.items()):
        all_test_classes.update(classes)
        print(f"   {file_path}: {len(classes)} classes")

    print(f"\n📊 Total test classes found: {len(all_test_classes)}")

    # Calculate coverage
    mapped_classes = set(spira_mappings.keys())
    unmapped_classes = all_test_classes - mapped_classes
    extra_mappings = mapped_classes - all_test_classes

    coverage_percent = (
        (len(mapped_classes & all_test_classes) / len(all_test_classes) * 100)
        if all_test_classes
        else 0
    )

    print_coverage_report(
        "CLASS",
        len(all_test_classes),
        len(mapped_classes & all_test_classes),
        len(unmapped_classes),
        len(extra_mappings),
        coverage_percent,
        unmapped_classes,
        extra_mappings,
        mapped_classes & all_test_classes,
        spira_mappings,
        test_classes_by_file,
        strict,
    )


def validate_module_mappings(test_dir: Path, spira_mappings: dict[str, str], strict: bool) -> None:
    """Validate module-level mappings."""
    print("\n🔎 Discovering test modules...")
    all_modules = discover_test_modules(test_dir)

    for module in all_modules:
        print(f"   {module}")

    print(f"\n📊 Total test modules found: {len(all_modules)}")

    # Calculate coverage
    all_modules_set = set(all_modules)
    mapped_modules = set(spira_mappings.keys())
    unmapped_modules = all_modules_set - mapped_modules
    extra_mappings = mapped_modules - all_modules_set

    coverage_percent = (
        (len(mapped_modules & all_modules_set) / len(all_modules_set) * 100)
        if all_modules_set
        else 0
    )

    print_coverage_report(
        "MODULE",
        len(all_modules_set),
        len(mapped_modules & all_modules_set),
        len(unmapped_modules),
        len(extra_mappings),
        coverage_percent,
        unmapped_modules,
        extra_mappings,
        mapped_modules & all_modules_set,
        spira_mappings,
        None,
        strict,
    )


def validate_marker_mappings(test_dir: Path, spira_mappings: dict[str, str], strict: bool) -> None:
    """Validate marker-level mappings."""
    print("\n🔎 Reading pytest markers from pyproject.toml...")
    all_markers = discover_markers(test_dir)

    if not all_markers:
        print("⚠️  No markers found in pyproject.toml")
        print("   Markers should be defined in [tool.pytest.ini_options]")
        return

    for marker in sorted(all_markers):
        print(f"   @pytest.mark.{marker}")

    print(f"\n📊 Total markers defined: {len(all_markers)}")

    # Calculate coverage
    mapped_markers = set(spira_mappings.keys())
    unmapped_markers = all_markers - mapped_markers
    extra_mappings = mapped_markers - all_markers

    coverage_percent = (
        (len(mapped_markers & all_markers) / len(all_markers) * 100) if all_markers else 0
    )

    print_coverage_report(
        "MARKER",
        len(all_markers),
        len(mapped_markers & all_markers),
        len(unmapped_markers),
        len(extra_mappings),
        coverage_percent,
        unmapped_markers,
        extra_mappings,
        mapped_markers & all_markers,
        spira_mappings,
        None,
        strict,
    )


def print_coverage_report(
    mode: str,
    total: int,
    mapped: int,
    unmapped_count: int,
    extra_count: int,
    coverage_percent: float,
    unmapped: set[str],
    extra: set[str],
    mapped_items: set[str],
    spira_mappings: dict[str, str],
    test_classes_by_file: dict[str, list[str]] | None,
    strict: bool,
) -> None:
    """Print coverage report for any mode."""
    # Report results
    print("\n" + "=" * 60)
    print(f"📈 {mode} COVERAGE REPORT")
    print("=" * 60)
    print(f"Total {mode.lower()}s:     {total}")
    print(f"Mapped to Spira:        {mapped}")
    print(f"Not mapped:             {unmapped_count}")
    print(f"Extra mappings:         {extra_count}")
    print(f"Coverage:               {coverage_percent:.1f}%")

    if unmapped:
        print(f"\n⚠️  {len(unmapped)} {mode.lower()}s NOT mapped to Spira:")
        for item in sorted(unmapped):
            # For classes, show which file contains them
            if test_classes_by_file:
                for file_path, classes in test_classes_by_file.items():
                    if item in classes:
                        print(f"   • {item} ({file_path})")
                        break
            else:
                print(f"   • {item}")

        print(f"\n💡 To map these {mode.lower()}s:")
        print("   1. Create test cases in Spira for each item")
        print("   2. Add mappings to spira.cfg [test_cases] section")
        print(f"   3. Format: {mode}Name = TC_ID (without TC: prefix)")
        if mode == "CLASS":
            print("   4. Example: TestGetMyTasksImpl = 4865")
        elif mode == "MODULE":
            print("   4. Example: test_mytasks = 5010")
        elif mode == "MARKER":
            print("   4. Example: unit = 5000")

    if extra:
        print(f"\n⚠️  {len(extra)} mappings in spira.cfg for non-existent {mode.lower()}s:")
        for item in sorted(extra):
            tc_id = spira_mappings[item]
            print(f"   • {item} = {tc_id}")
        print(f"\n💡 These mappings should be removed or the {mode.lower()} names corrected")

    if mapped_items:
        print(f"\n✅ {len(mapped_items)} correctly mapped {mode.lower()}s:")
        for item in sorted(mapped_items):
            tc_id = spira_mappings[item]
            print(f"   • {item} → TC:{tc_id}")

    # Exit status
    print("\n" + "=" * 60)
    if coverage_percent == 100:
        print(f"✅ SUCCESS: 100% {mode.lower()} coverage!")
        if not strict:
            sys.exit(0)
    elif strict:
        print(f"❌ FAILED: {coverage_percent:.1f}% {mode.lower()} coverage (--strict mode)")
        sys.exit(1)
    else:
        print(f"⚠️  WARNING: {coverage_percent:.1f}% {mode.lower()} coverage")
        print("   Run with --strict to enforce 100% coverage")


def main():
    parser = argparse.ArgumentParser(description="Validate Spira pytest integration configuration")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error if not 100%% coverage",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("spira.cfg"),
        help="Path to spira.cfg file (default: spira.cfg)",
    )
    parser.add_argument(
        "--mode",
        choices=["class", "module", "marker", "all"],
        default="class",
        help="Mapping mode to validate: class (default), module, marker, or all",
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    test_dir = project_root / "tests"
    config_path = project_root / args.config

    print("🔍 Spira pytest Integration Validation")
    print("=" * 60)
    print(f"Mode: {args.mode.upper()}")

    # Validate config format
    print("\n📋 Validating spira.cfg format...")
    config_issues = validate_config_format(config_path)
    if config_issues:
        print("❌ Configuration issues found:")
        for issue in config_issues:
            print(f"   • {issue}")
        if args.strict:
            sys.exit(1)
    else:
        print("✅ Configuration format is valid")

    # Load Spira mappings
    print(f"\n📖 Loading Spira test case mappings from {config_path}...")
    spira_mappings = load_spira_config(config_path)

    if args.mode == "all":
        # Run all three modes
        for mode in ["class", "module", "marker"]:
            print("\n" + "=" * 60)
            validate_mode(mode, test_dir, spira_mappings, args.strict)
    else:
        validate_mode(args.mode, test_dir, spira_mappings, args.strict)


if __name__ == "__main__":
    main()
