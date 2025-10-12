"""
Canvas LMS integration routes
"""
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timedelta
from bson import ObjectId
from typing import List

from app.util.db import get_database
from app.util.auth import verify_backend_token
from app.services.canvas_service import CanvasService
from app.models.schemas import (
    CanvasTokenUpdate,
    CanvasTokenResponse,
    CanvasCourseResponse,
    CanvasAssignmentResponse,
    CanvasSyncResponse,
    TrackCoursesRequest,
    TrackCoursesResponse,
    CanvasCalendarEvent,
    CanvasCalendarSyncResponse,
    CanvasCalendarEventType,
    EventType
)
import httpx

router = APIRouter(prefix="/canvas", tags=["Canvas"])

@router.post("/test-connection")
async def test_canvas_connection(
    token_data: CanvasTokenUpdate,
    user=Depends(verify_backend_token)
):
    """Test Canvas API connection with provided token"""
    try:
        base_url = token_data.canvas_base_url or "https://canvas.instructure.com"
        
        # Initialize Canvas service
        canvas_service = CanvasService(base_url, token_data.canvas_token)
        
        # Test connection
        result = canvas_service.test_connection()
        
        if result["success"]:
            return {
                "success": True,
                "message": "Canvas connection successful",
                "user": result["user"],
                "canvas_url": result["canvas_url"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Canvas connection failed: {result['error']}"
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test Canvas connection: {str(e)}"
        )

@router.post("/token", response_model=CanvasTokenResponse)
async def save_canvas_token(
    token_data: CanvasTokenUpdate,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Save or update Canvas Personal Access Token for user"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Prepare update data
        update_data = {
            "canvas_token": token_data.canvas_token,
            "canvas_base_url": token_data.canvas_base_url or "https://canvas.instructure.com",
            "canvas_token_updated_at": datetime.utcnow()
        }

        # Try to update by MongoDB _id first
        result = None
        try:
            result = await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
        except:
            pass

        # If not found by ObjectId, try email
        if not result or result.matched_count == 0:
            result = await db.users.update_one(
                {"email": email},
                {
                    "$set": update_data,
                    "$setOnInsert": {
                        "email": email,
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )

        if result.matched_count == 0 and not result.upserted_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return CanvasTokenResponse(
            success=True,
            message="Canvas token saved successfully",
            has_token=True
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save Canvas token: {str(e)}"
        )

@router.get("/token/status", response_model=CanvasTokenResponse)
async def check_canvas_token(
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Check if user has Canvas token configured"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Try to find user by MongoDB _id first
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass

        if not user_doc:
            user_doc = await db.users.find_one({"email": email})

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        has_token = "canvas_token" in user_doc and user_doc["canvas_token"]

        return CanvasTokenResponse(
            success=True,
            message="Token status retrieved",
            has_token=has_token
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check Canvas token status: {str(e)}"
        )

@router.delete("/token", response_model=CanvasTokenResponse)
async def delete_canvas_token(
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Remove Canvas token from user account"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Try to update by MongoDB _id first
        result = None
        try:
            result = await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$unset": {"canvas_token": "", "canvas_base_url": "", "canvas_token_updated_at": ""}}
            )
        except:
            pass

        # If not found by ObjectId, try email
        if not result or result.matched_count == 0:
            result = await db.users.update_one(
                {"email": email},
                {"$unset": {"canvas_token": "", "canvas_base_url": "", "canvas_token_updated_at": ""}}
            )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return CanvasTokenResponse(
            success=True,
            message="Canvas token removed successfully",
            has_token=False
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete Canvas token: {str(e)}"
        )

async def get_user_canvas_config(user_id: str, email: str, db):
    """Helper function to get user's Canvas configuration"""
    user_doc = None
    try:
        user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
    except:
        pass

    if not user_doc:
        user_doc = await db.users.find_one({"email": email})

    if not user_doc or "canvas_token" not in user_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Canvas token not configured. Please add your Canvas token first."
        )

    return {
        "token": user_doc["canvas_token"],
        "base_url": user_doc.get("canvas_base_url", "https://canvas.instructure.com"),
        "user_doc": user_doc
    }
    
async def fetch_canvas_calendar_events(config, tracked_course_ids, start_date=None, end_date=None):
    """Fetch calendar events from Canvas API for tracked courses"""
    try:
        # Prepare context codes for filtering (course_123, course_456, etc.)
        context_codes = [f"course_{course_id}" for course_id in tracked_course_ids]
        
        # Add user's personal calendar
        context_codes.append("user_self")
        
        if not context_codes:
            return []
            
        # Prepare query parameters
        params = {
            "context_codes[]": context_codes,
            "per_page": 100,
            "all_events": "true",  # Include assignments, calendar events, etc.
            "type": "event"  # Focus on calendar events first
        }
        
        # Add date filters if provided
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
            
        # Fetch calendar events from Canvas
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config['base_url']}/api/v1/calendar_events",
                headers={"Authorization": f"Bearer {config['token']}"},
                params=params
            )
            
            if response.status_code != 200:
                print(f"Failed to fetch calendar events: {response.status_code} {response.text}")
                return []
                
            events_data = response.json()
            
            # Convert to our schema
            events = []
            for event in events_data:
                # Determine event type
                event_type = CanvasCalendarEventType.CALENDAR
                if "assignment" in event:
                    event_type = CanvasCalendarEventType.ASSIGNMENT
                elif "discussion_topic" in event:
                    event_type = CanvasCalendarEventType.DISCUSSION
                elif "quiz" in event:
                    event_type = CanvasCalendarEventType.QUIZ
                    
                # Extract context name (course name or "Personal")
                context_name = "Personal"
                context_code = event.get("context_code", "")
                if context_code.startswith("course_"):
                    course_id = context_code.split("_")[1]
                    # Try to find course name
                    for course_id_str in tracked_course_ids:
                        if str(course_id) == str(course_id_str):
                            # This is a tracked course, get its name
                            context_name = f"Course {course_id}"  # Default if we can't find the name
                            break
                
                events.append(CanvasCalendarEvent(
                    id=str(event["id"]),
                    title=event.get("title", "Untitled Event"),
                    description=event.get("description"),
                    start_at=event.get("start_at"),
                    end_at=event.get("end_at"),
                    location_name=event.get("location_name"),
                    context_code=event.get("context_code", ""),
                    context_name=context_name,
                    html_url=event.get("html_url"),
                    all_day=event.get("all_day", False),
                    type=event_type
                ))
                
            return events
            
    except Exception as e:
        print(f"Error fetching Canvas calendar events: {str(e)}")
        return []
        
def map_canvas_event_to_calendar_event(canvas_event, user_id):
    """Convert Canvas calendar event to our calendar event format"""
    # Map Canvas event type to our event type
    event_type = EventType.ACADEMIC
    if canvas_event.type == CanvasCalendarEventType.CALENDAR:
        if canvas_event.context_code == "user_self":
            event_type = EventType.PERSONAL
        else:
            event_type = EventType.ACADEMIC
    elif canvas_event.type == CanvasCalendarEventType.ASSIGNMENT:
        event_type = EventType.ACADEMIC
    elif canvas_event.type == CanvasCalendarEventType.DISCUSSION:
        event_type = EventType.ACADEMIC
    elif canvas_event.type == CanvasCalendarEventType.QUIZ:
        event_type = EventType.ACADEMIC
        
    # Generate a color based on the context_code
    colors = {
        "user_self": "#4285F4",  # Blue for personal events
        "academic": "#0F9D58",    # Green for academic events
        "assignment": "#DB4437",  # Red for assignments
        "quiz": "#F4B400"         # Yellow for quizzes
    }
    
    # Default color based on event type
    color = colors.get("academic")
    
    # If it's a personal event, use that color
    if canvas_event.context_code == "user_self":
        color = colors.get("user_self")
    
    # If it's an assignment or quiz, use those colors
    if canvas_event.type == CanvasCalendarEventType.ASSIGNMENT:
        color = colors.get("assignment")
    elif canvas_event.type == CanvasCalendarEventType.QUIZ:
        color = colors.get("quiz")
    
    # Create event document
    now = datetime.utcnow()
    
    # Build location string
    location = canvas_event.location_name or ""
    if not location and canvas_event.context_name and canvas_event.context_name != "Personal":
        location = canvas_event.context_name
        
    # Build title with context if needed
    title = canvas_event.title
    if canvas_event.context_name and canvas_event.context_name != "Personal" and canvas_event.type != CanvasCalendarEventType.CALENDAR:
        title = f"{title} ({canvas_event.context_name})"
    
    # Handle end time if not provided
    end_time = canvas_event.end_at
    if not end_time and canvas_event.start_at:
        # Default to 1 hour duration if no end time
        end_time = canvas_event.start_at + timedelta(hours=1)
    
    return {
        "user_id": user_id,
        "title": title,
        "description": canvas_event.description,
        "start_time": canvas_event.start_at,
        "end_time": end_time,
        "location": location,
        "event_type": event_type,
        "priority": "medium",
        "is_recurring": False,
        "recurrence_pattern": None,
        "color": color,
        "notifications": [15, 60],  # Default notifications
        "canvas_id": canvas_event.id,
        "canvas_url": canvas_event.html_url,
        "canvas_context_code": canvas_event.context_code,
        "created_at": now,
        "updated_at": now
    }

@router.get("/courses", response_model=List[CanvasCourseResponse])
async def get_canvas_courses(
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Get user's Canvas courses using canvasapi library"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        config = await get_user_canvas_config(user_id, email, db)

        # Get user's tracked courses
        user_doc = config.get("user_doc", {})
        tracked_course_ids = user_doc.get("tracked_course_ids", [])

        # Initialize Canvas service
        canvas_service = CanvasService(config["base_url"], config["token"])
        
        # Fetch courses from Canvas using canvasapi
        courses = canvas_service.get_courses(enrollment_state="active", per_page=100)
        course_responses = []

        for course in courses:
            course_id = str(course["id"])
            is_tracked = course_id in tracked_course_ids

            # If user has tracked courses, only return those
            if tracked_course_ids and not is_tracked:
                continue

            course_responses.append(CanvasCourseResponse(
                id=course_id,
                name=course.get("name", ""),
                course_code=course.get("course_code", ""),
                enrollment_term_id=course.get("enrollment_term_id"),
                start_at=course.get("start_at"),
                end_at=course.get("end_at"),
                is_tracked=is_tracked
            ))

        return course_responses

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch Canvas courses: {str(e)}"
        )

@router.put("/courses/track", response_model=TrackCoursesResponse)
async def track_courses(
    track_request: TrackCoursesRequest,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Set which Canvas courses to track"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Try to update by MongoDB _id first
        result = None
        try:
            result = await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"tracked_course_ids": track_request.course_ids}}
            )
        except:
            pass

        # If not found by ObjectId, try email
        if not result or result.matched_count == 0:
            result = await db.users.update_one(
                {"email": email},
                {"$set": {"tracked_course_ids": track_request.course_ids}}
            )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return TrackCoursesResponse(
            success=True,
            message=f"Now tracking {len(track_request.course_ids)} courses",
            tracked_count=len(track_request.course_ids)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update tracked courses: {str(e)}"
        )


