# Milestone 0: Foundation & Infrastructure - Design

**Feature Name:** milestone-0-foundation
**Version:** 1.0
**Status:** Draft
**Created:** 2026-02-04
**Owner:** Development Team

---

## Overview

This document describes the technical design for establishing the development foundation and infrastructure for the Spira MCP Server enhancement project. It details the architecture, implementation approach, and technical decisions for the development environment, code quality tools, and testing framework.

**Related Documents:**
- [Requirements](./requirements.md)
- [Master Plan](../../../SPIRA_MCP_ENHANCEMENT_MASTER_PLAN.md)

---

## Architecture

### System Context

```
┌─────────────────────────────────────────────────────────────┐
│                    Development Environment                   │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Python     │  │   Linting    │  │   Testing    │     │
│  │   venv       │  │   Tools      │  │   Framework  │     │
│  │              │  │              │  │              │     │
│  │  - Python    │  │  - Ruff      │  │  - Pytest    │     │
│  │    3.13+     │  │  - Black     │  │  - Coverage  │     │
│  │  - Deps      │  │  - Mypy      │  │  - Mocks     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐                                           │
│  │ Pre-commit   │                                           │
│  │ Hooks        │                                           │
│  │              │                                           │
│  │  - Ruff      │                                           │
│  │  - Black     │                                           │
│  │  - Mypy      │                                           │
│  │  - Tests     │                                           │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Python Virtual Environment

**Purpose:** Isolate project dependencies and ensure consistent Python version across all developers.

**Implementation:**

```bash
# .python-version
3.13
```

```bash
# Setup script (in docs/development_setup.md)
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows

pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .
```

**Dependencies File:**

```txt
# requirements-dev.txt
# Linting and formatting
ruff>=0.1.0
black>=23.0.0
mypy>=1.7.0

# Testing
pytest>=8.4.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0

# Pre-commit
pre-commit>=3.5.0

# Existing dependencies (from pyproject.toml)
httpx>=0.28.1
mcp[cli]>=1.9.2
```

---

### 2. Code Quality Tools

#### 2.1 Ruff Configuration

**Purpose:** Fast Python linter and formatter.

**Configuration in `pyproject.toml`:**

```toml
[tool.ruff]
# Target Python 3.13+
target-version = "py313"

# Line length to match Black
line-length = 100

# Enable specific rule sets
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "SIM", # flake8-simplify
]

# Ignore specific rules
ignore = [
    "E501",  # Line too long (handled by Black)
]

# Exclude directories
exclude = [
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
]

[tool.ruff.per-file-ignores]
# Allow unused imports in __init__.py files
"__init__.py" = ["F401"]
# Allow print statements in scripts
"scripts/*.py" = ["T201"]

