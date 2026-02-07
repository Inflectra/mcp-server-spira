# Testing Strategy for Milestone 1

This document outlines the comprehensive testing strategy for the JSON-first transformation of MCP tools.

## Overview

Each "my work" tool requires **two types of tests**:

1. **Unit Tests** - Fast, isolated tests with mocked dependencies
2. **Integration Tests** - Real API tests verifying end-to-end functionality

## Test Structure

### Unit Tests Location
`tests/features/mywork/test_my<artifact>.py`

**Purpose**: Verify tool logic without external dependencies

**Characteristics**:
- Use mocked Spira client
- Fast execution (< 1 second)
- No network calls
- Run in CI/CD without credentials
- 100% code coverage target

**Coverage**:
- ✅ Successful retrieval scenarios
- ✅ Pagination edge cases
- ✅ Input validation errors
- ✅ API error handling
- ✅ JSON structure validation
- ✅ Tool integration with validation layer

### Integration Tests Location
`tests/integration/test_my<artifact>_json.py`

**Purpose**: Verify tool works with real Spira API

**Characteristics**:
- Use real Spira client
- Slower execution (1-3 seconds per test)
- Requires network and credentials
- Skipped in CI/CD without credentials
- Validates real-world behavior

**Coverage**:
- ✅ JSON output validation
- ✅ Pagination with real data
- ✅ Data preservation
- ✅ Field type checking
- ✅ Performance benchmarking
- ✅ Comparison with raw API

## Test Files Matrix

| Tool | Unit Tests | Integration Tests | Status |
|------|-----------|-------------------|--------|
| get_my_tasks | `test_mytasks.py` | `test_mytasks_json.py` | ✅ Complete |
| get_my_incidents | `test_myincidents.py` | `test_myincidents_json.py` | ⏳ Pending |
| get_my_requirements | `test_myrequirements.py` | `test_myrequirements_json.py` | ⏳ Pending |
| get_my_test_cases | `test_mytestcases.py` | `test_mytestcases_json.py` | ⏳ Pending |
| get_my_test_sets | `test_mytestsets.py` | `test_mytestsets_json.py` | ⏳ Pending |

## Unit Test Template

### Test Classes

```python
class TestGetMy<Artifact>Impl:
    """Tests for _get_my_<artifact>_impl function."""

    # Successful retrieval tests
    def test_successful_retrieval_with_default_pagination(self)
    def test_successful_retrieval_first_page(self)
    def test_successful_retrieval_middle_page(self)
    def test_successful_retrieval_last_page_full(self)
    def test_successful_retrieval_last_page_partial(self)

    # Edge cases
    def test_empty_results(self)
    def test_empty_results_with_offset(self)
    def test_custom_limit(self)
    def test_limit_larger_than_total(self)
    def test_single_<artifact>(self)

    # Data integrity
    def test_preserves_<artifact>_data_structure(self)
    def test_json_structure_validity(self)
    def test_pagination_metadata_accuracy(self)

    # Error handling
    def test_api_error_handling(self)
    def test_api_returns_none(self)


class TestGetMy<Artifact>ToolIntegration:
    """Integration tests for tool with validation."""

    # Validation tests
    def test_validation_limit_too_high(self)
    def test_validation_limit_zero(self)
    def test_validation_limit_negative(self)
    def test_validation_offset_negative(self)
    def test_validation_passes_with_valid_params(self)

    # Error handling
    def test_tool_handles_client_exception(self)


@pytest.mark.integration
class TestGetMy<Artifact>RealAPIIntegration:
    """Integration tests with real Spira API."""

    def test_returns_valid_json_structure(self)
    def test_pagination_works_with_real_data(self)
    def test_handles_empty_results(self)
    def test_preserves_<artifact>_fields(self)
    def test_error_handling_with_real_client(self)
```

### Expected Test Count

**Per Tool**:
- Unit tests: ~21 tests
- Integration tests (in unit file): ~5 tests (skipped without credentials)
- Integration tests (separate file): ~15-18 tests

**Total per tool**: ~40 tests

## Integration Test Template

See `tests/integration/INTEGRATION_TEST_TEMPLATE.md` for detailed template.

### Test Classes

