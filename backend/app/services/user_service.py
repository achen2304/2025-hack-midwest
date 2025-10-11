"""
User management service for CampusMind
Handles user creation and synchronization with Clerk
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..util.db import db_manager
from ..models.schemas import User

logger = logging.getLogger(__name__)


class UserService:
    """Service for managing user data in MongoDB"""

    def __init__(self):
        self.db = None

    async def _get_db(self) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if self.db is None:
            self.db = db_manager.get_database()
        return self.db

    async def create_or_update_user(
        self,
        user_id: str,
        email: str,
        name: str,
        university: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create or update user in database
        This should be called when a user first authenticates
        """
        db = await self._get_db()
        
        user_data = {
            "id": user_id,
            "email": email,
            "name": name,
            "university": university,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Use upsert to create or update
        result = await db.users.update_one(
            {"id": user_id},
            {
                "$set": {
                    "email": email,
                    "name": name,
                    "university": university,
                    "updated_at": datetime.utcnow()
                },
                "$setOnInsert": {
                    "id": user_id,
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )

        if result.upserted_id:
            logger.info(f"Created new user: {user_id}")
            return {"action": "created", "user_id": user_id}
        else:
            logger.info(f"Updated existing user: {user_id}")
            return {"action": "updated", "user_id": user_id}

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        db = await self._get_db()
        return await db.users.find_one({"id": user_id})

    async def user_exists(self, user_id: str) -> bool:
        """Check if user exists in database"""
        db = await self._get_db()
        user = await db.users.find_one({"id": user_id})
        return user is not None

    async def ensure_user_exists(
        self,
        user_id: str,
        email: str,
        name: str,
        university: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ensure user exists in database, create if not
        This is the main method to call from auth middleware
        """
        if not await self.user_exists(user_id):
            return await self.create_or_update_user(user_id, email, name, university)
        else:
            # Update existing user info in case it changed
            return await self.create_or_update_user(user_id, email, name, university)


# Create singleton instance
user_service = UserService()
