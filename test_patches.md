# filepath: /Users/josh/Python/3.7/Bite Map Project/bite-map/test_patches.md
# Test Patches for Bite Map Project

This document provides instructions for fixing the skipped tests in the Bite Map project.

## Summary of Skipped Tests

1. `test_extract_place()` in `test_place_utils.py` - Function behavior changed
2. `test_geocoder()` in `test_place_utils.py` - Logging behavior changed 
3. `test_process_queued_links()` in `test_worker.py` - Missing slugify dependency (FIXED)
4. `test_register_user()` in `test_auth.py` - Database connection required
5. `test_get_current_user()` in `test_auth.py` - Database connection required
6. `test_ingest_endpoint()` in `test_ingest.py` - Database connection required
7. `test_get_places_basic()` in `test_places.py` - Database connection required
8. `test_get_place_by_slug()` in `test_places.py` - Database connection required

## Fixing Database-Related Tests

For all tests marked "Database connection required", you can use the new database fixtures:

1. Import the fixtures in your test file:
   ```python
   from tests.db_fixtures import test_db_session, override_get_db
   ```

2. Create a mock app with dependency override:
   ```python
   @pytest.fixture
   def client_with_db(override_get_db):
       app.dependency_overrides[get_db] = override_get_db
       yield TestClient(app)
       app.dependency_overrides.clear()
   ```

3. Use the fixture in your test:
   ```python
   def test_register_user(client_with_db):
       # Use client_with_db instead of client
       response = client_with_db.post("/auth/register", json={"username": "test", "password": "test"})
       assert response.status_code == 200
   ```

## Fixing Specific Tests

### test_extract_place()

The function behavior changed. Update the test by:

1. Check the current implementation of the `extract_place` function
2. Update the test to match the new expected input/output
3. Add appropriate mocks for any external dependencies

### test_geocoder()

Logging behavior changed. Update the test by:

1. Use a custom logging handler to capture log messages
2. Update assertions to match the new logging behavior
3. Ensure the test is isolated from other tests

### Using the run_tests.py Script

The provided `run_tests.py` script helps run tests with a patched SQLite database:

```bash
# Run a specific test
./run_tests.py tests/test_worker.py::test_mock_extract_video_data

# Run all tests in a file
./run_tests.py tests/test_worker.py

# Run all tests
./run_tests.py
```

## Best Practices for Future Tests

1. Use SQLite for test databases instead of PostgreSQL
2. Use proper fixtures and mocks to avoid external dependencies
3. Organize tests to match the application structure
4. Keep tests isolated and independent of each other
