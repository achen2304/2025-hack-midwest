"""
Sync Agent - Strands AI Agent for intelligent Canvas & Calendar syncing
Uses Claude 3.7 Sonnet to make smart decisions about scheduling and syncing
"""
import os
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from strands import Agent, tool
from strands.models import BedrockModel

from ..services.canvas_service import canvas_service
from ..services.google_calendar_service import google_calendar_service
from ..services.sync_service import sync_service

logger = logging.getLogger(__name__)


# Define tools for the Sync Agent

@tool
async def get_canvas_courses(user_id: str) -> List[Dict[str, Any]]:
    """
    Get all active Canvas courses for a user.
    Use this to see what courses are available.
    """
    try:
        courses = await canvas_service.get_courses(
            enrollment_state="active"
        )
        return [
            {
                "id": course["id"],
                "name": course.get("name"),
                "course_code": course.get("course_code"),
                "term": course.get("term", {}).get("name")
            }
            for course in courses
        ]
    except Exception as e:
        logger.error(f"Error getting Canvas courses: {e}")
        return []


@tool
async def get_tracked_courses(user_id: str) -> List[Dict[str, Any]]:
    """
    Get list of courses the user is currently tracking.
    Only tracked courses are synced to calendar.
    """
    try:
        courses = await sync_service.get_tracked_courses(user_id)
        return [
            {
                "course_id": c["course_id"],
                "course_name": c["course_name"],
                "course_code": c.get("course_code"),
                "last_synced": c.get("last_synced")
            }
            for c in courses
        ]
    except Exception as e:
        logger.error(f"Error getting tracked courses: {e}")
        return []


@tool
async def get_upcoming_assignments(user_id: str, days_ahead: int = 30) -> List[Dict[str, Any]]:
    """
    Get upcoming assignments from Canvas across all courses.

    Args:
        user_id: User ID
        days_ahead: Number of days to look ahead (default: 30)
    """
    try:
        assignments = await canvas_service.get_upcoming_assignments(user_id, days_ahead)
        return [
            {
                "id": a["id"],
                "title": a.get("name"),
                "course": a.get("course_name"),
                "course_code": a.get("course_code"),
                "due_date": a.get("due_at"),
                "points": a.get("points_possible"),
                "submitted": a.get("has_submitted_submissions", False),
                "url": a.get("html_url")
            }
            for a in assignments
        ]
    except Exception as e:
        logger.error(f"Error getting upcoming assignments: {e}")
        return []


@tool
async def check_calendar_availability(user_id: str, start_time: str, end_time: str) -> Dict[str, Any]:
    """
    Check if a time slot is available on Google Calendar.

    Args:
        user_id: User ID
        start_time: Start time in ISO format
        end_time: End time in ISO format

    Returns:
        Dict with availability status and any conflicting events
    """
    try:
        access_token = await sync_service.get_valid_access_token(user_id)
        if not access_token:
            return {"available": False, "error": "Calendar not connected"}

        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))

        # Get events in that time range
        events = await google_calendar_service.get_events(
            access_token,
            time_min=start_dt,
            time_max=end_dt
        )

        if not events:
            return {"available": True, "conflicts": []}

        conflicts = [
            {
                "summary": e.get("summary"),
                "start": e.get("start", {}).get("dateTime"),
                "end": e.get("end", {}).get("dateTime")
            }
            for e in events
        ]

        return {"available": False, "conflicts": conflicts}

    except Exception as e:
        logger.error(f"Error checking calendar availability: {e}")
        return {"available": False, "error": str(e)}


@tool
async def create_calendar_event_from_assignment(
    user_id: str,
    assignment_id: str,
    course_name: str,
    assignment_title: str,
    due_date: str,
    description: str = None
) -> Dict[str, Any]:
    """
    Create a Google Calendar event for an assignment.

    Args:
        user_id: User ID
        assignment_id: Canvas assignment ID
        course_name: Course name
        assignment_title: Assignment title
        due_date: Due date in ISO format
        description: Optional assignment description
    """
    try:
        access_token = await sync_service.get_valid_access_token(user_id)
        if not access_token:
            return {"success": False, "error": "Calendar not connected"}

        due_dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))

        event_data = {
            "summary": f"{course_name}: {assignment_title}",
            "description": description or f"Assignment due for {course_name}",
            "start": {
                "dateTime": due_dt.isoformat(),
                "timeZone": "America/Chicago"
            },
            "end": {
                "dateTime": (due_dt + timedelta(hours=1)).isoformat(),
                "timeZone": "America/Chicago"
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60},
                    {"method": "popup", "minutes": 60}
                ]
            },
            "colorId": "11"  # Red for assignments
        }

        event = await google_calendar_service.create_event(access_token, event_data)

        return {
            "success": True,
            "event_id": event["id"],
            "event_link": event.get("htmlLink")
        }

    except Exception as e:
        logger.error(f"Error creating calendar event: {e}")
        return {"success": False, "error": str(e)}


