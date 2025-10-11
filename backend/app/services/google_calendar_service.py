"""
Google Calendar API Service for CampusMind
Handles all Google Calendar API interactions including events and tasks
"""
import httpx
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """Service for interacting with Google Calendar API"""

    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip('"')
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip('"')
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/callback")

        self.auth_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.calendar_api_base = "https://www.googleapis.com/calendar/v3"
        self.tasks_api_base = "https://www.googleapis.com/tasks/v1"

        if not self.client_id or not self.client_secret:
            logger.warning("Google OAuth credentials not found in environment variables")

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generate OAuth authorization URL for user to grant calendar access

        Args:
            state: Optional state parameter for CSRF protection

        Returns:
            Authorization URL to redirect user to
        """
        scopes = [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.events",
            "https://www.googleapis.com/auth/tasks"
        ]

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "access_type": "offline",  # Get refresh token
            "prompt": "consent"  # Force consent screen to get refresh token
        }

        if state:
            params["state"] = state

        return f"{self.auth_base_url}?{urlencode(params)}"

    async def exchange_code_for_tokens(self, auth_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens

        Args:
            auth_code: Authorization code from OAuth callback

        Returns:
            Dict containing access_token, refresh_token, expires_in, etc.
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.token_url, data=data)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error exchanging code for tokens: {e}")
            raise

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Refresh token from previous authorization

        Returns:
            Dict containing new access_token and expires_in
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.token_url, data=data)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            raise

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        access_token: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        api_base: str = None
    ) -> Any:
        """Make HTTP request to Google API"""
        base = api_base or self.calendar_api_base
        url = f"{base}/{endpoint}"

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
                return response.json() if response.text else {}
        except httpx.HTTPStatusError as e:
            logger.error(f"Google API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Google API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error making Google API request: {e}")
            raise

    async def list_calendars(self, access_token: str) -> List[Dict[str, Any]]:
        """List all calendars for the user"""
        result = await self._make_request(
            "GET",
            "users/me/calendarList",
            access_token
        )
        return result.get("items", [])

    async def get_calendar(self, access_token: str, calendar_id: str = "primary") -> Dict[str, Any]:
        """Get specific calendar details"""
        return await self._make_request(
            "GET",
            f"calendars/{calendar_id}",
            access_token
        )

    async def create_event(
        self,
        access_token: str,
        event_data: Dict[str, Any],
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """
        Create a calendar event

        Args:
            access_token: Google access token
            event_data: Event data in Google Calendar format
            calendar_id: Calendar ID (default: primary)

        Example event_data:
        {
            "summary": "Assignment Due: CS 101 Homework",
            "description": "Complete programming assignment",
            "start": {"dateTime": "2025-01-20T15:00:00-06:00"},
            "end": {"dateTime": "2025-01-20T16:00:00-06:00"},
            "location": "Online",
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60},
                    {"method": "popup", "minutes": 60}
                ]
            }
        }
        """
        return await self._make_request(
            "POST",
            f"calendars/{calendar_id}/events",
            access_token,
            json_data=event_data
        )

    async def get_events(
        self,
        access_token: str,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        calendar_id: str = "primary",
        max_results: int = 250
    ) -> List[Dict[str, Any]]:
        """
        Get calendar events within a time range

        Args:
            access_token: Google access token
            time_min: Start of time range (default: now)
            time_max: End of time range
            calendar_id: Calendar ID (default: primary)
            max_results: Maximum number of events to return
        """
        params = {
            "maxResults": max_results,
            "orderBy": "startTime",
            "singleEvents": True  # Expand recurring events
        }

        if time_min:
            params["timeMin"] = time_min.isoformat()
        else:
            params["timeMin"] = datetime.utcnow().isoformat() + "Z"

        if time_max:
            params["timeMax"] = time_max.isoformat()

        result = await self._make_request(
            "GET",
            f"calendars/{calendar_id}/events",
            access_token,
            params=params
        )
        return result.get("items", [])

    async def update_event(
        self,
        access_token: str,
        event_id: str,
        event_data: Dict[str, Any],
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Update an existing calendar event"""
        return await self._make_request(
            "PUT",
            f"calendars/{calendar_id}/events/{event_id}",
            access_token,
            json_data=event_data
        )

    async def delete_event(
        self,
        access_token: str,
        event_id: str,
        calendar_id: str = "primary"
    ) -> None:
        """Delete a calendar event"""
        await self._make_request(
            "DELETE",
            f"calendars/{calendar_id}/events/{event_id}",
            access_token
        )

    async def batch_create_events(
        self,
        access_token: str,
        events: List[Dict[str, Any]],
        calendar_id: str = "primary"
    ) -> List[Dict[str, Any]]:
        """
        Create multiple calendar events

        Args:
            access_token: Google access token
            events: List of event data dicts
            calendar_id: Calendar ID (default: primary)

        Returns:
            List of created event responses
        """
        created_events = []

        for event_data in events:
            try:
                created_event = await self.create_event(access_token, event_data, calendar_id)
                created_events.append(created_event)
            except Exception as e:
                logger.error(f"Error creating event {event_data.get('summary')}: {e}")
                created_events.append({"error": str(e), "event_data": event_data})

        return created_events

    # Google Tasks API methods

    async def list_task_lists(self, access_token: str) -> List[Dict[str, Any]]:
        """List all task lists"""
        result = await self._make_request(
            "GET",
            "users/@me/lists",
            access_token,
            api_base=self.tasks_api_base
        )
        return result.get("items", [])

    async def create_task(
        self,
        access_token: str,
        task_data: Dict[str, Any],
        tasklist_id: str = "@default"
    ) -> Dict[str, Any]:
        """
        Create a task in Google Tasks

        Args:
            access_token: Google access token
            task_data: Task data
            tasklist_id: Task list ID (default: @default)

        Example task_data:
        {
            "title": "Complete CS 101 Homework",
            "notes": "Programming assignment on data structures",
            "due": "2025-01-20T00:00:00.000Z"
        }
        """
        return await self._make_request(
            "POST",
            f"lists/{tasklist_id}/tasks",
            access_token,
            json_data=task_data,
            api_base=self.tasks_api_base
        )

    async def get_tasks(
        self,
        access_token: str,
        tasklist_id: str = "@default",
        show_completed: bool = False
    ) -> List[Dict[str, Any]]:
        """Get tasks from a task list"""
        params = {
            "showCompleted": str(show_completed).lower()
        }

        result = await self._make_request(
            "GET",
            f"lists/{tasklist_id}/tasks",
            access_token,
            params=params,
            api_base=self.tasks_api_base
        )
        return result.get("items", [])

    async def update_task(
        self,
        access_token: str,
        task_id: str,
        task_data: Dict[str, Any],
        tasklist_id: str = "@default"
    ) -> Dict[str, Any]:
        """Update an existing task"""
        return await self._make_request(
            "PUT",
            f"lists/{tasklist_id}/tasks/{task_id}",
            access_token,
            json_data=task_data,
            api_base=self.tasks_api_base
        )

    async def complete_task(
        self,
        access_token: str,
        task_id: str,
        tasklist_id: str = "@default"
    ) -> Dict[str, Any]:
        """Mark a task as completed"""
        task_data = {"status": "completed"}
        return await self.update_task(access_token, task_id, task_data, tasklist_id)

    async def test_connection(self, access_token: str) -> Dict[str, Any]:
        """Test Google Calendar API connection"""
        try:
            calendars = await self.list_calendars(access_token)
            return {
                "success": True,
                "calendars_count": len(calendars)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Create singleton instance
google_calendar_service = GoogleCalendarService()
