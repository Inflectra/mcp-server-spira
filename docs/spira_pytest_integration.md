# Spira pytest Integration

This project uses the [pytest-spiratest plugin](https://spiradoc.inflectra.com/Unit-Testing-Integration/Integrating-with-PyTest/) to automatically report test results to Spira.

## Quick Setup

1. **Install the plugin**:
   ```bash
   pip install pytest-spiratest
   ```

2. **Create `.env.spira` with your credentials**:
   ```bash
   cp .env.spira.template .env.spira
   # Edit .env.spira with your actual credentials
   ```

3. **Generate `spira.cfg`**:
   ```bash
   python scripts/generate_spira_cfg.py
   ```

4. **Run tests** - results automatically report to Spira:
   ```bash
   pytest tests/
   ```

## Configuration

### Credentials (`.env.spira`)

Store your Spira credentials in `.env.spira` (NOT in version control):

```bash
SPIRA_URL=https://your-instance.spiraservice.net
SPIRA_USERNAME=your_username
SPIRA_TOKEN={YOUR_API_KEY}
SPIRA_PRODUCT_ID=1
```

Get your API key (token) from: Spira > Administration > My Profile > API Keys

### Test Case Mappings (`spira.cfg`)

The `spira.cfg` file is **generated** from `.env.spira` and `spira.cfg.template`:

```bash
python scripts/generate_spira_cfg.py
```

This creates `spira.cfg` with your actual credentials substituted. The file is NOT in version control (it's in `.gitignore`).

**Note**: The pytest-spiratest plugin is case-insensitive for test class names.

## Mapping Strategy

**One test class = One Spira test case**

Each pytest test class maps to a single Spira test case. All test methods in that class report to the same test case.

Example:
```python
# This entire class → TC:123 in Spira
class TestGetMyTasksImpl:
    def test_successful_retrieval(self):  # ↓
        pass                               # ↓ All report to TC:123
    def test_pagination(self):             # ↓
        pass
```

## Adding New Test Classes

When you create a new test class:

1. **Add mapping to `spira.cfg.template`**:
   ```ini
   [test_cases]
   TestMyNewFeature = 456
   ```

2. **Regenerate `spira.cfg`**:
   ```bash
   python scripts/generate_spira_cfg.py
   ```

3. **Create test case in Spira**:
   - Name: `MyWork: My New Feature Tests` (or appropriate category)
   - Type: Automated
   - Note the test case ID (e.g., TC:456)

4. **Update the ID in `spira.cfg.template`** with the real TC ID

5. **Regenerate and validate**:
   ```bash
   python scripts/generate_spira_cfg.py
   python scripts/validate_spira_integration.py
   ```

6. **Run tests**:
   ```bash
   pytest tests/
   ```

## Validation

Check that all test classes are mapped:

```bash
# Check coverage
python scripts/validate_spira_integration.py

# Enforce 100% coverage (for CI/CD)
python scripts/validate_spira_integration.py --strict
```

The script will:
- Discover all test classes in the project
- Report which ones are mapped to Spira
- Show coverage percentage
- List unmapped test classes

## Current Test Classes

The project currently has **24 test classes**:

- **MyWork Tests** (3): TestGetMyTasksImpl, TestGetMyTasksToolIntegration, TestGetMyTasksRealAPIIntegration
- **Integration Tests** (4): TestCurrentServerDataStructure, TestCurrentServerIntegration, TestGetMyTasksJSONIntegration, TestGetMyTasksPerformance
- **Infrastructure Tests** (15): Error handling, pagination, responses, validation
- **Script Tests** (2): Documentation generator tests

Run `python scripts/validate_spira_integration.py` to see the complete list.

## Viewing Results

After running tests:

1. Go to Spira
2. Navigate to **Testing > Test Cases**
3. Open a test case (e.g., TC:123)
4. Click **Test Runs** tab
5. See execution history with pass/fail status

## Troubleshooting

### Tests run but no results in Spira

- Check `.env.spira` exists with correct credentials
- Verify test class names in `spira.cfg` match exactly (case-sensitive)
- Ensure test case IDs exist in Spira

### Authentication errors

- Use API key (not password) from Spira profile
- Verify username and product_id are correct

### Validation shows < 100% coverage

- Run validation to see unmapped classes
- Create test cases in Spira for unmapped classes
- Add mappings to `spira.cfg`

## CI/CD Integration

The validation script can enforce 100% coverage in CI/CD:

```yaml
- name: Validate Spira integration
  run: python scripts/validate_spira_integration.py --strict
```

Store credentials as secrets and create `.env.spira` in the CI environment.

## References

- [Official pytest-spiratest Documentation](https://spiradoc.inflectra.com/Unit-Testing-Integration/Integrating-with-PyTest/)
- Configuration generator: `scripts/generate_spira_cfg.py`
- Validation script: `scripts/validate_spira_integration.py`
- Template: `spira.cfg.template` (in version control)
- Credentials: `.env.spira` (NOT in version control)
- Generated config: `spira.cfg` (NOT in version control)
