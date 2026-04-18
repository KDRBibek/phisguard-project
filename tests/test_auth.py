"""
Unit tests for authentication endpoints and flow.
Tests login success, login failure, rate limiting, and logout.
"""

import pytest
import json
from app.services.auth_store import get_user_id_from_token


class TestLogin:
    """Test suite for login endpoint (/api/login)."""
    
    def test_admin_login_success(self, client):
        """Admin login with correct password should return token."""
        response = client.post(
            '/api/login',
            data=json.dumps({'password': 'test_admin_password', 'role': 'admin'}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['ok'] is True
        assert 'token' in data
        assert data['role'] == 'admin'
        assert data['user_id'] == 'admin'
    
    def test_user_login_success(self, client):
        """User login with correct password and name should return token."""
        response = client.post(
            '/api/login',
            data=json.dumps({
                'password': 'test_user_password',
                'role': 'user',
                'name': 'John Doe'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['ok'] is True
        assert 'token' in data
        assert data['role'] == 'user'
        assert 'user_id' in data
    
    def test_admin_login_wrong_password(self, client):
        """Admin login with wrong password should return 403."""
        response = client.post(
            '/api/login',
            data=json.dumps({'password': 'wrong_password', 'role': 'admin'}),
            content_type='application/json'
        )
        
        assert response.status_code == 403
        data = response.get_json()
        assert data['ok'] is False
        assert 'error' in data
    
    def test_user_login_wrong_password(self, client):
        """User login with wrong password should return 403."""
        response = client.post(
            '/api/login',
            data=json.dumps({
                'password': 'wrong_password',
                'role': 'user',
                'name': 'Jane Doe'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 403
        data = response.get_json()
        assert data['ok'] is False
    
    def test_user_login_missing_name(self, client):
        """User login without name should return 400."""
        response = client.post(
            '/api/login',
            data=json.dumps({
                'password': 'test_user_password',
                'role': 'user'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['ok'] is False
        assert 'name is required' in data['error']


class TestRateLimiting:
    """Test suite for rate limiting on login endpoint."""
    
    def test_rate_limiting_admin_lockout(self, client):
        """After 5 failed admin login attempts, client should be locked out (429)."""
        failed_attempts = 0
        
        # Make 5 failed attempts
        for i in range(5):
            response = client.post(
                '/api/login',
                data=json.dumps({'password': 'wrong_password', 'role': 'admin'}),
                content_type='application/json'
            )
            assert response.status_code == 403
            failed_attempts += 1
        
        # 6th attempt should be rate limited (429)
        response = client.post(
            '/api/login',
            data=json.dumps({'password': 'wrong_password', 'role': 'admin'}),
            content_type='application/json'
        )
        
        assert response.status_code == 429
        data = response.get_json()
        assert data['ok'] is False
        assert 'too many failed attempts' in data['error']
    
    def test_rate_limiting_user_lockout(self, client):
        """After 5 failed user login attempts, client should be locked out."""
        # Make 5 failed attempts
        for i in range(5):
            response = client.post(
                '/api/login',
                data=json.dumps({
                    'password': 'wrong_password',
                    'role': 'user',
                    'name': 'Test User'
                }),
                content_type='application/json'
            )
            assert response.status_code == 403
        
        # 6th attempt should be rate limited
        response = client.post(
            '/api/login',
            data=json.dumps({
                'password': 'wrong_password',
                'role': 'user',
                'name': 'Test User'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 429
    
    def test_successful_login_clears_failed_attempts(self, client):
        """Successful login should clear failed attempt counter."""
        # Make 2 failed attempts
        for i in range(2):
            client.post(
                '/api/login',
                data=json.dumps({'password': 'wrong_password', 'role': 'admin'}),
                content_type='application/json'
            )
        
        # Successful login should clear counter
        response = client.post(
            '/api/login',
            data=json.dumps({'password': 'test_admin_password', 'role': 'admin'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Should be able to make new attempts without rate limiting
        response = client.post(
            '/api/login',
            data=json.dumps({'password': 'wrong_password', 'role': 'admin'}),
            content_type='application/json'
        )
        assert response.status_code == 403  # Failed login, but not rate limited


class TestLogout:
    """Test suite for logout endpoint (/api/logout)."""
    
    def test_logout_with_token(self, client, admin_token):
        """Logout with valid token should revoke the token."""
        response = client.post(
            '/api/logout',
            data=json.dumps({'token': admin_token}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['ok'] is True
        
        # Token should no longer be valid
        user_id = get_user_id_from_token(admin_token)
        assert user_id is None
    
    def test_logout_with_header_token(self, client, admin_token):
        """Logout with token in header should also work."""
        headers = {'X-Token': admin_token}
        response = client.post(
            '/api/logout',
            headers=headers,
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['ok'] is True


class TestTokenValidation:
    """Test suite for token validation and expiration."""
    
    def test_valid_admin_token(self, app, admin_token):
        """Valid admin token should resolve to correct user and role."""
        from app.services.auth_store import get_user_id_from_token, is_admin_token
        
        with app.app_context():
            user_id = get_user_id_from_token(admin_token)
            assert user_id == 'test_admin'
            assert is_admin_token(admin_token) is True
    
    def test_valid_user_token(self, app, user_token):
        """Valid user token should resolve to user and not be admin."""
        from app.services.auth_store import get_user_id_from_token, is_admin_token
        
        with app.app_context():
            user_id = get_user_id_from_token(user_token)
            assert user_id is not None
            assert is_admin_token(user_token) is False
    
    def test_invalid_token(self, app):
        """Invalid token should return None."""
        from app.services.auth_store import get_user_id_from_token
        
        with app.app_context():
            user_id = get_user_id_from_token('invalid_token_xyz')
            assert user_id is None