@router.post("/sync", response_model=CanvasSyncResponse)
async def sync_canvas_data(
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Sync Canvas courses and assignments to database (tracked courses only)"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        config = await get_user_canvas_config(user_id, email, db)

        # Get user's MongoDB ID and tracked courses
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass

        if not user_doc:
            user_doc = await db.users.find_one({"email": email})

        if user_doc:
            db_user_id = str(user_doc["_id"])
        else:
            db_user_id = user_id  # Fallback to JWT sub

        tracked_course_ids = user_doc.get("tracked_course_ids", []) if user_doc else []

        # If no tracked courses, return empty sync result
        if not tracked_course_ids:
            return CanvasSyncResponse(
                success=True,
                message="No courses tracked. Please select courses to track first.",
                courses_synced=0,
                assignments_synced=0
            )

        async with httpx.AsyncClient() as client:
            # Fetch courses
            courses_response = await client.get(
                f"{config['base_url']}/api/v1/courses",
                headers={"Authorization": f"Bearer {config['token']}"},
                params={"enrollment_state": "active", "per_page": 100}
            )

            if courses_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to fetch courses from Canvas"
                )

            courses = courses_response.json()
            courses_synced = 0
            assignments_synced = 0

            # Sync only tracked courses
            for course in courses:
                course_id = str(course["id"])

                # Skip if not tracked
                if course_id not in tracked_course_ids:
                    continue
                await db.canvas_courses.update_one(
                    {"canvas_id": str(course["id"]), "user_id": db_user_id},
                    {
                        "$set": {
                            "canvas_id": str(course["id"]),
                            "user_id": db_user_id,
                            "name": course.get("name", ""),
                            "course_code": course.get("course_code", ""),
                            "enrollment_term_id": course.get("enrollment_term_id"),
                            "start_at": course.get("start_at"),
                            "end_at": course.get("end_at"),
                            "synced_at": datetime.utcnow()
                        }
                    },
                    upsert=True
                )
                courses_synced += 1

                # Fetch and sync assignments for this course
                assignments_response = await client.get(
                    f"{config['base_url']}/api/v1/courses/{course['id']}/assignments",
                    headers={"Authorization": f"Bearer {config['token']}"},
                    params={"per_page": 100, "include[]": "submission"}
                )

                if assignments_response.status_code == 200:
                    assignments = assignments_response.json()
                    for assignment in assignments:
                        # Get submission status from Canvas
                        submission = assignment.get("submission", {})
                        workflow_state = submission.get("workflow_state", "unsubmitted")

                        # Map Canvas workflow_state to our status
                        # Note: Canvas can only set not_started or completed
                        # "in_progress" can ONLY be set manually by the user
                        if workflow_state in ["submitted", "pending_review", "graded", "complete"]:
                            canvas_status = "completed"  # Student has submitted
                        else:
                            canvas_status = "not_started"

                        # Check if assignment already exists
                        existing = await db.assignments.find_one({
                            "canvas_id": str(assignment["id"]),
                            "user_id": db_user_id
                        })

                        # IMPORTANT: Preserve "in_progress" status if user manually set it
                        # Sync should NEVER overwrite in_progress status
                        if existing and existing.get("status") == "in_progress":
                            # Don't overwrite - user is working on it
                            final_status = "in_progress"
                        else:
                            # Use Canvas status (not_started or completed)
                            final_status = canvas_status

                        await db.assignments.update_one(
                            {"canvas_id": str(assignment["id"]), "user_id": db_user_id},
                            {
                                "$set": {
                                    "canvas_id": str(assignment["id"]),
                                    "user_id": db_user_id,
                                    "title": assignment.get("name", ""),
                                    "description": assignment.get("description"),
                                    "course": course.get("course_code", ""),
                                    "course_id": str(course["id"]),
                                    "due_date": assignment.get("due_at"),
                                    "points_possible": assignment.get("points_possible"),
                                    "submission_types": assignment.get("submission_types", []),
                                    "status": final_status,
                                    "canvas_workflow_state": workflow_state,
                                    "synced_at": datetime.utcnow()
                                },
                                "$setOnInsert": {
                                    "created_at": datetime.utcnow()
                                }
                            },
                            upsert=True
                        )
                        assignments_synced += 1

            return CanvasSyncResponse(
                success=True,
                message=f"Successfully synced {courses_synced} courses and {assignments_synced} assignments",
                courses_synced=courses_synced,
                assignments_synced=assignments_synced
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync Canvas data: {str(e)}"
        )

