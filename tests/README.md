# PHISGUARD Test Suite

This directory contains comprehensive automated tests for the PHISGUARD Flask backend application.

## Quick Start

### Run all tests
```bash
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_auth.py -v
```

### Run specific test
```bash
pytest tests/test_auth.py::TestLogin::test_admin_login_success -v
```

### Run with coverage (optional)
```bash
pytest tests/ --cov=app --cov-report=html
```

## Test Coverage

### Authentication Tests (`test_auth.py`)
- **Login Success**: Valid credentials for admin and user roles
- **Login Failure**: Invalid passwords and missing required fields
- **Rate Limiting**: 5 failed attempts trigger 15-minute lockout
- **Token Management**: Valid token resolution and expiration
- **Logout**: Token revocation and session cleanup

**Tests**: 14 passing

### Simulation Tests (`test_simulate.py`)
- **Email Scenarios**: Retrieve email phishing simulations
- **Email Actions**: Record user actions (open, click, report) on emails
- **SMS Scenarios**: Retrieve SMS phishing simulations
- **User Awareness**: Track user accuracy and performance metrics
- **User Feedback**: Get and reset user action history

**Tests**: 18 passing

### Admin Tests (`test_admin.py`)
- **Authorization**: Verify admin-only endpoints require admin token
- **Template Management**: Create, list, and delete email templates
- **Target Management**: Create and manage simulation targets (users)
- **Campaign Management**: Create campaigns with templates and targets
- **Analytics**: View campaign and user performance analytics

**Tests**: 17 passing

## Test Infrastructure

### Fixtures (`conftest.py`)

- **app**: Creates test application with in-memory SQLite database
- **client**: Flask test client for making HTTP requests
- **runner**: CLI test runner for Flask commands
- **admin_token**: Valid admin authentication token
- **user_token**: Valid user authentication token
- **auth_headers_admin**: HTTP headers with admin token
- **auth_headers_user**: HTTP headers with user token
- **reset_rate_limiting**: Autouse fixture for test isolation

### Test Configuration (`app/test_config.py`)

- Uses in-memory SQLite (`:memory:`) for fast test isolation
- `TESTING = True` enables test mode
- Isolated from production database

## Key Features Tested

✅ **Authentication**: Login, token management, rate limiting
✅ **Authorization**: Admin-only endpoints protected
✅ **Data Persistence**: User actions recorded in database
✅ **Feedback System**: Correct/incorrect evaluation of actions
✅ **Analytics**: Campaign and user performance tracking
✅ **Error Handling**: Proper HTTP status codes (400, 401, 403, 404, 429)

## Running Tests Locally

### Prerequisites
```bash
# Install test dependencies
pip install -r requirements.txt

# Set environment variables (for test credentials)
export ADMIN_PASSWORD=test_admin_password
export USER_PASSWORD=test_user_password
export SECRET_KEY=test-secret-key
```

### Execute tests
```bash
cd /path/to/phisguard
pytest tests/ -v
```

## Test Isolation

- Each test runs with a fresh, isolated in-memory database
- Rate limiting state (failed login attempts) is reset between tests
- Fixtures automatically clean up after each test
- No test dependencies - tests can run in any order

## Notes

- Tests use demo credentials set in environment during pytest initialization
- In-memory database means tests run very fast (~1-2 seconds total)
- All HTTP requests use `127.0.0.1` as test client IP
- Generated tokens are valid UUIDs stored in test database
