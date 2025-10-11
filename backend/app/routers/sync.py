"""
Sync orchestration endpoints for CampusMind
Manual sync triggers and Strands agent interactions
All endpoints require authentication via Clerk JWT token
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from ..models.schemas import APIResponse, SyncRequest, AgentRequest, AgentResponse
from ..services.sync_service import sync_service
from ..agents.sync_agent import sync_agent
from ..middleware.auth import get_current_user

# Apply auth to ALL endpoints in this router
router = APIRouter(
    prefix="/sync",
    tags=["sync"],
    dependencies=[Depends(get_current_user)]
)


def get_user_id(request: Request) -> str:
    """Helper to extract user_id from request state"""
    return request.state.user["user_id"]


@router.post("/canvas-to-calendar", response_model=APIResponse)
async def sync_canvas_to_calendar(request: Request, sync_request: SyncRequest):
    """
    Manually trigger sync from Canvas to Google Calendar
    Syncs all tracked courses' assignments to calendar
    """
    try:
        user_id = get_user_id(request)
        result = await sync_service.sync_canvas_to_calendar(
            user_id,
            force=sync_request.force
        )

        return APIResponse(
            success=result["status"] in ["success", "skipped"],
            message=result.get("message", "Sync completed"),
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=APIResponse)
async def get_sync_status(request: Request):
    """Get current sync status for user"""
    try:
        user_id = get_user_id(request)
        status = await sync_service.get_sync_status(user_id)
        return APIResponse(
            success=True,
            message="Sync status retrieved",
            data=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enable", response_model=APIResponse)
async def enable_auto_sync(request: Request, interval_hours: int = 24):
    """Enable automatic syncing"""
    try:
        user_id = get_user_id(request)
        success = await sync_service.enable_auto_sync(user_id, interval_hours)
        return APIResponse(
            success=success,
            message=f"Auto-sync enabled (every {interval_hours} hours)",
            data={"user_id": user_id, "interval_hours": interval_hours}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disable", response_model=APIResponse)
async def disable_auto_sync(request: Request):
    """Disable automatic syncing"""
    try:
        user_id = get_user_id(request)
        success = await sync_service.disable_auto_sync(user_id)
        return APIResponse(
            success=success,
            message="Auto-sync disabled",
            data={"user_id": user_id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Strands Agent Endpoints

@router.post("/agent/ask", response_model=AgentResponse)
async def ask_sync_agent(request: Request, agent_request: AgentRequest):
    """
    Ask the Strands Sync Agent a question
    The agent can help with scheduling, workload analysis, and smart syncing

    Example queries:
    - "What assignments do I have this week?"
    - "When should I schedule study time for my CS homework?"
    - "Analyze my workload for the next 2 weeks"
    - "Find available time slots for studying tomorrow"
    """
    try:
        user_id = get_user_id(request)
        response = sync_agent.ask(
            user_id,
            agent_request.query,
            agent_request.context
        )

        return AgentResponse(
            response=response,
            suggestions=[
                "View upcoming assignments",
                "Schedule study sessions",
                "Analyze workload"
            ],
            context=agent_request.context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/schedule-study", response_model=AgentResponse)
async def agent_schedule_study(request: Request, agent_request: AgentRequest):
    """
    Use agent to intelligently schedule study sessions
    The agent will analyze assignments and find optimal study times
    """
    try:
        user_id = get_user_id(request)
        query = f"""Analyze my upcoming assignments and suggest optimal study schedule.

        Consider:
        - Assignment due dates and priorities
        - My calendar availability
        - Recommended study duration based on assignment difficulty

        Create study sessions where appropriate.

        Additional context: {agent_request.query}"""

        response = sync_agent.ask(
            user_id,
            query,
            agent_request.context
        )

        return AgentResponse(
            response=response,
            suggestions=["View calendar", "Adjust study times", "Sync to calendar"],
            context=agent_request.context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/analyze-workload", response_model=AgentResponse)
async def agent_analyze_workload(request: Request, agent_request: AgentRequest):
    """
    Use agent to analyze workload and provide insights
    """
    try:
        user_id = get_user_id(request)
        query = f"""Analyze my academic workload for the next 2 weeks.

        Provide:
        - Total assignments and their distribution
        - Busy periods I should prepare for
        - Recommendations for time management
        - Any potential conflicts or overlaps

        {agent_request.query if agent_request.query else ''}"""

        response = sync_agent.ask(
            user_id,
            query,
            agent_request.context
        )

        return AgentResponse(
            response=response,
            suggestions=["Schedule study time", "View assignments", "Sync calendar"],
            context=agent_request.context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
