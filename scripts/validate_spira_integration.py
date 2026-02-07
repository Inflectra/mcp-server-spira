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
"""

import argparse
import ast
import configparser
import sys
from pathlib import Path


class TestClassDiscoverer(ast.NodeVisitor):
    """AST visitor to discover test classes in Python files."""

    def __init__(self):
        self.test_classes: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        """Visit class definitions and collect test classes."""
        # Check if class name starts with Test
        if node.name.startswith("Test"):
            self.test_classes.append(node.name)
        self.generic_visit(node)


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

    # Use RawConfigParser to preserve case
    config = configparser.RawConfigParser()
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
    try:
        config.read(config_path)
    except Exception as e:
        issues.append(f"Failed to parse spira.cfg: {e}")
        return issues

    # Check required sections
    if "credentials" not in config:
        issues.append("Missing [credentials] section")
    else:
        required_creds = ["url", "username", "api_key", "product_id"]
        for cred in required_creds:
            if cred not in config["credentials"]:
                issues.append(f"Missing credential: {cred}")

    if "test_cases" not in config:
        issues.append("Missing [test_cases] section")

    return issues


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
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    test_dir = project_root / "tests"
    config_path = project_root / args.config

    print("🔍 Spira pytest Integration Validation")
    print("=" * 60)

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

    # Discover test classes
    print(f"\n🔎 Discovering test classes in {test_dir}...")
    test_classes_by_file = discover_test_classes(test_dir)

    all_test_classes: set[str] = set()
    for file_path, classes in sorted(test_classes_by_file.items()):
        all_test_classes.update(classes)
        print(f"   {file_path}: {len(classes)} classes")

    print(f"\n📊 Total test classes found: {len(all_test_classes)}")

    # Load Spira mappings
    print(f"\n📖 Loading Spira test case mappings from {config_path}...")
    spira_mappings = load_spira_config(config_path)
    print(f"   Found {len(spira_mappings)} mapped test classes")

    # Calculate coverage
    mapped_classes = set(spira_mappings.keys())
    unmapped_classes = all_test_classes - mapped_classes
    extra_mappings = mapped_classes - all_test_classes

    coverage_percent = (
        (len(mapped_classes) / len(all_test_classes) * 100) if all_test_classes else 0
    )

    # Report results
    print("\n" + "=" * 60)
    print("📈 COVERAGE REPORT")
    print("=" * 60)
    print(f"Total test classes:     {len(all_test_classes)}")
    print(f"Mapped to Spira:        {len(mapped_classes)}")
    print(f"Not mapped:             {len(unmapped_classes)}")
    print(f"Coverage:               {coverage_percent:.1f}%")

    if unmapped_classes:
        print("\n⚠️  Test classes NOT mapped to Spira:")
        for class_name in sorted(unmapped_classes):
            # Find which file contains this class
            for file_path, classes in test_classes_by_file.items():
                if class_name in classes:
                    print(f"   • {class_name} ({file_path})")
                    break

        print("\n💡 To map these classes:")
        print("   1. Create test cases in Spira for each class")
        print("   2. Add mappings to spira.cfg [test_cases] section")
        print("   3. Format: ClassName = TC_ID (without TC: prefix)")

    if extra_mappings:
        print("\n⚠️  Mappings in spira.cfg for non-existent classes:")
        for class_name in sorted(extra_mappings):
            tc_id = spira_mappings[class_name]
            print(f"   • {class_name} = {tc_id}")
        print("\n💡 These mappings can be removed from spira.cfg")

    if mapped_classes:
        print("\n✅ Mapped test classes:")
        for class_name in sorted(mapped_classes):
            tc_id = spira_mappings[class_name]
            print(f"   • {class_name} → TC:{tc_id}")

    # Exit status
    print("\n" + "=" * 60)
    if coverage_percent == 100 and not config_issues:
        print("✅ SUCCESS: 100% coverage, all tests mapped to Spira!")
        sys.exit(0)
    elif args.strict:
        print(f"❌ FAILED: {coverage_percent:.1f}% coverage (--strict mode)")
        sys.exit(1)
    else:
        print(f"⚠️  WARNING: {coverage_percent:.1f}% coverage")
        print("   Run with --strict to enforce 100% coverage")
        sys.exit(0)


if __name__ == "__main__":
    main()
