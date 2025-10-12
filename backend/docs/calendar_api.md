# Calendar API Documentation

The Calendar API provides endpoints for managing personal and academic events in the CampusMind application. It supports standard CRUD operations for individual events, specialized endpoints for bulk creation of recurring class events, and integration with Canvas calendar events.

## Authentication

All Calendar API endpoints require authentication via JWT token. Include the token in the Authorization header as a Bearer token:

```
Authorization: Bearer <your-jwt-token>
```

## Base URL

```
/calendar
```

## Endpoints

### Individual Event Management

#### Create Event

```
POST /calendar/events
```

Create a single calendar event.

**Request Body:**

```json
{
  "title": "Meeting with Professor",
  "description": "Office hours discussion",
  "start_time": "2025-10-15T14:00:00Z",
  "end_time": "2025-10-15T15:00:00Z",
  "location": "Science Building, Room 302",
  "event_type": "academic",
  "priority": "high",
  "is_recurring": false,
  "color": "#4285F4",
  "notifications": [15, 60]
}
```

**Response:**

```json
{
  "id": "5f8a3d2e1c9d8b7a6e5f4c3b",
  "user_id": "5f8a3d2e1c9d8b7a6e5f4c3d",
  "title": "Meeting with Professor",
  "description": "Office hours discussion",
  "start_time": "2025-10-15T14:00:00Z",
  "end_time": "2025-10-15T15:00:00Z",
  "location": "Science Building, Room 302",
  "event_type": "academic",
  "priority": "high",
  "is_recurring": false,
  "recurrence_pattern": null,
  "color": "#4285F4",
  "notifications": [15, 60],
  "created_at": "2025-10-12T18:30:00Z",
  "updated_at": "2025-10-12T18:30:00Z"
}
```

#### Get Events

```
GET /calendar/events
```

Get all calendar events with optional filters.

**Query Parameters:**

- `start_date` (optional): Filter events starting from this date (ISO format)
- `end_date` (optional): Filter events until this date (ISO format)
- `event_type` (optional): Filter by event type (personal, academic, social, wellness, other)

**Response:**

```json
{
  "events": [
    {
      "id": "5f8a3d2e1c9d8b7a6e5f4c3b",
      "user_id": "5f8a3d2e1c9d8b7a6e5f4c3d",
      "title": "Meeting with Professor",
      "description": "Office hours discussion",
      "start_time": "2025-10-15T14:00:00Z",
      "end_time": "2025-10-15T15:00:00Z",
      "location": "Science Building, Room 302",
      "event_type": "academic",
      "priority": "high",
      "is_recurring": false,
      "recurrence_pattern": null,
      "color": "#4285F4",
      "notifications": [15, 60],
      "created_at": "2025-10-12T18:30:00Z",
      "updated_at": "2025-10-12T18:30:00Z"
    }
  ],
  "total": 1
}
```

#### Get Specific Event

```
GET /calendar/events/{event_id}
```

Get a specific calendar event by ID.

**Response:**

```json
{
  "id": "5f8a3d2e1c9d8b7a6e5f4c3b",
  "user_id": "5f8a3d2e1c9d8b7a6e5f4c3d",
  "title": "Meeting with Professor",
  "description": "Office hours discussion",
  "start_time": "2025-10-15T14:00:00Z",
  "end_time": "2025-10-15T15:00:00Z",
  "location": "Science Building, Room 302",
  "event_type": "academic",
  "priority": "high",
  "is_recurring": false,
  "recurrence_pattern": null,
  "color": "#4285F4",
  "notifications": [15, 60],
  "created_at": "2025-10-12T18:30:00Z",
  "updated_at": "2025-10-12T18:30:00Z"
}
```

#### Update Event

```
PUT /calendar/events/{event_id}
```

Update an existing calendar event.

**Request Body:**

```json
{
  "title": "Updated Meeting Title",
  "location": "Virtual Meeting Room"
}
```

**Response:**

```json
{
  "id": "5f8a3d2e1c9d8b7a6e5f4c3b",
  "user_id": "5f8a3d2e1c9d8b7a6e5f4c3d",
  "title": "Updated Meeting Title",
  "description": "Office hours discussion",
  "start_time": "2025-10-15T14:00:00Z",
  "end_time": "2025-10-15T15:00:00Z",
  "location": "Virtual Meeting Room",
  "event_type": "academic",
  "priority": "high",
  "is_recurring": false,
  "recurrence_pattern": null,
  "color": "#4285F4",
  "notifications": [15, 60],
  "created_at": "2025-10-12T18:30:00Z",
  "updated_at": "2025-10-12T19:15:00Z"
}
```

#### Delete Event

```
DELETE /calendar/events/{event_id}
```

Delete a calendar event.

**Response:**

- Status code: 204 No Content

