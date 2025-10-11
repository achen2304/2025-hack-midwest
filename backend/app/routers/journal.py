"""
Journal endpoints for CampusMind
All endpoints require authentication via Clerk JWT token
"""
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from typing import List, Optional
from datetime import datetime, timedelta
from ..models.schemas import JournalEntry, MoodLevel, APIResponse
from ..middleware.auth import get_current_user
from ..util.auth_helpers import get_user_id

# Apply auth to ALL endpoints in this router
router = APIRouter(
    prefix="/journal",
    tags=["journal"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/entries", response_model=APIResponse)
async def create_journal_entry(request: Request, entry: JournalEntry):
    """Create a new journal entry"""
    try:
        # TODO: Implement journal entry creation
        return APIResponse(
            success=True,
            message="Journal entry created successfully",
            data={"entry_id": entry.id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entries", response_model=List[JournalEntry])
async def get_journal_entries(
    request: Request,
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0, ge=0),
    mood_filter: Optional[MoodLevel] = Query(default=None)
):
    """Get journal entries for authenticated user"""
    try:
        user_id = get_user_id(request)
        # TODO: Implement journal entry retrieval
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entries/{entry_id}", response_model=JournalEntry)
async def get_journal_entry(request: Request, entry_id: str):
    """Get a specific journal entry"""
    try:
        # TODO: Implement single journal entry retrieval
        raise HTTPException(status_code=404, detail="Entry not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/entries/{entry_id}", response_model=APIResponse)
async def update_journal_entry(request: Request, entry_id: str, entry: JournalEntry):
    """Update a journal entry"""
    try:
        # TODO: Implement journal entry update
        return APIResponse(
            success=True,
            message="Journal entry updated successfully",
            data={"entry_id": entry_id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/entries/{entry_id}", response_model=APIResponse)
async def delete_journal_entry(request: Request, entry_id: str):
    """Delete a journal entry"""
    try:
        # TODO: Implement journal entry deletion
        return APIResponse(
            success=True,
            message="Journal entry deleted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mood-trends", response_model=APIResponse)
async def get_mood_trends(
    request: Request,
    days: int = Query(default=30, ge=1, le=365)
):
    """Get mood trends over time"""
    try:
        user_id = get_user_id(request)
        # TODO: Implement mood trend analysis
        return APIResponse(
            success=True,
            message="Mood trends retrieved",
            data={"trends": "Mood analysis coming soon"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
