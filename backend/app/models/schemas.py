"""
Pydantic schemas for CampusMind API
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MoodLevel(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    OKAY = "okay"
    POOR = "poor"
    TERRIBLE = "terrible"

class AssignmentStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"

class User(BaseModel):
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    name: str = Field(..., description="User name")
    university: Optional[str] = Field(None, description="University name")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class JournalEntry(BaseModel):
    id: str = Field(..., description="Journal entry ID")
    user_id: str = Field(..., description="User ID")
    content: str = Field(..., description="Journal entry content")
    mood: MoodLevel = Field(..., description="Mood level")
    tags: List[str] = Field(default_factory=list, description="Entry tags")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Assignment(BaseModel):
    id: str = Field(..., description="Assignment ID")
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., description="Assignment title")
    description: Optional[str] = Field(None, description="Assignment description")
    course: str = Field(..., description="Course name")
    due_date: datetime = Field(..., description="Due date")
    status: AssignmentStatus = Field(default=AssignmentStatus.NOT_STARTED)
    priority: int = Field(default=1, ge=1, le=5, description="Priority level 1-5")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class StudyPlan(BaseModel):
    id: str = Field(..., description="Study plan ID")
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., description="Plan title")
    description: Optional[str] = Field(None, description="Plan description")
    tasks: List[Dict[str, Any]] = Field(default_factory=list, description="Plan tasks")
    due_date: Optional[datetime] = Field(None, description="Plan due date")
    is_completed: bool = Field(default=False, description="Completion status")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CanvasCourse(BaseModel):
    id: str = Field(..., description="Canvas course ID")
    name: str = Field(..., description="Course name")
    course_code: str = Field(..., description="Course code")
    description: Optional[str] = Field(None, description="Course description")

class APIResponse(BaseModel):
    success: bool = Field(..., description="Response success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")

class AgentRequest(BaseModel):
    query: str = Field(..., description="User query")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    user_id: str = Field(..., description="User ID")

class AgentResponse(BaseModel):
    response: str = Field(..., description="Agent response")
    suggestions: Optional[List[str]] = Field(None, description="Action suggestions")
    context: Optional[Dict[str, Any]] = Field(None, description="Enriched context")
