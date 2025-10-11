"""
Google Calendar integration endpoints for CampusMind
All endpoints require authentication via Clerk JWT token
"""
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from fastapi.responses import RedirectResponse
from typing import Optional
from datetime import datetime, timedelta

from ..models.schemas import APIResponse, CalendarAuthRequest
from ..services.google_calendar_service import google_calendar_service
from ..services.sync_service import sync_service
from ..middleware.auth import get_current_user

# Apply auth to ALL endpoints in this router
router = APIRouter(
    prefix="/calendar",
    tags=["calendar"],
    dependencies=[Depends(get_current_user)]
)


def get_user_id(request: Request) -> str:
    """Helper to extract user_id from request state"""
    return request.state.user["user_id"]


@router.get("/auth-url", response_model=APIResponse)
async def get_auth_url(request: Request):
    """Get Google OAuth authorization URL"""
    try:
        user_id = get_user_id(request)
        # Use user_id as state parameter for CSRF protection
        auth_url = google_calendar_service.get_authorization_url(state=user_id)

        return APIResponse(
            success=True,
            message="Authorization URL generated",
            data={"auth_url": auth_url}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth", response_model=APIResponse)
async def complete_oauth(request: Request, auth_request: CalendarAuthRequest):
    """Exchange authorization code for tokens"""
    try:
        user_id = get_user_id(request)

        # Exchange code for tokens
        tokens = await google_calendar_service.exchange_code_for_tokens(auth_request.auth_code)

        # Save tokens to database
        await sync_service.save_user_tokens(
            user_id,
            tokens["access_token"],
            tokens["refresh_token"],
            tokens["expires_in"]
        )

        return APIResponse(
            success=True,
            message="Google Calendar connected successfully",
            data={"expires_in": tokens["expires_in"]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test", response_model=APIResponse)
async def test_calendar_connection(request: Request):
    """Test Google Calendar API connection"""
    try:
        user_id = get_user_id(request)
        access_token = await sync_service.get_valid_access_token(user_id)
        if not access_token:
            raise HTTPException(status_code=401, detail="Calendar not connected")

        result = await google_calendar_service.test_connection(access_token)
        if result["success"]:
            return APIResponse(
                success=True,
                message="Google Calendar connected",
                data=result
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calendars", response_model=APIResponse)
async def list_calendars(request: Request):
    """Get list of user's calendars"""
    try:
        user_id = get_user_id(request)
        access_token = await sync_service.get_valid_access_token(user_id)
        if not access_token:
            raise HTTPException(status_code=401, detail="Calendar not connected")

        calendars = await google_calendar_service.list_calendars(access_token)
        return APIResponse(
            success=True,
            message=f"Retrieved {len(calendars)} calendars",
            data={"calendars": calendars, "count": len(calendars)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events", response_model=APIResponse)
async def get_events(
    request: Request,
    days_ahead: int = 30,
    calendar_id: str = "primary"
):
    """Get calendar events"""
    try:
        user_id = get_user_id(request)
        access_token = await sync_service.get_valid_access_token(user_id)
        if not access_token:
            raise HTTPException(status_code=401, detail="Calendar not connected")

        time_min = datetime.utcnow()
        time_max = time_min + timedelta(days=days_ahead)

        events = await google_calendar_service.get_events(
            access_token,
            time_min=time_min,
            time_max=time_max,
            calendar_id=calendar_id
        )

        return APIResponse(
            success=True,
            message=f"Retrieved {len(events)} events",
            data={"events": events, "count": len(events)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events", response_model=APIResponse)
async def create_event(
    request: Request,
    event_data: dict,
    calendar_id: str = "primary"
):
    """Create a calendar event"""
    try:
        user_id = get_user_id(request)
        access_token = await sync_service.get_valid_access_token(user_id)
        if not access_token:
            raise HTTPException(status_code=401, detail="Calendar not connected")

        event = await google_calendar_service.create_event(
            access_token,
            event_data,
            calendar_id
        )

        return APIResponse(
            success=True,
            message="Event created successfully",
            data={"event": event}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/events/{event_id}", response_model=APIResponse)
async def update_event(
    request: Request,
    event_id: str,
    event_data: dict,
    calendar_id: str = "primary"
):
    """Update a calendar event"""
    try:
        user_id = get_user_id(request)
        access_token = await sync_service.get_valid_access_token(user_id)
        if not access_token:
            raise HTTPException(status_code=401, detail="Calendar not connected")

        event = await google_calendar_service.update_event(
            access_token,
            event_id,
            event_data,
            calendar_id
        )

        return APIResponse(
            success=True,
            message="Event updated successfully",
            data={"event": event}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/events/{event_id}", response_model=APIResponse)
async def delete_event(
    request: Request,
    event_id: str,
    calendar_id: str = "primary"
):
    """Delete a calendar event"""
    try:
        user_id = get_user_id(request)
        access_token = await sync_service.get_valid_access_token(user_id)
        if not access_token:
            raise HTTPException(status_code=401, detail="Calendar not connected")

        await google_calendar_service.delete_event(access_token, event_id, calendar_id)

        return APIResponse(
            success=True,
            message="Event deleted successfully",
            data={"event_id": event_id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Google Tasks endpoints

@router.get("/tasks/lists", response_model=APIResponse)
async def list_task_lists(request: Request):
    """Get user's task lists"""
    try:
        user_id = get_user_id(request)
        access_token = await sync_service.get_valid_access_token(user_id)
        if not access_token:
            raise HTTPException(status_code=401, detail="Calendar not connected")

        task_lists = await google_calendar_service.list_task_lists(access_token)
        return APIResponse(
            success=True,
            message=f"Retrieved {len(task_lists)} task lists",
            data={"task_lists": task_lists, "count": len(task_lists)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks", response_model=APIResponse)
async def get_tasks(
    request: Request,
    tasklist_id: str = "@default",
    show_completed: bool = False
):
    """Get tasks from a task list"""
    try:
        user_id = get_user_id(request)
        access_token = await sync_service.get_valid_access_token(user_id)
        if not access_token:
            raise HTTPException(status_code=401, detail="Calendar not connected")

        tasks = await google_calendar_service.get_tasks(
            access_token,
            tasklist_id,
            show_completed
        )

        return APIResponse(
            success=True,
            message=f"Retrieved {len(tasks)} tasks",
            data={"tasks": tasks, "count": len(tasks)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks", response_model=APIResponse)
async def create_task(
    request: Request,
    task_data: dict,
    tasklist_id: str = "@default"
):
    """Create a new task"""
    try:
        user_id = get_user_id(request)
        access_token = await sync_service.get_valid_access_token(user_id)
        if not access_token:
            raise HTTPException(status_code=401, detail="Calendar not connected")

        task = await google_calendar_service.create_task(
            access_token,
            task_data,
            tasklist_id
        )

        return APIResponse(
            success=True,
            message="Task created successfully",
            data={"task": task}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/tasks/{task_id}/complete", response_model=APIResponse)
async def complete_task(
    request: Request,
    task_id: str,
    tasklist_id: str = "@default"
):
    """Mark a task as completed"""
    try:
        user_id = get_user_id(request)
        access_token = await sync_service.get_valid_access_token(user_id)
        if not access_token:
            raise HTTPException(status_code=401, detail="Calendar not connected")

        task = await google_calendar_service.complete_task(
            access_token,
            task_id,
            tasklist_id
        )

        return APIResponse(
            success=True,
            message="Task marked as completed",
            data={"task": task}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
