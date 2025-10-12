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
    course_name: Optional[str] = Field(None, description="Name of the course/class")
    course_code: Optional[str] = Field(None, description="Course code (e.g., CS101)")
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

# Health Check and Feeling Level Models
class FeelingLevel(int, Enum):
    GREAT = 1
    GOOD = 2
    OKAY = 3
    STRESSED = 4
    OVERWHELMED = 5

class CourseFeeling(BaseModel):
    course_id: str = Field(..., description="Course ID")
    course_name: str = Field(..., description="Course name")
    feeling_level: FeelingLevel = Field(..., description="How the user feels about this course (1=great, 5=overwhelmed)")
    recorded_at: datetime = Field(default_factory=datetime.utcnow, description="When this feeling was recorded")

class HealthCheckIn(BaseModel):
    message: str = Field(..., description="User's response to the health check")
    sentiment: Optional[str] = Field(None, description="Detected sentiment (positive, neutral, negative)")
    current_study_context: Optional[str] = Field(None, description="What the user is currently studying")
    course_feelings: Optional[List[CourseFeeling]] = Field(default_factory=list, description="Feelings about specific courses")

class HealthCheckResponse(BaseModel):
    id: str
    user_id: str
    message: str
    sentiment: Optional[str] = None
    current_study_context: Optional[str] = None
    course_feelings: List[CourseFeeling] = Field(default_factory=list)
    created_at: datetime
    next_checkin_minutes: Optional[int] = Field(None, description="Minutes until next check-in")

class HealthCheckInRequest(BaseModel):
    message: str = Field(..., description="User's message/feeling")
    current_course_id: Optional[str] = Field(None, description="Course ID user is currently studying")
    feeling_level: Optional[FeelingLevel] = Field(None, description="Current feeling level for the course being studied")

# Study Session Models
class StudySessionCreate(BaseModel):
    course_id: str = Field(..., description="Course being studied")
    assignment_id: Optional[str] = Field(None, description="Related assignment if any")
    planned_duration: int = Field(..., description="Planned study duration in minutes")

class StudySessionUpdate(BaseModel):
    actual_duration: Optional[int] = Field(None, description="Actual study duration in minutes")
    feeling_before: Optional[FeelingLevel] = Field(None, description="Feeling level before study session")
    feeling_after: Optional[FeelingLevel] = Field(None, description="Feeling level after study session")
    completed: bool = Field(default=False, description="Whether the session was completed")
    notes: Optional[str] = Field(None, description="Session notes")

class StudySessionResponse(BaseModel):
    id: str
    user_id: str
    course_id: str
    assignment_id: Optional[str] = None
    planned_duration: int
    actual_duration: Optional[int] = None
    feeling_before: Optional[FeelingLevel] = None
    feeling_after: Optional[FeelingLevel] = None
    completed: bool = False
    notes: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None

# AI Schedule Generation Models
class ScheduleGenerationRequest(BaseModel):
    prioritize_courses: Optional[List[str]] = Field(default_factory=list, description="Course IDs to prioritize")
    start_date: Optional[datetime] = Field(None, description="Start date for schedule generation")
    end_date: Optional[datetime] = Field(None, description="End date for schedule generation")
    regenerate: bool = Field(default=False, description="Force regeneration of schedule")

class ScheduleGenerationResponse(BaseModel):
    success: bool
    message: str
    study_blocks_created: int
    break_blocks_created: int

# Document Upload and Storage Models
class DocumentType(str, Enum):
    LECTURE_NOTES = "lecture_notes"
    SLIDES = "slides"
    READING = "reading"
    TEXTBOOK = "textbook"
    OTHER = "other"

class DocumentUploadResponse(BaseModel):
    id: str
    user_id: str
    course_id: str
    filename: str
    document_type: DocumentType
    file_size: int
    total_chunks: int
    pages: int
    uploaded_at: datetime
    message: str

class DocumentListResponse(BaseModel):
    id: str
    course_id: str
    filename: str
    document_type: DocumentType
    file_size: int
    total_chunks: int
    pages: int
    uploaded_at: datetime

class DocumentSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    course_id: Optional[str] = Field(None, description="Filter by course")
    limit: int = Field(5, ge=1, le=20, description="Number of results")

class DocumentSearchResult(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    course_id: str
    text: str
    relevance_score: float
    chunk_index: int
    page_number: Optional[int] = None

# Study Assistant Chat Models
class ChatMessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    role: ChatMessageRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When message was sent")

class ChatSessionCreate(BaseModel):
    course_id: Optional[str] = Field(None, description="Optional course context")
    initial_message: str = Field(..., description="First question/message")

class ChatSessionResponse(BaseModel):
    id: str
    user_id: str
    course_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int

class ChatMessageRequest(BaseModel):
    message: str = Field(..., description="User's question or message")
    course_id: Optional[str] = Field(None, description="Optional course filter for document search")

class DocumentSource(BaseModel):
    document_id: str
    filename: str
    page_number: Optional[int] = None
    chunk_index: int
    relevance_score: float

class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    role: ChatMessageRole
    content: str
    sources: List[DocumentSource] = Field(default_factory=list, description="Documents referenced in answer")
    needs_clarification: bool = Field(default=False, description="Whether assistant needs clarification")
    follow_up_suggestions: List[str] = Field(default_factory=list, description="Suggested follow-up questions")
    documents_found: int = Field(default=0, description="Number of relevant documents found")
    timestamp: datetime

class ChatHistoryResponse(BaseModel):
    session_id: str
    course_id: Optional[str] = None
    messages: List[ChatMessageResponse]
    total_messages: int
    created_at: datetime
    updated_at: datetime

class DocumentSummaryRequest(BaseModel):
    document_id: str = Field(..., description="Document to summarize")

class DocumentSummaryResponse(BaseModel):
    document_id: str
    filename: str
    summary: str
    key_topics: List[str] = Field(default_factory=list)
    chunks_analyzed: int