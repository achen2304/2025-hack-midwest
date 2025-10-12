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
from fastapi import APIRouter, HTTPException, Depends, status, Query, Request
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
    request: Request,
    status_filter: Optional[str] = Query(None, alias="status"),
    course_id: Optional[str] = Query(None, description="Filter by course ID"),
    due_before: Optional[datetime] = Query(None),
    due_after: Optional[datetime] = Query(None),
    weeks: Optional[int] = Query(6, ge=1, le=52),
    user=Depends(verify_backend_token),
    db=Depends(get_database),
):
    try:
        # Resolve user
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user.get("sub"))})
        except Exception:
            pass
        if not user_doc:
            user_doc = await db.users.find_one({"email": user.get("email")})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")

        db_user_id = str(user_doc["_id"])

        # ----- Build one $and query -----
        and_terms: list[dict] = [{"user_id": db_user_id}]

        if status_filter:
            and_terms.append({"status": status_filter})

        if course_id:
            and_terms.append({"course_id": str(course_id).strip()})

        if due_before or due_after:
            date_q: dict = {}
            if due_before:
                date_q["$lte"] = due_before
            if due_after:
                date_q["$gte"] = due_after
            and_terms.append({"due_date": date_q})
        elif not course_id:
            now = datetime.utcnow()
            future = now + timedelta(weeks=weeks)
            and_terms.append({
                "$or": [
                    {"due_date": {"$gte": now, "$lte": future}},
                    {"due_date": None}
                ]
            })

        mongo_query = {"$and": and_terms} if len(and_terms) > 1 else and_terms[0]

        # Helpful debug
        print("assignments query:", mongo_query, "params:", dict(request.query_params))

        # ----- Query & sort (index-friendly) -----
        cursor = db.assignments.find(mongo_query, projection={
            "_id": 1, "canvas_id": 1, "title": 1, "description": 1,
            "due_date": 1, "course_id": 1, "points_possible": 1,
            "submission_types": 1, "status": 1, "canvas_workflow_state": 1
        }).sort("due_date", 1)
        docs = await cursor.to_list(length=None)

        # Gather course_ids present
        course_ids = sorted({str(d.get("course_id", "")) for d in docs if d.get("course_id")})

        # Batch load course info once
        course_map = {}
        if course_ids:
            # Assuming you store courses in db.courses with fields: user_id, course_id, name, code
            async for c in db.courses.find(
                {"user_id": db_user_id, "course_id": {"$in": course_ids}},
                projection={"course_id": 1, "name": 1, "course_code": 1, "_id": 0}
            ):
                course_map[str(c["course_id"])] = {
                    "course_name": c.get("name") or "",
                    "course_code": c.get("course_code") or ""
                }

        # Build response using the map
        assignments: List[CanvasAssignmentResponse] = []
        for doc in docs:
            cid = str(doc.get("course_id", ""))
            info = course_map.get(cid, {"course_name": "", "course_code": ""})
            assignments.append(CanvasAssignmentResponse(
                id=doc.get("canvas_id", str(doc["_id"])),
                name=doc.get("title", "Unnamed Assignment"),
                description=doc.get("description"),
                due_at=doc.get("due_date"),
                course_id=cid,
                course_name=info["course_name"],
                course_code=info["course_code"],
                points_possible=doc.get("points_possible"),
                submission_types=doc.get("submission_types", []),
                status=doc.get("status", "not_started"),
                canvas_workflow_state=doc.get("canvas_workflow_state")
            ))

        return assignments

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch assignments: {e}")



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
