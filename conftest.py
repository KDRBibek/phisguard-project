"""
Pytest configuration and fixtures for PHISGUARD Flask application.
Provides test app, database, and authentication tokens for test cases.
"""

import os
import sys
import pytest

# Set environment variables at the very start before ANY app imports
os.environ['ADMIN_PASSWORD'] = 'test_admin_password'
os.environ['USER_PASSWORD'] = 'test_user_password'
os.environ['SECRET_KEY'] = 'test-secret-key'

# Force reimport of auth_store and app modules with correct env vars
# This ensures auth_store.py sees the test credentials when it checks them
if 'app.services.auth_store' in sys.modules:
    del sys.modules['app.services.auth_store']
if 'app' in sys.modules:
    del sys.modules['app']

from uuid import uuid4
from app import create_app, db
from app.models import User, Session
from app.test_config import TestConfig


@pytest.fixture(autouse=True)
def reset_rate_limiting(app):
    """
    Autouse fixture that resets rate limiting state before each test.
    Ensures test isolation for rate limiting tests.
    """
    # This runs before each test
    from app.services import auth_store
    auth_store._failed_attempts.clear()
    yield
    # Cleanup after test
    auth_store._failed_attempts.clear()


@pytest.fixture
def app():
    """
    Create and configure a test application instance.
    Uses in-memory SQLite for test isolation and speed.
    """
    app = create_app(config_class=TestConfig)
    
    # Create all tables in the test database
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """
    Flask test client for making requests to the app.
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    CLI test runner for executing Flask CLI commands.
    """
    return app.test_cli_runner()


@pytest.fixture
def init_db(app):
    """
    Initialize database with seed data for tests.
    Also clears rate limiting state to ensure test isolation.
    """
    # Clear rate limiting state for test isolation
    from app.services import auth_store
    auth_store._failed_attempts.clear()
    
    with app.app_context():
        # Manually create an admin user in database
        db.session.commit()
        return {}


@pytest.fixture
def admin_token(app):
    """
    Create and return a valid admin authentication token.
    Token is stored in database and can be used in X-Token header.
    """
    from app.services.auth_store import issue_token
    
    with app.app_context():
        # Create an admin user in database
        admin_user = User(id='test_admin', role='admin')
        db.session.add(admin_user)
        db.session.commit()
        
        # Issue a token for the admin user
        token = issue_token('admin', admin_user.id)
        return token


@pytest.fixture
def user_token(app):
    """
    Create and return a valid user authentication token.
    Token is stored in database and can be used in X-Token header.
    """
    from app.services.auth_store import issue_token
    
    with app.app_context():
        # Create a regular user in database
        regular_user = User(id='test_user_1', role='user')
        db.session.add(regular_user)
        db.session.commit()
        
        # Issue a token for the regular user
        token = issue_token('user', regular_user.id)
        return token


@pytest.fixture
def auth_headers_admin(admin_token):
    """
    Return HTTP headers dictionary with admin authentication token.
    Use in test client requests: client.get('/api/endpoint', headers=auth_headers_admin)
    """
    return {'X-Token': admin_token}


@pytest.fixture
def auth_headers_user(user_token):
    """
    Return HTTP headers dictionary with user authentication token.
    Use in test client requests: client.get('/api/endpoint', headers=auth_headers_user)
    """
    return {'X-Token': user_token}
