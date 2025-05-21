import json
from unittest.mock import patch
import pytest

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

def test_verify_email_success(app, client, test_user):
    """Test successful email verification."""
    with app.app_context():
        # Get fresh user instance
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
        # Get fresh user instance and set up token
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
