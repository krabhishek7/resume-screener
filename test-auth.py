#!/usr/bin/env python3
"""
Test Authentication Script for ResuMatch
This script tests user registration and login with the FastAPI backend.
"""

import requests
import json
import time

# Configuration
API_URL = "http://localhost:8000/api/v1"
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123!",
    "full_name": "Test User"
}

def print_response(response, label):
    """Print a formatted API response"""
    print(f"\n{label} Response:")
    print(f"Status Code: {response.status_code}")
    print("Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    
    print("Body:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def test_health():
    """Test the health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{API_URL.split('/api/v1')[0]}/health")
        print_response(response, "Health")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_register():
    """Test user registration"""
    print("\n=== Testing User Registration ===")
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json=TEST_USER
        )
        print_response(response, "Register")
        
        if response.status_code == 200:
            print("\nUser registration successful!")
            return True
        elif response.status_code == 400 and "already registered" in response.text:
            print("\nUser already exists, continuing with login test.")
            return True
        else:
            print("\nUser registration failed.")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_login():
    """Test user login"""
    print("\n=== Testing User Login ===")
    
    # FastAPI OAuth2 password flow - try both username and email
    login_attempts = [
        {"username": TEST_USER["username"], "password": TEST_USER["password"]},
        {"username": TEST_USER["email"], "password": TEST_USER["password"]}
    ]
    
    for attempt_data in login_attempts:
        print(f"\nTrying login with: {attempt_data['username']}")
        try:
            response = requests.post(
                f"{API_URL}/auth/token",
                data=attempt_data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            print_response(response, "Login")
            
            if response.status_code == 200 and "access_token" in response.json():
                print("\nLogin successful!")
                token = response.json()["access_token"]
                return token
            else:
                print(f"\nLogin attempt with {attempt_data['username']} failed.")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nAll login attempts failed.")
    return None

def test_me(token):
    """Test getting current user info"""
    print("\n=== Testing Get Current User ===")
    try:
        response = requests.get(
            f"{API_URL}/auth/me",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )
        print_response(response, "Current User")
        
        if response.status_code == 200:
            print("\nGet current user successful!")
            return True
        else:
            print("\nGet current user failed.")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function"""
    print("ResuMatch Authentication Test")
    print("=" * 50)
    
    # Test health endpoint
    if not test_health():
        print("\nHealth check failed. Make sure the backend is running.")
        return
    
    # Test register
    if not test_register():
        print("\nRegistration test failed. Cannot continue.")
        return
    
    # Test login
    token = test_login()
    if not token:
        print("\nLogin test failed. Cannot continue.")
        return
    
    # Test get current user
    test_me(token)
    
    print("\n" + "=" * 50)
    print("Authentication flow test completed.")
    print("You can now try logging in through the frontend using:")
    print(f"Username/Email: {TEST_USER['username']} or {TEST_USER['email']}")
    print(f"Password: {TEST_USER['password']}")

if __name__ == "__main__":
    main() 