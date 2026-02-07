# Pre-commit Validation Tests

This directory contains `test_precommit_validation.py`, a pytest test suite that mirrors all pre-commit hooks for faster iteration during development.

## Why Use These Tests?

Pre-commit hooks can be slow to run, especially when you're iterating on fixes. These tests allow you to:

1. **Run checks faster** - No need to stage files or trigger git hooks
2. **Run specific checks** - Test only what you're working on
3. **Get detailed output** - Better error messages and context
4. **Integrate with IDE** - Run from your editor or test runner

## Quick Start

### Run All Pre-commit Validation Tests

```bash
pytest tests/test_precommit_validation.py -v -m precommit --no-cov
```

Or use the shorthand:

```bash
python tests/test_precommit_validation.py
```

### Run Specific Checks

```bash
# Only check trailing whitespace
pytest tests/test_precommit_validation.py::TestPreCommitValidation::test_no_trailing_whitespace -v --no-cov

# Only run ruff checks
pytest tests/test_precommit_validation.py::TestPreCommitValidation::test_ruff_check -v
pytest tests/test_precommit_validation.py::TestPreCommitValidation::test_ruff_format_check -v

# Only run mypy type checking
pytest tests/test_precommit_validation.py::TestPreCommitValidation::test_mypy_type_check -v
```

### Run Multiple Specific Tests

```bash
# Run only formatting checks
pytest tests/test_precommit_validation.py -k "ruff_format" -v

# Run only linting checks (ruff + mypy)
pytest tests/test_precommit_validation.py -k "ruff_check or mypy" -v
```

## Available Tests

### Standard Pre-commit Hooks

- `test_no_trailing_whitespace` - Checks for trailing whitespace in Python files
- `test_files_end_with_newline` - Ensures all files end with a newline
- `test_yaml_files_valid` - Validates YAML syntax
- `test_json_files_valid` - Validates JSON syntax
- `test_no_large_files` - Checks for files > 1MB
- `test_no_merge_conflicts` - Detects merge conflict markers

### Ruff Linting & Formatting

- `test_ruff_check` - Runs ruff linter
- `test_ruff_format_check` - Checks ruff formatting

Note: Ruff replaces Black, flake8, isort, and more in a single fast tool.

### Mypy Type Checking

- `test_mypy_type_check` - Runs mypy type checker

## Typical Workflow

### 1. Make Changes

Edit your Python files as needed.

### 2. Run Pre-commit Tests

```bash
pytest tests/test_precommit_validation.py -v -m precommit --no-cov
```

### 3. Fix Issues

Based on the test output, fix any issues:

```bash
# Fix ruff issues automatically
ruff check . --fix

# Fix ruff formatting
ruff format .

# For mypy issues, fix manually based on error messages
```

### 4. Re-run Tests

```bash
pytest tests/test_precommit_validation.py -v -m precommit --no-cov
```

### 5. Commit When All Pass

Once all tests pass, your code will also pass pre-commit hooks:

```bash
git add .
git commit -m "Your commit message"
```

## Integration with Development

### VS Code

Add to `.vscode/settings.json`:

```json
{
  "python.testing.pytestArgs": [
    "tests",
    "-v",
    "-m",
    "precommit",
    "--no-cov"
  ]
}
```

### Watch Mode

For continuous testing during development:

```bash
pytest-watch tests/test_precommit_validation.py -m precommit --no-cov
```

### CI/CD

These tests can also be run in CI/CD pipelines:

```yaml
# .github/workflows/test.yml
- name: Run pre-commit validation tests
  run: pytest tests/test_precommit_validation.py -v -m precommit --no-cov
```

## Troubleshooting

### Tests are skipped

If you see "Ruff not installed" or similar messages, install the required tools:

```bash
pip install -r requirements-dev.txt
```

### Tests timeout

If tests timeout, you can increase the timeout in the test file or run specific tests individually.

### False positives

If a test fails but you believe it's a false positive, check:

1. The actual pre-commit hook configuration in `.pre-commit-config.yaml`
2. The tool's configuration in `pyproject.toml`
3. Any exclude patterns that might apply

## Comparison with Pre-commit Hooks

| Feature | Pre-commit Tests | Pre-commit Hooks |
|---------|------------------|------------------|
| Speed | Fast | Slower |
| Granularity | Run individual tests | All or nothing |
| Output | Detailed pytest output | Hook output |
| IDE Integration | Excellent | Limited |
| Git Integration | None | Automatic on commit |
| Auto-fix | Manual | Some hooks auto-fix |

## Best Practices

1. **Run tests frequently** - Don't wait until commit time
2. **Fix issues incrementally** - Run specific tests as you work
3. **Use auto-fix tools** - Let ruff fix formatting and linting automatically
4. **Keep tests fast** - If tests become slow, optimize or split them
5. **Update tests with hooks** - When pre-commit config changes, update these tests

## Notes

- Large known files (like `SpiraRestAPI-v7.0-OpenAPI.json`) are excluded from size checks
- Tests use the same configuration as pre-commit hooks from `pyproject.toml`
- The full pytest suite is NOT run by pre-commit hooks to keep commits fast
- Run the full test suite manually before pushing: `pytest tests/ -v`
