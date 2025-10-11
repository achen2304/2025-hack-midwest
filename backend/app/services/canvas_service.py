"""
Canvas LMS API Service for CampusMind - Per-User Token Version
Handles all Canvas API interactions with per-user authentication
"""
import httpx
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class CanvasService:
    """Service for interacting with Canvas LMS API with per-user tokens"""

    def __init__(self):
        self.default_base_url = os.getenv("CANVAS_BASE_URL", "https://canvas.iastate.edu")
        # Keep fallback token for backwards compatibility
        self.fallback_token = os.getenv("CANVAS_API_TOKEN")
        self.db = None

    async def _get_db(self) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if self.db is None:
            from ..util.db import db_manager
            self.db = db_manager.get_database()
        return self.db

    async def save_user_canvas_token(
        self,
        user_id: str,
        canvas_token: str,
        canvas_base_url: str = None
    ) -> None:
        """Save user's Canvas token to database"""
        db = await self._get_db()

        await db.canvas_tokens.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "user_id": user_id,
                    "canvas_token": canvas_token,
                    "canvas_base_url": canvas_base_url or self.default_base_url,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )

    async def get_user_canvas_token(self, user_id: str) -> Optional[Dict[str, str]]:
        """Get user's Canvas token from database"""
        db = await self._get_db()
        token_doc = await db.canvas_tokens.find_one({"user_id": user_id})

        if token_doc is not None:
            return {
                "token": token_doc["canvas_token"],
                "base_url": token_doc.get("canvas_base_url", self.default_base_url)
            }

        # Fallback to environment variable for backwards compatibility
        if self.fallback_token:
            logger.info(f"Using fallback Canvas token for user {user_id}")
            return {
                "token": self.fallback_token,
                "base_url": self.default_base_url
            }

        return None

    async def remove_user_canvas_token(self, user_id: str) -> bool:
        """Remove user's Canvas token from database"""
        db = await self._get_db()
        result = await db.canvas_tokens.delete_one({"user_id": user_id})
        return result.deleted_count > 0

    async def test_user_token(self, user_id: str) -> Dict[str, Any]:
        """Test if user's Canvas token works"""
        try:
            user = await self.get_current_user(user_id)
            return {
                "success": True,
                "user": user.get("name"),
                "user_id": user.get("id")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        access_token: str,
        base_url: str = None,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Any:
        """Make HTTP request to Canvas API"""
        api_base = f"{base_url or self.default_base_url}/api/v1"
        url = f"{api_base}/{endpoint}"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Canvas API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Canvas API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error making Canvas API request: {e}")
            raise

    async def get_current_user(self, user_id: str) -> Dict[str, Any]:
        """Get current user information"""
        token_data = await self.get_user_canvas_token(user_id)
        if not token_data:
            raise Exception("Canvas not connected. Please add your Canvas token.")

        return await self._make_request("GET", "users/self", token_data["token"], token_data["base_url"])

    async def get_courses(
        self,
        user_id: str,
        enrollment_state: str = "active",
        include: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get user's courses"""
        token_data = await self.get_user_canvas_token(user_id)
        if not token_data:
            raise Exception("Canvas not connected")

        params = {
            "enrollment_state": enrollment_state,
            "per_page": 100
        }

        if include:
            params["include[]"] = include

        return await self._make_request("GET", "courses", token_data["token"], token_data["base_url"], params=params)

    async def get_course(self, user_id: str, course_id: str) -> Dict[str, Any]:
        """Get specific course details"""
        token_data = await self.get_user_canvas_token(user_id)
        if not token_data:
            raise Exception("Canvas not connected")

        return await self._make_request("GET", f"courses/{course_id}", token_data["token"], token_data["base_url"])

    async def get_assignments(
        self,
        user_id: str,
        course_id: str,
        order_by: str = "due_at",
        include: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get assignments for a course"""
        token_data = await self.get_user_canvas_token(user_id)
        if not token_data:
            raise Exception("Canvas not connected")

        params = {
            "order_by": order_by,
            "per_page": 100
        }

        if include:
            params["include[]"] = include

        return await self._make_request(
            "GET",
            f"courses/{course_id}/assignments",
            token_data["token"],
            token_data["base_url"],
            params=params
        )

    async def get_assignment(
        self,
        user_id: str,
        course_id: str,
        assignment_id: str
    ) -> Dict[str, Any]:
        """Get specific assignment details"""
        token_data = await self.get_user_canvas_token(user_id)
        if not token_data:
            raise Exception("Canvas not connected")

        return await self._make_request(
            "GET",
            f"courses/{course_id}/assignments/{assignment_id}",
            token_data["token"],
            token_data["base_url"]
        )

    async def get_upcoming_assignments(
        self,
        user_id: str,
        days_ahead: int = 30
    ) -> List[Dict[str, Any]]:
        """Get all upcoming assignments across all courses"""
        courses = await self.get_courses(user_id)
        all_assignments = []

        now = datetime.utcnow()
        future_date = now + timedelta(days=days_ahead)

        token_data = await self.get_user_canvas_token(user_id)

        for course in courses:
            try:
                assignments = await self.get_assignments(
                    user_id,
                    course["id"],
                    include=["submission"]
                )

                for assignment in assignments:
                    if assignment.get("due_at"):
                        due_date = datetime.fromisoformat(
                            assignment["due_at"].replace("Z", "+00:00")
                        )

                        if now <= due_date <= future_date:
                            assignment["course_name"] = course.get("name")
                            assignment["course_code"] = course.get("course_code")
                            all_assignments.append(assignment)
            except Exception as e:
                logger.error(f"Error fetching assignments for course {course['id']}: {e}")
                continue

        all_assignments.sort(key=lambda x: x.get("due_at", ""))
        return all_assignments

    async def get_calendar_events(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        context_codes: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get calendar events"""
        token_data = await self.get_user_canvas_token(user_id)
        if not token_data:
            raise Exception("Canvas not connected")

        params = {
            "per_page": 100
        }

        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        if context_codes:
            params["context_codes[]"] = context_codes

        return await self._make_request("GET", "calendar_events", token_data["token"], token_data["base_url"], params=params)

    async def get_all_grades(self, user_id: str) -> List[Dict[str, Any]]:
        """Get grades for all courses"""
        courses = await self.get_courses(user_id, include=["total_scores"])
        grades = []

        for course in courses:
            if "enrollments" in course:
                for enrollment in course["enrollments"]:
                    if enrollment.get("type") == "student":
                        grades.append({
                            "course_id": course["id"],
                            "course_name": course.get("name"),
                            "course_code": course.get("course_code"),
                            "current_score": enrollment.get("grades", {}).get("current_score"),
                            "final_score": enrollment.get("grades", {}).get("final_score"),
                            "current_grade": enrollment.get("grades", {}).get("current_grade"),
                            "final_grade": enrollment.get("grades", {}).get("final_grade")
                        })

        return grades

    async def test_connection(self, user_id: str = None) -> Dict[str, Any]:
        """Test Canvas API connection"""
        if not user_id:
            # Use fallback token for testing
            if not self.fallback_token:
                return {"success": False, "error": "No Canvas token configured"}
            user_id = "fallback"

        return await self.test_user_token(user_id)


# Create singleton instance
canvas_service = CanvasService()
