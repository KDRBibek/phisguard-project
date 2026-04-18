import os
import tempfile


class TestConfig:
    """Configuration for pytest - uses in-memory SQLite."""
    
    # Use in-memory SQLite for fast tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask test mode
    TESTING = True
    
    # Use a temp file for SECRET_KEY (tests don't need real security)
    SECRET_KEY = 'test-secret-key-not-for-production'
