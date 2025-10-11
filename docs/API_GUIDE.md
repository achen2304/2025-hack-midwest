# API Reference Guide

Complete API endpoint reference for CampusMind backend.

## Base URL

**Development:** `http://localhost:8000`
**Production:** `https://your-domain.com`

**Interactive Docs:** http://localhost:8000/docs

## Authentication

All endpoints (except `/`, `/health`, `/docs`, `/auth/*`) require authentication.

### Header Format

```http
Authorization: Bearer YOUR_JWT_TOKEN
```

### Get Test Token

```http
POST /auth/dev-token
Content-Type: application/json

{
  "user_id": "test_user",
  "email": "test@example.com",
  "name": "Test User"
}
```

---

## Endpoints

### Authentication

#### Get Dev Token (Development Only)
```http
POST /auth/dev-token
```

**Request Body:**
```json
{
  "user_id": "test_user_123",
  "email": "test@campusmind.com",
  "name": "Test User"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1Qi...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "user_id": "test_user_123",
    "email": "test@campusmind.com",
    "name": "Test User"
  }
}
```

---

### Canvas LMS

#### Connect Canvas Account
```http
POST /canvas/connect
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "canvas_token": "10835~xxxxx",
  "canvas_base_url": "https://canvas.iastate.edu"
}
```

#### Get Courses
```http
GET /canvas/courses?enrollment_state=active
Authorization: Bearer {token}
```

**Response:**
```json
[
  {
    "id": "12345",
    "name": "Introduction to Computer Science",
    "course_code": "CS 101",
    "enrollment_term_id": "123",
    "start_at": "2025-01-15T00:00:00Z",
    "end_at": "2025-05-15T00:00:00Z"
  }
]
```

#### Get Upcoming Assignments
```http
GET /canvas/assignments/upcoming?days_ahead=30
Authorization: Bearer {token}
```

#### Track Courses
```http
POST /canvas/track-courses
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "course_ids": ["12345", "67890"]
}
```

---

### Google Calendar

#### Get OAuth URL
```http
GET /calendar/auth-url
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "message": "Authorization URL generated",
  "data": {
    "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?..."
  }
}
```

#### Complete OAuth
```http
POST /calendar/auth
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "auth_code": "4/0AbC..."
}
```

#### Get Calendar Events
```http
GET /calendar/events?days_ahead=30&calendar_id=primary
Authorization: Bearer {token}
```

#### Create Event
```http
POST /calendar/events?calendar_id=primary
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "summary": "Study Session - CS 101",
  "description": "Prepare for midterm exam",
  "start": {
    "dateTime": "2025-10-15T10:00:00-05:00",
    "timeZone": "America/Chicago"
  },
  "end": {
    "dateTime": "2025-10-15T12:00:00-05:00",
    "timeZone": "America/Chicago"
  }
}
```

---

### Sync Orchestration

#### Sync Canvas to Calendar
```http
POST /sync/canvas-to-calendar
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "force": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Sync completed",
  "data": {
    "status": "success",
    "synced_count": 5,
    "skipped_count": 2,
    "errors": []
  }
}
```

#### Get Sync Status
```http
GET /sync/status
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "message": "Sync status retrieved",
  "data": {
    "last_canvas_sync": "2025-10-11T14:30:00Z",
    "last_calendar_sync": "2025-10-11T14:30:00Z",
    "sync_enabled": true,
    "auto_sync_interval_hours": 24,
    "last_sync_status": "success"
  }
}
```

#### Enable Auto-Sync
```http
POST /sync/enable?interval_hours=24
Authorization: Bearer {token}
```

#### Disable Auto-Sync
```http
POST /sync/disable
Authorization: Bearer {token}
```

---

### AI Agents

#### Ask Sync Agent
```http
POST /sync/agent/ask
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "query": "What assignments do I have this week?",
  "context": {}
}
```

**Response:**
```json
{
  "response": "You have 3 assignments this week: CS 101 homework due Wednesday, Math 201 problem set due Thursday, and English 102 essay due Friday.",
  "suggestions": [
    "View upcoming assignments",
    "Schedule study sessions",
    "Analyze workload"
  ],
  "context": {}
}
```

