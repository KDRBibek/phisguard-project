"""
Unit tests for admin endpoints (template and campaign management).
Tests require_admin decorator, template creation, and campaign creation.
"""

import pytest
import json
from app.models import Template, Campaign, Target


class TestAdminAuthorization:
    """Test suite for admin authorization decorator."""
    
    def test_analytics_requires_admin(self, client):
        """GET /api/analytics without token should return 401."""
        response = client.get('/api/analytics')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'unauthorized' in data.get('error', '').lower()
    
    def test_analytics_rejects_user_token(self, client, user_token):
        """GET /api/analytics with user token should return 401."""
        headers = {'X-Token': user_token}
        response = client.get('/api/analytics', headers=headers)
        
        assert response.status_code == 401
    
    def test_analytics_allows_admin_token(self, client, admin_token):
        """GET /api/analytics with admin token should return 200."""
        headers = {'X-Token': admin_token}
        response = client.get('/api/analytics', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)


class TestTemplateManagement:
    """Test suite for email template management endpoints."""
    
    def test_get_templates_requires_admin(self, client):
        """GET /api/templates without token should return 401."""
        response = client.get('/api/templates')
        
        assert response.status_code == 401
    
    def test_get_templates_empty(self, client, admin_token):
        """GET /api/templates should return list of templates."""
        headers = {'X-Token': admin_token}
        response = client.get('/api/templates', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_create_template_success(self, client, admin_token):
        """POST /api/templates should create a new template."""
        headers = {'X-Token': admin_token}
        
        template_data = {
            'name': 'Test Template',
            'sender': 'test@example.com',
            'subject': 'Test Subject',
            'body': 'This is a test email body',
            'is_phishing': False,
            'link_text': 'Click here',
            'link_url': 'https://example.com',
            'feedback': 'This is feedback text'
        }
        
        response = client.post(
            '/api/templates',
            data=json.dumps(template_data),
            content_type='application/json',
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'Test Template'
        assert data['sender'] == 'test@example.com'
        assert 'id' in data
    
    def test_create_template_missing_required_field(self, client, admin_token):
        """POST /api/templates without required fields should return 400."""
        headers = {'X-Token': admin_token}
        
        template_data = {
            'name': 'Incomplete Template',
            # Missing 'sender', 'subject', 'body'
        }
        
        response = client.post(
            '/api/templates',
            data=json.dumps(template_data),
            content_type='application/json',
            headers=headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'missing' in data.get('error', '')
    
    def test_create_phishing_template(self, client, admin_token):
        """Create template marked as phishing."""
        headers = {'X-Token': admin_token}
        
        template_data = {
            'name': 'Phishing Template',
            'sender': 'fake@bank.com',
            'subject': 'Urgent: Verify your account',
            'body': 'Click to verify your account immediately',
            'is_phishing': True,
            'difficulty': 'hard'
        }
        
        response = client.post(
            '/api/templates',
            data=json.dumps(template_data),
            content_type='application/json',
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['is_phishing'] is True
    
    def test_delete_template(self, client, admin_token, app):
        """DELETE /api/templates/<id> should delete template."""
        headers = {'X-Token': admin_token}
        
        # Create template
        template_data = {
            'name': 'To Delete',
            'sender': 'test@example.com',
            'subject': 'Delete me',
            'body': 'This will be deleted'
        }
        
        response = client.post(
            '/api/templates',
            data=json.dumps(template_data),
            content_type='application/json',
            headers=headers
        )
        
        template_id = response.get_json()['id']
        
        # Delete template
        response = client.delete(
            f'/api/templates/{template_id}',
            headers=headers
        )
        
        assert response.status_code == 200
        assert response.get_json()['ok'] is True


class TestTargetManagement:
    """Test suite for target (user) management endpoints."""
    
    def test_get_targets_requires_admin(self, client):
        """GET /api/targets without token should return 401."""
        response = client.get('/api/targets')
        
        assert response.status_code == 401
    
    def test_create_single_target(self, client, admin_token):
        """POST /api/targets should create a single target."""
        headers = {'X-Token': admin_token}
        
        target_data = {
            'name': 'John Smith',
            'email': 'john@company.com',
            'department': 'IT',
            'role': 'Engineer'
        }
        
        response = client.post(
            '/api/targets',
            data=json.dumps(target_data),
            content_type='application/json',
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['name'] == 'John Smith'
        assert data[0]['email'] == 'john@company.com'
    
    def test_create_multiple_targets(self, client, admin_token):
        """POST /api/targets with targets list should create multiple."""
        headers = {'X-Token': admin_token}
        
        targets_data = {
            'targets': [
                {'name': 'Alice', 'email': 'alice@company.com', 'department': 'HR'},
                {'name': 'Bob', 'email': 'bob@company.com', 'department': 'Sales'}
            ]
        }
        
        response = client.post(
            '/api/targets',
            data=json.dumps(targets_data),
            content_type='application/json',
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert len(data) == 2


class TestCampaignManagement:
    """Test suite for campaign management endpoints."""
    
    def test_get_campaigns_requires_admin(self, client):
        """GET /api/campaigns without token should return 401."""
        response = client.get('/api/campaigns')
        
        assert response.status_code == 401
    
    def test_get_campaigns_empty(self, client, admin_token):
        """GET /api/campaigns should return list of campaigns."""
        headers = {'X-Token': admin_token}
        response = client.get('/api/campaigns', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_create_campaign_requires_template_and_target(self, client, admin_token):
        """POST /api/campaigns must have template and targets."""
        headers = {'X-Token': admin_token}
        
        # Create template
        template_data = {
            'name': 'Campaign Template',
            'sender': 'security@company.com',
            'subject': 'Security Update',
            'body': 'Please click the link to verify'
        }
        
        response = client.post(
            '/api/templates',
            data=json.dumps(template_data),
            content_type='application/json',
            headers=headers
        )
        template_id = response.get_json()['id']
        
        # Create target
        target_data = {
            'name': 'Test User',
            'email': 'test@company.com'
        }
        
        response = client.post(
            '/api/targets',
            data=json.dumps(target_data),
            content_type='application/json',
            headers=headers
        )
        target_id = response.get_json()[0]['id']
        
        # Create campaign
        campaign_data = {
            'name': 'Test Campaign',
            'template_id': template_id,
            'target_ids': [target_id],
            'state': 'draft'
        }
        
        response = client.post(
            '/api/campaigns',
            data=json.dumps(campaign_data),
            content_type='application/json',
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'Test Campaign'
        assert data['state'] == 'draft'
    
    def test_create_campaign_missing_template(self, client, admin_token):
        """POST /api/campaigns without template should return 400."""
        headers = {'X-Token': admin_token}
        
        campaign_data = {
            'name': 'Bad Campaign',
            # Missing template_id
        }
        
        response = client.post(
            '/api/campaigns',
            data=json.dumps(campaign_data),
            content_type='application/json',
            headers=headers
        )
        
        assert response.status_code == 400
    
    def test_create_campaign_missing_targets(self, client, admin_token):
        """POST /api/campaigns without targets should return 400."""
        headers = {'X-Token': admin_token}
        
        # Create template
        template_data = {
            'name': 'Campaign Template',
            'sender': 'security@company.com',
            'subject': 'Security Update',
            'body': 'Please click the link'
        }
        
        response = client.post(
            '/api/templates',
            data=json.dumps(template_data),
            content_type='application/json',
            headers=headers
        )
        template_id = response.get_json()['id']
        
        # Try to create campaign with no targets
        campaign_data = {
            'name': 'Campaign No Targets',
            'template_id': template_id,
            'target_ids': [],
            'segment_department': 'NonExistentDept'  # No targets will match
        }
        
        response = client.post(
            '/api/campaigns',
            data=json.dumps(campaign_data),
            content_type='application/json',
            headers=headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'no targets' in data.get('error', '').lower()


class TestAnalytics:
    """Test suite for analytics endpoints."""
    
    def test_analytics_overview(self, client, admin_token):
        """GET /api/admin/analytics/overview should return overview data."""
        headers = {'X-Token': admin_token}
        response = client.get('/api/admin/analytics/overview', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        # Data might be dict or None depending on database state
        assert isinstance(data, (dict, type(None)))
    
    def test_analytics_email(self, client, admin_token):
        """GET /api/admin/analytics/email should return email metrics."""
        headers = {'X-Token': admin_token}
        response = client.get('/api/admin/analytics/email', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        # Data might be dict or None depending on database state
        assert isinstance(data, (dict, type(None)))
    
    def test_analytics_sms(self, client, admin_token):
        """GET /api/admin/analytics/sms should return SMS metrics."""
        headers = {'X-Token': admin_token}
        response = client.get('/api/admin/analytics/sms', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        # Data might be dict, list, or None depending on database state
        assert isinstance(data, (dict, list, type(None)))
    
    def test_activity_email_actions(self, client, admin_token):
        """GET /api/admin/activity/email-actions should return recent actions."""
        headers = {'X-Token': admin_token}
        response = client.get('/api/admin/activity/email-actions', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
