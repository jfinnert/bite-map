# Test Strategy for Bite Map

## Current Status - May 22, 2025

✅ **Test Consolidation Complete**: All tests have been moved to the `/tests/` directory  
✅ **API Tests Fixed**: Login endpoint test now passes  
✅ **Worker Tests Fixed**: Basic worker tests now pass  
✅ **Deprecation Warnings Fixed**: Updated SQLAlchemy and Pydantic code  
✅ **Hybrid Testing Strategy**: Implemented both local SQLite and Docker PostgreSQL testing  
✅ **Import Handling**: Added robust import resolution with `import_helper.py`  
✅ **Database Fixtures**: Implemented SQLite database fixtures for fast local testing

## Hybrid Testing Strategy

The Bite Map project employs a **hybrid testing strategy** that offers the best of both worlds:

1. **Local Development Testing**: Using SQLite for fast feedback cycles
2. **Docker-based Production Testing**: Using PostgreSQL for production-like validation

This approach maximizes developer productivity while ensuring compatibility with the production environment.

## Test Directory Organization

The Bite Map project uses a standardized testing approach with all tests located in the 
root `/tests` directory. This organization follows Python best practices and simplifies 
the test execution and maintenance.

## Test Structure

The test directory structure mirrors the application structure:

```
tests/
├── conftest.py           # Test fixtures and configuration
├── db_fixtures.py        # Database fixtures for testing
├── import_helper.py      # Import resolution for flexible test environments
├── test_worker.py        # Tests for the worker.py in the project root
├── api/                  # Tests for API endpoints
│   ├── test_auth.py
│   ├── test_ingest.py
│   └── test_places.py
└── utils/                # Tests for utility functions
    └── test_place_utils.py
```

## Running Tests

### Local Development Testing (Fast)

For quick feedback during development, use SQLite-based local testing:

```bash
# Run all tests locally with SQLite
make test-local

# Run specific test modules locally
make test-local-worker
make test-local-api
```

These commands use `run_tests.py` which:
- Patches the database connection to use SQLite
- Mocks hard-to-install dependencies
- Provides flexible import paths

### Docker-based Testing (Production-like)

For production-like validation, use PostgreSQL in Docker containers:

```bash
# Run all tests in Docker container with PostgreSQL
make test-docker

# Run specific test modules in Docker
make test-docker-worker
make test-docker-api
```

### Default Test Command

For convenience, the default test command runs the faster local tests:

```bash
make test
```

### CI Environment Testing

For Continuous Integration environments, a specialized configuration is available:

```bash
make test-ci
```

## Test Utilities

### Import Helper

The `import_helper.py` provides utilities for handling imports in different environments:

- `flexible_import(module_name)`: Import from either direct path or `app.` prefixed path
- `get_module(name)`: Get a module by name, trying different path strategies
- `patch_module_path(module_name)`: Decorator to ensure tests can import required modules

### Database Fixtures

The `db_fixtures.py` provides SQLite-based database fixtures for testing without PostgreSQL:

- In-memory SQLite database for fast testing
- Automatic schema creation
- Test data provisioning

## Writing New Tests

When writing new tests:

1. Place them in the appropriate directory under `/tests/`
2. Use `import_helper.py` for flexible imports
3. Use the database fixtures from `conftest.py` for database tests
4. Verify tests pass in both local and Docker environments

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
