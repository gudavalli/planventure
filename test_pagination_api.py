import requests
import json

# Test the pagination API
base_url = "http://localhost:5000/api/auth"

def test_login():
    """Test login and get token"""
    login_data = {
        "email": "admin.user@example.com",
        "password": "Password123"
    }
    
    try:
        response = requests.post(f"{base_url}/login", json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Login request failed: {e}")
        return None

def test_users_pagination(token):
    """Test users endpoint with pagination"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test first page
    print("Testing page 1 (per_page=5):")
    try:
        response = requests.get(f"{base_url}/users?page=1&per_page=5", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Users count: {len(data['users'])}")
            print(f"Pagination: {data['pagination']}")
            print(f"First user: {data['users'][0]['email'] if data['users'] else 'No users'}")
        else:
            print(f"Failed: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    
    print("\nTesting page 2 (per_page=5):")
    try:
        response = requests.get(f"{base_url}/users?page=2&per_page=5", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Users count: {len(data['users'])}")
            print(f"Pagination: {data['pagination']}")
            print(f"First user: {data['users'][0]['email'] if data['users'] else 'No users'}")
        else:
            print(f"Failed: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def test_roles_pagination(token):
    """Test roles endpoint with pagination"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\nTesting roles endpoint:")
    response = requests.get(f"{base_url}/roles", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"Roles: {data}")
    else:
        print(f"Failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("Testing pagination API...")
    
    # Login and get token
    token = test_login()
    if not token:
        print("Cannot proceed without token")
        exit(1)
    
    print(f"Login successful, token: {token[:20]}...")
    
    # Test pagination
    test_users_pagination(token)
    test_roles_pagination(token)
