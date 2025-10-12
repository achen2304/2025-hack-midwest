"""
Assignment management routes

IMPORTANT: This router pulls assignments from MongoDB (synced database), NOT directly from Canvas.

Flow:
1. GET /canvas/assignments - Fetches live from Canvas API (for preview)
2. POST /canvas/sync - Syncs Canvas → MongoDB (preserves in_progress status)
3. GET /assignments - Displays from MongoDB database (this router)

Status Rules:
- "not_started" - Canvas says unsubmitted
- "completed" - Canvas says submitted/graded (includes pending_review)
- "in_progress" - ONLY set manually by user via PUT /assignments/{id}/status
  → Sync will NEVER overwrite in_progress status
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from datetime import datetime, timedelta
from bson import ObjectId
from typing import List, Optional

from app.util.db import get_database
from app.util.auth import verify_backend_token
from app.models.schemas import CanvasAssignmentResponse
from pydantic import BaseModel, Field

router = APIRouter(prefix="/assignments", tags=["Assignments"])


async def get_course_info(db, course_id: str, user_id: str) -> dict:
    """Helper function to get course information by course_id"""
    try:
        course_doc = await db.canvas_courses.find_one({
            "canvas_id": course_id,
            "user_id": user_id
        })
        
        if course_doc:
            return {
                "course_name": course_doc.get("name", "Unknown Course"),
                "course_code": course_doc.get("course_code", "")
            }
        else:
            return {
                "course_name": "Unknown Course",
                "course_code": ""
            }
    except Exception:
        return {
            "course_name": "Unknown Course", 
            "course_code": ""
        }


class AssignmentStatusUpdate(BaseModel):
    status: str = Field(..., description="not_started, in_progress, or completed")


@router.get("", response_model=List[CanvasAssignmentResponse])
async def get_assignments(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    course_id: Optional[str] = Query(None, description="Filter by course ID"),
    due_before: Optional[datetime] = Query(None, description="Filter assignments due before this date"),
    due_after: Optional[datetime] = Query(None, description="Filter assignments due after this date"),
    weeks: Optional[int] = Query(6, ge=1, le=52, description="Number of weeks to fetch (default: 6)"),
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """
    Get assignments from MongoDB database (synced from Canvas)

    By default, fetches assignments for the next 6 weeks.
    Use 'weeks' parameter to adjust the time window (1-52 weeks).

    This pulls from the local database, NOT directly from Canvas.
    To sync latest from Canvas, use POST /canvas/sync first.
    """
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's MongoDB ID
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

        db_user_id = str(user_doc["_id"])

        # Build query filters
        query = {"user_id": db_user_id}

        if status_filter:
            query["status"] = status_filter

        if course_id:
            query["course_id"] = course_id

        # Date filtering: default to next 4-6 weeks if not specified
        if due_before or due_after:
            date_query = {}
            if due_before:
                date_query["$lte"] = due_before
            if due_after:
                date_query["$gte"] = due_after
            query["due_date"] = date_query
        else:
            # Default: fetch assignments for the next N weeks
            now = datetime.utcnow()
            future_date = now + timedelta(weeks=weeks)
            query["due_date"] = {
                "$gte": now,
                "$lte": future_date
            }

        # Fetch assignments from database, sorted by due_date
        cursor = db.assignments.find(query).sort("due_date", 1)
        assignments_docs = await cursor.to_list(length=None)

        assignments = []
        for doc in assignments_docs:
            # Get course information
            course_info = await get_course_info(db, doc.get("course_id", ""), db_user_id)
            
            assignments.append(CanvasAssignmentResponse(
                id=doc.get("canvas_id", str(doc["_id"])),
                name=doc.get("title", "Unnamed Assignment"),
                description=doc.get("description"),
                due_at=doc.get("due_date"),
                course_id=doc.get("course_id", ""),
                course_name=course_info["course_name"],
                course_code=course_info["course_code"],
                points_possible=doc.get("points_possible"),
                submission_types=doc.get("submission_types", []),
                status=doc.get("status", "not_started"),
                canvas_workflow_state=doc.get("canvas_workflow_state")
            ))

        return assignments

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch assignments: {str(e)}"
        )


@router.get("/{assignment_id}", response_model=CanvasAssignmentResponse)
async def get_assignment(
    assignment_id: str,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Get single assignment by ID"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's MongoDB ID
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

        db_user_id = str(user_doc["_id"])

        # Find assignment
        doc = await db.assignments.find_one({
            "canvas_id": assignment_id,
            "user_id": db_user_id
        })

        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )

        # Get course information
        course_info = await get_course_info(db, doc.get("course_id", ""), db_user_id)

        return CanvasAssignmentResponse(
            id=doc.get("canvas_id", str(doc["_id"])),
            name=doc.get("title", "Unnamed Assignment"),
            description=doc.get("description"),
            due_at=doc.get("due_date"),
            course_id=doc.get("course_id", ""),
            course_name=course_info["course_name"],
            course_code=course_info["course_code"],
            points_possible=doc.get("points_possible"),
            submission_types=doc.get("submission_types", []),
            status=doc.get("status", "not_started"),
            canvas_workflow_state=doc.get("canvas_workflow_state")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch assignment: {str(e)}"
        )


@router.put("/{assignment_id}/status", response_model=CanvasAssignmentResponse)
async def update_assignment_status(
    assignment_id: str,
    status_update: AssignmentStatusUpdate,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Update assignment completion status (not_started, in_progress, completed)"""
    try:
        # Validate status
        valid_statuses = ["not_started", "in_progress", "completed"]
        if status_update.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )

        user_id = user.get("sub")
        email = user.get("email")

        # Get user's MongoDB ID
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

        db_user_id = str(user_doc["_id"])

        # Update assignment status
        update_data = {
            "status": status_update.status,
            "updated_at": datetime.utcnow()
        }

        # Add completed_at timestamp if marking as completed
        if status_update.status == "completed":
            update_data["completed_at"] = datetime.utcnow()

        result = await db.assignments.update_one(
            {
                "canvas_id": assignment_id,
                "user_id": db_user_id
            },
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )

        # Fetch and return updated assignment
        doc = await db.assignments.find_one({
            "canvas_id": assignment_id,
            "user_id": db_user_id
        })

        # Get course information
        course_info = await get_course_info(db, doc.get("course_id", ""), db_user_id)

        return CanvasAssignmentResponse(
            id=doc.get("canvas_id", str(doc["_id"])),
            name=doc.get("title", "Unnamed Assignment"),
            description=doc.get("description"),
            due_at=doc.get("due_date"),
            course_id=doc.get("course_id", ""),
            course_name=course_info["course_name"],
            course_code=course_info["course_code"],
            points_possible=doc.get("points_possible"),
            submission_types=doc.get("submission_types", []),
            status=doc.get("status", "not_started"),
            canvas_workflow_state=doc.get("canvas_workflow_state")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update assignment status: {str(e)}"
        )


