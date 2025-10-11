"""
Sync Orchestration Service for CampusMind
Coordinates syncing between Canvas LMS and Google Calendar
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import asyncio

from .canvas_service import canvas_service
from .google_calendar_service import google_calendar_service
from ..util.db import db_manager

logger = logging.getLogger(__name__)


class SyncService:
    """Service for orchestrating sync between Canvas and Google Calendar"""

    def __init__(self):
        self.canvas = canvas_service
        self.google = google_calendar_service

    async def _get_db(self) -> AsyncIOMotorDatabase:
        """Get database instance"""
        db = db_manager.get_database()
        return db

    async def get_tracked_courses(self, user_id: str) -> List[Dict[str, Any]]:
        """Get list of courses user is tracking"""
        db = await self._get_db()
        cursor = db.tracked_courses.find({"user_id": user_id, "is_tracked": True})
        return await cursor.to_list(length=None)

    async def track_courses(
        self,
        user_id: str,
        course_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Mark courses as tracked for a user

        Args:
            user_id: User ID
            course_ids: List of Canvas course IDs to track

        Returns:
            Dict with tracking results
        """
        db = await self._get_db()
        tracked = []
        failed = []

        for course_id in course_ids:
            try:
                # Get course details from Canvas
                course = await self.canvas.get_course(str(course_id))

                # Check if already tracked
                existing = await db.tracked_courses.find_one({
                    "user_id": user_id,
                    "course_id": str(course_id)
                })

                if existing is not None:
                    # Update to tracked if was untracked
                    await db.tracked_courses.update_one(
                        {"_id": existing["_id"]},
                        {"$set": {"is_tracked": True}}
                    )
                else:
                    # Create new tracked course
                    tracked_course = {
                        "user_id": user_id,
                        "course_id": str(course_id),
                        "course_name": course.get("name", "Unknown Course"),
                        "course_code": course.get("course_code", ""),
                        "is_tracked": True,
                        "meeting_times": [],
                        "created_at": datetime.utcnow(),
                        "last_synced": None
                    }
                    await db.tracked_courses.insert_one(tracked_course)

                tracked.append(course_id)

            except Exception as e:
                logger.error(f"Error tracking course {course_id}: {e}")
                failed.append({"course_id": course_id, "error": str(e)})

        return {
            "tracked": tracked,
            "failed": failed,
            "total": len(course_ids)
        }

    async def untrack_course(self, user_id: str, course_id: str) -> bool:
        """Mark course as untracked"""
        db = await self._get_db()
        result = await db.tracked_courses.update_one(
            {"user_id": user_id, "course_id": course_id},
            {"$set": {"is_tracked": False}}
        )
        return result.modified_count > 0

    async def add_meeting_time(
        self,
        user_id: str,
        course_id: str,
        meeting_time: Dict[str, Any]
    ) -> bool:
        """Add meeting time to a tracked course"""
        db = await self._get_db()
        result = await db.tracked_courses.update_one(
            {"user_id": user_id, "course_id": course_id},
            {"$push": {"meeting_times": meeting_time}}
        )
        return result.modified_count > 0

    async def get_user_tokens(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's Google OAuth tokens from database"""
        db = await self._get_db()
        tokens = await db.google_tokens.find_one({"user_id": user_id})
        return tokens

    async def save_user_tokens(
        self,
        user_id: str,
        access_token: str,
        refresh_token: str,
        expires_in: int
    ) -> None:
        """Save user's Google OAuth tokens to database"""
        db = await self._get_db()
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        await db.google_tokens.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "user_id": user_id,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_at": expires_at,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )

    async def get_valid_access_token(self, user_id: str) -> Optional[str]:
        """Get valid access token, refreshing if necessary"""
        tokens = await self.get_user_tokens(user_id)
        if not tokens:
            return None

        # Check if token is expired or expiring soon (within 5 minutes)
        expires_at = tokens.get("expires_at")
        if expires_at and expires_at < datetime.utcnow() + timedelta(minutes=5):
            # Refresh token
            try:
                refresh_token = tokens.get("refresh_token")
                new_tokens = await self.google.refresh_access_token(refresh_token)

                await self.save_user_tokens(
                    user_id,
                    new_tokens["access_token"],
                    refresh_token,  # Keep same refresh token
                    new_tokens["expires_in"]
                )

                return new_tokens["access_token"]
            except Exception as e:
                logger.error(f"Error refreshing token for user {user_id}: {e}")
                return None

        return tokens.get("access_token")

    async def sync_canvas_to_calendar(
        self,
        user_id: str,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Main sync function: Sync Canvas assignments to Google Calendar

        Args:
            user_id: User ID
            force: Force sync even if recently synced

        Returns:
            Dict with sync results
        """
        db = await self._get_db()

        # Get sync state
        sync_state = await db.sync_state.find_one({"user_id": user_id})

        # Check if we need to sync
        if not force and sync_state:
            last_sync = sync_state.get("last_canvas_sync")
            interval_hours = sync_state.get("auto_sync_interval_hours", 24)

            if last_sync and datetime.utcnow() - last_sync < timedelta(hours=interval_hours):
                return {
                    "status": "skipped",
                    "message": "Sync not needed yet",
                    "last_sync": last_sync
                }

        # Get valid access token
        access_token = await self.get_valid_access_token(user_id)
        if not access_token:
            return {
                "status": "error",
                "message": "Google Calendar not connected"
            }

        # Get tracked courses
        tracked_courses = await self.get_tracked_courses(user_id)

        if not tracked_courses:
            return {
                "status": "error",
                "message": "No courses being tracked"
            }

        synced_count = 0
        failed_count = 0
        created_events = []
        errors = []

        # For each tracked course, get assignments and sync
        for course in tracked_courses:
            try:
                course_id = course["course_id"]

                # Get assignments from Canvas
                assignments = await self.canvas.get_assignments(
                    course_id,
                    include=["submission"]
                )

                # Filter for upcoming assignments with due dates
                for assignment in assignments:
                    due_at = assignment.get("due_at")
                    if not due_at:
                        continue

                    # Check if already synced
                    existing = await db.canvas_assignments.find_one({
                        "user_id": user_id,
                        "id": str(assignment["id"])
                    })

                    # Parse due date
                    due_date = datetime.fromisoformat(due_at.replace("Z", "+00:00"))

                    # Only sync future assignments
                    if due_date < datetime.utcnow():
                        continue

                    # Create calendar event
                    event_data = {
                        "summary": f"{course['course_code']}: {assignment['name']}",
                        "description": f"Assignment due for {course['course_name']}\n\n{assignment.get('description', '')[:500]}\n\nView in Canvas: {assignment.get('html_url')}",
                        "start": {
                            "dateTime": due_date.isoformat(),
                            "timeZone": "America/Chicago"
                        },
                        "end": {
                            "dateTime": (due_date + timedelta(hours=1)).isoformat(),
                            "timeZone": "America/Chicago"
                        },
                        "reminders": {
                            "useDefault": False,
                            "overrides": [
                                {"method": "email", "minutes": 24 * 60},  # 1 day before
                                {"method": "popup", "minutes": 60}  # 1 hour before
                            ]
                        },
                        "colorId": "11"  # Red color for assignments
                    }

                    try:
                        if existing and existing.get("google_event_id"):
                            # Update existing event
                            await self.google.update_event(
                                access_token,
                                existing["google_event_id"],
                                event_data
                            )
                        else:
                            # Create new event
                            created_event = await self.google.create_event(
                                access_token,
                                event_data
                            )

                            # Save to database
                            assignment_doc = {
                                "id": str(assignment["id"]),
                                "user_id": user_id,
                                "course_id": course_id,
                                "course_name": course["course_name"],
                                "course_code": course.get("course_code"),
                                "title": assignment["name"],
                                "description": assignment.get("description"),
                                "due_at": due_date,
                                "points_possible": assignment.get("points_possible"),
                                "html_url": assignment.get("html_url"),
                                "google_event_id": created_event["id"],
                                "synced_to_calendar": True,
                                "created_at": datetime.utcnow()
                            }

                            await db.canvas_assignments.update_one(
                                {"user_id": user_id, "id": str(assignment["id"])},
                                {"$set": assignment_doc},
                                upsert=True
                            )

                            created_events.append(created_event)

                        synced_count += 1

                    except Exception as e:
                        logger.error(f"Error syncing assignment {assignment['id']}: {e}")
                        failed_count += 1
                        errors.append(str(e))

                # Update last sync time for course
                await db.tracked_courses.update_one(
                    {"user_id": user_id, "course_id": course_id},
                    {"$set": {"last_synced": datetime.utcnow()}}
                )

            except Exception as e:
                logger.error(f"Error syncing course {course['course_id']}: {e}")
                failed_count += 1
                errors.append(str(e))

        # Update sync state
        await db.sync_state.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "user_id": user_id,
                    "last_canvas_sync": datetime.utcnow(),
                    "last_sync_status": "success" if failed_count == 0 else "partial",
                    "last_sync_error": errors[0] if errors else None,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )

        return {
            "status": "success",
            "synced_count": synced_count,
            "failed_count": failed_count,
            "created_events": len(created_events),
            "errors": errors if errors else None
        }

    async def get_sync_status(self, user_id: str) -> Dict[str, Any]:
        """Get current sync status for user"""
        db = await self._get_db()
        sync_state = await db.sync_state.find_one({"user_id": user_id})

        if not sync_state:
            return {
                "sync_enabled": False,
                "last_sync": None,
                "status": "never_synced"
            }

        return {
            "sync_enabled": sync_state.get("sync_enabled", True),
            "last_canvas_sync": sync_state.get("last_canvas_sync"),
            "last_calendar_sync": sync_state.get("last_calendar_sync"),
            "last_sync_status": sync_state.get("last_sync_status"),
            "last_sync_error": sync_state.get("last_sync_error"),
            "auto_sync_interval_hours": sync_state.get("auto_sync_interval_hours", 24)
        }

    async def enable_auto_sync(self, user_id: str, interval_hours: int = 24) -> bool:
        """Enable automatic syncing"""
        db = await self._get_db()
        result = await db.sync_state.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "sync_enabled": True,
                    "auto_sync_interval_hours": interval_hours,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        return True

    async def disable_auto_sync(self, user_id: str) -> bool:
        """Disable automatic syncing"""
        db = await self._get_db()
        result = await db.sync_state.update_one(
            {"user_id": user_id},
            {"$set": {"sync_enabled": False, "updated_at": datetime.utcnow()}},
            upsert=True
        )
        return True


# Create singleton instance
sync_service = SyncService()
