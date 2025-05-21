import json
from datetime import datetime, timedelta, UTC
from unittest.mock import patch
import pytest
from flask import url_for
from flask_jwt_extended import create_access_token
from app import db
from models import User
from models.roles import UserRole

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
def auth_headers(test_user):
    """Helper fixture to get authorization headers."""
    token = create_access_token(identity=str(test_user.id))
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def admin_headers(admin_user):
    """Get authorization headers for admin user."""
    token = create_access_token(identity=str(admin_user.id))
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def talent_lead_headers(talent_lead_user):
    """Get authorization headers for talent lead user."""
    token = create_access_token(identity=str(talent_lead_user.id))
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def candidate_headers(candidate_user):
    """Get authorization headers for candidate user."""
    token = create_access_token(identity=str(candidate_user.id))
    return {'Authorization': f'Bearer {token}'}

# User fixtures moved to conftest.py

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

def get_auth_token(app, client, test_user):
    """Helper function to get auth token."""
    with app.app_context():
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        return data['access_token']

def test_verify_email_success(app, client, test_user):
    """Test successful email verification."""
    with app.app_context():        # Get fresh user instance
        user = db.session.get(User, test_user.id)
        user.verification_token = 'test-verification-token'
        user.verification_token_expires = datetime.now(UTC) + timedelta(hours=1)
        db.session.commit()
        
        response = client.get('/api/auth/verify-email/test-verification-token')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Email verified successfully'
        
        # Verify the user's email is actually marked as verified
        db.session.refresh(user)
        assert user.is_verified
        assert user.verification_token is None

def test_verify_email_invalid_token(client):
    """Test email verification with invalid token."""
    response = client.get('/api/auth/verify-email/invalid-token')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Invalid verification token'

def test_verify_email_db_error(app, client, test_user, monkeypatch):
    """Test verify email with database error."""
    def mock_commit():
        raise Exception("Database error")
    
    with app.app_context():
        # Get fresh user instance
        user = db.session.get(User, test_user.id)
        user.verification_token = 'test-token'
        user.verification_token_expires = datetime.now(UTC) + timedelta(hours=1)
        db.session.commit()
        
        # Setup mock
        monkeypatch.setattr(db.session, 'commit', mock_commit)
        
        # Test
        response = client.get('/api/auth/verify-email/test-token')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
        
        # Reset session after test
        db.session.rollback()
        monkeypatch.undo()

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

