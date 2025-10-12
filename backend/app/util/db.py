"""
Database connection and utilities for CampusMind
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from typing import Optional

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            mongodb_uri = os.getenv("MONGODB_URI")
            db_name = os.getenv("DB_NAME", "campusmind")
            
            if not mongodb_uri:
                raise ValueError("MONGODB_URI environment variable is required")
            
            self.client = AsyncIOMotorClient(mongodb_uri)
            self.database = self.client[db_name]
            
            # Test connection
            await self.client.admin.command('ping')
            print(f"Connected to MongoDB Atlas database: {db_name}")
            
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            print("Running in development mode without database")
            # In development, we'll continue without database for basic API testing
            self.client = None
            self.database = None
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client is not None:
            self.client.close()
            print("Disconnected from MongoDB")

    def get_database(self) -> AsyncIOMotorDatabase:
        """Get the database instance"""
        if self.database is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.database
    
    async def create_collections(self):
        """Setup database indexes (collections auto-create on first insert)"""
        try:
            # MongoDB automatically creates collections on first document insert
            # We only set up essential indexes here

            # User indexes - only if users collection exists
            existing_collections = await self.database.list_collection_names()

            if "users" in existing_collections:
                await self.database.users.create_index("email", unique=True)
                print("Created indexes on users collection")
                
            # Calendar events indexes
            if "calendar_events" in existing_collections:
                # Index for user_id + start_time for efficient queries
                await self.database.calendar_events.create_index([
                    ("user_id", 1),
                    ("start_time", 1)
                ])
                # Index for user_id + end_time for efficient date range queries
                await self.database.calendar_events.create_index([
                    ("user_id", 1),
                    ("end_time", 1)
                ])
                # Index for user_id + event_type for filtering by type
                await self.database.calendar_events.create_index([
                    ("user_id", 1),
                    ("event_type", 1)
                ])
                print("Created indexes on calendar_events collection")

            # Other indexes will be created as needed when collections are first used

        except Exception as e:
            # Don't fail startup if indexes can't be created
            print(f"Note: Could not create indexes: {e}")
            pass

# Global database manager instance
db_manager = DatabaseManager()

async def get_database() -> AsyncIOMotorDatabase:
    """Dependency to get database instance"""
    return db_manager.get_database()
