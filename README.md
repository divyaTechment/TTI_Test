# Datadog TIA Test Suite

This project demonstrates Datadog Test Impact Analysis (TIA) features including:
- **Flaky Test Detection**: Tests that fail intermittently
- **Skipped Test Reporting**: Various skip scenarios and reasons
- **Test Optimization**: Intelligent test selection based on code changes

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   └── calculator.py          # Calculator module with basic operations
├── tests/
│   ├── conftest.py           # Pytest configuration and test optimization
│   ├── test_addition.py      # Addition tests
│   ├── test_subtraction.py   # Subtraction tests
│   ├── test_multiplication.py # Multiplication tests
│   ├── test_division.py      # Division tests
│   ├── test_parametrized.py  # Parametrized tests
│   ├── test_flaky.py         # Flaky tests for TIA demonstration
│   ├── test_skipped.py       # Skipped tests for TIA demonstration
│   └── integration/
│       └── test_integration.py # Integration tests
├── pytest.ini                # Pytest configuration
└── requirements.txt          # Python dependencies
```

## Installation

```bash
pip install -r requirements.txt
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Only Unit Tests
```bash
pytest -m unit
```

### Run Only Integration Tests
```bash
pytest -m integration
```

### Run Flaky Tests (normally skipped)
```bash
pytest --run-flaky -m flaky
```

### Run Skipped Tests (normally skipped)
```bash
pytest --run-skipped
```

## Test Optimization (Datadog TIA Feature)

The test suite includes intelligent test selection based on code changes, simulating Datadog TIA's test optimization functionality.

### Example: Run Tests Impacted by Specific Files

```bash
# Run only tests impacted by changes to calculator.add
pytest --changed-files="app/calculator.py"

# Run only tests impacted by changes to specific functions
pytest --changed-files="app/calculator.add,app/calculator.subtract"
```

The `conftest.py` automatically filters tests based on the `@pytest.mark.impact()` markers, showing how Datadog TIA selects only relevant tests when code changes.

## Flaky Tests

The `test_flaky.py` module contains several types of flaky tests:

1. **Random-based flakiness**: Tests that pass/fail randomly
2. **Time-based flakiness**: Tests that fail at certain times
3. **Conditional flakiness**: Tests that fail based on environment
4. **Race condition simulation**: Tests simulating concurrency issues
5. **Floating point precision**: Tests with precision-related flakiness

To run flaky tests:
```bash
pytest --run-flaky -m flaky
```

## Skipped Tests

The `test_skipped.py` module demonstrates various skip scenarios:

1. **Unconditional skip**: Tests skipped with reason
2. **Platform-based skip**: Tests skipped on specific platforms
3. **Version-based skip**: Tests skipped based on Python version
4. **Environment-based skip**: Tests skipped based on environment variables
5. **Feature not implemented**: Tests for unimplemented features
6. **Skipif decorator**: Tests using `@pytest.mark.skipif`

To run skipped tests:
```bash
pytest --run-skipped
```

## Test Markers

The project uses the following custom markers:

- `@pytest.mark.unit`: Quick unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.flaky`: Tests that may fail intermittently
- `@pytest.mark.slow`: Tests that take longer to run
- `@pytest.mark.impact("path")`: Marks test as impacted by code changes (for test optimization)

## Datadog TIA Integration

This test suite is designed to showcase Datadog Test Impact Analysis features:

1. **Flaky Test Detection**: Run tests multiple times to identify flaky behavior
2. **Skipped Test Analytics**: Track and report on skipped tests
3. **Test Selection Optimization**: Automatically select only impacted tests when code changes
4. **Test Execution Analytics**: Comprehensive reporting on test results

## Example Workflows

### Simulate CI/CD Test Selection
```bash
# Simulate changing only the add function
pytest --changed-files="app/calculator.add" -v

# Simulate changing multiple files
pytest --changed-files="app/calculator.add,app/calculator.multiply" -v
```

### Run Tests with Detailed Reporting
```bash
# Verbose output with test markers
pytest -v -m "unit or integration"

# HTML report (requires pytest-html)
pytest --html=report.html --self-contained-html
```

### Reproduce Flaky Tests
```bash
# Set seed for reproducible flaky test
FLAKY_SEED=42 pytest --run-flaky -m flaky test_flaky.py::test_flaky_random
```

## Notes

- Flaky tests are skipped by default. Use `--run-flaky` to include them.
- Skipped tests are skipped by default. Use `--run-skipped` to include them.
- The test optimization feature uses `@pytest.mark.impact()` markers to determine which tests to run based on changed files.

