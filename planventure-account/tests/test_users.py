import json
from flask_jwt_extended import create_access_token
from models.roles import UserRole

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
