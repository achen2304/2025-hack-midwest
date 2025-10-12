"""
Pydantic schemas for CampusMind API
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# User Profile Models
class UserProfileResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    university: Optional[str] = None
    image: Optional[str] = None
    created_at: datetime

class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, description="User's full name")
    university: Optional[str] = Field(None, description="University name")
    image: Optional[str] = Field(None, description="Profile image URL")

# Canvas Integration Models
class CanvasTokenUpdate(BaseModel):
    canvas_token: str = Field(..., description="Canvas Personal Access Token")
    canvas_base_url: Optional[str] = Field(None, description="Canvas instance URL (e.g., https://canvas.instructure.com)")

class CanvasTokenResponse(BaseModel):
    success: bool
    message: str
    has_token: bool

class CanvasCourseResponse(BaseModel):
    id: str
    name: str
    course_code: str
    enrollment_term_id: Optional[int] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    is_tracked: bool = Field(default=False, description="Whether this course is being tracked")

class TrackCoursesRequest(BaseModel):
    course_ids: List[str] = Field(..., description="List of Canvas course IDs to track")

class TrackCoursesResponse(BaseModel):
    success: bool
    message: str
    tracked_count: int

class CanvasAssignmentResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    course_id: str
    points_possible: Optional[float] = None
    submission_types: List[str] = Field(default_factory=list)
    status: str = Field(default="not_started", description="not_started, in_progress, or completed")
    canvas_workflow_state: Optional[str] = Field(None, description="Canvas submission workflow state")

class CanvasSyncResponse(BaseModel):
    success: bool
    message: str
    courses_synced: int
    assignments_synced: int

# User Preferences Models
class BlockedTime(BaseModel):
    day_of_week: str = Field(..., description="Day of week (Monday-Sunday)")
    start: str = Field(..., description="Start time (HH:MM format)")
    end: str = Field(..., description="End time (HH:MM format)")

class UserPreferences(BaseModel):
    study_block_duration: int = Field(default=60, description="Study block duration in minutes")
    break_duration: int = Field(default=15, description="Break duration in minutes")
    travel_duration: int = Field(default=10, description="Travel time buffer in minutes")
    recurring_blocked_times: List[BlockedTime] = Field(default_factory=list, description="Recurring blocked times")

class UserPreferencesResponse(BaseModel):
    user_id: str
    study_block_duration: int
    break_duration: int
    travel_duration: int
    recurring_blocked_times: List[BlockedTime]

# Calendar Event Models
class EventType(str, Enum):
    PERSONAL = "personal"
    ACADEMIC = "academic"
    SOCIAL = "social"
    WELLNESS = "wellness"
    OTHER = "other"

class EventPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class CalendarEventCreate(BaseModel):
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    start_time: datetime = Field(..., description="Event start time")
    end_time: datetime = Field(..., description="Event end time")
    location: Optional[str] = Field(None, description="Event location")
    event_type: EventType = Field(default=EventType.PERSONAL, description="Type of event")
    priority: EventPriority = Field(default=EventPriority.MEDIUM, description="Event priority")
    is_recurring: bool = Field(default=False, description="Whether this is a recurring event")
    recurrence_pattern: Optional[str] = Field(None, description="iCal recurrence rule (RRULE)")
    color: Optional[str] = Field(None, description="Event color (hex code)")
    notifications: Optional[List[int]] = Field(default_factory=list, description="Notification times in minutes before event")

class CalendarEventResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    event_type: EventType
    priority: EventPriority
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    color: Optional[str] = None
    notifications: List[int] = Field(default_factory=list)
    created_at: datetime
    updated_at: Optional[datetime] = None

class CalendarEventUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    start_time: Optional[datetime] = Field(None, description="Event start time")
    end_time: Optional[datetime] = Field(None, description="Event end time")
    location: Optional[str] = Field(None, description="Event location")
    event_type: Optional[EventType] = Field(None, description="Type of event")
    priority: Optional[EventPriority] = Field(None, description="Event priority")
    is_recurring: Optional[bool] = Field(None, description="Whether this is a recurring event")
    recurrence_pattern: Optional[str] = Field(None, description="iCal recurrence rule (RRULE)")
    color: Optional[str] = Field(None, description="Event color (hex code)")
    notifications: Optional[List[int]] = Field(None, description="Notification times in minutes before event")

class CalendarEventsResponse(BaseModel):
    events: List[CalendarEventResponse]
    total: int
    
class WeekDay(str, Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

class ClassEventCreate(BaseModel):
    title: str = Field(..., description="Class title")
    description: Optional[str] = Field(None, description="Class description")
    location: Optional[str] = Field(None, description="Class location")
    color: Optional[str] = Field(None, description="Event color (hex code)")
    
    # Days and times
    days_of_week: List[WeekDay] = Field(..., description="Days of the week when class occurs")
    start_time: str = Field(..., description="Class start time (HH:MM format)")
    end_time: str = Field(..., description="Class end time (HH:MM format)")
    
    # Term dates
    term_start_date: datetime = Field(..., description="First day of the term/semester")
    term_end_date: datetime = Field(..., description="Last day of the term/semester")
    
    # Optional fields
    notifications: Optional[List[int]] = Field(default_factory=list, description="Notification times in minutes before class")
    priority: EventPriority = Field(default=EventPriority.MEDIUM, description="Class priority")

class BulkEventsResponse(BaseModel):
    success: bool
    message: str
    events_created: int
    
# Canvas Calendar Sync Models
class CanvasCalendarEventType(str, Enum):
    ASSIGNMENT = "assignment"
    CALENDAR = "calendar_event"
    DISCUSSION = "discussion_topic"
    QUIZ = "quiz"
    
class CanvasCalendarEvent(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    location_name: Optional[str] = None
    context_code: str  # Example: "course_123" or "user_456"
    context_name: Optional[str] = None
    html_url: Optional[str] = None
    all_day: bool = False
    type: CanvasCalendarEventType
    
class CanvasCalendarSyncResponse(BaseModel):
    success: bool
    message: str
    events_synced: int
    courses_included: int