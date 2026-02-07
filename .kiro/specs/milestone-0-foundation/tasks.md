# Milestone 0: Foundation & Infrastructure - Tasks

**Feature Name:** milestone-0-foundation
**Version:** 1.0
**Status:** Ready for Implementation
**Created:** 2026-02-04

---

## Task List

### 1. Environment Setup

- [x] 1.1 Create Python version specification
  - [x] 1.1.1 Create `.python-version` file with Python 3.13
  - [x] 1.1.2 Test with pyenv (if available)
  - [x] 1.1.3 Document version requirement in README

- [x] 1.2 Create development dependencies file
  - [x] 1.2.1 Create `requirements-dev.txt` with all dev dependencies
  - [x] 1.2.2 Include ruff, black, mypy, pre-commit, pytest-cov, pytest-mock
  - [x] 1.2.3 Pin versions for reproducibility
  - [x] 1.2.4 Add comments explaining each dependency

- [x] 1.3 Test virtual environment setup
  - [x] 1.3.1 Create fresh virtual environment
  - [x] 1.3.2 Install dependencies from requirements-dev.txt
  - [x] 1.3.3 Install package in editable mode (`pip install -e .`)
  - [x] 1.3.4 Verify existing code runs successfully
  - [x] 1.3.5 Verify existing tests pass

---

### 2. Linting and Formatting Configuration

- [x] 2.1 Configure Ruff
  - [x] 2.1.1 Add `[tool.ruff]` section to `pyproject.toml`
  - [x] 2.1.2 Set target Python version to 3.13
  - [x] 2.1.3 Set line length to 100
  - [x] 2.1.4 Enable rule sets (E, W, F, I, N, UP, B, C4, SIM)
  - [x] 2.1.5 Configure exclusions (.git, .venv, __pycache__, etc.)
  - [x] 2.1.6 Add per-file ignores for __init__.py and scripts
  - [x] 2.1.7 Configure isort settings

- [x] 2.2 Configure Black
  - [x] 2.2.1 Add `[tool.black]` section to `pyproject.toml`
  - [x] 2.2.2 Set line length to 100
  - [x] 2.2.3 Set target version to py313
  - [x] 2.2.4 Configure exclusions

- [x] 2.3 Configure Mypy
  - [x] 2.3.1 Add `[tool.mypy]` section to `pyproject.toml`
  - [x] 2.3.2 Set Python version to 3.13
  - [x] 2.3.3 Enable warning flags
  - [x] 2.3.4 Start with lenient settings (disallow_untyped_defs = false)
  - [x] 2.3.5 Add overrides for third-party libraries without stubs

- [x] 2.4 Run linters on existing code
  - [x] 2.4.1 Run `ruff check .` and document issues
  - [x] 2.4.2 Run `black --check .` and document issues
  - [x] 2.4.3 Run `mypy src/` and document issues
  - [x] 2.4.4 Fix critical issues
  - [x] 2.4.5 Suppress or document non-critical issues
  - [x] 2.4.6 Verify all linters pass (or have documented exceptions)

---

### 3. Pre-commit Hooks

- [x] 3.1 Create pre-commit configuration
  - [x] 3.1.1 Create `.pre-commit-config.yaml` file
  - [x] 3.1.2 Add pre-commit/pre-commit-hooks repo
  - [x] 3.1.3 Add ruff-pre-commit repo
  - [x] 3.1.4 Add black repo
  - [x] 3.1.5 Add mypy repo
  - [x] 3.1.6 Add local pytest hook
  - [x] 3.1.7 Configure hook arguments

- [x] 3.2 Install and test pre-commit hooks
  - [x] 3.2.1 Run `pre-commit install`
  - [x] 3.2.2 Run `pre-commit run --all-files` to test
  - [x] 3.2.3 Make a test commit to verify hooks run
  - [x] 3.2.4 Test skipping hooks with `--no-verify`
  - [x] 3.2.5 Document hook usage

---

### 4. Testing Framework Configuration

- [x] 4.1 Configure pytest
  - [x] 4.1.1 Update `[tool.pytest.ini_options]` in `pyproject.toml`
  - [x] 4.1.2 Set pythonpath to "src"
  - [x] 4.1.3 Set testpaths to ["tests"]
  - [x] 4.1.4 Add coverage options to addopts
  - [x] 4.1.5 Define test markers (unit, integration, slow)

- [x] 4.2 Configure coverage
  - [x] 4.2.1 Add `[tool.coverage.run]` section to `pyproject.toml`
  - [x] 4.2.2 Set source to ["src/mcp_server_spira"]
  - [x] 4.2.3 Configure omit patterns
  - [x] 4.2.4 Add `[tool.coverage.report]` section
  - [x] 4.2.5 Configure exclude_lines for coverage

- [x] 4.3 Test the testing framework
  - [x] 4.3.1 Run `pytest` to verify existing tests pass
  - [x] 4.3.2 Run `pytest --cov` to generate coverage report
  - [x] 4.3.3 Run `pytest --cov --cov-report=html` to generate HTML report
  - [x] 4.3.4 Verify coverage report is accurate
  - [x] 4.3.5 Document testing commands

