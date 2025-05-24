# Bite Map Test Suite Review

## Current Test Status

The test suite is partially working, with 5 passing tests (38.5%) and 8 failing tests (61.5%). The working tests are primarily in the worker module, while the failing tests are in API and utility modules.

## Passing Tests

1. `test_worker.py::test_mock_extract_video_data`
2. `test_worker.py::test_parse_address`
3. `test_worker.py::test_process_queued_links`
4. `test_api/test_auth.py::test_login`
5. `test_api/test_ingest.py::test_health_endpoint`

## Failing Tests and Required Fixes

### Authentication Module (2 of 3 failing)

1. **test_register_user**: Missing `create_user` function in the auth module
   - The test needs to mock `api.endpoints.auth.create_user` but it doesn't exist
   - **Fix**: Create this function or update the test to use the real implementation

2. **test_get_current_user**: Route not found (404)
   - The `/auth/me` endpoint seems to be missing
   - **Fix**: Add this endpoint to the auth router

### Ingest Module (1 of 2 failing)

1. **test_ingest_endpoint**: Missing `add_source_link` function
   - The test tries to mock `api.endpoints.ingest.add_source_link`
   - **Fix**: Add this function to the ingest module or update the test

### Places Module (2 of 2 failing)

1. **test_get_places_basic**: Route not found (404)
   - The `/places/` route seems to be misconfigured
   - **Fix**: Check router configuration and update API path

2. **test_get_place_by_slug**: Missing function
   - The `get_place_by_slug` function doesn't exist in the places module
   - **Fix**: Implement this function or update the test

### Utilities Module (3 of 3 failing)

1. **test_format_place_slug**: Different behavior than expected
   - The function handles apostrophes differently than the test expects
   - **Fix**: Update the test expectation to match the actual behavior 

2. **test_extract_place**: Missing NLP processor
   - The `utils.nlp.place_extractor.nlp_processor` attribute doesn't exist
   - **Fix**: Check the actual implementation and update the test accordingly

3. **test_geocoder**: Returns None instead of expected data
   - Even with mocks, the function returns None
   - **Fix**: Debug the geocoder implementation to ensure it handles the mocked response correctly

## Root Causes

1. **API Structure Mismatch**: The API endpoints in the tests don't match the actual implementation
2. **Missing Helper Functions**: Several utility functions expected by tests are missing
3. **Implementation Changes**: Some functions behave differently than the tests expect

## Recommended Test Improvements

1. **Proper Isolation**: Use better dependency injection for easier mocking
2. **More Comprehensive Fixtures**: Create reusable test data
3. **Better Error Handling**: Add tests for error cases
4. **Integration Tests**: Add end-to-end tests for critical flows

## Action Plan

1. Fix the User model (completed)
2. Add the missing utility functions
3. Update the API endpoints to match test expectations
4. Fix or update the utility tests
5. Add comprehensive documentation on test patterns
6. Create a test coverage report
