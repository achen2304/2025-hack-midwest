"""
Action endpoints for CampusMind agents
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..models.schemas import AgentRequest, AgentResponse, APIResponse
from ..agents.academic_coach import AcademicCoach
from ..agents.wellness_companion import WellnessCompanion
from ..agents.context_enricher import ContextEnricher
from ..agents.action_agent import ActionAgent

router = APIRouter(prefix="/actions", tags=["actions"])

# Initialize agents
academic_coach = AcademicCoach()
wellness_companion = WellnessCompanion()
context_enricher = ContextEnricher()
action_agent = ActionAgent()

@router.post("/academic", response_model=AgentResponse)
async def academic_action(request: AgentRequest):
    """Handle academic coaching requests"""
    try:
        # Enrich context first
        enriched_context = await context_enricher.enrich_academic_context(
            request.query, request.user_id
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
async def wellness_action(request: AgentRequest):
    """Handle wellness companion requests"""
    try:
        # Enrich context first
        enriched_context = await context_enricher.enrich_wellness_context(
            request.query, request.user_id
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
async def sync_canvas_action(user_id: str):
    """Sync Canvas data using action agent"""
    try:
        result = await action_agent.sync_canvas_data(user_id)
        return APIResponse(
            success=True,
            message="Canvas sync action completed",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-event", response_model=APIResponse)
async def create_calendar_event(event_data: Dict[str, Any]):
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
async def send_notification(notification_data: Dict[str, Any]):
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
