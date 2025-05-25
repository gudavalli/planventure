#!/usr/bin/env python3
"""Test script to verify pagination functionality"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def login(email, password):
    """Login and get access token"""
    url = f"{BASE_URL}/auth/login"
    data = {"email": email, "password": password}
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_users_pagination(token):
    """Test users pagination endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test page 1
    print("Testing page 1...")
    response = requests.get(f"{BASE_URL}/auth/users?page=1&per_page=10", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"Page 1 successful:")
        print(f"  Users count: {len(data['users'])}")
        print(f"  Pagination: {data['pagination']}")
    else:
        print(f"Page 1 failed: {response.status_code} - {response.text}")
        return
    
    # Test page 2
    print("\nTesting page 2...")
    response = requests.get(f"{BASE_URL}/auth/users?page=2&per_page=10", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"Page 2 successful:")
        print(f"  Users count: {len(data['users'])}")
        print(f"  Pagination: {data['pagination']}")
    else:
        print(f"Page 2 failed: {response.status_code} - {response.text}")

    # Test page 4 (should be last page with 38 users)
    print("\nTesting page 4...")
    response = requests.get(f"{BASE_URL}/auth/users?page=4&per_page=10", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"Page 4 successful:")
        print(f"  Users count: {len(data['users'])}")
        print(f"  Pagination: {data['pagination']}")
    else:
        print(f"Page 4 failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("Testing pagination functionality...")
    
    # Try to login as admin
    token = login("admin.user@example.com", "password")
    if not token:
        # Try default password
        token = login("admin.user@example.com", "AdminPassword123!")
    
    if token:
        print("Login successful!")
        test_users_pagination(token)
    else:
        print("Could not login to test pagination")
