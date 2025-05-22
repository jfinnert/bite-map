# Test Strategy for Bite Map

## Current Status - May 21, 2025

✅ **Test Consolidation Complete**: All tests have been moved to the `/tests/` directory  
✅ **API Tests Fixed**: Login endpoint test now passes  
✅ **Worker Tests Fixed**: Basic worker tests now pass  
✅ **Deprecation Warnings Fixed**: Updated SQLAlchemy and Pydantic code Project

## Test Directory Organization

The Bite Map project uses a standardized testing approach with all tests located in the 
root `/tests` directory. This organization follows Python best practices and simplifies 
the test execution and maintenance.

## Test Structure

The test directory structure mirrors the application structure:

```
tests/
├── conftest.py           # Test fixtures and configuration
├── test_worker.py        # Tests for the worker.py in the project root
├── api/                  # Tests for API endpoints
│   ├── test_auth.py
│   ├── test_ingest.py
│   └── test_places.py
└── utils/                # Tests for utility functions
    └── test_place_utils.py
```

## Running Tests

### Using Docker (Recommended)

To run all tests:
```bash
make test-in-container
```

To run specific test files:
```bash
docker-compose -f docker-compose.test.yml exec test pytest -xvs tests/path/to/test_file.py
```

### Using Local Environment

To run tests in the local environment:
```bash
cd /path/to/bite-map
PYTHONPATH=. pytest -xvs tests/
```

## Mocking Strategy

The tests use pytest-mock to mock database connections and external services.
Mock configurations are centralized in `conftest.py` where possible.

## Lint and Type Checking

To ensure code quality, run:
```bash
# Add linting commands here when implemented
```

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Merge to main branch
