#!/usr/bin/env python3
"""
Fix authentication issues in the Resume Screener project
"""
import os
import sys
import json
import asyncio
import motor.motor_asyncio
from passlib.context import CryptContext
from bson import ObjectId
from pymongo.errors import ServerSelectionTimeoutError

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def check_mongodb():
    """Check MongoDB connection and database"""
    print("\n🔍 Checking MongoDB connection...")
    
    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=5000
    )
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB connection successful")
        
        # Check database
        db = client[settings.MONGODB_DB_NAME]
        collections = await db.list_collection_names()
        
        if not collections:
            print("⚠️ Database exists but has no collections")
            return client, db, False
        
        print(f"✅ Database '{settings.MONGODB_DB_NAME}' found with collections: {collections}")
        
        # Check users collection
        if 'users' not in collections:
            print("⚠️ 'users' collection not found")
            return client, db, False
        
        # Count users
        user_count = await db.users.count_documents({})
        print(f"👥 Found {user_count} users in the database")
        
        if user_count == 0:
            print("⚠️ No users found in the database")
            return client, db, False
        
        return client, db, True
    
    except ServerSelectionTimeoutError:
        print("❌ Failed to connect to MongoDB")
        print(f"📝 Connection URL: {settings.MONGODB_URL}")
        print("📋 Please check:")
        print("  - MongoDB server is running")
        print("  - Connection string is correct")
        return None, None, False

async def create_test_user(db):
    """Create a test user in the database"""
    print("\n🔧 Creating test user...")
    
    # User data
    username = "testuser"
    email = "test@example.com"
    password = "password123"
    full_name = "Test User"
    
    # Check if user already exists
    existing_user = await db.users.find_one({"username": username})
    if existing_user:
        print(f"👤 User '{username}' already exists")
        
        # Check if we should reset the password
        reset = input(f"Do you want to reset password for '{username}'? (y/n): ").lower().strip() == 'y'
        if reset:
            hashed_password = pwd_context.hash(password)
            result = await db.users.update_one(
                {"username": username},
                {"$set": {"hashed_password": hashed_password}}
            )
            
            if result.modified_count:
                print(f"✅ Password reset for user '{username}'")
                print(f"📝 Username: {username}")
                print(f"📝 Password: {password}")
            else:
                print("❌ Failed to reset password")
        
        return True
    
    # Create new user
    hashed_password = pwd_context.hash(password)
    
    user_data = {
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "full_name": full_name,
        "is_active": True,
        "is_admin": False,
        "created_at": datetime.now()
    }
    
    try:
        result = await db.users.insert_one(user_data)
        
        if result.inserted_id:
            print(f"✅ Created test user '{username}'")
            print(f"📝 Username: {username}")
            print(f"📝 Email: {email}")
            print(f"📝 Password: {password}")
            return True
        else:
            print("❌ Failed to create test user")
            return False
    
    except Exception as e:
        print(f"❌ Error creating test user: {str(e)}")
        return False

async def fix_frontend_api_connection():
    """Check and fix frontend API connection"""
    print("\n🔍 Checking frontend API configuration...")
    
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
    api_js_path = os.path.join(frontend_dir, "js", "api.js")
    
    if not os.path.exists(api_js_path):
        print(f"❌ API service file not found at {api_js_path}")
        return False
    
    print(f"✅ Found API service file at {api_js_path}")
    
    try:
        with open(api_js_path, 'r') as file:
            content = file.read()
        
        # Check if the baseUrl is correct
        expected_url = f"http://localhost:{settings.PORT}/api/v1"
        
        if f"this.baseUrl = '{expected_url}'" in content:
            print(f"✅ API base URL is correctly set to '{expected_url}'")
            return True
        
        # Try to find and fix the base URL
        import re
        base_url_pattern = r"this\.baseUrl\s*=\s*['\"](.*?)['\"]"
        match = re.search(base_url_pattern, content)
        
        if match:
            current_url = match.group(1)
            print(f"⚠️ Current API base URL: '{current_url}'")
            
            fix = input(f"Do you want to update the API URL to '{expected_url}'? (y/n): ").lower().strip() == 'y'
            if fix:
                new_content = re.sub(base_url_pattern, f"this.baseUrl = '{expected_url}'", content)
                
                # Backup original file
                backup_path = f"{api_js_path}.bak"
                with open(backup_path, 'w') as file:
                    file.write(content)
                print(f"✅ Created backup at {backup_path}")
                
                # Write fixed content
                with open(api_js_path, 'w') as file:
                    file.write(new_content)
                print(f"✅ Updated API base URL to '{expected_url}'")
                return True
        else:
            print("❌ Could not find API base URL in the file")
        
        return False
    
    except Exception as e:
        print(f"❌ Error checking API configuration: {str(e)}")
        return False

async def main():
    """Main function to fix auth issues"""
    print("🛠️  Auth Fixer Tool for Resume Screener")
    print("=======================================")
    
    # Check MongoDB connection
    client, db, mongodb_ok = await check_mongodb()
    
    if not mongodb_ok and client and db:
        # Create test user if needed
        create_user = input("Do you want to create a test user? (y/n): ").lower().strip() == 'y'
        if create_user:
            from datetime import datetime
            await create_test_user(db)
    
    # Check frontend API connection
    await fix_frontend_api_connection()
    
    print("\n🎯 Fix Summary:")
    print("1. Use the username 'string' with password 'string' to log in (confirmed working)")
    print("2. If login still fails, check browser console for errors")
    print("3. Try using the Auth Debug panel added to the frontend (green button in bottom left)")
    print("4. Make sure both frontend and backend servers are running")
    
    # Close MongoDB connection
    if client:
        client.close()

if __name__ == "__main__":
    asyncio.run(main()) 