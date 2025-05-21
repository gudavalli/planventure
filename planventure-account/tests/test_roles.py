import json
from models.roles import UserRole
from app import db

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

def test_list_roles(client, auth_headers):
    """Test listing available roles."""
    response = client.get('/api/auth/roles', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['roles']) == len(UserRole)
    assert any(r['value'] == UserRole.ADMIN.value for r in data['roles'])
    assert any(r['value'] == UserRole.TALENT_LEAD.value for r in data['roles'])
    assert any(r['value'] == UserRole.CANDIDATE.value for r in data['roles'])