[tool.ruff.isort]
known-first-party = ["mcp_server_spira"]
```

#### 2.2 Black Configuration

**Purpose:** Opinionated code formatter.

**Configuration in `pyproject.toml`:**

```toml
[tool.black]
line-length = 100
target-version = ['py313']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.mypy_cache
  | \.pytest_cache
  | \.venv
  | __pycache__
  | build
  | dist
)/
'''
```

#### 2.3 Mypy Configuration

**Purpose:** Static type checker.

**Configuration in `pyproject.toml`:**

```toml
[tool.mypy]
python_version = "3.13"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Start lenient, tighten later
disallow_incomplete_defs = false
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

# Ignore missing imports for third-party libraries without stubs
[[tool.mypy.overrides]]
module = [
    "mcp.*",
    "httpx.*",
]
ignore_missing_imports = true
```

---

### 3. Pre-commit Hooks

**Purpose:** Automatically run checks before each commit.

**Configuration in `.pre-commit-config.yaml`:**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--ignore-missing-imports]

  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        args: [tests/, -v, --tb=short]
```

**Setup Commands:**

```bash
# Install pre-commit hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Skip hooks for urgent commits (use sparingly)
git commit --no-verify -m "urgent fix"
```

---

### 4. Testing Framework

**Purpose:** Comprehensive testing with coverage reporting.

**Configuration in `pyproject.toml`:**

```toml
[tool.pytest.ini_options]
pythonpath = "src"
testpaths = ["tests"]
addopts = [
    "--import-mode=importlib",
    "--cov=mcp_server_spira",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=0",  # Start at 0, increase later
    "-v",
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow tests",
]

[tool.coverage.run]
source = ["src/mcp_server_spira"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/.venv/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
```

**Test Commands:**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_api_coverage_tracker.py

# Run tests matching pattern
pytest -k "test_parse"

# Generate HTML coverage report
pytest --cov --cov-report=html
# Open htmlcov/index.html in browser
```

---

## Implementation Plan

### Phase 1: Environment Setup (Day 1)

**Tasks:**
1. Create `.python-version` file
2. Create `requirements-dev.txt`
3. Update `pyproject.toml` with tool configurations
4. Test virtual environment setup
5. Document setup process

**Validation:**
- Virtual environment can be created successfully
- All dependencies install without errors
- Existing code runs in new environment

### Phase 2: Linting & Formatting (Day 1-2)

**Tasks:**
1. Configure Ruff in `pyproject.toml`
2. Configure Black in `pyproject.toml`
3. Configure Mypy in `pyproject.toml`
4. Run linters on existing code
5. Fix or suppress linting issues
6. Document linting commands

**Validation:**
- All linters run successfully
- Existing code passes linting (or issues are documented)
- Linting commands are documented

### Phase 3: Pre-commit Hooks (Day 2)

**Tasks:**
1. Create `.pre-commit-config.yaml`
2. Install pre-commit hooks
3. Test hooks on sample commits
4. Document hook usage
5. Add skip instructions for urgent commits

**Validation:**
- Hooks run automatically on commit
- Hooks catch style issues
- Hooks can be skipped when needed

### Phase 4: Testing Framework (Day 2-3)

**Tasks:**
1. Update pytest configuration in `pyproject.toml`
2. Configure coverage reporting
3. Run existing tests
4. Generate coverage report
5. Document testing commands

**Validation:**
- All existing tests pass
- Coverage report generates successfully
- Testing commands are documented

### Phase 5: Documentation (Day 3-4)

**Tasks:**
1. Write `docs/development_setup.md`
2. Write `docs/architecture.md`
3. Update main README with links
4. Add troubleshooting section
5. Review and polish documentation

**Validation:**
- New developer can follow setup instructions
- Architecture is clearly explained
- Documentation is linked from README

---

## Correctness Properties

### Property 1: Environment Reproducibility
**Validates:** Requirements AC-0.1.1 through AC-0.1.5

**Property:** Given the same `.python-version` and `requirements-dev.txt`, any developer should be able to create an identical environment.

**Test Strategy:**
- Create environment on different machines
- Verify same package versions installed
- Verify existing code runs identically

### Property 2: Linting Consistency
**Validates:** Requirements AC-0.2.1 through AC-0.2.7

**Property:** Running linters multiple times on the same code should produce identical results.

**Test Strategy:**
- Run linters twice on same code
- Compare outputs
- Verify deterministic behavior

---

## Security Considerations

1. **Pre-commit Hooks:** Check for accidentally committed secrets
2. **Dependencies:** Use known, trusted packages only

---

## Performance Considerations

1. **Pre-commit Hooks:** Should run in < 10 seconds for typical changes

---

## Maintenance Considerations

1. **Tool Updates:** Pin versions in `requirements-dev.txt`
2. **Configuration Changes:** Document all configuration options

---

## Open Issues

1. **Issue #1:** Should pre-commit hooks run tests on every commit?
   - **Decision:** Yes, but allow skipping for urgent commits

2. **Issue #2:** What should the initial linting strictness be?
   - **Decision:** Start lenient, gradually tighten rules

---

## Future Enhancements

1. **CI/CD Integration:** Automate linting and testing in CI/CD pipeline
2. **IDE Integration:** Configure IDE settings for consistent development experience
3. **Code Metrics:** Track code quality metrics over time

---

**End of Design Document**
