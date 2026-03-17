# Development Setup Guide

**Spira MCP Server - Development Environment Setup**

This guide will help you set up your development environment for the Spira MCP Server project. Follow these steps to get started quickly.

---

## Quick Start

**Estimated Time:** 10-15 minutes (excluding Python 3.12 installation)

```bash
# 1. Clone the repository (if not already done)
# Skip this step if you already have the repository
git clone https://github.com/Inflectra/spira-mcp-server.git
cd mcp-server-spira

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .

# 4. Set up pre-commit hooks
pre-commit install

# 5. Run tests to verify setup
pytest

# 6. You're ready to develop!
```

---

## Prerequisites

### Required Software

- **Python 3.12+** (specified in `.python-version`)
- **Git** (for version control and pre-commit hooks)
- **pip** (Python package installer, comes with Python)

### Recommended Tools

- **pyenv** - For managing Python versions
- **VS Code** or **PyCharm** - IDEs with Python support
- **httpie** or **curl** - For testing API endpoints

---

## Python Version Requirement

**Estimated Time:** 1 minute (if already installed) or 10-15 minutes (first-time installation)

This project requires **Python 3.12 or higher**.

### Check Your Python Version

```bash
python --version
# Should output: Python 3.12.x
```

### Installing Python 3.12

#### Using pyenv (Recommended)

```bash
# Install pyenv (if not already installed)
# macOS
brew install pyenv

# Linux
curl https://pyenv.run | bash

# Install Python 3.12
pyenv install 3.12

# Set as local version for this project
pyenv local 3.12
```

#### Direct Installation