def test_get_current_user_success(app, client, test_user, auth_headers):
    """Test getting current user details with valid token."""
    response = client.get('/api/auth/me', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['email'] == test_user.email

def test_get_current_user_no_token(client):
    """Test getting current user without token."""
    response = client.get('/api/auth/me')
    assert response.status_code == 401

def test_get_current_user_db_error(app, client, test_user, auth_headers, monkeypatch):
    """Test get current user with database error."""
    def mock_execute(*args, **kwargs):
        raise Exception("Database error")
    
    monkeypatch.setattr('routes.auth.db.session.execute', mock_execute)
    response = client.get('/api/auth/me', headers=auth_headers)
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data
    assert 'details' in data

def test_get_profile_success(app, client, test_user, auth_headers):
    """Test getting user profile with valid token."""
    response = client.get('/api/auth/profile', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['email'] == test_user.email

def test_update_profile_success(app, client, test_user, auth_headers):
    """Test updating user profile."""
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
      # Verify changes were saved
    with app.app_context():
        user = db.session.get(User, test_user.id)
        assert user.first_name == 'John'
        assert user.last_name == 'Doe'
        assert user.phone == '1234567890'

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
    
    # Setup mock
    monkeypatch.setattr(db.session, 'commit', mock_commit)
    
    # Test
    response = client.put('/api/auth/profile', json={
        'first_name': 'John'
    }, headers=auth_headers)
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data
    assert 'details' in data
    
    # Reset session after test
    db.session.rollback()
    monkeypatch.undo()

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
    
    # Setup mock
    monkeypatch.setattr(db.session, 'commit', mock_commit)
    
    # Test
    response = client.post('/api/auth/change-password', json={
        'current_password': 'password123',
        'new_password': 'newpassword123'
    }, headers=auth_headers)
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data
    
    # Reset session after test
    db.session.rollback()
    monkeypatch.undo()

def setup_password_reset_token(app, test_user):
    """Helper function to set up password reset token."""
    with app.app_context():
        # Get a fresh user instance from the database
        user = db.session.get(User, test_user.id)
        user.reset_token = 'test-reset-token'
        user.reset_token_expires = datetime.now(UTC) + timedelta(hours=1)
        db.session.commit()
        return 'test-reset-token'

def test_reset_password_success(app, client, test_user):
    """Test password reset with valid token."""
    with app.app_context():
        # Use the helper function to set up the token
        token = setup_password_reset_token(app, test_user)
        
        # Perform the password reset
        response = client.post(f'/api/auth/reset-password/{token}',
            json={'password': 'newpassword123'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Password reset successful'

        # Verify the new password works
        response = client.post('/api/auth/login', json={
            'email': test_user.email,
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
    data = json.loads(response.data)
    assert data['error'] == 'Invalid or expired reset token'

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

def test_password_reset_db_error(app, client, test_user, monkeypatch):
    """Test password reset with database error."""
    def mock_commit():
        raise Exception("Database error")
    
    with app.app_context():
        # Get fresh user instance and set up token
        token = setup_password_reset_token(app, test_user)
        
        # Setup mock
        monkeypatch.setattr(db.session, 'commit', mock_commit)
        
        # Test
        response = client.post(f'/api/auth/reset-password/{token}',
            json={'password': 'newpassword123'}
        )
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
        
        # Reset session after test
        db.session.rollback()
        monkeypatch.undo()

def test_admin_list_roles(client, admin_headers):
    """Test listing roles as admin."""
    response = client.get('/api/auth/roles', headers=admin_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'roles' in data
    roles = data['roles']
    assert len(roles) == 3  # ADMIN, TALENT_LEAD, CANDIDATE
    assert any(role['value'] == UserRole.ADMIN.value for role in roles)
    assert any(role['value'] == UserRole.TALENT_LEAD.value for role in roles)
    assert any(role['value'] == UserRole.CANDIDATE.value for role in roles)

def test_non_admin_list_roles(client, talent_lead_headers):
    """Test listing roles as non-admin."""
    response = client.get('/api/auth/roles/admin', headers=talent_lead_headers)
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Insufficient permissions'

def test_admin_update_user_role(client, admin_headers, candidate_user):
    """Test updating user role as admin."""
    response = client.put(
        f'/api/auth/users/{candidate_user.id}/role',
        headers=admin_headers,
        json={'role': UserRole.TALENT_LEAD.value}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'user' in data
    assert data['user']['role'] == UserRole.TALENT_LEAD.value

def test_non_admin_update_user_role(client, talent_lead_headers, candidate_user):
    """Test updating user role as non-admin."""
    response = client.put(
        f'/api/auth/users/{candidate_user.id}/role',
        headers=talent_lead_headers,
        json={'role': UserRole.TALENT_LEAD.value}
    )
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Insufficient permissions'

def test_admin_list_users(client, admin_headers, admin_user, talent_lead_user, candidate_user):
    """Test listing users as admin."""
    response = client.get('/api/auth/users', headers=admin_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'users' in data
    users = data['users']
    assert len(users) >= 3  # admin, talent_lead, and candidate users
    roles = [user['role'] for user in users]
    assert UserRole.ADMIN.value in roles
    assert UserRole.TALENT_LEAD.value in roles
    assert UserRole.CANDIDATE.value in roles

def test_talent_lead_list_users(client, talent_lead_headers, admin_user, talent_lead_user, candidate_user):
    """Test listing users as talent lead."""
    response = client.get('/api/auth/users', headers=talent_lead_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'users' in data
    users = data['users']
    assert all(user['role'] == UserRole.CANDIDATE.value for user in users)

def test_candidate_list_users(client, candidate_headers):
    """Test listing users as candidate."""
    response = client.get('/api/auth/users', headers=candidate_headers)
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Insufficient permissions'

def test_register_with_role(client, admin_headers):
    """Test registering a new user with a specific role as admin."""
    response = client.post('/api/auth/register', 
        headers=admin_headers,
        json={
            'email': 'newtalent@example.com',
            'password': 'password123',
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
            'password': 'password123',
            'role': UserRole.ADMIN.value
        }
    )
    assert response.status_code == 403

def test_update_user_role(client, auth_headers, admin_user, test_user):
    """Test updating a user's role."""
    # Get admin token
    admin_token = create_access_token(identity=str(admin_user.id))
    admin_headers = {'Authorization': f'Bearer {admin_token}'}
    
    # Try to update role without admin privileges
    response = client.put(
        f'/api/auth/users/{test_user.id}/role',
        headers=auth_headers,
        json={'role': UserRole.TALENT_LEAD.value}
    )
    assert response.status_code == 403
    
    # Update role with admin privileges
    response = client.put(
        f'/api/auth/users/{test_user.id}/role',
        headers=admin_headers,
        json={'role': UserRole.TALENT_LEAD.value}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['user']['role'] == UserRole.TALENT_LEAD.value

def test_list_roles(client, auth_headers):
    """Test listing available roles."""
    response = client.get('/api/auth/roles', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['roles']) == len(UserRole)
    assert any(r['value'] == UserRole.ADMIN.value for r in data['roles'])
    assert any(r['value'] == UserRole.TALENT_LEAD.value for r in data['roles'])
    assert any(r['value'] == UserRole.CANDIDATE.value for r in data['roles'])

def test_list_users_by_role(client, auth_headers, admin_user, test_user):
    """Test listing users filtered by role."""
    # Get admin token
    admin_token = create_access_token(identity=str(admin_user.id))
    admin_headers = {'Authorization': f'Bearer {admin_token}'}
    
    # Test without admin privileges
    response = client.get('/api/auth/users/roles', headers=auth_headers)
    assert response.status_code == 403
    
    # Test with admin privileges
    response = client.get('/api/auth/users/roles', headers=admin_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data['users'], list)
    
    # Test filtering by role
    response = client.get(
        f'/api/auth/users/roles?role={UserRole.ADMIN.value}',
        headers=admin_headers
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert all(user['role'] == UserRole.ADMIN.value for user in data['users'])
