import json
from datetime import datetime, timedelta, UTC
from app import db
from models.user import User

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
