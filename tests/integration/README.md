# Integration Tests

This directory contains integration tests that verify the MCP server against a real Spira instance.

## Prerequisites

1. **Spira Instance**: Access to a Spira instance (cloud or on-premise)
2. **Test Data**: Spira instance should have some test data (tasks, incidents, etc.)
3. **Credentials**: Valid Spira API credentials

## Setup

### 1. Create `.env` File

Create a `.env` file in the project root with your Spira credentials:

```bash
# Spira API Configuration
INFLECTRA_SPIRA_BASE_URL=https://your-instance.spiraservice.net
INFLECTRA_SPIRA_USERNAME=your-username
INFLECTRA_SPIRA_API_KEY=your-api-key
```

**Note**: The `.env` file is automatically loaded by `conftest.py` before running integration tests.

### 2. Verify Credentials

Test your connection:

```bash
pytest tests/integration/test_current_server.py::TestCurrentServerIntegration::test_connection_to_spira -v -s
```

## Running Integration Tests

### Run All Integration Tests

```bash
pytest tests/integration/ -v -s
```

### Run Specific Test Files

```bash
# Test current (markdown-based) implementation
pytest tests/integration/test_current_server.py -v -s

# Test new (JSON-based) get_my_tasks implementation
pytest tests/integration/test_mytasks_json.py -v -s
```

### Run Specific Test Classes

```bash
# Test JSON structure and pagination
pytest tests/integration/test_mytasks_json.py::TestGetMyTasksJSONIntegration -v -s

# Test performance
pytest tests/integration/test_mytasks_json.py::TestGetMyTasksPerformance -v -s
```

### Run Specific Tests

```bash
# Test pagination with default parameters
pytest tests/integration/test_mytasks_json.py::TestGetMyTasksJSONIntegration::test_pagination_default_parameters -v -s

# Test data preservation
pytest tests/integration/test_mytasks_json.py::TestGetMyTasksJSONIntegration::test_data_preservation -v -s
```

## Test Categories

### Current Implementation Tests (`test_current_server.py`)

Tests for the **existing markdown-based** implementation:
- Connection verification
- Markdown output format
- Truncation behavior (silent truncation at 25 items)
- Error handling
- Raw API response structure

### JSON Implementation Tests (`test_mytasks_json.py`)

Tests for the **new JSON-based** `get_my_tasks` implementation:

#### Basic Functionality
- ✅ Returns valid JSON
- ✅ Correct JSON structure (data + pagination)
- ✅ Pagination metadata accuracy

#### Pagination Tests
- ✅ Default parameters (limit=25, offset=0)
- ✅ First page retrieval
- ✅ Second page retrieval
- ✅ Last page with partial results
- ✅ Offset beyond available data
- ✅ Custom limits
- ✅ Large limits (100+)

#### Data Integrity
- ✅ All task fields preserved
- ✅ Data types preserved correctly
- ✅ Comparison with raw API data
- ✅ No silent truncation

#### Error Handling
- ✅ Empty results handling
- ✅ API error handling
- ✅ Graceful error responses

#### Performance
- ✅ Performance with large limits (500)

## Test Markers

Integration tests use pytest markers for organization:

```bash
# Run only integration tests
pytest -m integration -v -s

# Skip integration tests (run only unit tests)
pytest -m "not integration" -v

# Run only slow tests
pytest -m slow -v -s

# Skip slow tests
pytest -m "not slow" -v
```

## Understanding Test Output

### Successful Test Output

```
✓ JSON validation test:
   Result type: <class 'str'>
   Result length: 1234 characters
   ✓ Valid JSON
   ✓ Has required structure (data, pagination)

✓ Default pagination test:
   Total tasks from API: 47
   Pagination metadata:
     - limit: 25
     - offset: 0
     - returned_count: 25
     - total_count: 47
     - has_more: True
   ✓ Pagination metadata is accurate
```

### Skipped Tests

Tests are skipped when:
- No `.env` file or credentials not set
- Not enough test data (e.g., need > 25 tasks for pagination tests)

```
SKIPPED [1] tests/integration/test_mytasks_json.py:123:
  Not enough tasks for second page test (need > 10)
```

## Troubleshooting

### Tests Are Skipped

**Problem**: All integration tests are skipped

**Solution**:
1. Verify `.env` file exists in project root
2. Check credentials are correct
3. Ensure `INFLECTRA_SPIRA_BASE_URL` is set

### Connection Errors

**Problem**: `Failed to connect to Spira`

**Solutions**:
1. Verify Spira instance is accessible
2. Check URL format (should include `https://`)
3. Verify API key is valid
4. Check network/firewall settings

### Not Enough Test Data

**Problem**: Some tests skip due to insufficient data

**Solution**: Add more test data to your Spira instance:
- Create tasks assigned to your user
- Create incidents, requirements, etc.
- Aim for 50+ items for comprehensive pagination testing

### Slow Tests

**Problem**: Tests take too long

**Solution**:
1. Skip slow tests: `pytest -m "not slow"`
2. Use smaller limits in tests
3. Check network latency to Spira instance

## Best Practices

### 1. Use Test Data

- Use a **test/development** Spira instance, not production
- Create dedicated test data that won't change
- Document expected test data in test docstrings

### 2. Clean Test Environment

- Don't rely on specific task IDs or names
- Tests should work with any reasonable dataset
- Use `pytest.skip()` when prerequisites aren't met

### 3. Verbose Output

Always use `-s` flag to see detailed output:

```bash
pytest tests/integration/ -v -s
```

This shows:
- Connection status
- Data counts
- Pagination details
- Performance metrics

### 4. Isolate Tests

Each test should be independent:
- Don't rely on test execution order
- Don't modify data that other tests need
- Use fixtures for shared setup

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  integration:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt

      - name: Create .env file
        run: |
          echo "INFLECTRA_SPIRA_BASE_URL=${{ secrets.SPIRA_BASE_URL }}" >> .env
          echo "INFLECTRA_SPIRA_USERNAME=${{ secrets.SPIRA_USERNAME }}" >> .env
          echo "INFLECTRA_SPIRA_API_KEY=${{ secrets.SPIRA_API_KEY }}" >> .env

      - name: Run integration tests
        run: |
          pytest tests/integration/ -v -s --tb=short
```

## Contributing

When adding new integration tests:

1. **Follow naming convention**: `test_*.py`
2. **Use pytest markers**: `@pytest.mark.integration`
3. **Skip when no credentials**: Use `pytestmark` or `@pytest.mark.skipif`
4. **Add docstrings**: Explain what the test verifies
5. **Print useful output**: Help debug failures
6. **Handle edge cases**: Skip when prerequisites aren't met

## Example Test Template

```python
@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("INFLECTRA_SPIRA_BASE_URL"),
    reason="Requires Spira credentials"
)
def test_my_feature(spira_client):
    """Test description explaining what is verified."""

    # Arrange
    result = my_function(spira_client, param=value)

    # Act
    parsed = json.loads(result)

    # Assert
    assert "expected_field" in parsed

    # Print useful debug info
    print(f"\n✓ Test passed:")
    print(f"  Field value: {parsed['expected_field']}")
```

## Support

For issues with integration tests:

1. Check this README
2. Review test output with `-v -s` flags
3. Verify `.env` configuration
4. Check Spira instance accessibility
5. Open an issue with test output and environment details
