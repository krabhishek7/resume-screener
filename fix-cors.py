#!/usr/bin/env python3
"""
CORS Fix Script for ResuMatch
This script ensures the FastAPI backend has proper CORS settings to work with the frontend.
"""

import os
import re
import sys
import subprocess

# Define the application.py file path
APP_FILE = os.path.join("app", "core", "application.py")
CORS_PATTERN = r"app\.add_middleware\(\s*CORSMiddleware[^)]*\)"
FRONTEND_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080"
]

def check_cors_config():
    """Check the CORS configuration in application.py"""
    if not os.path.exists(APP_FILE):
        print(f"Error: {APP_FILE} not found")
        return False
    
    with open(APP_FILE, "r") as f:
        content = f.read()
    
    cors_middleware = re.search(CORS_PATTERN, content, re.DOTALL)
    if not cors_middleware:
        print("Error: CORS middleware not found in application.py")
        return False
    
    cors_config = cors_middleware.group(0)
    print("\nCurrent CORS configuration:")
    print("-" * 50)
    print(cors_config)
    print("-" * 50)
    
    # Check if allow_origins has the frontend URLs
    if all(origin in cors_config for origin in FRONTEND_ORIGINS):
        print("\nCORS configuration looks good! Frontend origins are already allowed.")
        return True
    
    # Ask if they want to update the configuration
    if "allow_origins=[\"*\"]" in cors_config or "allow_origins=['*']" in cors_config:
        print("\nCORS is configured to allow all origins (*), which should work but is not recommended for production.")
        return True
    
    return False

def update_cors_config():
    """Update the CORS configuration to allow frontend origins"""
    with open(APP_FILE, "r") as f:
        content = f.read()
    
    cors_middleware = re.search(CORS_PATTERN, content, re.DOTALL)
    if not cors_middleware:
        print("Error: CORS middleware not found in application.py")
        return False
    
    cors_config = cors_middleware.group(0)
    
    # Check if we have allow_origins parameter
    if "allow_origins" in cors_config:
        # Replace the allow_origins parameter
        if "allow_origins=[\"*\"]" in cors_config or "allow_origins=['*']" in cors_config:
            print("CORS already allows all origins (*), no change needed.")
            return True
        
        # Replace the allow_origins with our frontend URLs
        updated_cors = re.sub(
            r'allow_origins=\[[^\]]*\]', 
            f'allow_origins={FRONTEND_ORIGINS + ["*"]}',
            cors_config
        )
    else:
        # Add the allow_origins parameter
        updated_cors = cors_config.replace(
            "CORSMiddleware,",
            f"CORSMiddleware,\n        allow_origins={FRONTEND_ORIGINS + ['*']},",
        )
    
    # Update the content
    updated_content = content.replace(cors_config, updated_cors)
    
    # Write the updated content
    with open(APP_FILE, "w") as f:
        f.write(updated_content)
    
    print("\nCORS configuration updated successfully!")
    print("\nNew CORS configuration:")
    print("-" * 50)
    print(updated_cors)
    print("-" * 50)
    
    return True

def check_backend_running():
    """Check if the backend is running"""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("Backend is running on port 8000")
            return True
    except:
        pass
    
    print("Backend does not appear to be running on port 8000")
    return False

def check_frontend_running():
    """Check if the frontend is running"""
    try:
        import requests
        response = requests.get("http://localhost:8080", timeout=2)
        if response.status_code == 200:
            print("Frontend is running on port 8080")
            return True
    except:
        pass
    
    print("Frontend does not appear to be running on port 8080")
    return False

def restart_backend():
    """Restart the backend server"""
    print("\nRestarting the backend server...")
    
    # Find the backend process
    try:
        backend_pids = subprocess.check_output(
            "ps aux | grep 'python main.py' | grep -v grep | awk '{print $2}'",
            shell=True
        ).decode().strip().split("\n")
        
        # Kill the process
        for pid in backend_pids:
            if pid:
                subprocess.run(f"kill -9 {pid}", shell=True)
                print(f"Killed backend process {pid}")
    except:
        print("No running backend process found")
    
    # Start the backend in the background
    subprocess.Popen(
        "python main.py",
        shell=True,
        start_new_session=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("Backend restarted in the background")
    
    # Wait for it to start
    import time
    for _ in range(5):
        time.sleep(1)
        if check_backend_running():
            return True
    
    print("Backend failed to start properly")
    return False

def main():
    """Main function"""
    print("ResuMatch CORS Fix Tool")
    print("=" * 50)
    
    # Check the current configuration
    cors_ok = check_cors_config()
    
    if not cors_ok:
        print("\nWould you like to update the CORS configuration to allow frontend connections? (y/n)")
        choice = input("> ").strip().lower()
        
        if choice == "y":
            if update_cors_config():
                print("\nCORS configuration updated.")
                
                # Check if backend is running
                backend_running = check_backend_running()
                if backend_running:
                    print("\nThe backend server needs to be restarted for the changes to take effect.")
                    print("Would you like to restart it now? (y/n)")
                    restart_choice = input("> ").strip().lower()
                    
                    if restart_choice == "y":
                        restart_backend()
                else:
                    print("\nPlease start the backend server:")
                    print("python main.py")
            else:
                print("\nFailed to update CORS configuration.")
        else:
            print("\nCORS configuration not updated.")
    
    # Check if frontend and backend are running
    print("\nChecking server status:")
    backend_running = check_backend_running()
    frontend_running = check_frontend_running()
    
    if not backend_running:
        print("\nTo start the backend server, run:")
        print("python main.py")
    
    if not frontend_running:
        print("\nTo start the frontend server, run:")
        print("python serve-frontend.py")
    
    if backend_running and frontend_running:
        print("\nBoth servers are running! You should be able to connect to the frontend at:")
        print("http://localhost:8080")
        
        print("\nTo test API connectivity, open your browser's developer tools (F12) and check the console for errors.")
        print("You can also use the debug panel that appears on the frontend.")
    
    print("\nTroubleshooting Tips:")
    print("1. Make sure MongoDB is running if authentication issues persist")
    print("2. Check browser console for CORS or connection errors")
    print("3. Verify that the frontend is connecting to http://localhost:8000")
    print("4. Try disabling browser extensions that might block requests")

if __name__ == "__main__":
    main() 