# Canvas API Integration

This document describes the Canvas LMS API integration in CampusMind, implemented using the [canvasapi Python library](https://canvasapi.readthedocs.io/en/stable/).

## Overview

The Canvas API integration allows CampusMind to:
- Fetch user courses and assignments
- Sync calendar events from Canvas
- Track assignment submission status
- Provide seamless integration with Canvas LMS

## Architecture

### Canvas Service (`app/services/canvas_service.py`)

The `CanvasService` class provides a high-level interface to the Canvas API:

```python
from app.services.canvas_service import CanvasService

# Initialize service
canvas_service = CanvasService(base_url, access_token)

# Get user courses
courses = canvas_service.get_courses()

# Get course assignments
assignments = canvas_service.get_course_assignments(course_id)

# Get calendar events
events = canvas_service.get_calendar_events()
```

### Canvas Router (`app/routers/canvas.py`)

The Canvas router provides REST API endpoints:

- `POST /canvas/test-connection` - Test Canvas API connection
- `POST /canvas/token` - Save Canvas access token
- `GET /canvas/courses` - Get user's courses
- `GET /canvas/assignments` - Get assignments from tracked courses
- `POST /canvas/sync` - Sync Canvas data to database
- `POST /canvas/calendar/sync` - Sync Canvas calendar events

## Setup

### 1. Install Dependencies

The `canvasapi` library is already installed. If you need to reinstall:

```bash
cd backend
source venv/bin/activate
pip install canvasapi
```

### 2. Generate Canvas Access Token

1. Log into your Canvas instance
2. Go to Account → Settings
3. Click "Approved Integrations"
4. Click "New Access Token"
5. Set appropriate permissions:
   - `url:GET|/api/v1/courses` - Read courses
   - `url:GET|/api/v1/courses/:course_id/assignments` - Read assignments
   - `url:GET|/api/v1/calendar_events` - Read calendar events
   - `url:GET|/api/v1/users/self` - Read user profile

### 3. Configure Canvas URL

Determine your Canvas instance URL:
- University Canvas: `https://your-university.instructure.com`
- Canvas Free for Teachers: `https://canvas.instructure.com`
- Canvas Beta: `https://canvas.beta.instructure.com`

## Usage Examples

### Testing Connection

```bash
curl -X POST "http://localhost:8000/canvas/test-connection" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "canvas_token": "YOUR_CANVAS_TOKEN",
    "canvas_base_url": "https://your-university.instructure.com"
  }'
```

### Getting Courses

```bash
curl -X GET "http://localhost:8000/canvas/courses" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Getting Assignments

```bash
curl -X GET "http://localhost:8000/canvas/assignments" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Syncing Data

```bash
curl -X POST "http://localhost:8000/canvas/sync" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Canvas API Features

### Course Management

The integration supports:
- Fetching active courses
- Filtering by tracked courses
- Getting course details (name, code, term, dates)

### Assignment Tracking

Features include:
- Fetching assignments from tracked courses
- Submission status tracking
- Due date management
- Points and grading information

### Calendar Integration

Calendar features:
- Fetching Canvas calendar events
- Supporting multiple event types (assignments, discussions, quizzes)
- Personal and course calendar events
- Date range filtering

## Error Handling

The Canvas service includes comprehensive error handling:

### Common Errors

1. **Invalid Access Token**
   ```python
   ValueError: Invalid Canvas access token
   ```

2. **Course Not Found**
   ```python
   ValueError: Course 123 not found or not accessible
   ```

3. **API Rate Limiting**
   ```python
   CanvasException: Rate limit exceeded
   ```

### Error Responses

The API returns appropriate HTTP status codes:
- `400 Bad Request` - Invalid configuration
- `401 Unauthorized` - Invalid token
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Best Practices

### Token Management

1. **Secure Storage**: Store Canvas tokens securely in the database
2. **Token Refresh**: Implement token refresh logic if needed
3. **Permission Scope**: Use minimal required permissions

### API Usage

1. **Rate Limiting**: Respect Canvas API rate limits
2. **Pagination**: Use pagination for large datasets
3. **Caching**: Implement caching for frequently accessed data
4. **Error Handling**: Always handle Canvas API exceptions

### Data Sync

1. **Incremental Sync**: Sync only changed data when possible
2. **Conflict Resolution**: Handle data conflicts appropriately
3. **User Preferences**: Respect user's tracked course preferences

## Troubleshooting

### Connection Issues

1. **Check Canvas URL**: Ensure the Canvas URL is correct
2. **Verify Token**: Confirm the access token is valid
3. **Check Permissions**: Ensure token has required permissions
4. **Network Access**: Verify network connectivity to Canvas

### Data Issues

1. **Empty Results**: Check if user has active enrollments
2. **Missing Courses**: Verify course visibility settings
3. **Assignment Status**: Check submission workflow states

### Performance Issues

1. **Large Datasets**: Use pagination and filtering
2. **Frequent API Calls**: Implement caching
3. **Concurrent Requests**: Respect rate limits

## Development

### Running Examples

```bash
cd backend/examples
python canvas_api_example.py
```

### Testing

```bash
# Test Canvas service
python -c "
from app.services.canvas_service import CanvasService
canvas = CanvasService('https://canvas.instructure.com', 'YOUR_TOKEN')
print(canvas.test_connection())
"
```

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## API Reference

### CanvasService Methods

- `test_connection()` - Test API connection
- `get_user_info()` - Get current user information
- `get_courses(enrollment_state, per_page)` - Get user courses
- `get_course_assignments(course_id, per_page)` - Get course assignments
- `get_calendar_events(context_codes, start_date, end_date, per_page)` - Get calendar events
- `get_course_by_id(course_id)` - Get specific course details
- `get_assignment_by_id(course_id, assignment_id)` - Get specific assignment details

### Canvas Router Endpoints

- `POST /canvas/test-connection` - Test connection
- `POST /canvas/token` - Save/update token
- `GET /canvas/token/status` - Check token status
- `DELETE /canvas/token` - Remove token
- `GET /canvas/courses` - Get courses
- `PUT /canvas/courses/track` - Track courses
- `GET /canvas/assignments` - Get assignments
- `POST /canvas/sync` - Sync data
- `POST /canvas/calendar/sync` - Sync calendar events

## Resources

- [Canvas API Documentation](https://canvas.instructure.com/doc/api/)
- [canvasapi Python Library](https://canvasapi.readthedocs.io/en/stable/)
- [Canvas API Authentication](https://canvas.instructure.com/doc/api/file.oauth.html)
- [Canvas API Rate Limiting](https://canvas.instructure.com/doc/api/file.rate_limiting.html)