```python
class TestGetMy<Artifact>JSONIntegration:
    """Integration tests for JSON-based implementation."""

    # Core functionality
    def test_returns_valid_json(self)
    def test_json_structure(self)
    def test_pagination_default_parameters(self)

    # Pagination scenarios
    def test_pagination_first_page(self)
    def test_pagination_second_page(self)  # if enough data
    def test_pagination_last_page(self)  # if enough data
    def test_pagination_beyond_end(self)
    def test_custom_limit(self)
    def test_large_limit(self)

    # Data integrity
    def test_data_preservation(self)
    def test_<artifact>_data_types(self)
    def test_pagination_metadata_accuracy(self)
    def test_comparison_with_raw_api(self)

    # Quality checks
    def test_no_silent_truncation(self)  # if enough data
    def test_json_formatting(self)
    def test_error_handling_with_real_api(self)


class TestGetMy<Artifact>Performance:
    """Performance tests."""

    @pytest.mark.slow
    def test_performance_with_large_limit(self)
```

## Test Execution

### Run All Tests

```bash
# All unit tests
pytest tests/features/mywork/ -v

# All integration tests
pytest tests/integration/ -v -s

# All tests for one tool
pytest tests/features/mywork/test_mytasks.py tests/integration/test_mytasks_json.py -v -s
```

### Run Specific Test Types

```bash
# Only unit tests (no integration)
pytest -m "not integration" -v

# Only integration tests
pytest -m integration -v -s

# Skip slow tests
pytest -m "not slow" -v
```

### CI/CD Execution

```bash
# Fast tests for CI (no credentials needed)
pytest tests/features/ -v --tb=short

# Full test suite (requires credentials)
pytest tests/ -v -s
```

## Coverage Requirements

### Unit Tests
- **Target**: 100% coverage for tool implementation
- **Minimum**: 80% coverage for modified code
- **Measure**: `pytest --cov=src/mcp_server_spira/features/mywork/tools/my<artifact> --cov-report=term-missing`

### Integration Tests
- **Target**: All critical paths tested with real API
- **Minimum**: Core functionality verified
- **Measure**: Manual verification of test scenarios

## Test Data Requirements

### Unit Tests
- No external data needed (uses mocks)
- Test data defined in test files

### Integration Tests
- Requires `.env` file with credentials
- Requires Spira instance with test data
- Recommended: 50+ items per artifact type for comprehensive pagination testing
- Minimum: 1+ items per artifact type for basic testing

## Best Practices

### Unit Tests
1. ✅ Use descriptive test names
2. ✅ Test one thing per test
3. ✅ Use mocks for external dependencies
4. ✅ Test edge cases and error conditions
5. ✅ Verify JSON structure and content
6. ✅ Check pagination metadata accuracy

### Integration Tests
1. ✅ Use real Spira client
2. ✅ Print helpful debug information
3. ✅ Skip tests when prerequisites not met
4. ✅ Adapt to available data
5. ✅ Test performance with large limits
6. ✅ Compare with raw API responses

### Both
1. ✅ Follow naming conventions
2. ✅ Add clear docstrings
3. ✅ Group related tests in classes
4. ✅ Use pytest fixtures for setup
5. ✅ Mark slow tests appropriately
6. ✅ Keep tests independent

## Troubleshooting

### Unit Tests Failing
- Check mock setup
- Verify expected vs actual JSON structure
- Review pagination calculations
- Check error response format

### Integration Tests Skipped
- Verify `.env` file exists
- Check credentials are valid
- Ensure Spira instance is accessible
- Confirm test data exists

### Integration Tests Failing
- Check network connectivity
- Verify API endpoint availability
- Review Spira instance data
- Check for API changes

## Maintenance

### When Adding New Tools
1. Copy unit test template from `test_mytasks.py`
2. Copy integration test template from `INTEGRATION_TEST_TEMPLATE.md`
3. Customize for artifact type
4. Run tests to verify
5. Update this document

### When Modifying Existing Tools
1. Update unit tests first
2. Verify unit tests pass
3. Update integration tests
4. Run full test suite
5. Check coverage reports

## Success Criteria

A tool is considered fully tested when:

- ✅ Unit tests achieve 100% code coverage
- ✅ All unit tests pass
- ✅ Integration tests cover all critical scenarios
- ✅ All integration tests pass (with credentials)
- ✅ Performance is acceptable (< 10s for limit=500)
- ✅ Documentation is complete

## References

- Unit test example: `tests/features/mywork/test_mytasks.py`
- Integration test example: `tests/integration/test_mytasks_json.py`
- Integration test template: `tests/integration/INTEGRATION_TEST_TEMPLATE.md`
- Integration test guide: `tests/integration/README.md`
- Common infrastructure tests: `tests/features/common/`
