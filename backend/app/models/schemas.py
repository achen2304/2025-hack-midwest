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