@router.post("/calendar/sync", response_model=CanvasCalendarSyncResponse)
async def sync_canvas_calendar(
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """
    Sync Canvas calendar events to the database
    
    This endpoint fetches calendar events from Canvas for tracked courses and the user's personal calendar,
    then syncs them to the database as calendar events. This allows users to see their Canvas events
    in the CampusMind calendar.
    """
    try:
        user_id = user.get("sub")
        email = user.get("email")

        config = await get_user_canvas_config(user_id, email, db)

        # Get user's MongoDB ID and tracked courses
        user_doc = config.get("user_doc")
        
        if user_doc:
            db_user_id = str(user_doc["_id"])
        else:
            db_user_id = user_id  # Fallback to JWT sub

        tracked_course_ids = user_doc.get("tracked_course_ids", []) if user_doc else []

        # If no tracked courses, we can still sync personal calendar
        if not tracked_course_ids:
            # Just inform the user that we're only syncing personal events
            print("No tracked courses found, only syncing personal calendar")

        # Fetch calendar events from Canvas
        # Default to fetching events for the next 3 months
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=90)  # 3 months ahead
        
        canvas_events = await fetch_canvas_calendar_events(
            config, 
            tracked_course_ids,
            start_date=start_date,
            end_date=end_date
        )
        
        if not canvas_events:
            return CanvasCalendarSyncResponse(
                success=True,
                message="No calendar events found in Canvas for the selected date range.",
                events_synced=0,
                courses_included=len(tracked_course_ids)
            )
            
        # Convert Canvas events to our calendar event format
        events_to_sync = []
        for canvas_event in canvas_events:
            calendar_event = map_canvas_event_to_calendar_event(canvas_event, db_user_id)
            events_to_sync.append(calendar_event)
            
        # Sync events to database
        events_synced = 0
        for event in events_to_sync:
            # Use canvas_id as a unique identifier to avoid duplicates
            await db.calendar_events.update_one(
                {
                    "canvas_id": event["canvas_id"],
                    "user_id": db_user_id
                },
                {
                    "$set": event,
                    "$setOnInsert": {
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            events_synced += 1
            
        return CanvasCalendarSyncResponse(
            success=True,
            message=f"Successfully synced {events_synced} calendar events from Canvas",
            events_synced=events_synced,
            courses_included=len(tracked_course_ids)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync Canvas calendar events: {str(e)}"
        )
