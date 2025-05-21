import json
from app import db
from models.user import User

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
    
    monkeypatch.setattr(db.session, 'commit', mock_commit)
    
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
