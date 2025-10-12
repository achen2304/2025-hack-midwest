"""
Health check and wellness monitoring routes
"""
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timedelta
from bson import ObjectId
from typing import List, Optional

from app.util.db import get_database
from app.util.auth import verify_backend_token
from app.agents import get_health_check_agent
from app.models.schemas import (
    HealthCheckInRequest,
    HealthCheckResponse,
    FeelingLevel,
    CourseFeeling,
    StudySessionCreate,
    StudySessionUpdate,
    StudySessionResponse
)

router = APIRouter(prefix="/health", tags=["Health & Wellness"])


@router.post("/checkin", response_model=HealthCheckResponse)
async def health_checkin(
    checkin: HealthCheckInRequest,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """
    Record a health check-in from the user.
    Analyzes sentiment and stores feeling level for the current course being studied.
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

        # Get recent feelings for context
        recent_feelings = []
        if checkin.current_course_id:
            # Get recent feelings for this course
            cursor = db.health_checkins.find({
                "user_id": db_user_id,
                "course_feelings.course_id": checkin.current_course_id
            }).sort("created_at", -1).limit(5)

            async for doc in cursor:
                for feeling in doc.get("course_feelings", []):
                    if feeling.get("course_id") == checkin.current_course_id:
                        recent_feelings.append({
                            "feeling_level": feeling.get("feeling_level"),
                            "recorded_at": feeling.get("recorded_at")
                        })

        # Get current course name if provided
        current_course_name = None
        if checkin.current_course_id:
            course = await db.canvas_courses.find_one({
                "canvas_id": checkin.current_course_id,
                "user_id": db_user_id
            })
            if course:
                current_course_name = course.get("name", "Unknown Course")

        # Use AI agent to analyze the check-in
        agent = get_health_check_agent()
        analysis = await agent.analyze_checkin(
            user_message=checkin.message,
            current_course=current_course_name,
            recent_feelings=recent_feelings
        )

        # Build course feelings list
        course_feelings = []
        if checkin.current_course_id and checkin.feeling_level:
            course_feelings.append({
                "course_id": checkin.current_course_id,
                "course_name": current_course_name or "Unknown",
                "feeling_level": checkin.feeling_level,
                "recorded_at": datetime.utcnow()
            })

        # Store the check-in in database
        checkin_doc = {
            "user_id": db_user_id,
            "message": checkin.message,
            "sentiment": analysis.get("sentiment", "neutral"),
            "current_study_context": current_course_name,
            "course_feelings": course_feelings,
            "next_checkin_minutes": analysis.get("next_checkin_minutes", 60),
            "needs_break": analysis.get("needs_break", False),
            "ai_suggestions": analysis.get("suggestions", ""),
            "created_at": datetime.utcnow()
        }

        result = await db.health_checkins.insert_one(checkin_doc)

        return HealthCheckResponse(
            id=str(result.inserted_id),
            user_id=db_user_id,
            message=checkin.message,
            sentiment=analysis.get("sentiment"),
            current_study_context=current_course_name,
            course_feelings=[CourseFeeling(**cf) for cf in course_feelings],
            created_at=checkin_doc["created_at"],
            next_checkin_minutes=analysis.get("next_checkin_minutes")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record health check-in: {str(e)}"
        )


@router.get("/checkins", response_model=List[HealthCheckResponse])
async def get_health_checkins(
    limit: int = 20,
    course_id: Optional[str] = None,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Get user's health check-in history"""
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

        # Build query
        query = {"user_id": db_user_id}
        if course_id:
            query["course_feelings.course_id"] = course_id

        # Fetch check-ins
        cursor = db.health_checkins.find(query).sort("created_at", -1).limit(limit)

        checkins = []
        async for doc in cursor:
            course_feelings = [
                CourseFeeling(**cf) for cf in doc.get("course_feelings", [])
            ]

            checkins.append(HealthCheckResponse(
                id=str(doc["_id"]),
                user_id=db_user_id,
                message=doc.get("message", ""),
                sentiment=doc.get("sentiment"),
                current_study_context=doc.get("current_study_context"),
                course_feelings=course_feelings,
                created_at=doc.get("created_at", datetime.utcnow()),
                next_checkin_minutes=doc.get("next_checkin_minutes")
            ))

        return checkins

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch health check-ins: {str(e)}"
        )


