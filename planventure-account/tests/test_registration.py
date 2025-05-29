import json
from unittest.mock import patch
import pytest
from app import db
from models.roles import UserRole

def test_register(client):
    """Test user registration."""
    response = client.post('/api/auth/register', json={
        'email': 'new@example.com',
        'password': 'Newpassword123'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'user' in data
    assert data['user']['email'] == 'new@example.com'

def test_register_duplicate_email(client, test_user):
    """Test registration with existing email."""
    response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'password': 'Password123'
    })
    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Account already exists'

def test_register_db_error(client, monkeypatch):
    """Test registration with database error."""
    def mock_commit():
        raise Exception("Database error")
    
    monkeypatch.setattr(db.session, 'commit', mock_commit)
    response = client.post('/api/auth/register', json={
        'email': 'new@example.com',
        'password': 'Password123'
    })
    
    assert response.status_code == 503
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Service temporarily unavailable'
    assert 'details' in data
    assert 'database error' in data['details'].lower()

def test_register_verify_email_error(client, monkeypatch):
    """Test registration with email verification error."""
    def mock_send_email(*args, **kwargs):
        raise Exception("Email error")
    
    monkeypatch.setattr('routes.auth.send_verification_email', mock_send_email)
    response = client.post('/api/auth/register', json={
        'email': 'new@example.com',
        'password': 'Password123'
    })
    # User should still be registered even if email fails
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'user' in data
    assert 'warning' in data

def test_register_with_role(client, admin_headers):
    """Test registering a new user with a specific role as admin."""
    response = client.post('/api/auth/register', 
        headers=admin_headers,
        json={
            'email': 'newtalent@example.com',
            'password': 'Password123',
            'role': UserRole.TALENT_LEAD.value
        }
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['user']['role'] == UserRole.TALENT_LEAD.value

def test_register_with_role_unauthorized(client, talent_lead_headers):
    """Test registering a new user with a role as non-admin."""
    response = client.post('/api/auth/register',
        headers=talent_lead_headers,
        json={
            'email': 'newuser@example.com',
            'password': 'Password123',
            'role': UserRole.ADMIN.value
        }
    )
    assert response.status_code == 403

def test_register_allowed_domain(client, app):
    """Test registration with an allowed email domain."""
    with app.app_context():
        original_domains = current_app.config.get('ALLOWED_EMAIL_DOMAINS')
        current_app.config['ALLOWED_EMAIL_DOMAINS'] = ['example.com', 'test.com']

    response = client.post('/api/auth/register', json={
        'email': 'user@example.com',
        'password': 'Password123!'
    })
    assert response.status_code == 201 # Assuming registration is successful
    data = json.loads(response.data)
    assert data['user']['email'] == 'user@example.com'

    # Restore original config
    with app.app_context():
        if original_domains is not None:
            current_app.config['ALLOWED_EMAIL_DOMAINS'] = original_domains
        else:
            # If it wasn't there, clean up by removing the key
            if 'ALLOWED_EMAIL_DOMAINS' in current_app.config:
                 del current_app.config['ALLOWED_EMAIL_DOMAINS']


def test_register_disallowed_domain(client, app):
    """Test registration with a disallowed email domain."""
    with app.app_context():
        original_domains = current_app.config.get('ALLOWED_EMAIL_DOMAINS')
        current_app.config['ALLOWED_EMAIL_DOMAINS'] = ['specific.com']

    response = client.post('/api/auth/register', json={
        'email': 'user@anotherdomain.com',
        'password': 'Password123!'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Invalid email domain'

    # Restore original config
    with app.app_context():
        if original_domains is not None:
            current_app.config['ALLOWED_EMAIL_DOMAINS'] = original_domains
        else:
            if 'ALLOWED_EMAIL_DOMAINS' in current_app.config:
                del current_app.config['ALLOWED_EMAIL_DOMAINS']
