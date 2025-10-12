"""
Calendar management routes for personal events
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from datetime import datetime, timedelta, time
from bson import ObjectId
from typing import List, Optional, Dict
import calendar
from dateutil.rrule import rrule, WEEKLY
from dateutil.parser import parse
import re

from app.util.db import get_database
from app.util.auth import verify_backend_token
from app.models.schemas import (
    CalendarEventCreate,
    CalendarEventResponse,
    CalendarEventUpdate,
    CalendarEventsResponse,
    EventType,
    EventPriority,
    ClassEventCreate,
    WeekDay,
    BulkEventsResponse
)

router = APIRouter(prefix="/calendar", tags=["Calendar"])

# Helper functions for recurring events
def get_weekday_index(day_name: str) -> int:
    """Convert day name to weekday index (0=Monday, 6=Sunday)"""
    days = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }
    return days.get(day_name.lower(), 0)

def parse_time_str(time_str: str) -> time:
    """Parse time string in HH:MM format to datetime.time object"""
    if not re.match(r"^\d{1,2}:\d{2}$", time_str):
        raise ValueError("Time must be in HH:MM format")
    
    hour, minute = map(int, time_str.split(':'))
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        raise ValueError("Invalid time values")
    
    return time(hour, minute)

def generate_class_events(class_event: ClassEventCreate, user_id: str) -> List[Dict]:
    """Generate individual event documents for each class occurrence"""
    events = []
    
    # Parse start and end times
    try:
        start_time_obj = parse_time_str(class_event.start_time)
        end_time_obj = parse_time_str(class_event.end_time)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid time format: {str(e)}"
        )
    
    # Get weekday indices (0=Monday, 6=Sunday)
    weekdays = [get_weekday_index(day) for day in class_event.days_of_week]
    
    # Set term start and end dates to midnight
    term_start = datetime.combine(class_event.term_start_date.date(), time(0, 0))
    term_end = datetime.combine(class_event.term_end_date.date(), time(23, 59, 59))
    
    # Generate all occurrences using dateutil.rrule
    now = datetime.utcnow()
    
    for weekday in weekdays:
        # Find the first occurrence of this weekday after the term start
        first_day = term_start
        while calendar.weekday(first_day.year, first_day.month, first_day.day) != weekday:
            first_day += timedelta(days=1)
            
            # If we've gone past the term end, skip this weekday
            if first_day > term_end:
                break
        
        # Generate all occurrences of this weekday within the term
        occurrences = list(rrule(
            freq=WEEKLY,
            dtstart=first_day,
            until=term_end
        ))
        
        # Create an event for each occurrence
        for occurrence in occurrences:
            # Combine occurrence date with class times
            event_start = datetime.combine(occurrence.date(), start_time_obj)
            event_end = datetime.combine(occurrence.date(), end_time_obj)
            
            # Create event document
            event_doc = {
                "user_id": user_id,
                "title": class_event.title,
                "description": class_event.description,
                "start_time": event_start,
                "end_time": event_end,
                "location": class_event.location,
                "event_type": EventType.ACADEMIC,  # Classes are academic events
                "priority": class_event.priority,
                "is_recurring": True,  # Mark as part of a recurring series
                "recurrence_pattern": f"WEEKLY;BYDAY={WeekDay(class_event.days_of_week[0]).name[:2]}",
                "color": class_event.color,
                "notifications": class_event.notifications,
                "created_at": now,
                "updated_at": now
            }
            
            events.append(event_doc)
    
    return events

@router.post("/events", response_model=CalendarEventResponse)
async def create_event(
    event: CalendarEventCreate,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Create a new calendar event"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's MongoDB ID
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass

        if not user_doc:
            user_doc = await db.users.find_one({"email": email})

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        db_user_id = str(user_doc["_id"])

        # Validate event dates
        if event.end_time <= event.start_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End time must be after start time"
            )

        # Create event document
        now = datetime.utcnow()
        event_doc = {
            "user_id": db_user_id,
            "title": event.title,
            "description": event.description,
            "start_time": event.start_time,
            "end_time": event.end_time,
            "location": event.location,
            "event_type": event.event_type,
            "priority": event.priority,
            "is_recurring": event.is_recurring,
            "recurrence_pattern": event.recurrence_pattern,
            "color": event.color,
            "notifications": event.notifications,
            "created_at": now,
            "updated_at": now
        }

        result = await db.calendar_events.insert_one(event_doc)
        
        # Get the created event
        created_event = await db.calendar_events.find_one({"_id": result.inserted_id})
        
        return CalendarEventResponse(
            id=str(created_event["_id"]),
            user_id=created_event["user_id"],
            title=created_event["title"],
            description=created_event.get("description"),
            start_time=created_event["start_time"],
            end_time=created_event["end_time"],
            location=created_event.get("location"),
            event_type=created_event["event_type"],
            priority=created_event["priority"],
            is_recurring=created_event.get("is_recurring", False),
            recurrence_pattern=created_event.get("recurrence_pattern"),
            color=created_event.get("color"),
            notifications=created_event.get("notifications", []),
            created_at=created_event["created_at"],
            updated_at=created_event.get("updated_at")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create event: {str(e)}"
        )

@router.get("/events", response_model=CalendarEventsResponse)
async def get_events(
    start_date: Optional[datetime] = Query(None, description="Filter events starting from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter events until this date"),
    event_type: Optional[EventType] = Query(None, description="Filter by event type"),
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Get user's calendar events with optional date range and type filters"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's MongoDB ID
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass

        if not user_doc:
            user_doc = await db.users.find_one({"email": email})

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        db_user_id = str(user_doc["_id"])

        # Build query filters
        query = {"user_id": db_user_id}

        # Date range filter
        if start_date or end_date:
            date_query = {}
            if start_date:
                # Events that end after the start date
                date_query["end_time"] = {"$gte": start_date}
            if end_date:
                # Events that start before the end date
                if "end_time" in date_query:
                    date_query["start_time"] = {"$lte": end_date}
                else:
                    date_query["start_time"] = {"$lte": end_date}
            
            # Add date filters to main query
            query.update(date_query)

        # Event type filter
        if event_type:
            query["event_type"] = event_type

        # Fetch events, sorted by start time
        cursor = db.calendar_events.find(query).sort("start_time", 1)
        events_docs = await cursor.to_list(length=None)

        # Count total events
        total_events = len(events_docs)

        # Convert to response model
        events = []
        for doc in events_docs:
            events.append(CalendarEventResponse(
                id=str(doc["_id"]),
                user_id=doc["user_id"],
                title=doc["title"],
                description=doc.get("description"),
                start_time=doc["start_time"],
                end_time=doc["end_time"],
                location=doc.get("location"),
                event_type=doc["event_type"],
                priority=doc["priority"],
                is_recurring=doc.get("is_recurring", False),
                recurrence_pattern=doc.get("recurrence_pattern"),
                color=doc.get("color"),
                notifications=doc.get("notifications", []),
                created_at=doc["created_at"],
                updated_at=doc.get("updated_at")
            ))

        return CalendarEventsResponse(
            events=events,
            total=total_events
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch events: {str(e)}"
        )

@router.get("/events/{event_id}", response_model=CalendarEventResponse)
async def get_event(
    event_id: str,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Get a specific calendar event by ID"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's MongoDB ID
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass

        if not user_doc:
            user_doc = await db.users.find_one({"email": email})

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        db_user_id = str(user_doc["_id"])

        # Find event by ID
        try:
            event_doc = await db.calendar_events.find_one({
                "_id": ObjectId(event_id),
                "user_id": db_user_id
            })
        except:
            event_doc = None

        if not event_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        return CalendarEventResponse(
            id=str(event_doc["_id"]),
            user_id=event_doc["user_id"],
            title=event_doc["title"],
            description=event_doc.get("description"),
            start_time=event_doc["start_time"],
            end_time=event_doc["end_time"],
            location=event_doc.get("location"),
            event_type=event_doc["event_type"],
            priority=event_doc["priority"],
            is_recurring=event_doc.get("is_recurring", False),
            recurrence_pattern=event_doc.get("recurrence_pattern"),
            color=event_doc.get("color"),
            notifications=event_doc.get("notifications", []),
            created_at=event_doc["created_at"],
            updated_at=event_doc.get("updated_at")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch event: {str(e)}"
        )

@router.put("/events/{event_id}", response_model=CalendarEventResponse)
async def update_event(
    event_id: str,
    event_update: CalendarEventUpdate,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Update a calendar event"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's MongoDB ID
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass

        if not user_doc:
            user_doc = await db.users.find_one({"email": email})

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        db_user_id = str(user_doc["_id"])

        # Find event by ID
        try:
            event_doc = await db.calendar_events.find_one({
                "_id": ObjectId(event_id),
                "user_id": db_user_id
            })
        except:
            event_doc = None

        if not event_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        # Build update document with only provided fields
        update_data = {}
        for field, value in event_update.model_dump(exclude_unset=True).items():
            if value is not None:  # Skip None values
                update_data[field] = value

        # If both start_time and end_time are provided, validate
        if "start_time" in update_data and "end_time" in update_data:
            if update_data["end_time"] <= update_data["start_time"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="End time must be after start time"
                )
        # If only start_time is provided, validate against existing end_time
        elif "start_time" in update_data:
            if update_data["start_time"] >= event_doc["end_time"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Start time must be before end time"
                )
        # If only end_time is provided, validate against existing start_time
        elif "end_time" in update_data:
            if update_data["end_time"] <= event_doc["start_time"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="End time must be after start time"
                )

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        # Add updated_at timestamp
        update_data["updated_at"] = datetime.utcnow()

        # Update event
        await db.calendar_events.update_one(
            {"_id": ObjectId(event_id)},
            {"$set": update_data}
        )

        # Fetch updated event
        updated_event = await db.calendar_events.find_one({"_id": ObjectId(event_id)})

        return CalendarEventResponse(
            id=str(updated_event["_id"]),
            user_id=updated_event["user_id"],
            title=updated_event["title"],
            description=updated_event.get("description"),
            start_time=updated_event["start_time"],
            end_time=updated_event["end_time"],
            location=updated_event.get("location"),
            event_type=updated_event["event_type"],
            priority=updated_event["priority"],
            is_recurring=updated_event.get("is_recurring", False),
            recurrence_pattern=updated_event.get("recurrence_pattern"),
            color=updated_event.get("color"),
            notifications=updated_event.get("notifications", []),
            created_at=updated_event["created_at"],
            updated_at=updated_event.get("updated_at")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update event: {str(e)}"
        )

@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: str,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Delete a calendar event"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's MongoDB ID
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass

        if not user_doc:
            user_doc = await db.users.find_one({"email": email})

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        db_user_id = str(user_doc["_id"])

        # Delete event
        try:
            result = await db.calendar_events.delete_one({
                "_id": ObjectId(event_id),
                "user_id": db_user_id
            })
        except:
            result = None

        if not result or result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete event: {str(e)}"
        )

@router.post("/classes", response_model=BulkEventsResponse)
async def create_class_events(
    class_event: ClassEventCreate,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """
    Create recurring class events for an entire term
    
    This endpoint allows users to easily add an entire class schedule at once.
    For example, a class that meets Tuesday and Wednesday from 11am to 1pm,
    starting August 23 and ending December 1.
    """
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's MongoDB ID
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass

        if not user_doc:
            user_doc = await db.users.find_one({"email": email})

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        db_user_id = str(user_doc["_id"])
        
        # Validate term dates
        if class_event.term_end_date <= class_event.term_start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Term end date must be after term start date"
            )
            
        # Generate all class event occurrences
        events = generate_class_events(class_event, db_user_id)
        
        if not events:
            return BulkEventsResponse(
                success=True,
                message="No events were created. Check that your term dates and days of week are valid.",
                events_created=0
            )
            
        # Insert all events in one bulk operation
        result = await db.calendar_events.insert_many(events)
        
        return BulkEventsResponse(
            success=True,
            message=f"Successfully created {len(result.inserted_ids)} class events",
            events_created=len(result.inserted_ids)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create class events: {str(e)}"
        )

@router.get("/events/upcoming", response_model=List[CalendarEventResponse])
async def get_upcoming_events(
    days: int = Query(7, description="Number of days to look ahead"),
    limit: int = Query(10, description="Maximum number of events to return"),
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Get upcoming calendar events for the next X days"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's MongoDB ID
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass

        if not user_doc:
            user_doc = await db.users.find_one({"email": email})

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        db_user_id = str(user_doc["_id"])

        # Calculate date range
        now = datetime.utcnow()
        end_date = now + timedelta(days=days)

        # Query for upcoming events
        cursor = db.calendar_events.find({
            "user_id": db_user_id,
            "start_time": {"$gte": now, "$lte": end_date}
        }).sort("start_time", 1).limit(limit)

        events_docs = await cursor.to_list(length=None)

        # Convert to response model
        events = []
        for doc in events_docs:
            events.append(CalendarEventResponse(
                id=str(doc["_id"]),
                user_id=doc["user_id"],
                title=doc["title"],
                description=doc.get("description"),
                start_time=doc["start_time"],
                end_time=doc["end_time"],
                location=doc.get("location"),
                event_type=doc["event_type"],
                priority=doc["priority"],
                is_recurring=doc.get("is_recurring", False),
                recurrence_pattern=doc.get("recurrence_pattern"),
                color=doc.get("color"),
                notifications=doc.get("notifications", []),
                created_at=doc["created_at"],
                updated_at=doc.get("updated_at")
            ))

        return events

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch upcoming events: {str(e)}"
        )