---

### 5. Documentation

- [x] 5.1 Write development setup guide
  - [x] 5.1.1 Create `docs/development_setup.md`
  - [x] 5.1.2 Document Python version requirement
  - [x] 5.1.3 Document virtual environment setup
  - [x] 5.1.4 Document dependency installation
  - [x] 5.1.5 Document running tests
  - [x] 5.1.6 Document running linters
  - [x] 5.1.7 Document pre-commit hook setup
  - [x] 5.1.8 Add troubleshooting section
  - [x] 5.1.9 Add quick start commands

- [x] 5.2 Write architecture documentation
  - [x] 5.2.1 Create `docs/architecture.md`
  - [x] 5.2.2 Document directory structure
  - [x] 5.2.3 Document feature-based organization
  - [x] 5.2.4 Document tool registration pattern
  - [x] 5.2.5 Document SpiraClient usage
  - [x] 5.2.6 Add architecture diagrams
  - [x] 5.2.7 Reference master plan

- [x] 5.3 Update main README
  - [x] 5.3.1 Add link to development setup guide
  - [x] 5.3.2 Add link to architecture documentation
  - [x] 5.3.3 Add link to master plan
  - [x] 5.3.4 Update project status

---

### 6. Integration and Validation

- [x] 6.1 Run full test suite
  - [x] 6.1.1 Run `pytest` to verify all tests pass
  - [x] 6.1.2 Run `pytest --cov` to check coverage
  - [x] 6.1.3 Review coverage report
  - [x] 6.1.4 Fix any failing tests

- [x] 6.2 Run all linters
  - [x] 6.2.1 Run `ruff check .`
  - [x] 6.2.2 Run `black --check .`
  - [x] 6.2.3 Run `mypy src/`
  - [x] 6.2.4 Fix any issues

- [x] 6.3 Test pre-commit hooks
  - [x] 6.3.1 Make a test commit
  - [x] 6.3.2 Verify all hooks run
  - [x] 6.3.3 Verify hooks catch issues
  - [x] 6.3.4 Test skipping hooks

- [x] 6.4 Test new developer onboarding
  - [x] 6.4.1 Have someone follow setup guide
  - [x] 6.4.2 Collect feedback
  - [x] 6.4.3 Update documentation based on feedback
  - [x] 6.4.4 Verify setup takes < 15 minutes

---

### 7. Final Review and Cleanup

- [ ] 7.1 Code review
  - [ ] 7.1.1 Review all new code
  - [ ] 7.1.2 Check for code quality issues
  - [ ] 7.1.3 Verify design patterns are followed
  - [ ] 7.1.4 Address review comments

- [ ] 7.2 Documentation review
  - [ ] 7.2.1 Review all documentation
  - [ ] 7.2.2 Check for clarity and completeness
  - [ ] 7.2.3 Verify all links work
  - [ ] 7.2.4 Fix any issues

- [ ] 7.3 Final validation
  - [ ] 7.3.1 Verify all acceptance criteria are met
  - [ ] 7.3.2 Verify all tasks are complete
  - [ ] 7.3.3 Run full test suite one final time
  - [ ] 7.3.4 Generate final coverage report

- [ ] 7.4 Prepare for next milestone
  - [ ] 7.4.1 Update project status
  - [ ] 7.4.2 Tag milestone-0 release
  - [ ] 7.4.3 Update master plan if needed

---

## Task Dependencies

```
1. Environment Setup (1.1, 1.2, 1.3)
   ↓
2. Linting Configuration (2.1, 2.2, 2.3, 2.4)
   ↓
3. Pre-commit Hooks (3.1, 3.2)
   ↓
4. Testing Framework (4.1, 4.2, 4.3)
   ↓
5. Documentation (5.1, 5.2, 5.3)
   ↓
6. Integration (6.1, 6.2, 6.3, 6.4)
   ↓
7. Final Review (7.1, 7.2, 7.3, 7.4)
```

---

## Estimated Effort

| Task Group | Estimated Hours |
|------------|----------------|
| 1. Environment Setup | 2 hours |
| 2. Linting Configuration | 3 hours |
| 3. Pre-commit Hooks | 2 hours |
| 4. Testing Framework | 2 hours |
| 5. Documentation | 4 hours |
| 6. Integration | 2 hours |
| 7. Final Review | 2 hours |
| **Total** | **17 hours (~2 days)** |

---

## Success Criteria

All tasks must be completed and the following must be true:

- [ ] Virtual environment can be created in < 5 minutes
- [ ] All linters pass on existing code
- [ ] Pre-commit hooks run successfully
- [ ] All existing tests pass
- [ ] Coverage report generates successfully
- [ ] Documentation is complete and clear
- [ ] New developer can onboard in < 15 minutes

---

**End of Tasks Document**
