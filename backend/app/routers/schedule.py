"""
AI-powered schedule generation routes
"""
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timedelta
from bson import ObjectId
from typing import List, Optional

from app.util.db import get_database
from app.util.auth import verify_backend_token
from app.agents import get_schedule_maker_agent
from app.models.schemas import (
    ScheduleGenerationRequest,
    ScheduleGenerationResponse,
    CalendarEventResponse,
    EventType,
    EventPriority
)

router = APIRouter(prefix="/schedule", tags=["AI Schedule"])


@router.post("/generate", response_model=ScheduleGenerationResponse)
async def generate_schedule(
    request: ScheduleGenerationRequest,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """
    Generate an AI-powered study schedule based on assignments, exams, and user preferences.

    This implements the core scheduling workflow:
    1. Reads "pillars" (fixed events: classes, exams, locked events)
    2. Wipes previous AI-generated STUDY_BLOCK and BREAK events
    3. Plans with priority (allocates more time to prioritized courses)
    4. Writes the new schedule to the database
    """
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's actual MongoDB ID
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

        # Get user preferences
        prefs_doc = await db.user_preferences.find_one({"user_id": db_user_id})
        if prefs_doc:
            user_preferences = {
                "study_block_duration": prefs_doc.get("study_block_duration", 60),
                "break_duration": prefs_doc.get("break_duration", 15),
                "travel_duration": prefs_doc.get("travel_duration", 10),
                "recurring_blocked_times": prefs_doc.get("recurring_blocked_times", [])
            }
        else:
            user_preferences = {
                "study_block_duration": 60,
                "break_duration": 15,
                "travel_duration": 10,
                "recurring_blocked_times": []
            }

        # Set date range for schedule generation
        start_date = request.start_date or datetime.utcnow()
        end_date = request.end_date or (start_date + timedelta(days=14))  # Default 2 weeks

        # Step 1: Get all assignments that need study time
        assignments_cursor = db.assignments.find({
            "user_id": db_user_id,
            "status": {"$in": ["not_started", "in_progress"]},
            "due_date": {
                "$gte": start_date,
                "$lte": end_date + timedelta(days=7)  # Include assignments due within a week after range
            }
        }).sort("due_date", 1)

        assignments = []
        async for assignment in assignments_cursor:
            assignments.append({
                "id": str(assignment["_id"]),
                "title": assignment.get("title", "Untitled"),
                "course_id": assignment.get("course_id"),
                "course": assignment.get("course", "Unknown"),
                "due_date": assignment.get("due_date"),
                "status": assignment.get("status"),
                "points_possible": assignment.get("points_possible", 0)
            })

        # Step 2: Get all "pillar" events (classes, exams, locked events, personal events)
        # These are events that CANNOT be moved or deleted by the AI
        pillars_cursor = db.calendar_events.find({
            "user_id": db_user_id,
            "start_time": {"$gte": start_date, "$lte": end_date},
            "$or": [
                {"event_type": {"$in": ["academic", "personal", "social", "wellness"]}},
                {"is_locked": True}
            ]
        }).sort("start_time", 1)

        existing_events = []
        async for event in pillars_cursor:
            existing_events.append({
                "id": str(event["_id"]),
                "title": event.get("title"),
                "start_time": event.get("start_time"),
                "end_time": event.get("end_time"),
                "event_type": event.get("event_type"),
                "is_locked": event.get("is_locked", False)
            })

        # Step 3: Get recent wellness state to inform schedule intensity
        recent_checkin = await db.health_checkins.find_one(
            {"user_id": db_user_id},
            sort=[("created_at", -1)]
        )

        wellness_state = "normal"
        if recent_checkin:
            sentiment = recent_checkin.get("sentiment", "neutral")
            if sentiment in ["stressed", "overwhelmed"]:
                wellness_state = "stressed"
            elif sentiment == "positive":
                wellness_state = "good"

        # Step 4: WIPE previous AI-generated events if regenerating
        if request.regenerate:
            # Delete all STUDY_BLOCK and BREAK events in the date range
            await db.calendar_events.delete_many({
                "user_id": db_user_id,
                "event_type": "other",  # We'll use "other" type for AI-generated blocks
                "source": "CAMPUSMIND_AI",  # Mark AI-generated events
                "start_time": {"$gte": start_date, "$lte": end_date}
            })

        # Step 5: Use AI agent to generate the schedule
        agent = get_schedule_maker_agent()
        schedule_result = await agent.generate_schedule(
            assignments=assignments,
            existing_events=existing_events,
            user_preferences=user_preferences,
            prioritize_courses=request.prioritize_courses,
            wellness_state=wellness_state
        )

        if not schedule_result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=schedule_result.get("message", "Failed to generate schedule")
            )

        # Step 6: Write the new schedule to database
        study_blocks_created = 0
        break_blocks_created = 0

        for event in schedule_result.get("schedule", []):
            event_type = "other"  # Use "other" for AI-generated blocks
            is_study_block = event.get("type") == "STUDY_BLOCK"
            is_break = event.get("type") == "BREAK"

            # Parse datetime strings if needed
            start_time = event.get("start_time")
            end_time = event.get("end_time")
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time.replace("Z", "+00:00"))

            event_doc = {
                "user_id": db_user_id,
                "title": event.get("title", "Study Block" if is_study_block else "Break"),
                "description": f"AI-generated {'study block' if is_study_block else 'break'}",
                "start_time": start_time,
                "end_time": end_time,
                "location": "",
                "event_type": event_type,
                "priority": "high" if is_study_block else "low",
                "is_recurring": False,
                "recurrence_pattern": None,
                "color": "#4CAF50" if is_study_block else "#2196F3",  # Green for study, blue for break
                "notifications": [15] if is_study_block else [],
                "source": "CAMPUSMIND_AI",  # Mark as AI-generated
                "ai_generated": True,
                "block_type": event.get("type"),
                "course_id": event.get("course_id"),
                "assignment_id": event.get("assignment_id"),
                "is_locked": False,  # AI events start unlocked
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            await db.calendar_events.insert_one(event_doc)

            if is_study_block:
                study_blocks_created += 1
            elif is_break:
                break_blocks_created += 1

        return ScheduleGenerationResponse(
            success=True,
            message=f"Successfully generated schedule with {study_blocks_created} study blocks and {break_blocks_created} breaks",
            study_blocks_created=study_blocks_created,
            break_blocks_created=break_blocks_created
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate schedule: {str(e)}"
        )


@router.get("/ai-blocks")
async def get_ai_generated_blocks(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Get all AI-generated study blocks and breaks"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's actual MongoDB ID
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

        # Set default date range
        if not start_date:
            start_date = datetime.utcnow()
        if not end_date:
            end_date = start_date + timedelta(days=14)

        # Query for AI-generated events
        cursor = db.calendar_events.find({
            "user_id": db_user_id,
            "source": "CAMPUSMIND_AI",
            "start_time": {"$gte": start_date, "$lte": end_date}
        }).sort("start_time", 1)

        blocks = []
        async for event in cursor:
            blocks.append({
                "id": str(event["_id"]),
                "title": event.get("title"),
                "block_type": event.get("block_type"),
                "start_time": event.get("start_time"),
                "end_time": event.get("end_time"),
                "course_id": event.get("course_id"),
                "assignment_id": event.get("assignment_id"),
                "is_locked": event.get("is_locked", False),
                "color": event.get("color")
            })

        return {
            "blocks": blocks,
            "total": len(blocks)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch AI-generated blocks: {str(e)}"
        )


@router.delete("/ai-blocks/clear")
async def clear_ai_blocks(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Clear all AI-generated blocks in a date range"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's actual MongoDB ID
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

        # Set default date range
        if not start_date:
            start_date = datetime.utcnow()
        if not end_date:
            end_date = start_date + timedelta(days=365)  # Clear up to 1 year ahead

        # Delete AI-generated events
        result = await db.calendar_events.delete_many({
            "user_id": db_user_id,
            "source": "CAMPUSMIND_AI",
            "start_time": {"$gte": start_date, "$lte": end_date}
        })

        return {
            "success": True,
            "message": f"Cleared {result.deleted_count} AI-generated blocks",
            "blocks_deleted": result.deleted_count
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear AI blocks: {str(e)}"
        )


@router.put("/ai-blocks/{block_id}/lock")
async def toggle_block_lock(
    block_id: str,
    lock: bool,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Lock or unlock an AI-generated block to prevent it from being rescheduled"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's actual MongoDB ID
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

        # Update the lock status
        result = await db.calendar_events.update_one(
            {"_id": ObjectId(block_id), "user_id": db_user_id},
            {"$set": {"is_locked": lock, "updated_at": datetime.utcnow()}}
        )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Block not found"
            )

        return {
            "success": True,
            "message": f"Block {'locked' if lock else 'unlocked'} successfully",
            "is_locked": lock
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle block lock: {str(e)}"
        )