@router.get("/count/by-status")
async def get_assignment_counts(
    weeks: Optional[int] = Query(6, ge=1, le=52, description="Number of weeks to count (default: 6)"),
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Get count of assignments by status (default: next 6 weeks)"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's MongoDB ID
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

        db_user_id = str(user_doc["_id"])

        # Build date filter for next N weeks
        now = datetime.utcnow()
        future_date = now + timedelta(weeks=weeks)
        date_filter = {
            "due_date": {
                "$gte": now,
                "$lte": future_date
            }
        }

        # Count assignments by status
        not_started = await db.assignments.count_documents({
            "user_id": db_user_id,
            "status": "not_started",
            **date_filter
        })

        in_progress = await db.assignments.count_documents({
            "user_id": db_user_id,
            "status": "in_progress",
            **date_filter
        })

        completed = await db.assignments.count_documents({
            "user_id": db_user_id,
            "status": "completed",
            **date_filter
        })

        total = not_started + in_progress + completed

        return {
            "total": total,
            "not_started": not_started,
            "in_progress": in_progress,
            "completed": completed
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get assignment counts: {str(e)}"
        )


@router.get("/course/{course_id}", response_model=List[CanvasAssignmentResponse])
async def get_assignments_by_course(
    course_id: str,
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    due_before: Optional[datetime] = Query(None, description="Filter assignments due before this date"),
    due_after: Optional[datetime] = Query(None, description="Filter assignments due after this date"),
    weeks: Optional[int] = Query(6, ge=1, le=52, description="Number of weeks to fetch (default: 6)"),
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """
    Get assignments for a specific course/class from MongoDB database
    
    By default, fetches assignments for the next 6 weeks.
    Use 'weeks' parameter to adjust the time window (1-52 weeks).
    """
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's MongoDB ID
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

        db_user_id = str(user_doc["_id"])

        # Verify the course exists and belongs to the user
        course_doc = await db.canvas_courses.find_one({
            "canvas_id": course_id,
            "user_id": db_user_id
        })

        if not course_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found or not accessible"
            )

        # Build query filters
        query = {
            "user_id": db_user_id,
            "course_id": course_id
        }

        if status_filter:
            query["status"] = status_filter

        # Date filtering: default to next N weeks if not specified
        if due_before or due_after:
            date_query = {}
            if due_before:
                date_query["$lte"] = due_before
            if due_after:
                date_query["$gte"] = due_after
            query["due_date"] = date_query
        else:
            # Default: fetch assignments for the next N weeks
            now = datetime.utcnow()
            future_date = now + timedelta(weeks=weeks)
            query["due_date"] = {
                "$gte": now,
                "$lte": future_date
            }

        # Fetch assignments from database, sorted by due_date
        cursor = db.assignments.find(query).sort("due_date", 1)
        assignments_docs = await cursor.to_list(length=None)

        assignments = []
        for doc in assignments_docs:
            # Get course information (we already have it, but using helper for consistency)
            course_info = await get_course_info(db, course_id, db_user_id)
            
            assignments.append(CanvasAssignmentResponse(
                id=doc.get("canvas_id", str(doc["_id"])),
                name=doc.get("title", "Unnamed Assignment"),
                description=doc.get("description"),
                due_at=doc.get("due_date"),
                course_id=doc.get("course_id", ""),
                course_name=course_info["course_name"],
                course_code=course_info["course_code"],
                points_possible=doc.get("points_possible"),
                submission_types=doc.get("submission_types", []),
                status=doc.get("status", "not_started"),
                canvas_workflow_state=doc.get("canvas_workflow_state")
            ))

        return assignments

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch assignments for course: {str(e)}"
        )
