"""
Canvas LMS integration routes
"""
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from bson import ObjectId
from typing import List

from app.util.db import get_database
from app.util.auth import verify_backend_token
from app.models.schemas import (
    CanvasTokenUpdate,
    CanvasTokenResponse,
    CanvasCourseResponse,
    CanvasAssignmentResponse,
    CanvasSyncResponse,
    TrackCoursesRequest,
    TrackCoursesResponse
)
import httpx

router = APIRouter(prefix="/canvas", tags=["Canvas"])

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
                {"$set": update_data}
            )

        if result.matched_count == 0:
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
async def get_canvas_token_status(
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Check if user has a Canvas token configured"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Try to find user by MongoDB _id first
        user_doc = None
        try:
            user_doc = await db.users.find_one(
                {"_id": ObjectId(user_id)},
                {"canvas_token": 1}
            )
        except:
            pass

        # If not found by ObjectId, try email
        if not user_doc:
            user_doc = await db.users.find_one(
                {"email": email},
                {"canvas_token": 1}
            )

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        has_token = "canvas_token" in user_doc and user_doc["canvas_token"] is not None

        return CanvasTokenResponse(
            success=True,
            message="Token status retrieved" if has_token else "No token configured",
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
        "base_url": user_doc.get("canvas_base_url", "https://canvas.instructure.com")
    }

@router.get("/courses", response_model=List[CanvasCourseResponse])
async def get_canvas_courses(
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Get user's Canvas courses (all if no tracking set, otherwise only tracked ones)"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        config = await get_user_canvas_config(user_id, email, db)

        # Get user's tracked course IDs
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass

        if not user_doc:
            user_doc = await db.users.find_one({"email": email})

        tracked_course_ids = user_doc.get("tracked_course_ids", []) if user_doc else []

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config['base_url']}/api/v1/courses",
                headers={"Authorization": f"Bearer {config['token']}"},
                params={"enrollment_state": "active", "per_page": 100}
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Canvas API error: {response.status_code}"
                )

            courses_data = response.json()
            courses = []

            for course in courses_data:
                course_id = str(course["id"])

                # If user has tracked courses, only include those
                # Otherwise, include all courses (initial pull)
                if tracked_course_ids and course_id not in tracked_course_ids:
                    continue

                courses.append(CanvasCourseResponse(
                    id=course_id,
                    name=course.get("name", "Unnamed Course"),
                    course_code=course.get("course_code", ""),
                    enrollment_term_id=course.get("enrollment_term_id"),
                    start_at=course.get("start_at"),
                    end_at=course.get("end_at"),
                    is_tracked=course_id in tracked_course_ids
                ))

            return courses

    except HTTPException:
        raise
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
    """Set which courses to track for this user"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Update user document with tracked course IDs
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
            message=f"Now tracking {len(track_request.course_ids)} course(s)",
            tracked_count=len(track_request.course_ids)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update tracked courses: {str(e)}"
        )

@router.get("/assignments", response_model=List[CanvasAssignmentResponse])
async def get_canvas_assignments(
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Get user's Canvas assignments from tracked courses only"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        config = await get_user_canvas_config(user_id, email, db)

        # Get user's tracked course IDs
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass

        if not user_doc:
            user_doc = await db.users.find_one({"email": email})

        tracked_course_ids = user_doc.get("tracked_course_ids", []) if user_doc else []

        # If no tracked courses, return empty list
        if not tracked_course_ids:
            return []

        # First get courses
        async with httpx.AsyncClient() as client:
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
            all_assignments = []

            # Get assignments for each tracked course only
            for course in courses:
                course_id = str(course["id"])

                # Skip if not tracked
                if course_id not in tracked_course_ids:
                    continue

                assignments_response = await client.get(
                    f"{config['base_url']}/api/v1/courses/{course_id}/assignments",
                    headers={"Authorization": f"Bearer {config['token']}"},
                    params={"per_page": 100, "include[]": "submission"}  # Include submission status
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
                            status = "completed"  # Student has submitted
                        else:
                            status = "not_started"

                        all_assignments.append(CanvasAssignmentResponse(
                            id=str(assignment["id"]),
                            name=assignment.get("name", "Unnamed Assignment"),
                            description=assignment.get("description"),
                            due_at=assignment.get("due_at"),
                            course_id=course_id,
                            points_possible=assignment.get("points_possible"),
                            submission_types=assignment.get("submission_types", []),
                            status=status,
                            canvas_workflow_state=workflow_state
                        ))

            # Sort assignments by due_date (None values at the end)
            all_assignments.sort(key=lambda x: (x.due_at is None, x.due_at))

            return all_assignments

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch Canvas assignments: {str(e)}"
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