#### Get Upcoming Events

```
GET /calendar/events/upcoming
```

Get upcoming events for the next X days.

**Query Parameters:**

- `days` (optional, default: 7): Number of days to look ahead
- `limit` (optional, default: 10): Maximum number of events to return

**Response:**

```json
[
  {
    "id": "5f8a3d2e1c9d8b7a6e5f4c3b",
    "user_id": "5f8a3d2e1c9d8b7a6e5f4c3d",
    "title": "Meeting with Professor",
    "description": "Office hours discussion",
    "start_time": "2025-10-15T14:00:00Z",
    "end_time": "2025-10-15T15:00:00Z",
    "location": "Science Building, Room 302",
    "event_type": "academic",
    "priority": "high",
    "is_recurring": false,
    "recurrence_pattern": null,
    "color": "#4285F4",
    "notifications": [15, 60],
    "created_at": "2025-10-12T18:30:00Z",
    "updated_at": "2025-10-12T18:30:00Z"
  }
]
```

### Bulk Class Event Creation

```
POST /calendar/classes
```

Create recurring class events for an entire term. This endpoint allows users to easily add an entire class schedule at once.

**Request Body:**

```json
{
  "title": "Introduction to Computer Science",
  "description": "CS101 - Fundamentals of programming",
  "location": "Computer Science Building, Room 101",
  "color": "#4285F4",
  "days_of_week": ["tuesday", "thursday"],
  "start_time": "11:00",
  "end_time": "12:30",
  "term_start_date": "2025-08-23T00:00:00Z",
  "term_end_date": "2025-12-15T00:00:00Z",
  "notifications": [30, 60],
  "priority": "medium"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Successfully created 32 class events",
  "events_created": 32
}
```

## Data Models

### Event Types

- `personal`: Personal events
- `academic`: Academic events (classes, study sessions)
- `social`: Social events
- `wellness`: Wellness and health events
- `other`: Other events

### Event Priorities

- `low`: Low priority
- `medium`: Medium priority
- `high`: High priority

### Days of Week

- `monday`
- `tuesday`
- `wednesday`
- `thursday`
- `friday`
- `saturday`
- `sunday`

## Canvas Calendar Integration

The Calendar API integrates with Canvas LMS to synchronize calendar events from Canvas into the CampusMind calendar system.

### Canvas Calendar Sync

```
POST /canvas/calendar/sync
```

Synchronize calendar events from Canvas LMS to the CampusMind calendar.

**Description:**

- Fetches calendar events from Canvas for tracked courses and the user's personal calendar
- Converts Canvas events to CampusMind calendar events
- Stores them in the database with Canvas-specific metadata
- Automatically assigns appropriate event types and colors based on the Canvas event type
- Default sync period is 3 months from current date

**Response:**

```json
{
  "success": true,
  "message": "Successfully synced 42 calendar events from Canvas",
  "events_synced": 42,
  "courses_included": 3
}
```

**Canvas Event Types Mapping:**

- Canvas assignments → Academic events (red color)
- Canvas quizzes → Academic events (yellow color)
- Canvas discussions → Academic events (green color)
- Course calendar events → Academic events (green color)
- Personal calendar events → Personal events (blue color)

**Additional Metadata:**
Calendar events synced from Canvas include additional metadata:

- `canvas_id`: The original Canvas event ID
- `canvas_url`: Direct link to the event in Canvas
- `canvas_context_code`: Canvas context code (e.g., "course_123" or "user_self")

## Examples

### Example 1: Creating a One-Time Study Session

```json
{
  "title": "Study Session for Midterm",
  "description": "Review chapters 5-8",
  "start_time": "2025-10-18T15:00:00Z",
  "end_time": "2025-10-18T18:00:00Z",
  "location": "Library, Study Room 3",
  "event_type": "academic",
  "priority": "high",
  "is_recurring": false,
  "notifications": [60, 1440]
}
```

### Example 2: Creating a Recurring Class Schedule

```json
{
  "title": "Data Structures and Algorithms",
  "description": "CS202 - Advanced programming concepts",
  "location": "Engineering Building, Room 305",
  "color": "#0F9D58",
  "days_of_week": ["monday", "wednesday", "friday"],
  "start_time": "14:00",
  "end_time": "15:30",
  "term_start_date": "2025-08-25T00:00:00Z",
  "term_end_date": "2025-12-10T00:00:00Z",
  "notifications": [15, 30],
  "priority": "high"
}
```

## Error Codes

- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Notes

- All timestamps should be in ISO 8601 format (UTC)
- Time format for class schedules should be in 24-hour format (HH:MM)
- The bulk class creation endpoint will automatically generate individual events for each class session throughout the term
- Events are stored with user-specific access control
- Calendar events can be filtered by date range and event type
