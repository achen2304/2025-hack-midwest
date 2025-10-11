"""
Action endpoints for CampusMind agents
All endpoints require authentication via Clerk JWT token
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any
from ..models.schemas import AgentRequest, AgentResponse, APIResponse
from ..agents.academic_coach import AcademicCoach
from ..agents.wellness_companion import WellnessCompanion
from ..agents.context_enricher import ContextEnricher
from ..agents.action_agent import ActionAgent
from ..middleware.auth import get_current_user
from ..util.auth_helpers import get_user_id

# Apply auth to ALL endpoints in this router
router = APIRouter(
    prefix="/actions",
    tags=["actions"],
    dependencies=[Depends(get_current_user)]
)

# Initialize agents
academic_coach = AcademicCoach()
wellness_companion = WellnessCompanion()
context_enricher = ContextEnricher()
action_agent = ActionAgent()


@router.post("/academic", response_model=AgentResponse)
async def academic_action(request: Request, agent_request: AgentRequest):
    """Handle academic coaching requests"""
    try:
        user_id = get_user_id(request)

        # Enrich context first
        enriched_context = await context_enricher.enrich_academic_context(
            agent_request.query, user_id
        )

        # Get academic coach response
        # TODO: Implement actual agent processing
        response = "Academic coaching response coming soon"

        return AgentResponse(
            response=response,
            suggestions=["Create study plan", "Review assignments"],
            context=enriched_context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wellness", response_model=AgentResponse)
async def wellness_action(request: Request, agent_request: AgentRequest):
    """Handle wellness companion requests"""
    try:
        user_id = get_user_id(request)

        # Enrich context first
        enriched_context = await context_enricher.enrich_wellness_context(
            agent_request.query, user_id
        )

        # Get wellness companion response
        # TODO: Implement actual agent processing
        response = "Wellness companion response coming soon"

        return AgentResponse(
            response=response,
            suggestions=["Journal entry", "Mood check", "Wellness activity"],
            context=enriched_context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-canvas", response_model=APIResponse)
async def sync_canvas_action(request: Request):
    """Sync Canvas data using action agent"""
    try:
        user_id = get_user_id(request)
        result = await action_agent.sync_canvas_data(user_id)
        return APIResponse(
            success=True,
            message="Canvas sync action completed",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-event", response_model=APIResponse)
async def create_calendar_event(request: Request, event_data: Dict[str, Any]):
    """Create calendar event using action agent"""
    try:
        result = await action_agent.create_calendar_event(event_data)
        return APIResponse(
            success=True,
            message="Calendar event created",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-notification", response_model=APIResponse)
async def send_notification(request: Request, notification_data: Dict[str, Any]):
    """Send notification using action agent"""
    try:
        result = await action_agent.send_notification(notification_data)
        return APIResponse(
            success=True,
            message="Notification sent",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
