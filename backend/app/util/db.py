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
            raise
    
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
        """Create necessary collections with proper indexes"""
        try:
            # Create collections if they don't exist
            collections = [
                "users", "journal_entries", "assignments", 
                "study_plans", "canvas_courses", "vector_embeddings"
            ]
            
            for collection_name in collections:
                if collection_name not in await self.database.list_collection_names():
                    await self.database.create_collection(collection_name)
                    print(f"Created collection: {collection_name}")
            
            # Create indexes for better performance
            await self._create_indexes()
            
        except Exception as e:
            print(f"Error creating collections: {e}")
            raise
    
    async def _create_indexes(self):
        """Create database indexes"""
        try:
            # User indexes
            await self.database.users.create_index("email", unique=True)
            await self.database.users.create_index("university")
            
            # Journal entry indexes
            await self.database.journal_entries.create_index("user_id")
            await self.database.journal_entries.create_index("created_at")
            await self.database.journal_entries.create_index("mood")
            
            # Assignment indexes
            await self.database.assignments.create_index("user_id")
            await self.database.assignments.create_index("due_date")
            await self.database.assignments.create_index("status")
            
            # Study plan indexes
            await self.database.study_plans.create_index("user_id")
            await self.database.study_plans.create_index("created_at")
            
            print("Database indexes created successfully")
            
        except Exception as e:
            print(f"Error creating indexes: {e}")
            raise

# Global database manager instance
db_manager = DatabaseManager()

async def get_database() -> AsyncIOMotorDatabase:
    """Dependency to get database instance"""
    return db_manager.get_database()
