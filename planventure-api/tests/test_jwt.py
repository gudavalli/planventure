"""Test JWT authentication functionality."""
import pytest
from auth.jwt import jwt, user_identity_lookup, user_lookup_callback
from models import User

def test_user_identity_lookup_with_user(test_user):
    """Test user_identity_lookup with User object."""
    result = user_identity_lookup(test_user)
    assert result == str(test_user.id)

def test_user_identity_lookup_with_id():
    """Test user_identity_lookup with user ID."""
    result = user_identity_lookup(1)
    assert result == "1"

def test_user_identity_lookup_invalid():
    """Test user_identity_lookup with invalid input."""
    result = user_identity_lookup(None)
    assert result is None
    result = user_identity_lookup("invalid")
    assert result == "invalid"

def test_user_lookup_callback_valid(app, test_user):
    """Test user_lookup_callback with valid data."""
    with app.app_context():
        jwt_data = {"sub": str(test_user.id)}
        user = user_lookup_callback({}, jwt_data)
        assert user is not None
        assert user.id == test_user.id

def test_user_lookup_callback_invalid(app):
    """Test user_lookup_callback with invalid data."""
    with app.app_context():
        # Test with non-existent user ID
        jwt_data = {"sub": "999"}
        user = user_lookup_callback({}, jwt_data)
        assert user is None

        # Test with invalid sub claim
        jwt_data = {"sub": None}
        user = user_lookup_callback({}, jwt_data)
        assert user is None

        # Test with missing sub claim
        jwt_data = {}
        user = user_lookup_callback({}, jwt_data)
        assert user is None

def test_token_error_handlers(client):
    """Test JWT error handler responses."""    # Test missing token
    response = client.get('/api/auth/profile')
    assert response.status_code == 401
    data = response.get_json()
    assert 'message' in data

    # Test invalid token
    response = client.get('/api/auth/profile', headers={'Authorization': 'Bearer invalid'})
    assert response.status_code == 401
    data = response.get_json()
    assert 'message' in data

    # Test expired token (would require a token specifically crafted to be expired)
    # This is tested indirectly through integration tests
