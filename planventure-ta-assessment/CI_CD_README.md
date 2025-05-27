# Assessment System CI/CD Pipeline

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline setup for the PlanVenture Assessment System.

## Overview

The CI/CD pipeline is implemented using GitHub Actions and provides comprehensive testing, code quality checks, security scanning, and performance monitoring for the assessment system.

## Pipeline Structure

### 1. Main Test Job (`test`)
- **Triggers**: Push/PR to `main` or `develop` branches affecting `planventure-ta-assessment/**`
- **Matrix Strategy**: Tests across Python 3.9, 3.10, and 3.11
- **Steps**:
  - Code checkout and Python setup
  - Dependency caching and installation
  - Code quality checks (flake8, black, isort)
  - Database initialization
  - Comprehensive test suite execution
  - Coverage reporting

### 2. Security Scan Job (`security-scan`)
- **Dependencies**: Runs after main tests pass
- **Tools**:
  - `safety`: Scans for known security vulnerabilities in dependencies
  - `bandit`: Static security analysis for Python code
- **Outputs**: Security scan reports as artifacts

### 3. Performance Test Job (`performance-test`)
- **Dependencies**: Runs after main tests pass
- **Features**:
  - Benchmark testing for critical endpoints
  - Performance regression detection
  - Load testing simulation

### 4. API Documentation Job (`api-documentation`)
- **Dependencies**: Runs after main tests pass
- **Purpose**: Generates and validates API documentation
- **Future**: Will integrate with Swagger/OpenAPI generation

### 5. Notification Job (`notify`)
- **Dependencies**: Runs after all jobs complete
- **Purpose**: Provides consolidated status reporting

## Test Categories

### Unit Tests
- **Location**: `tests/test_delete_endpoint_unit.py`, `tests/test_error_handling_comprehensive.py`
- **Purpose**: Test individual components in isolation
- **Coverage**: DELETE endpoint functionality, error handling, edge cases

### Integration Tests
- **Location**: `tests/test_integration.py`
- **Purpose**: Test complete workflows and component interactions
- **Coverage**: Template lifecycle, question associations, API consistency

### Performance Tests
- **Location**: `tests/test_performance.py`
- **Purpose**: Ensure system performance meets requirements
- **Coverage**: Response times, concurrent operations, bulk operations

## Configuration Files

### `.github/workflows/assessment-system-tests.yml`
Main GitHub Actions workflow definition with:
- Multi-Python version testing
- Comprehensive test execution
- Security scanning
- Performance monitoring
- Artifact collection

### `pytest.ini`
Pytest configuration with:
- Test discovery settings
- Custom markers for test categorization
- Verbose output configuration
- Warning filters

### `requirements-dev.txt`
Development dependencies including:
- Testing frameworks (pytest, pytest-flask, pytest-cov)
- Code quality tools (flake8, black, isort)
- Security tools (safety, bandit)
- Performance testing (pytest-benchmark, locust)

### `.bandit`
Security scanning configuration:
- Excluded directories and files
- Security test selection
- Confidence and severity levels
- Output formatting

### `pyproject.toml`
Code formatting configuration for black:
- Line length limits
- Python version targets
- File inclusion/exclusion patterns

## Running the Pipeline

### GitHub Actions (Automatic)
The pipeline runs automatically on:
- Push to `main` or `develop` branches
- Pull requests targeting `main` or `develop`
- Manual workflow dispatch

### Local Simulation
Run the pipeline locally using:
```bash
python run_local_pipeline.py
```

This script simulates the GitHub Actions workflow locally, including:
- Dependency installation
- Code quality checks
- Security scanning
- Database initialization
- Test execution
- Coverage reporting

## Test Execution

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Unit tests only
python -m pytest tests/ -m unit -v

# Integration tests only
python -m pytest tests/ -m integration -v

# Performance tests only
python -m pytest tests/ -m performance -v

# API endpoint tests
python -m pytest tests/ -m api -v
```

### Run with Coverage
```bash
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing
```

## Code Quality Standards

### Linting with flake8
- Maximum line length: 127 characters
- Maximum complexity: 10
- Checks for syntax errors and code quality issues

### Code Formatting with black
- Automatic code formatting
- Line length: 127 characters
- Target Python versions: 3.9, 3.10, 3.11

### Import Sorting with isort
- Automatic import organization
- Consistent import formatting

## Security Scanning

### Dependency Vulnerability Scanning
- Tool: `safety`
- Scans `requirements.txt` for known vulnerabilities
- Fails build on high-severity issues

### Static Code Analysis
- Tool: `bandit`
- Scans Python code for security issues
- Configurable severity and confidence levels

## Performance Monitoring

### Benchmark Testing
- Uses `pytest-benchmark` for performance measurement
- Tracks response times for critical endpoints
- Detects performance regressions

### Load Testing
- Simulates concurrent operations
- Tests bulk operations performance
- Validates system behavior under stress

## Artifacts and Reporting

### Test Results
- JUnit XML reports
- HTML coverage reports
- Performance benchmark results

### Security Reports
- Bandit JSON security scan reports
- Safety vulnerability reports

### Coverage Reports
- HTML coverage reports
- XML coverage for external services (Codecov)

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies in `requirements.txt` are installed
2. **Database Errors**: Run `python init_db.py` to initialize the database
3. **Test Failures**: Check test output for specific error messages
4. **Performance Issues**: Review benchmark results and optimize slow operations

### Debug Commands
```bash
# Check Python path issues
python -c "import sys; print(sys.path)"

# Verify database initialization
python -c "from models.database import db; print('DB OK')"

# Run single test with maximum verbosity
python -m pytest tests/test_delete_endpoint_unit.py::TestDeleteEndpoint::test_delete_existing_question -v -s
```

## Future Enhancements

1. **Deployment Pipeline**: Add staging and production deployment jobs
2. **Database Migrations**: Automated schema migration testing
3. **API Documentation**: Automated Swagger/OpenAPI generation
4. **Monitoring**: Integration with monitoring services
5. **Notifications**: Slack/email notifications for failures
6. **Parallel Testing**: Optimize test execution time with parallel runs

## Contributing

When contributing to the assessment system:
1. Ensure all tests pass locally using `python run_local_pipeline.py`
2. Add tests for new functionality
3. Follow code quality standards (flake8, black, isort)
4. Update documentation as needed
5. Verify security scans pass

## Support

For issues with the CI/CD pipeline:
1. Check GitHub Actions logs for detailed error information
2. Run local pipeline simulation to reproduce issues
3. Review test output and error messages
4. Consult this documentation for troubleshooting steps
