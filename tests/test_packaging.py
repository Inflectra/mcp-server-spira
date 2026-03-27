# Feature: kiro-power-packaging
"""Packaging integrity tests — verify repo files are correctly configured."""

from pathlib import Path

import pytest

# Resolve the repo root relative to this test file (tests/ → repo root)
REPO_ROOT = Path(__file__).parent.parent

# POWER.md lives in the power-spira subdirectory
POWER_MD_PATH = REPO_ROOT / "power-spira" / "POWER.md"

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter delimited by '---' lines.

    Returns an empty dict if no frontmatter block is found.
    """
    import yaml

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}
    yaml_block = "\n".join(lines[1:end])
    return yaml.safe_load(yaml_block) or {}


def _load_toml(path: Path) -> dict:
    """Load a TOML file using tomllib (stdlib, Python 3.11+)."""
    import tomllib

    with path.open("rb") as fh:
        return tomllib.load(fh)


# ---------------------------------------------------------------------------
# pyproject.toml tests
# ---------------------------------------------------------------------------


class TestPyprojectScripts:
    """Verify [project.scripts] in pyproject.toml."""

    def test_project_scripts_section_exists(self):
        """pyproject.toml must have a [project.scripts] table."""
        data = _load_toml(REPO_ROOT / "pyproject.toml")
        assert "scripts" in data.get("project", {}), (
            "[project.scripts] section is missing from pyproject.toml"
        )

    def test_mcp_server_spira_entry_point_present(self):
        """[project.scripts] must declare the mcp-server-spira entry point."""
        data = _load_toml(REPO_ROOT / "pyproject.toml")
        scripts = data.get("project", {}).get("scripts", {})
        assert "mcp-server-spira" in scripts, (
            "mcp-server-spira entry point is missing from [project.scripts]"
        )

    def test_mcp_server_spira_entry_point_value(self):
        """The mcp-server-spira entry point must point to mcp_server_spira.server:main."""
        data = _load_toml(REPO_ROOT / "pyproject.toml")
        scripts = data.get("project", {}).get("scripts", {})
        assert scripts.get("mcp-server-spira") == "mcp_server_spira.server:main", (
            f"Expected 'mcp_server_spira.server:main', got {scripts.get('mcp-server-spira')!r}"
        )


# ---------------------------------------------------------------------------
# POWER.md tests
# ---------------------------------------------------------------------------


class TestPowerMdExists:
    """Verify POWER.md is present at the repo root."""

    def test_power_md_file_exists(self):
        """POWER.md must exist at the repository root."""
        power_md = POWER_MD_PATH
        assert power_md.exists(), f"POWER.md not found at {power_md}"
        assert power_md.is_file(), "POWER.md exists but is not a regular file"


class TestPowerMdFrontmatter:
    """Verify POWER.md YAML frontmatter contains required fields."""

    @pytest.fixture(scope="class")
    def frontmatter(self):
        """Parse and return the POWER.md frontmatter once per class."""
        text = (POWER_MD_PATH).read_text(encoding="utf-8")
        return _parse_frontmatter(text)

    def test_frontmatter_has_name(self, frontmatter):
        """POWER.md frontmatter must contain a 'name' field."""
        assert "name" in frontmatter, "POWER.md frontmatter is missing 'name'"
        assert frontmatter["name"], "'name' in POWER.md frontmatter must not be empty"

    def test_frontmatter_has_description(self, frontmatter):
        """POWER.md frontmatter must contain a 'description' field."""
        assert "description" in frontmatter, "POWER.md frontmatter is missing 'description'"
        assert frontmatter["description"], "'description' in POWER.md frontmatter must not be empty"

    def test_frontmatter_has_keywords(self, frontmatter):
        """POWER.md frontmatter must contain a non-empty 'keywords' list."""
        assert "keywords" in frontmatter, "POWER.md frontmatter is missing 'keywords'"
        keywords = frontmatter["keywords"]
        assert isinstance(keywords, list), f"'keywords' must be a list, got {type(keywords)}"
        assert len(keywords) > 0, "'keywords' list must not be empty"


class TestPowerMdEnvVars:
    """Verify POWER.md mentions all required environment variables."""

    REQUIRED_ENV_VARS = [
        "INFLECTRA_SPIRA_BASE_URL",
        "INFLECTRA_SPIRA_USERNAME",
        "INFLECTRA_SPIRA_API_KEY",
        "SPIRA_PROJECT_ID",
    ]

    @pytest.fixture(scope="class")
    def power_md_content(self):
        """Read POWER.md content once per class."""
        return (POWER_MD_PATH).read_text(encoding="utf-8")

    @pytest.mark.parametrize("env_var", REQUIRED_ENV_VARS)
    def test_env_var_mentioned(self, power_md_content, env_var):
        """POWER.md must mention each required environment variable."""
        assert env_var in power_md_content, (
            f"POWER.md does not mention required env var '{env_var}'"
        )


# ---------------------------------------------------------------------------
# MANIFEST.in tests
# ---------------------------------------------------------------------------


class TestManifestIn:
    """Verify MANIFEST.in includes POWER.md."""

    def test_manifest_includes_power_md(self):
        """MANIFEST.in must include POWER.md in the source distribution."""
        manifest = (REPO_ROOT / "MANIFEST.in").read_text(encoding="utf-8")
        assert "POWER.md" in manifest, "MANIFEST.in does not include POWER.md"


# ---------------------------------------------------------------------------
# .gitignore tests
# ---------------------------------------------------------------------------


class TestGitignore:
    """Verify .gitignore includes generated artefacts."""

    def test_gitignore_includes_coverage_json(self):
        """coverage.json must be listed in .gitignore."""
        gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        assert "coverage.json" in gitignore, ".gitignore does not include 'coverage.json'"
