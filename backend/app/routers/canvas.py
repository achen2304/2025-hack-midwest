"""
Canvas LMS integration endpoints for CampusMind
All endpoints require authentication via Clerk JWT token
"""
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from typing import List, Optional, Dict
from ..models.schemas import (
    CanvasCourse, APIResponse, TrackedCourse,
    TrackCourseRequest, UntrackCourseRequest, AddMeetingTimeRequest,
    CanvasTokenRequest
)
from ..services.canvas_service import canvas_service
from ..services.sync_service import sync_service
from ..middleware.auth import get_current_user

# Apply auth to ALL endpoints in this router
router = APIRouter(
    prefix="/canvas",
    tags=["canvas"],
    dependencies=[Depends(get_current_user)]
)


def get_user_id(request: Request) -> str:
    """Helper to extract user_id from request state"""
    return request.state.user["user_id"]


# Canvas Token Management

@router.post("/connect", response_model=APIResponse)
async def connect_canvas(request: Request, token_request: CanvasTokenRequest):
    """
    Save user's Canvas Personal Access Token
    Users get their token from: Canvas → Settings → Approved Integrations → New Access Token

    Requires: Bearer token in Authorization header
    """
    try:
        user_id = get_user_id(request)

        await canvas_service.save_user_canvas_token(
            user_id,
            token_request.canvas_token,
            token_request.canvas_base_url
        )

        # Test the token
        test_result = await canvas_service.test_user_token(user_id)

        if test_result["success"]:
            return APIResponse(
                success=True,
                message=f"Canvas connected successfully as {test_result['user']}",
                data=test_result
            )
        else:
            # Remove invalid token
            await canvas_service.remove_user_canvas_token(user_id)
            raise HTTPException(status_code=401, detail=f"Invalid Canvas token: {test_result['error']}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/disconnect", response_model=APIResponse)
async def disconnect_canvas(request: Request):
    """Remove user's Canvas token"""
    try:
        user_id = get_user_id(request)
        success = await canvas_service.remove_user_canvas_token(user_id)
        return APIResponse(
            success=success,
            message="Canvas disconnected" if success else "No Canvas connection found",
            data={"user_id": user_id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test", response_model=APIResponse)
async def test_canvas_connection(request: Request):
    """Test Canvas API connection for authenticated user"""
    try:
        user_id = get_user_id(request)
        result = await canvas_service.test_connection(user_id)
        if result["success"]:
            return APIResponse(
                success=True,
                message=f"Canvas connected as {result['user']}",
                data=result
            )
        else:
            raise HTTPException(status_code=401, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/courses", response_model=List[dict])
async def get_canvas_courses(request: Request, enrollment_state: str = "active"):
    """Get all active Canvas courses for authenticated user"""
    try:
        user_id = get_user_id(request)
        courses = await canvas_service.get_courses(user_id, enrollment_state=enrollment_state)
        return [
            {
                "id": str(course["id"]),
                "name": course.get("name"),
                "course_code": course.get("course_code"),
                "enrollment_term_id": course.get("enrollment_term_id"),
                "start_at": course.get("start_at"),
                "end_at": course.get("end_at")
            }
            for course in courses
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/courses/{course_id}")
async def get_course(request: Request, course_id: str):
    """Get specific course details"""
    try:
        user_id = get_user_id(request)
        course = await canvas_service.get_course(user_id, course_id)
        return course
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/courses/{course_id}/assignments")
async def get_course_assignments(request: Request, course_id: str):
    """Get assignments for a specific course"""
    try:
        user_id = get_user_id(request)
        assignments = await canvas_service.get_assignments(
            user_id,
            course_id,
            include=["submission"]
        )
        return assignments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assignments/upcoming", response_model=APIResponse)
async def get_upcoming_assignments(request: Request, days_ahead: int = 30):
    """Get all upcoming assignments across all courses"""
    try:
        user_id = get_user_id(request)
        assignments = await canvas_service.get_upcoming_assignments(user_id, days_ahead)
        return APIResponse(
            success=True,
            message=f"Retrieved {len(assignments)} upcoming assignments",
            data={"assignments": assignments, "count": len(assignments)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/grades", response_model=APIResponse)
async def get_all_grades(request: Request):
    """Get grades for all courses"""
    try:
        user_id = get_user_id(request)
        grades = await canvas_service.get_all_grades(user_id)
        return APIResponse(
            success=True,
            message="Grades retrieved successfully",
            data={"grades": grades}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calendar-events", response_model=APIResponse)
async def get_calendar_events(
    request: Request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get Canvas calendar events"""
    try:
        from datetime import datetime
        user_id = get_user_id(request)
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None

        events = await canvas_service.get_calendar_events(user_id, start, end)
        return APIResponse(
            success=True,
            message="Calendar events retrieved",
            data={"events": events, "count": len(events)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Course Tracking Endpoints

@router.get("/tracked-courses", response_model=List[dict])
async def get_tracked_courses(request: Request):
    """Get courses user is tracking"""
    try:
        user_id = get_user_id(request)
        courses = await sync_service.get_tracked_courses(user_id)
        return courses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/track-courses", response_model=APIResponse)
async def track_courses(request: Request, track_request: TrackCourseRequest):
    """Track selected courses for syncing"""
    try:
        user_id = get_user_id(request)
        result = await sync_service.track_courses(user_id, track_request.course_ids)
        return APIResponse(
            success=True,
            message=f"Tracked {len(result['tracked'])} courses",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/untrack-course", response_model=APIResponse)
async def untrack_course(request: Request, untrack_request: UntrackCourseRequest):
    """Stop tracking a course"""
    try:
        user_id = get_user_id(request)
        success = await sync_service.untrack_course(user_id, untrack_request.course_id)
        return APIResponse(
            success=success,
            message="Course untracked" if success else "Failed to untrack course",
            data={"course_id": untrack_request.course_id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add-meeting-time", response_model=APIResponse)
async def add_meeting_time(request: Request, meeting_request: AddMeetingTimeRequest):
    """Add meeting time to a tracked course"""
    try:
        user_id = get_user_id(request)
        success = await sync_service.add_meeting_time(
            user_id,
            meeting_request.course_id,
            meeting_request.meeting_time.dict()
        )
        return APIResponse(
            success=success,
            message="Meeting time added" if success else "Failed to add meeting time",
            data=meeting_request.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