@tool
async def create_study_session(
    user_id: str,
    course_name: str,
    start_time: str,
    duration_hours: int,
    location: str = None
) -> Dict[str, Any]:
    """
    Create a study session event on Google Calendar.

    Args:
        user_id: User ID
        course_name: Course name for the study session
        start_time: Start time in ISO format
        duration_hours: Duration in hours
        location: Optional study location
    """
    try:
        access_token = await sync_service.get_valid_access_token(user_id)
        if not access_token:
            return {"success": False, "error": "Calendar not connected"}

        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        end_dt = start_dt + timedelta(hours=duration_hours)

        event_data = {
            "summary": f"Study: {course_name}",
            "description": f"Study session for {course_name}",
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": "America/Chicago"
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": "America/Chicago"
            },
            "location": location,
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 15}
                ]
            },
            "colorId": "9"  # Blue for study sessions
        }

        event = await google_calendar_service.create_event(access_token, event_data)

        return {
            "success": True,
            "event_id": event["id"],
            "event_link": event.get("htmlLink")
        }

    except Exception as e:
        logger.error(f"Error creating study session: {e}")
        return {"success": False, "error": str(e)}


@tool
async def analyze_workload(user_id: str, days_ahead: int = 14) -> Dict[str, Any]:
    """
    Analyze the user's workload over the next N days.
    Returns statistics about assignments, deadlines, and busy periods.

    Args:
        user_id: User ID
        days_ahead: Number of days to analyze (default: 14)
    """
    try:
        assignments = await canvas_service.get_upcoming_assignments(user_id, days_ahead)

        # Group by week
        by_week = {}
        total_points = 0

        for assignment in assignments:
            due_at = assignment.get("due_at")
            if not due_at:
                continue

            due_date = datetime.fromisoformat(due_at.replace("Z", "+00:00"))
            week_start = due_date - timedelta(days=due_date.weekday())
            week_key = week_start.strftime("%Y-%m-%d")

            if week_key not in by_week:
                by_week[week_key] = {
                    "week_start": week_key,
                    "assignments": 0,
                    "total_points": 0
                }

            by_week[week_key]["assignments"] += 1
            points = assignment.get("points_possible", 0)
            by_week[week_key]["total_points"] += points if points else 0
            total_points += points if points else 0

        return {
            "total_assignments": len(assignments),
            "total_points": total_points,
            "by_week": list(by_week.values()),
            "average_per_week": len(assignments) / max(1, len(by_week))
        }

    except Exception as e:
        logger.error(f"Error analyzing workload: {e}")
        return {"error": str(e)}


class SyncAgent:
    """Intelligent Sync Agent using Claude 3.7 Sonnet"""

    def __init__(self):
        # Initialize Bedrock model with Claude 3.7 Sonnet
        self.model = BedrockModel(
            model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            region=os.getenv("AWS_DEFAULT_REGION", "us-west-2"),
            temperature=0.7,
            max_tokens=4096
        )

        # Create agent with tools
        self.agent = Agent(
            model=self.model,
            tools=[
                get_canvas_courses,
                get_tracked_courses,
                get_upcoming_assignments,
                check_calendar_availability,
                create_calendar_event_from_assignment,
                create_study_session,
                analyze_workload
            ],
            system_prompt="""You are an intelligent academic scheduling assistant for college students.

Your responsibilities:
1. Help students manage their Canvas assignments and Google Calendar
2. Analyze workload and suggest optimal study schedules
3. Sync assignments to calendar with smart scheduling
4. Detect conflicts and propose solutions
5. Provide proactive suggestions based on upcoming deadlines

When syncing assignments:
- Create calendar events for assignments with due dates
- Add appropriate reminders (1 day before + 1 hour before)
- Use descriptive titles with course codes
- Include assignment details and links

When suggesting study sessions:
- Consider assignment difficulty and points value
- Find available time slots without conflicts
- Suggest breaking large assignments into multiple study sessions
- Recommend study times based on when assignments are due

Be helpful, organized, and proactive. Always explain your reasoning."""
        )

    def ask(self, user_id: str, query: str, context: Dict[str, Any] = None) -> str:
        """
        Ask the agent a question

        Args:
            user_id: User ID for context
            query: User's question or request
            context: Additional context

        Returns:
            Agent's response
        """
        # Build context-aware query
        full_query = f"User ID: {user_id}\n\n{query}"

        if context:
            full_query += f"\n\nAdditional context: {context}"

        try:
            response = self.agent(full_query)
            return response
        except Exception as e:
            logger.error(f"Error getting agent response: {e}")
            return f"I encountered an error: {str(e)}"


# Create singleton instance
sync_agent = SyncAgent()
