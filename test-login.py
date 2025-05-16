#!/usr/bin/env python3
"""
Test login functionality for Resume Screener
"""
import asyncio
import requests
import json
import sys
from urllib.parse import urlencode

# Backend URL
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

def test_login(username, password):
    """Test login with the given credentials"""
    print(f"🔑 Testing login for user: {username}")
    
    # Login endpoint
    login_url = f"{API_URL}/auth/token"
    
    # Form data for login
    data = {
        "username": username,
        "password": password
    }
    
    # Headers
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        # Make the request
        print(f"📡 Sending POST request to {login_url}")
        print(f"📦 Data: {data}")
        
        response = requests.post(
            login_url,
            data=urlencode(data),
            headers=headers
        )
        
        # Check if successful
        if response.status_code == 200:
            print(f"✅ Login successful! Status: {response.status_code}")
            token_data = response.json()
            print(f"🔖 Token type: {token_data.get('token_type', 'unknown')}")
            print(f"🔑 Access token: {token_data.get('access_token', '')[:20]}... (truncated)")
            
            # Now test the /me endpoint to verify token works
            if 'access_token' in token_data:
                test_me_endpoint(token_data['access_token'])
            
            return True
        else:
            print(f"❌ Login failed! Status: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error during login request: {str(e)}")
        return False

def test_me_endpoint(token):
    """Test the /me endpoint with the given token"""
    print("\n🧪 Testing /me endpoint with token")
    
    # Me endpoint
    me_url = f"{API_URL}/auth/me"
    
    # Headers with token
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        # Make the request
        print(f"📡 Sending GET request to {me_url}")
        response = requests.get(me_url, headers=headers)
        
        # Check if successful
        if response.status_code == 200:
            print(f"✅ /me endpoint successful! Status: {response.status_code}")
            user_data = response.json()
            # Remove sensitive information for display
            if "hashed_password" in user_data:
                del user_data["hashed_password"]
            print(f"👤 User data: {json.dumps(user_data, indent=2)}")
            return True
        else:
            print(f"❌ /me endpoint failed! Status: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error during /me request: {str(e)}")
        return False

if __name__ == "__main__":
    # Get credentials from command line args or use default test user
    if len(sys.argv) > 2:
        username = sys.argv[1]
        password = sys.argv[2]
    else:
        # Try each of the users we found in the database
        users = [
            ("testuser", "password123"),
            ("string", "string"),
            ("igabhi2000", "password123")
        ]
        
        success = False
        for username, password in users:
            print(f"\n🧪 Trying user: {username}")
            if test_login(username, password):
                success = True
                break
        
        if not success:
            print("\n❌ Failed to login with any of the test users")
            print("🔎 Try providing username and password as arguments:")
            print("    python test-login.py username password") 