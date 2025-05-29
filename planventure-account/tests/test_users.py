import json
from datetime import datetime, timedelta, UTC
from unittest.mock import patch
import pytest
from flask import current_app
from flask_jwt_extended import create_access_token

from models import User # Assuming User is in models/__init__.py or models.py
from models.roles import UserRole
from app import db # For session management if needed directly in tests

# Helper to create a user instance for model tests if not using a fixture that already does
def create_user_for_test(email="modeltest@example.com", password="Password123"):
    return User(email=email, password=password)

class TestUserModel:
    def test_generate_verification_token(self, app):
        """Test User.generate_verification_token() method."""
        with app.app_context():
            user = create_user_for_test()
            # Ensure config is set for testing this, or mock it
            original_expiry_hours = current_app.config.get('EMAIL_VERIFICATION_TOKEN_EXPIRES_HOURS')
            current_app.config['EMAIL_VERIFICATION_TOKEN_EXPIRES_HOURS'] = 48 # Test with a specific value
            
            user.generate_verification_token()
            
            assert user.verification_token is not None
            assert len(user.verification_token) > 20 # Check for a reasonable token length
            assert not user.verification_token_used
            
            expected_expiry_delta = timedelta(hours=48)
            # Allow a small delta for the time it takes to execute the code
            assert user.verification_token_expires > datetime.now(UTC) + expected_expiry_delta - timedelta(seconds=10)
            assert user.verification_token_expires < datetime.now(UTC) + expected_expiry_delta + timedelta(seconds=10)

            # Restore original config if it was changed
            if original_expiry_hours is not None:
                current_app.config['EMAIL_VERIFICATION_TOKEN_EXPIRES_HOURS'] = original_expiry_hours
            else:
                # If it wasn't there, clean up
                del current_app.config['EMAIL_VERIFICATION_TOKEN_EXPIRES_HOURS']


    def test_verify_email_success(self, app):
        """Test successful email verification."""
        with app.app_context():
            user = create_user_for_test()
            user.generate_verification_token() # Generates token and sets expiry
            token_to_verify = user.verification_token
            
            assert not user.is_verified
            assert not user.verification_token_used
            
            result = user.verify_email(token_to_verify)
            
            assert result is True
            assert user.is_verified is True
            assert user.verification_token_used is True
            assert user.verification_token is None
            assert user.verification_token_expires is None

    def test_verify_email_invalid_token(self, app):
        """Test email verification with an invalid token."""
        with app.app_context():
            user = create_user_for_test()
            user.generate_verification_token()
            
            result = user.verify_email("thisisawrongtoken")
            
            assert result is False
            assert not user.is_verified
            assert not user.verification_token_used

    def test_verify_email_expired_token(self, app):
        """Test email verification with an expired token."""
        with app.app_context():
            user = create_user_for_test()
            # Mock current_app.config for expiry for predictability
            original_expiry_hours = current_app.config.get('EMAIL_VERIFICATION_TOKEN_EXPIRES_HOURS')
            current_app.config['EMAIL_VERIFICATION_TOKEN_EXPIRES_HOURS'] = 1 # Expires in 1 hour
            
            user.generate_verification_token()
            token_to_verify = user.verification_token
            
            # Simulate time passing so token is expired
            # We need to mock datetime.now(UTC) within User.verify_email()
            # or ensure the token_expires is in the past before calling verify_email
            
            # Option 1: Directly manipulate verification_token_expires (simpler for this model test)
            user.verification_token_expires = datetime.now(UTC) - timedelta(hours=2)
            
            result = user.verify_email(token_to_verify)
            
            assert result is False
            assert not user.is_verified
            assert not user.verification_token_used # Should remain false as verification failed

            # Restore original config
            if original_expiry_hours is not None:
                current_app.config['EMAIL_VERIFICATION_TOKEN_EXPIRES_HOURS'] = original_expiry_hours
            else:
                del current_app.config['EMAIL_VERIFICATION_TOKEN_EXPIRES_HOURS']


    def test_verify_email_token_already_used(self, app):
        """Test email verification if token was already marked as used."""
        with app.app_context():
            user = create_user_for_test()
            user.generate_verification_token()
            token_to_verify = user.verification_token
            
            user.verification_token_used = True # Manually mark as used
            
            result = user.verify_email(token_to_verify)
            
            assert result is False
            assert not user.is_verified # is_verified should not change
            assert user.verification_token_used is True # Remains true


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