#### Schedule Study Sessions
```http
POST /sync/agent/schedule-study
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "query": "I need help preparing for my CS midterm next week",
  "context": {}
}
```

#### Analyze Workload
```http
POST /sync/agent/analyze-workload
Authorization: Bearer {token}
```

---

### Journal (In Progress)

#### Create Journal Entry
```http
POST /journal/entries
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "id": "entry_123",
  "user_id": "user_123",
  "content": "Today was a productive day...",
  "mood": "good",
  "tags": ["productive", "studying"],
  "created_at": "2025-10-11T14:30:00Z"
}
```

#### Get Journal Entries
```http
GET /journal/entries?limit=10&offset=0&mood_filter=good
Authorization: Bearer {token}
```

#### Get Mood Trends
```http
GET /journal/mood-trends?days=30
Authorization: Bearer {token}
```

---

### Study Plans (In Progress)

#### Create Study Plan
```http
POST /plan/plans
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "id": "plan_123",
  "user_id": "user_123",
  "title": "Midterm Study Plan",
  "description": "Comprehensive study schedule for midterms",
  "tasks": [
    {
      "task": "Review Chapter 1-3",
      "duration": "2 hours",
      "completed": false
    }
  ],
  "due_date": "2025-10-20T00:00:00Z",
  "is_completed": false
}
```

#### Generate AI Study Plan
```http
POST /plan/generate
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "course_data": [
    {
      "course": "CS 101",
      "topics": ["algorithms", "data structures"],
      "difficulty": "medium"
    }
  ],
  "preferences": {
    "study_hours_per_day": 3,
    "break_frequency": 60
  }
}
```

---

## Response Format

### Success Response

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data here
  }
}
```

### Error Response

```json
{
  "detail": "Error message here"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Postman Collection

### Import Collection

1. Open Postman
2. File → Import
3. Create new collection: "CampusMind API"

### Environment Variables

Create environment with:

```
base_url: http://localhost:8000
token: {{access_token}}
```

### Collection Structure

```
CampusMind API/
├── Auth/
│   └── Get Dev Token
├── Canvas/
│   ├── Connect Canvas
│   ├── Get Courses
│   ├── Get Upcoming Assignments
│   └── Track Courses
├── Calendar/
│   ├── Get Auth URL
│   ├── Complete OAuth
│   └── Get Events
└── Sync/
    ├── Sync Canvas to Calendar
    ├── Get Sync Status
    └── Ask Agent
```

### Test Script (Add to Collection)

```javascript
// Auto-set token from dev-token response
if (pm.response.code === 200 && pm.request.url.includes('dev-token')) {
    var data = pm.response.json();
    pm.environment.set('access_token', data.access_token);
}
```

---

## cURL Examples

### Get Dev Token & Use It

```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/dev-token | jq -r '.access_token')

# Use token
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/canvas/courses
```

### Connect Canvas

```bash
curl -X POST http://localhost:8000/canvas/connect \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "canvas_token": "10835~xxxxx",
    "canvas_base_url": "https://canvas.iastate.edu"
  }'
```

### Get Upcoming Assignments

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/canvas/assignments/upcoming?days_ahead=7"
```

### Sync to Calendar

```bash
curl -X POST http://localhost:8000/sync/canvas-to-calendar \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

### Ask AI Agent

```bash
curl -X POST http://localhost:8000/sync/agent/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What should I focus on this week?",
    "context": {}
  }'
```

---

## Rate Limiting

Currently no rate limiting implemented. In production, consider:

- 100 requests per minute per user
- 1000 requests per hour per user

---

## Next Steps

- [ ] Test all endpoints with Postman
- [ ] Create Postman collection
- [ ] Set up monitoring
- [ ] Add rate limiting
- [ ] Implement webhooks

## Resources

- [Interactive API Docs](http://localhost:8000/docs) - Test live
- [ReDoc Documentation](http://localhost:8000/redoc) - Alternative view
- [Postman Learning Center](https://learning.postman.com/)
