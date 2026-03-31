# ReportPortal Integration Test Suite

This directory contains comprehensive tests for the ReportPortal JUnit integration tools.

## Structure

```
tests/
├── README.md                    # This file
├── conftest.py                  # Pytest configuration and shared fixtures
├── run_tests.py                 # Test runner script
├── fixtures/
│   └── sample_junit_data.py     # Sample JUnit XML data for testing
├── unit/                        # Unit tests for individual components
│   ├── test_property_enums.py   # Tests for property enums and validation
│   ├── test_junit_parser.py     # Tests for JUnit XML parsing
│   ├── test_property_processor.py  # Tests for property filtering
│   └── test_reportportal_client_wrapper.py  # Tests for RP client wrapper
└── integration/                 # Integration tests for complete workflows
    └── test_full_workflow.py    # End-to-end workflow testing
```

## Running Tests

### Using the test runner script

```bash
# Run all tests
./tests/run_tests.py

# Run only unit tests
./tests/run_tests.py --test-type unit

# Run only integration tests  
./tests/run_tests.py --test-type integration

# Run tests with coverage
./tests/run_tests.py --coverage --html-report

# Run tests for specific module
./tests/run_tests.py --module property_enums --verbose
```

### Using pytest directly

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run with coverage
pytest --cov=src/reportportal --cov-report=html

# Run specific test file
pytest tests/unit/test_property_enums.py

# Run specific test class
pytest tests/unit/test_property_enums.py::TestReportPortalProperties

# Run specific test method
pytest tests/unit/test_property_enums.py::TestReportPortalProperties::test_rp_property_values
```

## Test Categories

### Unit Tests

- **property_enums**: Tests for all enum classes, validation functions, and legacy compatibility
- **junit_parser**: Tests for JUnit XML parsing, timestamp conversion, property extraction, and name conversion
- **property_processor**: Tests for property filtering, suite/case property processing, and launch property building
- **reportportal_client_wrapper**: Tests for ReportPortal client operations, session management, and auto-analysis

### Integration Tests

- **full_workflow**: End-to-end tests that verify the complete workflow from JUnit XML to ReportPortal reporting
- **component_interaction**: Tests for data flow between different components
- **error_handling**: Tests for error scenarios and edge cases

## Fixtures and Test Data

### Available Fixtures (conftest.py)

- `mock_rp_client`: Mock ReportPortal client for testing
- `sample_junit_xml`: Basic JUnit XML content
- `temp_junit_file`: Temporary JUnit XML file
- `sample_options`: Mock command line options
- `mock_requests_response`: Mock HTTP response for API testing
- `mock_logger`: Mock logger instance
- `sample_properties`: Sample property data
- `sample_suite_data`: Sample test suite data structure

### Sample JUnit Data (fixtures/sample_junit_data.py)

Various JUnit XML samples for different testing scenarios:
- Simple test suite with passing tests
- Complex test suite with all status types (PASSED, FAILED, ERROR, SKIPPED)
- Multi-suite XML with different test levels
- Info-collector suite for environment data
- Property-heavy suite for testing filtering
- Empty test suite for edge case testing

## Test Markers

The test suite uses pytest markers for categorization:

```bash
# Run tests by marker
pytest -m "unit"
pytest -m "integration"  
pytest -m "component('TestComponent')"
pytest -m "color('green')"
```

Available markers:
- `unit`: Unit tests for individual components
- `integration`: Integration tests for complete workflows
- `slow`: Slow running tests
- `component(name)`: Tests for specific components
- `color(color)`: Color-coded test markers
- `issue(id)`: Tests related to specific issues
- `platform(type)`: Platform-specific tests
- `build(type)`: Build-specific tests
- `level(type)`: Test level markers

## Coverage

Generate coverage reports to ensure comprehensive test coverage:

```bash
# Terminal coverage report
pytest --cov=src/reportportal --cov-report=term-missing

# HTML coverage report
pytest --cov=src/reportportal --cov-report=html:tests/coverage_html

# Combined reports
pytest --cov=src/reportportal --cov-report=term-missing --cov-report=html:tests/coverage_html
```

## Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Mocking**: Use mocks for external dependencies (ReportPortal API, file system, etc.)
3. **Fixtures**: Use fixtures for common test data and setup
4. **Descriptive Names**: Test names should clearly describe what is being tested
5. **Documentation**: Add docstrings to test classes and methods
6. **Edge Cases**: Include tests for error conditions and edge cases
7. **Integration**: Verify component interactions with integration tests

## Adding New Tests

When adding new functionality:

1. Add unit tests for the new component in `tests/unit/`
2. Add integration tests if the component interacts with others
3. Update fixtures and sample data as needed
4. Run the full test suite to ensure no regressions
5. Update documentation and docstrings

Example test structure:
```python
class TestNewComponent:
    """Test NewComponent class."""
    
    def test_basic_functionality(self):
        """Test basic functionality works correctly."""
        # Arrange
        component = NewComponent()
        
        # Act
        result = component.do_something()
        
        # Assert
        assert result == expected_value
    
    def test_error_handling(self):
        """Test error handling for invalid input."""
        component = NewComponent()
        
        with pytest.raises(ValueError, match="Invalid input"):
            component.do_something_invalid()
```