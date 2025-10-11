"""
Data ingestion endpoints for CampusMind
All endpoints require authentication via Clerk JWT token
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from ..models.schemas import Assignment, JournalEntry, APIResponse
from ..services.retrieve import DataRetrievalService
from ..middleware.auth import get_current_user
from ..util.auth_helpers import get_user_id

# Apply auth to ALL endpoints in this router
router = APIRouter(
    prefix="/ingest",
    tags=["ingest"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/assignments", response_model=APIResponse)
async def ingest_assignments(request: Request, assignments: List[Assignment]):
    """Ingest assignments from external sources"""
    try:
        user_id = get_user_id(request)
        # TODO: Implement assignment ingestion logic
        return APIResponse(
            success=True,
            message=f"Successfully ingested {len(assignments)} assignments",
            data={"count": len(assignments)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/journal", response_model=APIResponse)
async def ingest_journal_entry(request: Request, entry: JournalEntry):
    """Ingest a new journal entry"""
    try:
        user_id = get_user_id(request)
        # TODO: Implement journal entry ingestion logic
        return APIResponse(
            success=True,
            message="Journal entry ingested successfully",
            data={"entry_id": entry.id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/canvas/sync", response_model=APIResponse)
async def sync_canvas_data(request: Request):
    """Sync data from Canvas LMS"""
    try:
        user_id = get_user_id(request)
        # TODO: Implement Canvas sync logic
        return APIResponse(
            success=True,
            message="Canvas data sync initiated",
            data={"sync_status": "in_progress"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
