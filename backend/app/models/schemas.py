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

class AgentResponse(BaseModel):
    response: str = Field(..., description="Agent response")
    suggestions: Optional[List[str]] = Field(None, description="Action suggestions")
    context: Optional[Dict[str, Any]] = Field(None, description="Enriched context")

class MeetingTimeSource(str, Enum):
    CANVAS = "canvas"
    MANUAL = "manual"

class MeetingTime(BaseModel):
    day: str = Field(..., description="Day of week (Monday, Tuesday, etc.)")
    start_time: str = Field(..., description="Start time (HH:MM format)")
    end_time: str = Field(..., description="End time (HH:MM format)")
    location: Optional[str] = Field(None, description="Meeting location")
    source: MeetingTimeSource = Field(..., description="Source of meeting time")

class TrackedCourse(BaseModel):
    user_id: str = Field(..., description="User ID")
    course_id: str = Field(..., description="Canvas course ID")
    course_name: str = Field(..., description="Course name")
    course_code: str = Field(..., description="Course code")
    is_tracked: bool = Field(default=True, description="Whether course is actively tracked")
    meeting_times: List[MeetingTime] = Field(default_factory=list, description="Course meeting times")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_synced: Optional[datetime] = Field(None, description="Last sync timestamp")

class CanvasAssignment(BaseModel):
    id: str = Field(..., description="Canvas assignment ID")
    user_id: str = Field(..., description="User ID")
    course_id: str = Field(..., description="Canvas course ID")
    course_name: str = Field(..., description="Course name")
    course_code: Optional[str] = Field(None, description="Course code")
    title: str = Field(..., description="Assignment title")
    description: Optional[str] = Field(None, description="Assignment description")
    due_at: Optional[datetime] = Field(None, description="Due date")
    points_possible: Optional[float] = Field(None, description="Points possible")
    submission_types: List[str] = Field(default_factory=list, description="Submission types")
    html_url: str = Field(..., description="Canvas assignment URL")
    has_submitted: bool = Field(default=False, description="Whether user has submitted")
    calendar_event_id: Optional[str] = Field(None, description="Linked Google Calendar event ID")
    synced_to_calendar: bool = Field(default=False, description="Whether synced to calendar")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CalendarEventSource(str, Enum):
    CANVAS = "canvas"
    MANUAL = "manual"
    GOOGLE = "google"

class CalendarEvent(BaseModel):
    id: str = Field(..., description="Internal event ID")
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    start_time: datetime = Field(..., description="Event start time")
    end_time: datetime = Field(..., description="Event end time")
    location: Optional[str] = Field(None, description="Event location")
    source: CalendarEventSource = Field(..., description="Event source")
    canvas_assignment_id: Optional[str] = Field(None, description="Linked Canvas assignment ID")
    google_event_id: Optional[str] = Field(None, description="Google Calendar event ID")
    is_recurring: bool = Field(default=False, description="Whether event is recurring")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SyncState(BaseModel):
    user_id: str = Field(..., description="User ID")
    last_canvas_sync: Optional[datetime] = Field(None, description="Last Canvas sync time")
    last_calendar_sync: Optional[datetime] = Field(None, description="Last Calendar sync time")
    sync_enabled: bool = Field(default=True, description="Whether auto-sync is enabled")
    auto_sync_interval_hours: int = Field(default=24, description="Auto-sync interval in hours")
    last_sync_status: str = Field(default="pending", description="Status of last sync")
    last_sync_error: Optional[str] = Field(None, description="Last sync error message")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TrackCourseRequest(BaseModel):
    course_ids: List[str] = Field(..., description="List of Canvas course IDs to track")

class UntrackCourseRequest(BaseModel):
    course_id: str = Field(..., description="Canvas course ID to untrack")

class AddMeetingTimeRequest(BaseModel):
    course_id: str = Field(..., description="Canvas course ID")
    meeting_time: MeetingTime = Field(..., description="Meeting time to add")

class SyncRequest(BaseModel):
    force: bool = Field(default=False, description="Force sync even if recently synced")

class CalendarAuthRequest(BaseModel):
    auth_code: str = Field(..., description="OAuth authorization code")

class CanvasTokenRequest(BaseModel):
    canvas_token: str = Field(..., description="Canvas Personal Access Token")
    canvas_base_url: str = Field(default="https://canvas.iastate.edu", description="Canvas base URL")