@router.get("/course-feelings/{course_id}")
async def get_course_feelings(
    course_id: str,
    days: int = 30,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Get feeling level trends for a specific course"""
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

        # Calculate date range
        start_date = datetime.utcnow() - timedelta(days=days)

        # Fetch check-ins with feelings for this course
        cursor = db.health_checkins.find({
            "user_id": db_user_id,
            "course_feelings.course_id": course_id,
            "created_at": {"$gte": start_date}
        }).sort("created_at", 1)

        feelings_data = []
        async for doc in cursor:
            for feeling in doc.get("course_feelings", []):
                if feeling.get("course_id") == course_id:
                    feelings_data.append({
                        "feeling_level": feeling.get("feeling_level"),
                        "recorded_at": feeling.get("recorded_at"),
                        "sentiment": doc.get("sentiment")
                    })

        # Calculate statistics
        if feelings_data:
            feeling_levels = [f["feeling_level"] for f in feelings_data]
            avg_feeling = sum(feeling_levels) / len(feeling_levels)
            trend = "improving" if len(feeling_levels) > 1 and feeling_levels[-1] < feeling_levels[0] else "worsening" if len(feeling_levels) > 1 and feeling_levels[-1] > feeling_levels[0] else "stable"
        else:
            avg_feeling = 0
            trend = "no_data"

        return {
            "course_id": course_id,
            "feelings_count": len(feelings_data),
            "average_feeling_level": round(avg_feeling, 2),
            "trend": trend,
            "feelings": feelings_data
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get course feelings: {str(e)}"
        )


@router.post("/study-session", response_model=StudySessionResponse)
async def create_study_session(
    session: StudySessionCreate,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Start a new study session"""
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

        # Create study session
        session_doc = {
            "user_id": db_user_id,
            "course_id": session.course_id,
            "assignment_id": session.assignment_id,
            "planned_duration": session.planned_duration,
            "completed": False,
            "started_at": datetime.utcnow()
        }

        result = await db.study_sessions.insert_one(session_doc)

        return StudySessionResponse(
            id=str(result.inserted_id),
            user_id=db_user_id,
            course_id=session.course_id,
            assignment_id=session.assignment_id,
            planned_duration=session.planned_duration,
            started_at=session_doc["started_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create study session: {str(e)}"
        )


@router.put("/study-session/{session_id}", response_model=StudySessionResponse)
async def update_study_session(
    session_id: str,
    update: StudySessionUpdate,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Update a study session (typically when ending it)"""
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

        # Build update dict
        update_dict = {"updated_at": datetime.utcnow()}
        if update.actual_duration is not None:
            update_dict["actual_duration"] = update.actual_duration
        if update.feeling_before is not None:
            update_dict["feeling_before"] = update.feeling_before
        if update.feeling_after is not None:
            update_dict["feeling_after"] = update.feeling_after
        if update.completed:
            update_dict["completed"] = True
            update_dict["ended_at"] = datetime.utcnow()
        if update.notes:
            update_dict["notes"] = update.notes

        # Update session
        result = await db.study_sessions.update_one(
            {"_id": ObjectId(session_id), "user_id": db_user_id},
            {"$set": update_dict}
        )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study session not found"
            )

        # Fetch updated session
        session_doc = await db.study_sessions.find_one({"_id": ObjectId(session_id)})

        return StudySessionResponse(
            id=str(session_doc["_id"]),
            user_id=db_user_id,
            course_id=session_doc["course_id"],
            assignment_id=session_doc.get("assignment_id"),
            planned_duration=session_doc["planned_duration"],
            actual_duration=session_doc.get("actual_duration"),
            feeling_before=session_doc.get("feeling_before"),
            feeling_after=session_doc.get("feeling_after"),
            completed=session_doc.get("completed", False),
            notes=session_doc.get("notes"),
            started_at=session_doc["started_at"],
            ended_at=session_doc.get("ended_at")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update study session: {str(e)}"
        )


@router.get("/study-sessions", response_model=List[StudySessionResponse])
async def get_study_sessions(
    limit: int = 20,
    course_id: Optional[str] = None,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Get user's study session history"""
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

        # Build query
        query = {"user_id": db_user_id}
        if course_id:
            query["course_id"] = course_id

        # Fetch sessions
        cursor = db.study_sessions.find(query).sort("started_at", -1).limit(limit)

        sessions = []
        async for doc in cursor:
            sessions.append(StudySessionResponse(
                id=str(doc["_id"]),
                user_id=db_user_id,
                course_id=doc["course_id"],
                assignment_id=doc.get("assignment_id"),
                planned_duration=doc["planned_duration"],
                actual_duration=doc.get("actual_duration"),
                feeling_before=doc.get("feeling_before"),
                feeling_after=doc.get("feeling_after"),
                completed=doc.get("completed", False),
                notes=doc.get("notes"),
                started_at=doc["started_at"],
                ended_at=doc.get("ended_at")
            ))

        return sessions

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch study sessions: {str(e)}"
        )
