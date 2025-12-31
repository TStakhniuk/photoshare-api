#!/usr/bin/env python3
"""Script to test Admin API functionality."""
import requests
import json

BASE_URL = "http://localhost:8000"

# Create admin user first (manually via database or script)
# For testing, we'll create a regular user and test admin endpoints

def create_admin_user():
    """Create an admin user for testing."""
    print("\n=== Creating Admin User ===")
    # Note: In real scenario, this would be done via database migration or admin script
    # For now, we'll test with existing user
    pass

def test_admin_activate_by_id(admin_token, user_id):
    """Test admin activating user by ID."""
    print(f"\n=== Testing Admin Activate User by ID ({user_id}) ===")
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.put(f"{BASE_URL}/admin/users/{user_id}/activate", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ User activated: {json.dumps(response.json(), indent=2)}")
        return response.json()
    else:
        print(f"❌ Error: {response.text}")
        return None

def test_admin_deactivate_by_id(admin_token, user_id):
    """Test admin deactivating user by ID."""
    print(f"\n=== Testing Admin Deactivate User by ID ({user_id}) ===")
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.put(f"{BASE_URL}/admin/users/{user_id}/deactivate", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ User deactivated: {json.dumps(response.json(), indent=2)}")
        return response.json()
    else:
        print(f"❌ Error: {response.text}")
        return None

def test_admin_activate_by_username(admin_token, username):
    """Test admin activating user by username."""
    print(f"\n=== Testing Admin Activate User by Username ({username}) ===")
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.put(f"{BASE_URL}/admin/users/{username}/activate", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ User activated: {json.dumps(response.json(), indent=2)}")
        return response.json()
    else:
        print(f"❌ Error: {response.text}")
        return None

def test_admin_deactivate_by_username(admin_token, username):
    """Test admin deactivating user by username."""
    print(f"\n=== Testing Admin Deactivate User by Username ({username}) ===")
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.put(f"{BASE_URL}/admin/users/{username}/deactivate", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ User deactivated: {json.dumps(response.json(), indent=2)}")
        return response.json()
    else:
        print(f"❌ Error: {response.text}")
        return None

if __name__ == "__main__":
    print("🔐 Starting Admin API Tests...")
    print("\n⚠️  Note: Admin tests require an admin user token.")
    print("   To test admin endpoints, you need to:")
    print("   1. Create an admin user in the database")
    print("   2. Login as admin user")
    print("   3. Use admin token for testing")
    print("\n   For now, testing will show expected behavior with non-admin user...")
    
    # Test with regular user (should fail with 403)
    print("\n=== Testing Admin Endpoint with Regular User (should fail) ===")
    # First create and login as regular user
    signup_data = {"username": "regularuser", "email": "regular@example.com", "password": "pass123"}
    requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    
    login_data = {"username": "regular@example.com", "password": "pass123"}
    login_resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if login_resp.status_code == 200:
        regular_token = login_resp.json()["access_token"]
        # Try to activate user (should fail)
        response = requests.put(f"{BASE_URL}/admin/users/1/activate", 
                               headers={"Authorization": f"Bearer {regular_token}"})
        print(f"Status: {response.status_code}")
        if response.status_code == 403:
            print("✅ Correctly rejected non-admin user")
        else:
            print(f"❌ Unexpected response: {response.text}")
    
    print("\n✅ Admin endpoint security test completed!")
    print("   (Full admin tests require admin user setup)")

