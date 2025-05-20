import json
from datetime import datetime, timedelta, UTC
from unittest.mock import patch
import pytest
from flask import url_for
from flask_jwt_extended import create_access_token
from app import db
from models import User

@pytest.fixture
def mock_smtp(monkeypatch):
    """Mock SMTP connection for testing."""
    class MockSMTP:
        def __init__(self, *args, **kwargs):
            pass
        
        def starttls(self):
            return True
            
        def login(self, username, password):
            return True
            
        def send_message(self, msg):
            return True
            
        def quit(self):
            pass
            
        def __enter__(self):
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
    
    monkeypatch.setattr('smtplib.SMTP', MockSMTP)
    return MockSMTP

@pytest.fixture
def auth_headers(client, test_user):
    """Helper fixture to get authorization headers."""
    # First log in to get a valid token from the app's JWT manager
    response = client.post('/api/auth/login', json={
        'email': test_user.email,
        'password': 'password123'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    return {'Authorization': f'Bearer {data["access_token"]}'}

def test_register(client):
    """Test user registration."""
    response = client.post('/api/auth/register', json={
        'email': 'new@example.com',
        'password': 'newpassword123'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'user' in data
    assert data['user']['email'] == 'new@example.com'

def test_register_duplicate_email(client, test_user):
    """Test registration with existing email."""
    response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Email already registered'

def test_register_db_error(client, monkeypatch):
    """Test registration with database error."""
    def mock_commit():
        raise Exception("Database error")
    
    monkeypatch.setattr(db.session, 'commit', mock_commit)
    response = client.post('/api/auth/register', json={
        'email': 'new@example.com',
        'password': 'newpassword123'
    })
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data
    assert 'details' in data

def test_register_verify_email_error(client, monkeypatch):
    """Test registration with email verification error."""
    def mock_send_email(*args, **kwargs):
        raise Exception("Email error")
    
    monkeypatch.setattr('routes.auth.send_verification_email', mock_send_email)
    response = client.post('/api/auth/register', json={
        'email': 'new@example.com',
        'password': 'newpassword123'
    })
    # User should still be registered even if email fails
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'user' in data

def test_login_success(client, test_user):
    """Test successful login."""
    # Set a strong secret key for testing
    client.application.config['JWT_SECRET_KEY'] = 'this-is-a-secret-key-for-testing-32-bytes'
    
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    print(f"\n=== Login Response ===")
    print(f"Status code: {response.status_code}")
    print(f"Access token: {data['access_token']}")
    print(f"Token type: {data.get('token_type', 'Not specified')}")
    print(f"User info: {data.get('user', {})}")
    print(f"JWT Secret Key: {client.application.config['JWT_SECRET_KEY']}")
    print("====================")

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post('/api/auth/login', json={
        'email': 'wrong@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Invalid email or password'

def test_login_missing_fields(client):
    """Test login with missing fields."""
    response = client.post('/api/auth/login', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Email and password are required'

def test_login_token_generation_error(client, test_user, monkeypatch):
    """Test login with token generation error."""
    def mock_create_token(*args, **kwargs):
        raise Exception("Token generation error")
    
    monkeypatch.setattr('routes.auth.create_access_token', mock_create_token)
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data
    assert 'details' in data

def get_auth_token(client, test_user):
    """Helper function to get auth token."""
    with client.application.app_context():
        # Update user's last login to ensure session is active
        test_user.last_login = datetime.now(UTC)
        db.session.commit()
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        return data['access_token']

def test_verify_email_success(client, test_user):
    """Test successful email verification."""
    response = client.get('/api/auth/verify-email/test-verification-token')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Email verified successfully'

def test_verify_email_invalid_token(client):
    """Test email verification with invalid token."""
    response = client.get('/api/auth/verify-email/invalid-token')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Invalid verification token'

def test_verify_email_db_error(client, test_user, monkeypatch):
    """Test verify email with database error."""
    def mock_commit():
        raise Exception("Database error")
    
    with client.application.app_context():
        test_user.verification_token = 'test-token'
        db.session.add(test_user)
        db.session.commit()
        
    monkeypatch.setattr(db.session, 'commit', mock_commit)
    response = client.get('/api/auth/verify-email/test-token')
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data

def test_forgot_password_existing_email(client, test_user, mock_smtp):
    """Test forgot password with existing email."""
    response = client.post('/api/auth/forgot-password', json={
        'email': 'test@example.com'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Password reset instructions sent'

def test_forgot_password_nonexistent_email(client):
    """Test forgot password with non-existent email."""
    response = client.post('/api/auth/forgot-password', json={
        'email': 'nonexistent@example.com'
    })
    assert response.status_code == 200  # Should still return 200 for security
    data = json.loads(response.data)
    assert data['message'] == 'If the email exists, you will receive a reset link'

def test_forgot_password_missing_email(client):
    """Test forgot password with missing email."""
    response = client.post('/api/auth/forgot-password', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Email is required'

def test_forgot_password_email_error(client, test_user, mock_smtp, monkeypatch):
    """Test forgot password with email sending error."""
    def mock_send_email(*args, **kwargs):
        return False
    
    monkeypatch.setattr('routes.auth.send_password_reset_email', mock_send_email)
    response = client.post('/api/auth/forgot-password', json={
        'email': 'test@example.com'
    })
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Failed to send reset email'

def test_get_current_user_success(client, test_user, auth_headers):
    """Test getting current user details with valid token."""
    with client.application.app_context():
        response = client.get('/api/auth/me', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['email'] == 'test@example.com'

def test_get_current_user_no_token(client):
    """Test getting current user without token."""
    response = client.get('/api/auth/me')
    assert response.status_code == 401

def test_get_current_user_db_error(client, auth_headers, monkeypatch):
    """Test get current user with database error."""
    def mock_execute(*args, **kwargs):
        raise Exception("Database error")
    
    monkeypatch.setattr('routes.auth.db.session.execute', mock_execute)
    response = client.get('/api/auth/me', headers=auth_headers)
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data
    assert 'details' in data

def test_get_profile_success(client, test_user, auth_headers):
    """Test getting user profile with valid token."""
    with client.application.app_context():
        response = client.get('/api/auth/profile', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['email'] == 'test@example.com'

def test_update_profile_success(client, test_user, auth_headers):
    """Test updating user profile."""
    with client.application.app_context():
        profile_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '1234567890'
        }
        response = client.put('/api/auth/profile',
            json=profile_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['first_name'] == 'John'
        assert data['last_name'] == 'Doe'
        assert data['phone'] == '1234567890'

def test_update_profile_no_token(client):
    """Test updating profile without token."""
    response = client.put('/api/auth/profile', json={
        'first_name': 'John'
    })
    assert response.status_code == 401

def test_update_profile_invalid_field(client, test_user, auth_headers):
    """Test updating profile with invalid field."""
    response = client.put('/api/auth/profile', json={
        'invalid_field': 'value'
    }, headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'invalid_field' not in data

def test_update_profile_db_error(client, test_user, auth_headers, monkeypatch):
    """Test profile update with database error."""
    def mock_commit():
        raise Exception("Database error")
    
    monkeypatch.setattr(db.session, 'commit', mock_commit)
    response = client.put('/api/auth/profile', json={
        'first_name': 'John'
    }, headers=auth_headers)
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data
    assert 'details' in data

def test_profile_data_error(client, test_user, auth_headers, monkeypatch):
    """Test profile endpoints with data errors."""
    def mock_to_dict(*args, **kwargs):
        raise Exception("Data error")
    
    monkeypatch.setattr(User, 'to_dict', mock_to_dict)
    
    # Test GET request
    response = client.get('/api/auth/profile', headers=auth_headers)
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data
    
    # Test PUT request
    response = client.put('/api/auth/profile', json={'first_name': 'John'}, headers=auth_headers)
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data

def test_change_password_success(client, test_user, auth_headers):
    """Test successful password change."""
    response = client.post('/api/auth/change-password', json={
        'current_password': 'password123',
        'new_password': 'newpassword123'
    }, headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Password changed successfully'

    # Verify can login with new password
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'newpassword123'
    })
    assert response.status_code == 200

def test_change_password_wrong_current(client, test_user, auth_headers):
    """Test password change with wrong current password."""
    response = client.post('/api/auth/change-password', json={
        'current_password': 'wrongpassword',
        'new_password': 'newpassword123'
    }, headers=auth_headers)
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['error'] == 'Current password is incorrect'

def test_change_password_missing_fields(client, test_user, auth_headers):
    """Test password change with missing fields."""
    response = client.post('/api/auth/change-password', json={}, headers=auth_headers)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Current and new password are required'

def test_change_password_db_error(client, test_user, auth_headers, monkeypatch):
    """Test change password with database error."""
    def mock_commit():
        raise Exception("Database error")
    
    monkeypatch.setattr(db.session, 'commit', mock_commit)
    response = client.post('/api/auth/change-password', json={
        'current_password': 'password123',
        'new_password': 'newpassword123'
    }, headers=auth_headers)
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data

def setup_password_reset_token(client, test_user):
    """Helper function to set up password reset token."""
    with client.application.app_context():
        test_user.reset_token = 'test-reset-token'
        test_user.reset_token_expires = datetime.now(UTC) + timedelta(hours=1)
        db.session.add(test_user)
        db.session.commit()
        return 'test-reset-token'

def test_reset_password_success(client, test_user):
    """Test password reset with valid token."""
    with client.application.app_context():
        # Use the helper function to set up the token
        token = setup_password_reset_token(client, test_user)

        # Perform the password reset
        response = client.post('/api/auth/reset-password/test-reset-token',
            json={'password': 'newpassword123'}
        )
        assert response.status_code == 200
        assert json.loads(response.data)['message'] == 'Password reset successful'

        # Verify the new password works
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'newpassword123'
        })
        assert response.status_code == 200
        assert 'access_token' in json.loads(response.data)

def test_reset_password_invalid_token(client):
    """Test password reset with invalid token."""
    response = client.post('/api/auth/reset-password/invalid-token',
        json={'password': 'newpassword123'}
    )
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'Invalid or expired reset token'

def test_reset_password_expired_token(client, test_user):
    """Test reset password with expired token."""
    test_user.reset_token = 'expired-token'
    test_user.reset_token_expires = datetime.now(UTC) - timedelta(hours=2)
    db.session.commit()
    
    response = client.post('/api/auth/reset-password/expired-token', json={
        'password': 'newpassword123'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Invalid or expired reset token'

def test_password_reset_db_error(client, test_user, monkeypatch):
    """Test password reset with database error."""
    def mock_commit():
        raise Exception("Database error")
    
    with client.application.app_context():
        # Set up a valid reset token
        test_user.reset_token = 'test-token'
        test_user.reset_token_expires = datetime.now(UTC) + timedelta(hours=1)
        db.session.add(test_user)
        db.session.commit()
        
    monkeypatch.setattr(db.session, 'commit', mock_commit)
    response = client.post('/api/auth/reset-password/test-token', json={'password': 'newpass'})
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data
