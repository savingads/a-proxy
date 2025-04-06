# A-Proxy Test Suite

This directory contains unit tests for the A-Proxy application.

## Running Tests

### Using Docker (Recommended)

When running A-Proxy in Docker, you can run tests within the container:

```bash
# Run all tests
docker-compose exec a-proxy python tests/test_runner.py

# Run a specific test file
docker-compose exec a-proxy python -m unittest tests/test_database.py

# Run a specific test case or method
docker-compose exec a-proxy python -m unittest tests.test_database.TestDatabase
docker-compose exec a-proxy python -m unittest tests.test_database.TestDatabase.test_save_and_get_persona
```

### Manual Method

If you're running A-Proxy directly on your system:

```bash
# Run all tests
python tests/test_runner.py

# Run individual test files
python -m unittest tests/test_database.py

# Run a specific test case or method
python -m unittest tests.test_database.TestDatabase
python -m unittest tests.test_database.TestDatabase.test_save_and_get_persona
```

## Test Structure

- `test_runner.py`: Main test runner script that discovers and runs all tests
- `test_config.py`: Shared test configuration, fixtures, and utility functions
- `test_database.py`: Tests for database operations
- `test_app.py`: Tests for Flask application routes
- `test_utils_vpn.py`: Tests for VPN utility functions
- `test_templates.py`: Tests for template inheritance and rendering
- `test_migration.py`: Tests for database migration functionality

## Writing New Tests

When adding new tests:

1. Create a new file named `test_*.py` following the naming convention
2. Use the `unittest` framework for consistency
3. Import shared fixtures from `test_config.py` where appropriate
4. Add docstrings to test classes and methods for clarity
5. Update this README if necessary to document new test files

## Test Database

Tests use a temporary SQLite database file that is created and cleaned up for each test. This ensures that tests don't modify the main application database.

## Mocking External Services

Tests that interact with external services (like VPN operations and IP geo-location) use mocking to avoid actual network requests.
