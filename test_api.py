#!/usr/bin/env python3
"""Script to test PhotoShare API functionality."""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_signup():
    """Test user registration."""
    print("\n=== Testing Signup ===")
    data = {
        "username": "apitestuser",
        "email": "apitest@example.com",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/auth/signup", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print(f"✅ User created: {response.json()}")
        return response.json()
    else:
        print(f"❌ Error: {response.text}")
        return None

def test_login(email, password):
    """Test user login."""
    print("\n=== Testing Login ===")
    data = {
        "username": email,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        tokens = response.json()
        print(f"✅ Login successful")
        print(f"   Access Token: {tokens['access_token'][:30]}...")
        return tokens
    else:
        print(f"❌ Error: {response.text}")
        return None

def test_get_profile(token):
    """Test getting own profile."""
    print("\n=== Testing Get My Profile ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Profile retrieved: {json.dumps(response.json(), indent=2)}")
        return response.json()
    else:
        print(f"❌ Error: {response.text}")
        return None

def test_update_profile(token):
    """Test updating profile."""
    print("\n=== Testing Update Profile ===")
    headers = {"Authorization": f"Bearer {token}"}
    data = {"username": "updatedapitest"}
    response = requests.put(f"{BASE_URL}/users/me", headers=headers, json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Profile updated: {json.dumps(response.json(), indent=2)}")
        return response.json()
    else:
        print(f"❌ Error: {response.text}")
        return None

def test_get_public_profile(username):
    """Test getting public profile."""
    print("\n=== Testing Get Public Profile ===")
    response = requests.get(f"{BASE_URL}/users/{username}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Public profile: {json.dumps(response.json(), indent=2)}")
        return response.json()
    else:
        print(f"❌ Error: {response.text}")
        return None

def test_refresh_token(refresh_token):
    """Test refreshing tokens."""
    print("\n=== Testing Refresh Token ===")
    data = {"refresh_token": refresh_token}
    response = requests.post(f"{BASE_URL}/auth/refresh", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        tokens = response.json()
        print(f"✅ Tokens refreshed")
        print(f"   New Access Token: {tokens['access_token'][:30]}...")
        return tokens
    else:
        print(f"❌ Error: {response.text}")
        return None

def test_admin_activate(token, user_id):
    """Test admin activating user."""
    print("\n=== Testing Admin Activate User ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(f"{BASE_URL}/admin/users/{user_id}/activate", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ User activated: {json.dumps(response.json(), indent=2)}")
        return response.json()
    else:
        print(f"❌ Error: {response.text}")
        return None

if __name__ == "__main__":
    print("🚀 Starting API Tests...")
    
    # Test signup
    user = test_signup()
    if not user:
        print("\n❌ Signup failed, cannot continue tests")
        exit(1)
    
    # Test login
    tokens = test_login("apitest@example.com", "testpass123")
    if not tokens:
        print("\n❌ Login failed, cannot continue tests")
        exit(1)
    
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    
    # Test get profile
    profile = test_get_profile(access_token)
    
    # Test update profile
    updated_profile = test_update_profile(access_token)
    
    # Test get public profile
    test_get_public_profile("updatedapitest")
    
    # Test refresh token
    new_tokens = test_refresh_token(refresh_token)
    
    # Note: Admin tests require admin user, skipping for now
    print("\n✅ Basic API tests completed!")
    print("   (Admin tests require admin user setup)")

