#!/usr/bin/env python3
"""
Comprehensive diagnostic script for Resume Screener API
Tests all critical endpoints and identifies issues
"""
import os
import sys
import json
import requests
from urllib.parse import urlencode
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init()

# Constants
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"
TEST_CREDENTIALS = [
    ("string", "string"),
    ("testuser", "password123")
]

def print_header(title):
    """Print a formatted header"""
    print(f"\n{Fore.BLUE}{'=' * 60}")
    print(f"{Fore.CYAN}{title.center(60)}")
    print(f"{Fore.BLUE}{'=' * 60}{Style.RESET_ALL}")

def print_success(message):
    """Print a success message"""
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")

def print_error(message):
    """Print an error message"""
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")

def print_warning(message):
    """Print a warning message"""
    print(f"{Fore.YELLOW}⚠️ {message}{Style.RESET_ALL}")

def print_info(message):
    """Print an info message"""
    print(f"{Fore.CYAN}ℹ️ {message}{Style.RESET_ALL}")

def test_health_endpoint():
    """Test the health check endpoint"""
    print_header("Health Check Test")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            print_success(f"Health check successful: {response.status_code}")
            print_info(f"Response: {response.json()}")
            return True
        else:
            print_error(f"Health check failed with status code: {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Health check failed with exception: {str(e)}")
        return False

def test_cors():
    """Test CORS configuration"""
    print_header("CORS Configuration Test")
    
    try:
        response = requests.options(
            f"{BASE_URL}/health",
            headers={"Origin": "http://localhost:8080"},
            timeout=5
        )
        
        if response.status_code in [200, 204]:
            print_success(f"CORS pre-flight successful: {response.status_code}")
            
            # Check CORS headers
            headers = response.headers
            if "Access-Control-Allow-Origin" in headers:
                print_success(f"Access-Control-Allow-Origin: {headers['Access-Control-Allow-Origin']}")
            else:
                print_error("Missing Access-Control-Allow-Origin header")
            
            if "Access-Control-Allow-Methods" in headers:
                print_success(f"Access-Control-Allow-Methods: {headers['Access-Control-Allow-Methods']}")
            else:
                print_error("Missing Access-Control-Allow-Methods header")
            
            if "Access-Control-Allow-Headers" in headers:
                print_success(f"Access-Control-Allow-Headers: {headers['Access-Control-Allow-Headers']}")
            else:
                print_error("Missing Access-Control-Allow-Headers header")
            
            return True
        else:
            print_error(f"CORS pre-flight failed with status code: {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"CORS test failed with exception: {str(e)}")
        return False

def try_login():
    """Try to login with test credentials"""
    print_header("Authentication Test")
    
    for username, password in TEST_CREDENTIALS:
        print_info(f"Trying to login with username: {username}")
        
        try:
            data = {
                "username": username,
                "password": password
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            response = requests.post(
                f"{API_URL}/auth/token",
                data=urlencode(data),
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                token_data = response.json()
                print_success(f"Login successful with {username}")
                print_info(f"Token type: {token_data.get('token_type')}")
                print_info(f"Access token: {token_data.get('access_token')[:20]}... (truncated)")
                return token_data.get('access_token')
            else:
                print_error(f"Login failed for {username} with status code: {response.status_code}")
                print_info(f"Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print_error(f"Login attempt failed with exception: {str(e)}")
    
    print_error("All login attempts failed")
    return None

def test_authentication(token):
    """Test authentication with the token"""
    print_header("User Authentication Test")
    
    if not token:
        print_error("No token available to test authentication")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.get(
            f"{API_URL}/auth/me",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print_success("Authentication successful")
            print_info(f"Username: {user_data.get('username')}")
            print_info(f"Email: {user_data.get('email')}")
            return True
        else:
            print_error(f"Authentication failed with status code: {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Authentication test failed with exception: {str(e)}")
        return False

def test_file_upload(token):
    """Test file upload with the token"""
    print_header("File Upload Test")
    
    if not token:
        print_error("No token available to test file upload")
        return False
    
    # Create a test file
    file_content = "This is a test resume file."
    file_path = "test_resume.txt"
    
    with open(file_path, "w") as f:
        f.write(file_content)
    
    try:
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        files = {
            "file": ("test_resume.txt", open(file_path, "rb"), "text/plain")
        }
        
        data = {
            "candidate_name": "Test User",
            "candidate_email": "test@example.com",
            "test_upload": "true"
        }
        
        print_info(f"Sending file upload request to {API_URL}/resumes/upload")
        print_info(f"File: {file_path}")
        print_info(f"Token: {token[:20]}... (truncated)")
        
        response = requests.post(
            f"{API_URL}/resumes/upload",
            headers=headers,
            files=files,
            data=data,
            timeout=10
        )
        
        if response.status_code == 200:
            print_success(f"File upload successful: {response.status_code}")
            print_info(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print_error(f"File upload failed with status code: {response.status_code}")
            print_info(f"Response: {response.text}")
            
            # Detailed error info
            print_warning("Possible causes:")
            print("1. CORS issues preventing file upload")
            print("2. Authentication token expired or invalid")
            print("3. File validation failed")
            print("4. Missing required fields")
            
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"File upload test failed with exception: {str(e)}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(file_path):
            os.remove(file_path)

def main():
    """Run all tests"""
    print_header("Resume Screener API Diagnostic")
    print_info(f"Testing API at {BASE_URL}")
    
    # Test 1: Health Check
    health_ok = test_health_endpoint()
    
    if not health_ok:
        print_error("Health check failed. API server may not be running properly.")
        print_warning("Suggestions:")
        print("1. Check if backend server is running")
        print("2. Make sure the server is listening on port 8000")
        print("3. Check server logs for errors")
        return
    
    # Test 2: CORS
    cors_ok = test_cors()
    
    if not cors_ok:
        print_error("CORS test failed. This will cause frontend connection issues.")
        print_warning("Suggestions:")
        print("1. Check CORS middleware in the application")
        print("2. Ensure CORS headers are properly set")
        print("3. Restart the backend server")
    
    # Test 3: Authentication
    token = try_login()
    
    if not token:
        print_error("All login attempts failed. Authentication is not working.")
        print_warning("Suggestions:")
        print("1. Check if users exist in the database")
        print("2. Verify authentication routes are working")
        print("3. Reset test user passwords if needed")
        return
    
    # Test 4: Authentication Verification
    auth_ok = test_authentication(token)
    
    if not auth_ok:
        print_error("Authentication verification failed.")
        print_warning("Suggestions:")
        print("1. Token validation may be faulty")
        print("2. User data retrieval may have issues")
        print("3. Check token expiration and validation logic")
    
    # Test 5: File Upload
    upload_ok = test_file_upload(token)
    
    if not upload_ok:
        print_error("File upload test failed.")
        print_warning("Suggestions:")
        print("1. Check file upload endpoint implementation")
        print("2. Verify form data handling")
        print("3. Examine authentication in the upload endpoint")
        print("4. Check file saving and processing logic")
    
    # Final summary
    print_header("Diagnostic Summary")
    
    if health_ok and cors_ok and token and auth_ok and upload_ok:
        print_success("All tests passed! The API appears to be working correctly.")
    else:
        print_error("Some tests failed. Please address the issues above.")
        print_info("After fixing issues, restart the backend server and run this script again.")

if __name__ == "__main__":
    main() 