- **macOS:** Download from [python.org](https://www.python.org/downloads/) or use Homebrew
- **Linux:** Use your distribution's package manager
- **Windows:** Download from [python.org](https://www.python.org/downloads/)

---

## Virtual Environment Setup

**Estimated Time:** 2-3 minutes

A virtual environment isolates project dependencies from your system Python installation.

### Creating the Virtual Environment

```bash
# Navigate to project root
cd mcp-server-spira

# Create virtual environment
python -m venv .venv
```

### Activating the Virtual Environment

**Unix/macOS:**
```bash
source .venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

### Verifying Activation

When activated, your prompt should show `(.venv)` at the beginning:

```bash
(.venv) user@machine:~/mcp-server-spira$
```

### Deactivating

```bash
deactivate
```

---

## Dependency Installation

**Estimated Time:** 3-5 minutes (depends on network speed)

### Install All Dependencies

```bash
# Ensure virtual environment is activated
# Upgrade pip first
pip install --upgrade pip

# Install development dependencies
pip install -r requirements-dev.txt

# Install the package in editable mode
pip install -e .
```

### What Gets Installed

**Development Tools:**
- `ruff` - Fast Python linter
- `black` - Code formatter
- `mypy` - Type checker
- `pre-commit` - Git hook framework

**Testing Tools:**
- `pytest` - Testing framework
- `pytest-cov` - Coverage plugin
- `pytest-mock` - Mocking support

**Project Dependencies:**
- `httpx` - HTTP client for API calls
- `mcp[cli]` - Model Context Protocol SDK
- Other dependencies from `pyproject.toml`

### Verifying Installation

```bash
# Check installed packages
pip list

# Verify key tools are available
ruff --version
black --version
mypy --version
pytest --version
```

---

## Environment Configuration

### Setting Up Environment Variables

The Spira MCP Server requires API credentials to connect to your Spira instance. These are configured using environment variables.

#### Using .envrc (Recommended)

1. **Copy the example file:**
   ```bash
   cp .envrc.example .envrc
   ```

2. **Edit .envrc with your credentials:**
   ```bash
   # Open in your editor
   nano .envrc
   # or
   code .envrc
   ```

3. **Configure your Spira connection:**
   ```bash
   export SPIRA_BASE_URL="https://your-spira-instance.com"
   export SPIRA_USERNAME="your-username"
   export SPIRA_API_KEY="your-api-key"
   ```

4. **Load the environment variables:**
   ```bash
   # If using direnv (recommended)
   direnv allow

   # Or manually source the file
   source .envrc
   ```

#### Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `SPIRA_BASE_URL` | Your Spira instance URL | `https://demo.spiratest.net` |
| `SPIRA_USERNAME` | Your Spira username | `administrator` |
| `SPIRA_API_KEY` | Your Spira API key | `{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}` |

**Note:** Environment variables are only needed when running the MCP server or integration tests. Unit tests use mocks and don't require real credentials.

---

## Verify Your Setup

After completing the setup, run these commands to verify everything is working:

```bash
# 1. Check Python version
python --version
# Expected: Python 3.12.x

# 2. Verify virtual environment is activated
which python
# Expected: /path/to/project/.venv/bin/python

# 3. Run the validation script
python tests/test_onboarding_validation.py
# Expected: All checks pass

# 4. Run tests
pytest
# Expected: All tests pass

# 5. Run linters
ruff check .
black --check .
mypy src/
# Expected: No errors (or only documented issues)

# 6. Test pre-commit hooks
pre-commit run --all-files
# Expected: All hooks pass
```

If all commands succeed, your development environment is ready! 🎉

---

## Running Tests

### Basic Test Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_server.py

# Run tests matching a pattern
pytest -k "test_mytasks"

# Run only unit tests (if marked)
pytest -m unit
```

### Running Tests with Coverage

```bash
# Run tests with coverage report
pytest --cov

# Generate HTML coverage report
pytest --cov --cov-report=html

# Open coverage report in browser
# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html

# Windows
start htmlcov/index.html
```

### Test Markers

Tests can be marked with categories:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

---

## Running Linters

### Ruff (Linting)

```bash
# Check for linting issues
ruff check .

# Auto-fix issues where possible
ruff check . --fix

# Check specific file
ruff check src/mcp_server_spira/server.py
```

### Black (Formatting)

```bash
# Check if files need formatting
black --check .

# Format all files
black .

# Format specific file
black src/mcp_server_spira/server.py
```

### Mypy (Type Checking)

```bash
# Run type checking
mypy src/

# Check specific file
mypy src/mcp_server_spira/server.py

# Show error codes
mypy src/ --show-error-codes
```

### Run All Linters

```bash
# Run all checks manually
ruff check .
black --check .
mypy src/
```

---

## Pre-commit Hook Setup

**Estimated Time:** 1-2 minutes

Pre-commit hooks automatically run checks before each commit.

### Installing Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Verify installation
pre-commit --version
```

### Running Hooks Manually

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Run specific hook
pre-commit run ruff
pre-commit run black
pre-commit run mypy
```

### Making Commits

```bash
# Normal commit (hooks run automatically)
git add .
git commit -m "Your commit message"

# If hooks fail, fix issues and try again
# Or skip hooks for urgent commits (use sparingly!)
git commit --no-verify -m "Urgent fix"
```

### Testing Pre-commit Hooks

To verify your pre-commit hooks are working:

```bash
# Make a test change
echo "# Test" >> test_file.py

# Stage the file
git add test_file.py

# Try to commit (hooks will run)
git commit -m "Test commit"

# If hooks pass, remove the test file
git reset HEAD test_file.py
rm test_file.py
```

### Updating Hooks

```bash
# Update hook versions
pre-commit autoupdate

# Re-install after updates
pre-commit install
```

---

## Troubleshooting

### Issue: Python version not found

**Problem:** `python: command not found` or wrong version

**Solution:**
```bash
# Check if Python is installed
which python
which python3

# Use python3 explicitly if needed
python3 -m venv .venv

# Or install Python 3.12 using pyenv
pyenv install 3.12
pyenv local 3.12
```

### Issue: Virtual environment activation fails

**Problem:** Permission denied or script execution disabled

**Solution (Windows PowerShell):**
```powershell
# Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
.venv\Scripts\Activate.ps1
```

**Solution (Unix/macOS):**
```bash
# Make activation script executable
chmod +x .venv/bin/activate

# Then activate
source .venv/bin/activate
```

### Issue: Dependency installation fails

**Problem:** Package conflicts or network issues

**Solution:**
```bash
# Clear pip cache
pip cache purge

# Upgrade pip
pip install --upgrade pip

# Try installing again
pip install -r requirements-dev.txt

# If specific package fails, install individually
pip install ruff
pip install black
# etc.
```

### Issue: Pre-commit hooks are slow

**Problem:** Hooks take too long to run

**Solution:**
```bash
# Hooks only run on changed files by default
# For urgent commits, skip hooks temporarily
git commit --no-verify -m "message"

# Or disable specific slow hooks in .pre-commit-config.yaml
```

### Issue: Tests fail after setup

**Problem:** Tests pass in CI but fail locally

**Solution:**
```bash
# Ensure you're using correct Python version
python --version

# Reinstall dependencies
pip install -r requirements-dev.txt --force-reinstall

# Clear pytest cache
rm -rf .pytest_cache
pytest --cache-clear

# Set up environment variables (if running integration tests)
cp .envrc.example .envrc
# Edit .envrc with your credentials
source .envrc
```

### Issue: Import errors in tests

**Problem:** `ModuleNotFoundError: No module named 'mcp_server_spira'`

**Solution:**
```bash
# Install package in editable mode
pip install -e .

# Verify installation
pip show mcp-server-spira

# Check PYTHONPATH
echo $PYTHONPATH
```

### Issue: Mypy reports missing stubs

**Problem:** `error: Skipping analyzing "mcp": module is installed, but missing library stubs`

**Solution:**
```bash
# This is expected for some third-party libraries
# Add to pyproject.toml:
# [[tool.mypy.overrides]]
# module = ["mcp.*"]
# ignore_missing_imports = true

# Or install type stubs if available
pip install types-httpx
```

---

## Common Mistakes and Quick Fixes

### Mistake 1: Forgot to Activate Virtual Environment

**Symptom:** `ModuleNotFoundError` or packages not found

**Quick Fix:**
```bash
# Check if venv is activated (look for (.venv) in prompt)
# If not, activate it:
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate  # Windows
```

### Mistake 2: Running Commands Outside Project Directory

**Symptom:** Commands fail or can't find files

**Quick Fix:**
```bash
# Navigate to project root
cd /path/to/mcp-server-spira

# Verify you're in the right place
ls -la | grep pyproject.toml
```

### Mistake 3: Using Wrong Python Version

**Symptom:** Syntax errors or package incompatibilities

**Quick Fix:**
```bash
# Check Python version
python --version

# If wrong version, use python3.12 explicitly
python3.12 -m venv .venv

# Or use pyenv
pyenv local 3.12
```

### Mistake 4: Not Installing Package in Editable Mode

**Symptom:** Changes to code don't take effect

**Quick Fix:**
```bash
# Install in editable mode
pip install -e .

# Verify installation
pip show mcp-server-spira
```

### Mistake 5: Skipping Pre-commit Hook Installation

**Symptom:** Commits succeed but fail in CI

**Quick Fix:**
```bash
# Install pre-commit hooks
pre-commit install

# Test hooks
pre-commit run --all-files
```

---

## Development Workflow

### Typical Development Cycle

1. **Create a feature branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes**
   - Edit code in `src/mcp_server_spira/`
   - Add tests in `tests/`

3. **Run tests locally**
   ```bash
   pytest
   ```

4. **Run linters**
   ```bash
   ruff check . --fix
   black .
   mypy src/
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add new feature"
   # Pre-commit hooks run automatically
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/my-new-feature
   ```

### Before Submitting a PR

```bash
# Run full test suite
pytest --cov

# Run all linters
pre-commit run --all-files

# Verify coverage is acceptable
pytest --cov --cov-report=term-missing

# Check for any uncommitted changes
git status
```

---

## IDE Configuration

### VS Code

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### PyCharm

1. **Set Python Interpreter:**
   - File → Settings → Project → Python Interpreter
   - Select `.venv/bin/python`

2. **Configure pytest:**
   - File → Settings → Tools → Python Integrated Tools
   - Set Default test runner to "pytest"

3. **Enable Black:**
   - File → Settings → Tools → Black
   - Check "On code reformat"

---

## Additional Resources

- **Project Documentation:** See `README.md`
- **Architecture Guide:** See `docs/architecture.md`
- **Master Plan:** See `SPIRA_MCP_ENHANCEMENT_MASTER_PLAN.md`
- **API Reference:** See `SpiraRestAPI-v7.0-OpenAPI.json`

---

## Getting Help

If you encounter issues not covered in this guide:

1. Check existing GitHub issues
2. Review the troubleshooting section above
3. Ask in the project's communication channel
4. Create a new GitHub issue with:
   - Your Python version (`python --version`)
   - Your OS and version
   - Complete error message
   - Steps to reproduce

---

## Next Steps

After completing this setup, you're ready to start contributing! Here's what to do next:

### 1. Understand the Project (15-30 minutes)
- Read the [Architecture Documentation](./architecture.md)
- Review the [Master Plan](../SPIRA_MCP_ENHANCEMENT_MASTER_PLAN.md)
- Skim the [API Specification](../SpiraRestAPI-v7.0-OpenAPI.json)

### 2. Explore the Codebase (15-30 minutes)
- Browse `src/mcp_server_spira/` to understand the structure
- Look at existing tools in `src/mcp_server_spira/features/`
- Review test files in `tests/` to see testing patterns

### 3. Pick Your First Task (5 minutes)
- Check current milestone tasks in `.kiro/specs/`
- Look for issues labeled "good first issue" (if using GitHub)
- Ask the team what needs help

### 4. Make Your First Contribution (1-2 hours)
- Create a feature branch: `git checkout -b feature/your-feature`
- Make your changes
- Write tests for your changes
- Run tests and linters
- Commit and push
- Create a pull request

### 5. Join the Community
- Introduce yourself to the team
- Ask questions when you're stuck
- Share your feedback on the onboarding process

**Remember:** Everyone was new once. Don't hesitate to ask questions!

---

**Happy Coding! 🚀**
