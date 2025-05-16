#!/usr/bin/env python3
"""
Test MongoDB connection for Resume Screener
"""
import asyncio
import motor.motor_asyncio
from pymongo.errors import ServerSelectionTimeoutError

from app.core.config import settings

async def test_mongodb_connection():
    # Create a MongoDB client instance
    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=5000  # 5 second timeout
    )
    
    try:
        # Test the connection
        await client.admin.command('ping')
        print(f"✅ MongoDB connection successful at {settings.MONGODB_URL}")
        
        # Get the database
        db = client[settings.MONGODB_DB_NAME]
        print(f"✅ Database '{settings.MONGODB_DB_NAME}' accessed")
        
        # List collections
        collections = await db.list_collection_names()
        print(f"📝 Collections in database: {collections}")
        
        # Check if users collection exists
        if 'users' in collections:
            # Count users
            user_count = await db.users.count_documents({})
            print(f"👤 Found {user_count} users in the database")
            
            # List first 5 users (with limited fields for privacy)
            users = await db.users.find({}, {'username': 1, 'email': 1, '_id': 0}).limit(5).to_list(length=5)
            print(f"👥 Sample users (max 5): {users}")
        else:
            print("❌ Users collection not found")
        
        return True
    
    except ServerSelectionTimeoutError:
        print(f"❌ Could not connect to MongoDB at {settings.MONGODB_URL}")
        print("📋 Please check:")
        print("  - MongoDB server is running")
        print("  - Connection string is correct")
        print("  - Network/firewall settings allow connection")
        return False
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_mongodb_connection()) 