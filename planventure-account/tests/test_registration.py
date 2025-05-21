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
