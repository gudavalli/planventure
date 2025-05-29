import json
from unittest.mock import patch, MagicMock
import pytest
from datetime import datetime, timedelta, UTC

from flask import current_app
from flask_jwt_extended import create_access_token

from app import db
from models import User
from models.roles import UserRole

# Helper to create a user with specific properties for auth tests
def create_auth_test_user(email, password, is_verified=False, role=UserRole.CANDIDATE.value, add_to_session=True, commit=True):
    user = User(email=email, password=password, role=role)
    user.is_verified = is_verified
    if is_verified: # If user is pre-verified, token logic might be different
        user.verification_token = None
        user.verification_token_expires = None
        user.verification_token_used = True
    
    if add_to_session:
        db.session.add(user)
    if commit:
        db.session.commit()
    return user

class TestVerifyEmailEndpoint:
    def test_verify_email_success(self, client, app):
        """Test successful email verification via endpoint."""
        with app.app_context():
            # User model's __init__ calls generate_verification_token
            user = User(email="verify_success_endpoint@example.com", password="Password123")
            db.session.add(user)
            db.session.commit() 
            
            token = user.verification_token
            assert token is not None, "Verification token should be generated"
            assert not user.is_verified
            assert not user.verification_token_used

            # Mock admin notification to isolate this test for now
            # This will be tested in detail in TestAdminNotificationOnVerification
            with patch('routes.auth.send_admin_user_verification_notification', return_value=True) as mock_notify_admin:
                response = client.get(f'/api/auth/verify-email/{token}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Email verified successfully'

            verified_user = db.session.get(User, user.id)
            assert verified_user.is_verified is True
            assert verified_user.verification_token_used is True
            assert verified_user.verification_token is None
            # The call to mock_notify_admin will be asserted in a different test class

    def test_verify_email_invalid_token_endpoint(self, client, app):
        """Test email verification with an invalid token via endpoint."""
        with app.app_context():
            response = client.get('/api/auth/verify-email/thisisnotavalidtoken_endpoint')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Invalid verification token'

    def test_verify_email_expired_token_endpoint(self, client, app):
        """Test email verification with an expired token via endpoint."""
        with app.app_context():
            user = User(email="expiredtoken_endpoint_test@example.com", password="Password123")
            db.session.add(user)
            db.session.commit() # Token generated
            
            # Manually set token expiry to the past
            user.verification_token_expires = datetime.now(UTC) - timedelta(hours=current_app.config.get('EMAIL_VERIFICATION_TOKEN_EXPIRES_HOURS', 24) + 1)
            db.session.commit()

            response = client.get(f'/api/auth/verify-email/{user.verification_token}')
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'Invalid or expired token' in data['error']
            
            unverified_user = db.session.get(User, user.id)
            assert not unverified_user.is_verified

    def test_verify_email_token_already_used_endpoint(self, client, app):
        """Test verification endpoint with a token that's already marked as used."""
        with app.app_context():
            user = User(email="usedtoken_endpoint_test@example.com", password="Password123")
            db.session.add(user)
            db.session.commit() # Token generated
            
            original_token = user.verification_token 
            user.verification_token_used = True # Mark as used
            db.session.commit()

            response = client.get(f'/api/auth/verify-email/{original_token}')
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'Invalid or expired token' in data['error'] 

            db_user = db.session.get(User, user.id)
            assert not db_user.is_verified # Should not become verified


class TestLoginVerifiedCheck:
    def test_login_verified_user(self, client, app):
        """Test successful login for a verified user."""
        with app.app_context():
            create_auth_test_user("verifiedlogin_endpoint@example.com", "Password123", is_verified=True)

        response = client.post('/api/auth/login', json={
            'email': "verifiedlogin_endpoint@example.com",
            'password': "Password123"
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data

    def test_login_unverified_user(self, client, app):
        """Test failed login for an unverified user."""
        with app.app_context():
            create_auth_test_user("unverifiedlogin_endpoint@example.com", "Password123", is_verified=False)

        response = client.post('/api/auth/login', json={
            'email': "unverifiedlogin_endpoint@example.com",
            'password': "Password123"
        })
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'Email not verified'
        assert 'Please verify your email address' in data['details']

    def test_login_non_existent_user(self, client, app):
        """Test failed login for a user that does not exist."""
        with app.app_context(): # Context for consistency
            pass
        response = client.post('/api/auth/login', json={
            'email': 'idonotexist_endpoint@example.com',
            'password': 'Password123'
        })
        assert response.status_code == 401 
        data = json.loads(response.data)
        assert data['error'] == 'Invalid email or password'

class TestAdminNotificationOnVerification:
    def test_admin_notification_sent_when_admins_exist(self, client, app):
        """Test admin notification is sent when admin users exist and a user verifies."""
        with app.app_context():
            admin1 = create_auth_test_user("admin1_notify@example.com", "Password123", is_verified=True, role=UserRole.ADMIN.value)
            admin2 = create_auth_test_user("admin2_notify@example.com", "Password123", is_verified=True, role=UserRole.ADMIN.value)
            
            candidate_user = User(email="candidate_notify@example.com", password="Password123")
            db.session.add(candidate_user)
            db.session.commit() # Token generated
            candidate_token = candidate_user.verification_token

            frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
            expected_role_assignment_url = f"{frontend_url}/admin/assign-role/{candidate_user.id}"

            with patch('routes.auth.send_admin_user_verification_notification', return_value=True) as mock_send_notification:
                response = client.get(f'/api/auth/verify-email/{candidate_token}')
            
            assert response.status_code == 200 # Verification should succeed
            
            assert mock_send_notification.call_count == 2 # Called for each admin
            # Check call arguments for one of the calls (order of admin_users might vary)
            # We need to ensure that the candidate_user object passed to the mock is the one from the DB after verification
            verified_candidate_user = db.session.get(User, candidate_user.id)

            # Check call for admin1
            call_args_admin1 = mock_send_notification.call_args_list[0][0]
            assert call_args_admin1[0].id == admin1.id
            assert call_args_admin1[1].id == verified_candidate_user.id
            assert call_args_admin1[1].is_verified is True # Ensure the user passed is now verified
            assert call_args_admin1[2] == expected_role_assignment_url
            
            # Check call for admin2
            call_args_admin2 = mock_send_notification.call_args_list[1][0]
            assert call_args_admin2[0].id == admin2.id
            assert call_args_admin2[1].id == verified_candidate_user.id
            assert call_args_admin2[1].is_verified is True
            assert call_args_admin2[2] == expected_role_assignment_url
            
            db.session.delete(admin1)
            db.session.delete(admin2)
            db.session.delete(verified_candidate_user)
            db.session.commit()

    def test_admin_notification_not_sent_when_no_admins_exist(self, client, app):
        """Test admin notification is not sent if no admin users exist."""
        with app.app_context():
            # Ensure no admin users, or they are not fetched
            # This test assumes other tests clean up admins or this runs in isolation for admin checks.
            # For safety, explicitly delete any admins if fixtures create them by default.
            # Here, we rely on create_auth_test_user to not create admins unless specified.
            
            candidate_user = User(email="candidate_no_admin_notify@example.com", password="Password123")
            db.session.add(candidate_user)
            db.session.commit()
            candidate_token = candidate_user.verification_token

            with patch('routes.auth.send_admin_user_verification_notification', return_value=True) as mock_send_notification:
                response = client.get(f'/api/auth/verify-email/{candidate_token}')
            
            assert response.status_code == 200 # Verification should still succeed
            mock_send_notification.assert_not_called()
            
            verified_user = db.session.get(User, candidate_user.id)
            db.session.delete(verified_user)
            db.session.commit()


    def test_admin_notification_failure_does_not_block_verification(self, client, app):
        """Test that user verification succeeds even if admin notification fails."""
        with app.app_context():
            admin_user = create_auth_test_user("admin_fail_notify@example.com", "Password123", is_verified=True, role=UserRole.ADMIN.value)
            candidate_user = User(email="candidate_fail_notify@example.com", password="Password123")
            db.session.add(candidate_user)
            db.session.commit()
            candidate_token = candidate_user.verification_token

            with patch('routes.auth.send_admin_user_verification_notification', side_effect=Exception("SMTP Error")) as mock_send_notification:
                with patch.object(current_app.logger, 'error') as mock_logger_error:
                    response = client.get(f'/api/auth/verify-email/{candidate_token}')
            
            assert response.status_code == 200 # Verification should still succeed
            data = json.loads(response.data)
            assert data['message'] == 'Email verified successfully'
            
            verified_candidate_user = db.session.get(User, candidate_user.id)
            assert verified_candidate_user.is_verified is True # User is verified
            
            mock_send_notification.assert_called_once() # Notification was attempted
            mock_logger_error.assert_called_with(f"Failed to send admin notification emails: SMTP Error")

            db.session.delete(admin_user)
            db.session.delete(verified_candidate_user)
            db.session.commit()

class TestAdminRoleAssignmentEndpoints:
    def test_get_users_for_assignment_as_admin(self, client, app, admin_headers):
        """Test GET /admin/users/assign-role as admin."""
        with app.app_context():
            # Verified candidate, should be listed
            user1 = create_auth_test_user("verified_candidate1@example.com", "Password123", is_verified=True, role=UserRole.CANDIDATE.value)
            # Unverified candidate, should NOT be listed
            user2 = create_auth_test_user("unverified_candidate@example.com", "Password123", is_verified=False, role=UserRole.CANDIDATE.value)
            # Verified non-candidate, should NOT be listed
            user3 = create_auth_test_user("verified_talent@example.com", "Password123", is_verified=True, role=UserRole.TALENT_LEAD.value)
            # Another verified candidate
            user4 = create_auth_test_user("verified_candidate2@example.com", "Password123", is_verified=True, role=UserRole.CANDIDATE.value)

            response = client.get('/api/auth/admin/users/assign-role', headers=admin_headers)
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert 'users_awaiting_assignment' in data
            listed_user_ids = {u['id'] for u in data['users_awaiting_assignment']}
            
            assert user1.id in listed_user_ids
            assert user4.id in listed_user_ids
            assert user2.id not in listed_user_ids
            assert user3.id not in listed_user_ids
            assert len(listed_user_ids) == 2

            # Clean up
            db.session.delete(user1)
            db.session.delete(user2)
            db.session.delete(user3)
            db.session.delete(user4)
            db.session.commit()

    def test_get_users_for_assignment_as_non_admin(self, client, app, talent_lead_headers): # Using talent_lead as non-admin
        """Test GET /admin/users/assign-role as non-admin."""
        with app.app_context(): # Context for consistency
            pass
        response = client.get('/api/auth/admin/users/assign-role', headers=talent_lead_headers)
        assert response.status_code == 403 # Expecting Forbidden

    def test_assign_role_as_admin_success(self, client, app, admin_headers):
        """Test PUT /admin/users/<id>/assign-role as admin for a valid user and role."""
        with app.app_context():
            user_to_promote = create_auth_test_user("promotable_candidate@example.com", "Password123", is_verified=True, role=UserRole.CANDIDATE.value)
            user_id = user_to_promote.id
            new_role = UserRole.TALENT_LEAD.value

            response = client.put(f'/api/auth/admin/users/{user_id}/assign-role', headers=admin_headers, json={'role': new_role})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['user']['id'] == user_id
            assert data['user']['role'] == new_role
            
            updated_user = db.session.get(User, user_id)
            assert updated_user.role == new_role
            
            db.session.delete(updated_user)
            db.session.commit()

    def test_assign_role_as_admin_to_unverified_user(self, client, app, admin_headers):
        """Test PUT /admin/users/<id>/assign-role for an unverified user."""
        with app.app_context():
            unverified_user = create_auth_test_user("assign_unverified@example.com", "Password123", is_verified=False, role=UserRole.CANDIDATE.value)
            user_id = unverified_user.id
            new_role = UserRole.TALENT_LEAD.value

            response = client.put(f'/api/auth/admin/users/{user_id}/assign-role', headers=admin_headers, json={'role': new_role})
            assert response.status_code == 400 # As per route logic: "Cannot assign role to an unverified user."
            data = json.loads(response.data)
            assert data['error'] == 'User is not verified'

            db_user = db.session.get(User, user_id)
            assert db_user.role == UserRole.CANDIDATE.value # Role should not change
            
            db.session.delete(db_user)
            db.session.commit()

    def test_assign_role_as_admin_invalid_user_id(self, client, app, admin_headers):
        """Test PUT /admin/users/<id>/assign-role with a non-existent user ID."""
        with app.app_context(): # Context for consistency
            pass
        non_existent_user_id = 99999
        new_role = UserRole.TALENT_LEAD.value
        response = client.put(f'/api/auth/admin/users/{non_existent_user_id}/assign-role', headers=admin_headers, json={'role': new_role})
        assert response.status_code == 404 # User not found

    def test_assign_role_as_admin_invalid_role_value(self, client, app, admin_headers):
        """Test PUT /admin/users/<id>/assign-role with an invalid role value."""
        with app.app_context():
            user = create_auth_test_user("assign_invalid_role@example.com", "Password123", is_verified=True, role=UserRole.CANDIDATE.value)
            user_id = user.id
            invalid_role = "super_mega_admin"

            response = client.put(f'/api/auth/admin/users/{user_id}/assign-role', headers=admin_headers, json={'role': invalid_role})
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'Invalid role provided' in data['error']
            
            db_user = db.session.get(User, user_id)
            assert db_user.role == UserRole.CANDIDATE.value # Role should not change
            
            db.session.delete(db_user)
            db.session.commit()

    def test_assign_role_as_non_admin(self, client, app, talent_lead_headers):
        """Test PUT /admin/users/<id>/assign-role as non-admin."""
        with app.app_context():
            user_to_assign = create_auth_test_user("candidate_for_non_admin_assign@example.com", "Password123", is_verified=True, role=UserRole.CANDIDATE.value)
            user_id = user_to_assign.id
            new_role = UserRole.TALENT_LEAD.value

            response = client.put(f'/api/auth/admin/users/{user_id}/assign-role', headers=talent_lead_headers, json={'role': new_role})
            assert response.status_code == 403 # Forbidden
            
            db_user = db.session.get(User, user_id) # Fetch user from db
            assert db_user.role == UserRole.CANDIDATE.value # Role should not change
            
            db.session.delete(db_user)
            db.session.commit()
