"""
Unit tests for simulation endpoints (email and SMS phishing simulations).
Tests scenario retrieval, user actions (open/click/report), and feedback.
"""

import pytest
import json
from app.models import Email, UserAction


class TestEmailScenarios:
    """Test suite for email scenario endpoints."""
    
    def test_get_all_emails(self, client):
        """GET /api/emails should return list of emails."""
        response = client.get('/api/emails')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        # Emails are seeded during app initialization
        assert len(data) > 0
        
        # Verify email structure
        email = data[0]
        assert 'id' in email
        assert 'subject' in email
        assert 'sender' in email
        assert 'is_phishing' in email
    
    def test_get_single_email(self, client):
        """GET /api/emails/<id> should return specific email."""
        # Get all emails first
        response = client.get('/api/emails')
        emails = response.get_json()
        assert len(emails) > 0
        
        email_id = emails[0]['id']
        
        # Get specific email
        response = client.get(f'/api/emails/{email_id}')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['id'] == email_id
        assert 'subject' in data


class TestEmailActions:
    """Test suite for email action endpoints (open, click, report)."""
    
    def test_open_email_with_token(self, client, user_token):
        """POST /api/emails/<id>/open should record email open action."""
        # Get an email
        response = client.get('/api/emails')
        emails = response.get_json()
        email_id = emails[0]['id']
        
        # Open email with token
        response = client.post(
            f'/api/emails/{email_id}/open',
            data=json.dumps({'token': user_token}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'subject' in data
    
    def test_click_email_phishing(self, client, user_token, app):
        """POST /api/emails/<id>/click on phishing email should return feedback."""
        with app.app_context():
            # Find a phishing email
            phishing_email = Email.query.filter_by(is_phishing=True).first()
            if not phishing_email:
                pytest.skip("No phishing emails found in database")
            
            email_id = phishing_email.id
        
        response = client.post(
            f'/api/emails/{email_id}/click',
            data=json.dumps({'token': user_token}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['correct'] is False
        assert 'phishing' in data['message'].lower()
        assert 'time_to_action_seconds' in data
    
    def test_click_email_safe(self, client, user_token, app):
        """POST /api/emails/<id>/click on safe email should return positive feedback."""
        with app.app_context():
            # Find a safe email
            safe_email = Email.query.filter_by(is_phishing=False).first()
            if not safe_email:
                pytest.skip("No safe emails found in database")
            
            email_id = safe_email.id
        
        response = client.post(
            f'/api/emails/{email_id}/click',
            data=json.dumps({'token': user_token}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['correct'] is True
        assert 'legitimate' in data['message'].lower()
    
    def test_report_email_phishing(self, client, user_token, app):
        """POST /api/emails/<id>/report on phishing email should be correct."""
        with app.app_context():
            phishing_email = Email.query.filter_by(is_phishing=True).first()
            if not phishing_email:
                pytest.skip("No phishing emails found in database")
            
            email_id = phishing_email.id
        
        response = client.post(
            f'/api/emails/{email_id}/report',
            data=json.dumps({'token': user_token}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['correct'] is True
        assert 'phishing' in data['message'].lower()
    
    def test_report_email_safe(self, client, user_token, app):
        """POST /api/emails/<id>/report on safe email should be incorrect."""
        with app.app_context():
            safe_email = Email.query.filter_by(is_phishing=False).first()
            if not safe_email:
                pytest.skip("No safe emails found in database")
            
            email_id = safe_email.id
        
        response = client.post(
            f'/api/emails/{email_id}/report',
            data=json.dumps({'token': user_token}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['correct'] is False
        assert 'legitimate' in data['message'].lower()


class TestSMSScenarios:
    """Test suite for SMS scenario endpoints."""
    
    def test_get_all_sms(self, client):
        """GET /api/sms should return list of SMS messages."""
        response = client.get('/api/sms')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify SMS structure
        sms = data[0]
        assert 'id' in sms
        assert 'is_phishing' in sms


class TestUserAwareness:
    """Test suite for user awareness statistics endpoint."""
    
    def test_awareness_unauthenticated(self, client):
        """GET /api/awareness without token should return 401."""
        response = client.get('/api/awareness')
        
        assert response.status_code == 401
    
    def test_awareness_authenticated_no_actions(self, client, user_token):
        """GET /api/awareness with token but no actions should return stats."""
        headers = {'X-Token': user_token}
        response = client.get('/api/awareness', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_checked' in data
        assert 'correct' in data
        assert 'accuracy_percent' in data
        assert data['total_checked'] == 0
    
    def test_awareness_after_actions(self, client, user_token, app):
        """GET /api/awareness should reflect user actions."""
        headers = {'X-Token': user_token}
        
        with app.app_context():
            safe_email = Email.query.filter_by(is_phishing=False).first()
            if not safe_email:
                pytest.skip("No safe emails found in database")
            
            email_id = safe_email.id
        
        # User clicks on safe email (correct action)
        response = client.post(
            f'/api/emails/{email_id}/click',
            data=json.dumps({'token': user_token}),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Check awareness
        response = client.get('/api/awareness', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['total_checked'] == 1
        assert data['correct'] == 1
        assert data['accuracy_percent'] == 100.0


class TestUserFeedback:
    """Test suite for user feedback endpoints."""
    
    def test_feedback_unauthenticated(self, client):
        """GET /api/feedback without token should return 401."""
        response = client.get('/api/feedback')
        
        assert response.status_code == 401
    
    def test_feedback_empty(self, client, user_token):
        """GET /api/feedback with no actions should return empty list."""
        headers = {'X-Token': user_token}
        response = client.get('/api/feedback', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_feedback_after_action(self, client, user_token, app):
        """GET /api/feedback should return actions after user interacts."""
        headers = {'X-Token': user_token}
        
        with app.app_context():
            phishing_email = Email.query.filter_by(is_phishing=True).first()
            if not phishing_email:
                pytest.skip("No phishing emails found in database")
            
            email_id = phishing_email.id
        
        # User reports phishing email
        response = client.post(
            f'/api/emails/{email_id}/report',
            data=json.dumps({'token': user_token}),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Get feedback
        response = client.get('/api/feedback', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        
        feedback_item = data[0]
        assert feedback_item['channel'] == 'email'
        assert feedback_item['action'] == 'reported'
        assert feedback_item['correct'] is True
    
    def test_feedback_reset(self, client, user_token, app):
        """POST /api/feedback/reset should clear user actions."""
        headers = {'X-Token': user_token}
        
        with app.app_context():
            email = Email.query.first()
            if not email:
                pytest.skip("No emails found in database")
            
            email_id = email.id
        
        # Create an action
        client.post(
            f'/api/emails/{email_id}/click',
            data=json.dumps({'token': user_token}),
            content_type='application/json'
        )
        
        # Verify action exists
        response = client.get('/api/feedback', headers=headers)
        assert len(response.get_json()) > 0
        
        # Reset feedback
        response = client.post(
            '/api/feedback/reset',
            data=json.dumps({'token': user_token}),
            content_type='application/json',
            headers=headers
        )
        assert response.status_code == 200
        assert response.get_json()['ok'] is True
        
        # Verify feedback is cleared
        response = client.get('/api/feedback', headers=headers)
        assert len(response.get_json()) == 0
