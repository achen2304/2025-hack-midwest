"""
Canvas API Service using canvasapi library
Enhanced Canvas LMS integration with proper error handling and caching
"""
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException, InvalidAccessToken, ResourceDoesNotExist
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CanvasService:
    """Canvas API service wrapper using canvasapi library"""
    
    def __init__(self, base_url: str, access_token: str):
        """
        Initialize Canvas service
        
        Args:
            base_url: Canvas instance URL (e.g., https://your-school.instructure.com)
            access_token: Canvas Personal Access Token
        """
        self.base_url = base_url.rstrip('/')
        self.access_token = access_token
        
        try:
            self.canvas = Canvas(self.base_url, access_token)
            # Test the connection by getting current user
            self.current_user = self.canvas.get_current_user()
            logger.info(f"Canvas service initialized for user: {self.current_user.name}")
        except InvalidAccessToken:
            raise ValueError("Invalid Canvas access token")
        except CanvasException as e:
            raise ValueError(f"Canvas API error: {str(e)}")
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        try:
            user = self.canvas.get_current_user()
            return {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "avatar_url": getattr(user, 'avatar_url', None),
                "time_zone": getattr(user, 'time_zone', None)
            }
        except CanvasException as e:
            logger.error(f"Error getting user info: {str(e)}")
            raise
    
    def get_courses(self, enrollment_state: str = "active", per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Get user's courses from Canvas
        
        Args:
            enrollment_state: Filter by enrollment state ('active', 'invited', etc.)
            per_page: Number of courses per page (max 100)
            
        Returns:
            List of course dictionaries
        """
        try:
            courses = self.canvas.get_courses(
                enrollment_state=enrollment_state,
                per_page=per_page
            )
            
            course_list = []
            for course in courses:
                course_data = {
                    "id": course.id,
                    "name": course.name,
                    "course_code": course.course_code,
                    "enrollment_term_id": course.enrollment_term_id,
                    "start_at": course.start_at.isoformat() if course.start_at else None,
                    "end_at": course.end_at.isoformat() if course.end_at else None,
                    "workflow_state": course.workflow_state,
                    "public_syllabus": getattr(course, 'public_syllabus', False),
                    "public_description": getattr(course, 'public_description', None),
                    "syllabus_body": getattr(course, 'syllabus_body', None),
                    "total_students": getattr(course, 'total_students', 0)
                }
                course_list.append(course_data)
                
            logger.info(f"Retrieved {len(course_list)} courses")
            return course_list
            
        except CanvasException as e:
            logger.error(f"Error getting courses: {str(e)}")
            raise
    
    def get_course_assignments(self, course_id: int, per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Get assignments for a specific course
        
        Args:
            course_id: Canvas course ID
            per_page: Number of assignments per page (max 100)
            
        Returns:
            List of assignment dictionaries with submission status
        """
        try:
            course = self.canvas.get_course(course_id)
            assignments = course.get_assignments(per_page=per_page)
            
            assignment_list = []
            for assignment in assignments:
                # Get submission for current user
                submission = None
                try:
                    submission = assignment.get_submission(self.current_user)
                except ResourceDoesNotExist:
                    # No submission exists yet
                    pass
                except CanvasException as e:
                    logger.warning(f"Could not get submission for assignment {assignment.id}: {str(e)}")
                
                assignment_data = {
                    "id": assignment.id,
                    "name": assignment.name,
                    "description": assignment.description,
                    "due_at": assignment.due_at.isoformat() if assignment.due_at else None,
                    "points_possible": assignment.points_possible,
                    "submission_types": assignment.submission_types,
                    "workflow_state": assignment.workflow_state,
                    "published": assignment.published,
                    "html_url": assignment.html_url,
                    "course_id": course_id,
                    "submission": {
                        "id": submission.id if submission else None,
                        "workflow_state": submission.workflow_state if submission else "unsubmitted",
                        "submitted_at": submission.submitted_at.isoformat() if submission and submission.submitted_at else None,
                        "score": submission.score if submission else None,
                        "grade": submission.grade if submission else None
                    } if submission else {
                        "id": None,
                        "workflow_state": "unsubmitted",
                        "submitted_at": None,
                        "score": None,
                        "grade": None
                    }
                }
                assignment_list.append(assignment_data)
                
            logger.info(f"Retrieved {len(assignment_list)} assignments for course {course_id}")
            return assignment_list
            
        except ResourceDoesNotExist:
            logger.error(f"Course {course_id} not found or not accessible")
            raise ValueError(f"Course {course_id} not found or not accessible")
        except CanvasException as e:
            logger.error(f"Error getting assignments for course {course_id}: {str(e)}")
            raise
    
    def get_calendar_events(self, 
                          context_codes: Optional[List[str]] = None,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Get calendar events from Canvas
        
        Args:
            context_codes: List of context codes (e.g., ['course_123', 'user_self'])
            start_date: Start date for events
            end_date: End date for events
            per_page: Number of events per page (max 100)
            
        Returns:
            List of calendar event dictionaries
        """
        try:
            events = self.canvas.get_calendar_events(
                context_codes=context_codes or [],
                start_date=start_date,
                end_date=end_date,
                per_page=per_page,
                all_events=True  # Include assignments, discussions, etc.
            )
            
            event_list = []
            for event in events:
                event_data = {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "start_at": event.start_at.isoformat() if event.start_at else None,
                    "end_at": event.end_at.isoformat() if event.end_at else None,
                    "all_day": event.all_day,
                    "location_name": event.location_name,
                    "context_code": event.context_code,
                    "context_name": getattr(event, 'context_name', None),
                    "html_url": event.html_url,
                    "type": "calendar"
                }
                
                # Determine event type based on context
                if hasattr(event, 'assignment') and event.assignment:
                    event_data["type"] = "assignment"
                    event_data["assignment"] = {
                        "id": event.assignment.id,
                        "name": event.assignment.name,
                        "points_possible": event.assignment.points_possible
                    }
                elif hasattr(event, 'discussion_topic') and event.discussion_topic:
                    event_data["type"] = "discussion"
                elif hasattr(event, 'quiz') and event.quiz:
                    event_data["type"] = "quiz"
                
                event_list.append(event_data)
                
            logger.info(f"Retrieved {len(event_list)} calendar events")
            return event_list
            
        except CanvasException as e:
            logger.error(f"Error getting calendar events: {str(e)}")
            raise
    
    def get_course_by_id(self, course_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific course"""
        try:
            course = self.canvas.get_course(course_id)
            return {
                "id": course.id,
                "name": course.name,
                "course_code": course.course_code,
                "enrollment_term_id": course.enrollment_term_id,
                "start_at": course.start_at.isoformat() if course.start_at else None,
                "end_at": course.end_at.isoformat() if course.end_at else None,
                "workflow_state": course.workflow_state,
                "public_syllabus": getattr(course, 'public_syllabus', False),
                "public_description": getattr(course, 'public_description', None),
                "syllabus_body": getattr(course, 'syllabus_body', None),
                "total_students": getattr(course, 'total_students', 0),
                "html_url": course.html_url
            }
        except ResourceDoesNotExist:
            raise ValueError(f"Course {course_id} not found or not accessible")
        except CanvasException as e:
            logger.error(f"Error getting course {course_id}: {str(e)}")
            raise
    
    def get_assignment_by_id(self, course_id: int, assignment_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific assignment"""
        try:
            course = self.canvas.get_course(course_id)
            assignment = course.get_assignment(assignment_id)
            
            # Get submission for current user
            submission = None
            try:
                submission = assignment.get_submission(self.current_user)
            except ResourceDoesNotExist:
                pass
            except CanvasException as e:
                logger.warning(f"Could not get submission for assignment {assignment_id}: {str(e)}")
            
            return {
                "id": assignment.id,
                "name": assignment.name,
                "description": assignment.description,
                "due_at": assignment.due_at.isoformat() if assignment.due_at else None,
                "points_possible": assignment.points_possible,
                "submission_types": assignment.submission_types,
                "workflow_state": assignment.workflow_state,
                "published": assignment.published,
                "html_url": assignment.html_url,
                "course_id": course_id,
                "submission": {
                    "id": submission.id if submission else None,
                    "workflow_state": submission.workflow_state if submission else "unsubmitted",
                    "submitted_at": submission.submitted_at.isoformat() if submission and submission.submitted_at else None,
                    "score": submission.score if submission else None,
                    "grade": submission.grade if submission else None,
                    "body": getattr(submission, 'body', None) if submission else None
                } if submission else {
                    "id": None,
                    "workflow_state": "unsubmitted",
                    "submitted_at": None,
                    "score": None,
                    "grade": None,
                    "body": None
                }
            }
        except ResourceDoesNotExist:
            raise ValueError(f"Assignment {assignment_id} not found in course {course_id}")
        except CanvasException as e:
            logger.error(f"Error getting assignment {assignment_id}: {str(e)}")
            raise
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the Canvas API connection and return user info"""
        try:
            user = self.canvas.get_current_user()
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email
                },
                "canvas_url": self.base_url
            }
        except CanvasException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def create_context_codes(course_ids: List[int]) -> List[str]:
        """Create context codes for Canvas API calls"""
        return [f"course_{course_id}" for course_id in course_ids] + ["user_self"]
