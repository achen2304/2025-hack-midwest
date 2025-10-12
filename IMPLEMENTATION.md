# CampusMind Implementation Documentation

## Overview

CampusMind is an AI-powered academic and wellness assistant for college students that integrates with Canvas LMS to help manage coursework and schedules.

## Architecture

### Tech Stack

- **Frontend**: Next.js 14 (App Router), React, TypeScript, TailwindCSS
- **Backend**: FastAPI (Python), Motor (async MongoDB driver)
- **Database**: MongoDB Atlas
- **Authentication**: NextAuth.js with credentials provider

### System Flow

```
User (Browser)
    ↓
Next.js Frontend (Port 3000)
    ↓
API Proxy (/api/backend/[...path])
    ↓
FastAPI Backend (Port 8000)
    ↓
MongoDB Atlas (campusmind database)
```

---

## Authentication System

### How It Works

1. **User Registration** (`/api/signup`)

   - User provides email, password, and name
   - Password is hashed with bcrypt (12 rounds)
   - User stored in `campusmind.users` collection

2. **User Login** (`/api/auth/[...nextauth]`)

   - NextAuth validates credentials against MongoDB
   - Creates JWT session token stored in HTTP-only cookie
   - JWT contains: `sub` (user ID), `email`, `name`, `picture`

3. **API Authentication Flow**
   - Frontend makes request to `/api/backend/*`
   - Next.js proxy validates NextAuth session
   - Proxy mints a new backend JWT (15-minute expiry)
   - Backend JWT sent to FastAPI with request
   - FastAPI validates JWT and extracts user info

### JWT Structure

**NextAuth JWT** (session cookie):

- Issuer: `nextauth`
- Contains: user session data
- Expires: per session configuration

**Backend JWT** (Authorization header):

- Issuer: `nextapp`
- Audience: `fastapi`
- Contains: `sub`, `email`, `name`, `picture`
- Expires: 15 minutes
- Signed with: `BACKEND_JWT_SECRET`

---

## Database Structure

### Collections

#### `users`

```javascript
{
  _id: ObjectId,
  email: string (unique),
  name: string,
  hashedPassword: string,
  image: string,
  university: string,
  canvas_token: string (encrypted),
  canvas_base_url: string,
  canvas_token_updated_at: datetime,
  tracked_course_ids: [string],  // Canvas course IDs
  created_at: datetime
}
```

#### `user_preferences`

```javascript
{
  _id: ObjectId,
  user_id: string (references users._id),
  study_block_duration: int (minutes),
  break_duration: int (minutes),
  travel_duration: int (minutes),
  recurring_blocked_times: [
    {
      day_of_week: string,
      start: string (HH:MM),
      end: string (HH:MM)
    }
  ],
  updated_at: datetime
}
```

#### `canvas_courses`

```javascript
{
  _id: ObjectId,
  canvas_id: string,
  user_id: string,
  name: string,
  course_code: string,
  enrollment_term_id: int,
  start_at: datetime,
  end_at: datetime,
  synced_at: datetime
}
```

#### `assignments`

```javascript
{
  _id: ObjectId,
  canvas_id: string,
  user_id: string,
  title: string,
  description: string,
  course: string,
  course_id: string,
  due_date: datetime,
  points_possible: float,
  submission_types: [string],
  status: string,  // "not_started", "in_progress", "completed"
  canvas_workflow_state: string,  // Canvas's original workflow_state
  completed_at: datetime,  // Timestamp when marked completed
  synced_at: datetime,
  created_at: datetime,
  updated_at: datetime
}
```

---

## API Endpoints

### User Profile Management

#### `GET /user/profile`

Get current user's profile information.

- **Auth**: Required
- **Returns**: User profile with id, email, name, university, image
- **Auto-creates**: Profile if doesn't exist

#### `PUT /user/profile`

Update user's profile information.

- **Auth**: Required
- **Body**: `{ name?, university?, image? }`
- **Returns**: Updated profile

#### `GET /user/preferences`

Get user's scheduling preferences.

- **Auth**: Required
- **Returns**: Preferences or defaults if not set

#### `PUT /user/preferences`

Update scheduling preferences.

- **Auth**: Required
- **Body**: `{ study_block_duration, break_duration, travel_duration, recurring_blocked_times }`

---

### Canvas Integration

#### Canvas Token Management

**`POST /canvas/token`**
Save Canvas Personal Access Token.

- **Auth**: Required
- **Body**: `{ canvas_token: string, canvas_base_url?: string }`
- **Storage**: Encrypted in user document

**`GET /canvas/token/status`**
Check if user has configured Canvas token.

- **Auth**: Required
- **Returns**: `{ has_token: boolean }`

**`DELETE /canvas/token`**
Remove Canvas token from account.

- **Auth**: Required
- **Also clears**: `canvas_base_url`, `canvas_token_updated_at`

#### Course Tracking System

**`GET /canvas/courses`**
Get user's Canvas courses with smart filtering.

- **Auth**: Required
- **Behavior**:
  - **First time** (no tracked courses): Returns ALL courses
  - **After tracking**: Returns only tracked courses
- **Returns**: Array of courses with `is_tracked` flag

**`PUT /canvas/courses/track`**
Set which courses to track.

- **Auth**: Required
- **Body**: `{ course_ids: [string] }`
- **Effect**: All future requests only work with these courses
- **Returns**: `{ tracked_count: int, message: string }`

**Flow Example:**

```
1. User: GET /canvas/courses → Returns all 10 courses
2. User selects: Course A, Course B, Course C
3. User: PUT /canvas/courses/track → { course_ids: ["A", "B", "C"] }
4. Future GET /canvas/courses → Returns only A, B, C
5. Future GET /canvas/assignments → Only from A, B, C
6. Future POST /canvas/sync → Only syncs A, B, C
```

#### `GET /canvas/assignments`

Get assignments from tracked courses directly from Canvas API (live preview).

- **Auth**: Required
- **Behavior**:
  - Fetches live from Canvas API (not from database)
  - Returns empty if no courses tracked
  - Includes submission status from Canvas
  - **Sorted by due_date** (earliest first)
- **Returns**: Array of assignments with status and due dates

#### `POST /canvas/sync`

Sync tracked courses and assignments from Canvas to MongoDB database.

- **Auth**: Required
- **Behavior**:
  - Syncs only tracked courses
  - Updates or inserts (upsert) courses and assignments
  - **Smart status preservation**: NEVER overwrites "in_progress" status
  - Maps Canvas submission states:
    - `submitted`, `pending_review`, `graded` → `completed`
    - `unsubmitted` → `not_started`
    - User's `in_progress` → preserved unchanged
  - Returns 0 if no courses tracked
- **Returns**: `{ courses_synced: int, assignments_synced: int }`

#### `POST /canvas/calendar/sync`

Sync Canvas calendar events to the CampusMind calendar system.

- **Auth**: Required
- **Behavior**:
  - Fetches events from Canvas for tracked courses and personal calendar
  - Converts Canvas events to CampusMind calendar events
  - Maps event types:
    - Canvas assignments → Academic events (red color)
    - Canvas quizzes → Academic events (yellow color)
    - Canvas discussions → Academic events (green color)
    - Course calendar events → Academic events (green color)
    - Personal calendar events → Personal events (blue color)
  - Syncs 3 months of events by default
  - Preserves Canvas metadata (IDs, URLs, context codes)
- **Returns**: `{ success: bool, message: string, events_synced: int, courses_included: int }`

---

### Assignment Management

**IMPORTANT**: These endpoints pull from MongoDB (synced database), NOT directly from Canvas.

**Data Flow**:

```
1. GET /canvas/assignments → Live preview from Canvas API
2. POST /canvas/sync → Sync Canvas data to MongoDB
3. GET /assignments → Display from MongoDB database
```

#### `GET /assignments`

Get all synced assignments from MongoDB database.

- **Auth**: Required
- **Query Params**:
  - `status` - Filter by status (not_started, in_progress, completed)
  - `course_id` - Filter by course ID
  - `due_before` - Filter assignments due before date
  - `due_after` - Filter assignments due after date
- **Returns**: Array of assignments **sorted by due_date** (earliest first)
- **Note**: To get latest from Canvas, run `/canvas/sync` first

#### `GET /assignments/{assignment_id}`

Get single assignment details from database.

- **Auth**: Required
- **Returns**: Assignment with full details

#### `PUT /assignments/{assignment_id}/status`

Update assignment completion status (**USER ONLY** - not synced to Canvas).

- **Auth**: Required
- **Body**: `{ status: "not_started" | "in_progress" | "completed" }`
- **Behavior**:
  - Only users can set "in_progress" status
  - Canvas sync will NEVER overwrite "in_progress"
  - Adds `completed_at` timestamp when marking completed
- **Returns**: Updated assignment

#### `GET /assignments/count/by-status`

Get count of assignments grouped by status.

- **Auth**: Required
- **Returns**: `{ total: int, not_started: int, in_progress: int, completed: int }`

---

### Assignment Status System

#### Status Values

| Status        | Set By        | Description                                            |
| ------------- | ------------- | ------------------------------------------------------ |
| `not_started` | Canvas Sync   | Assignment is unsubmitted in Canvas                    |
| `completed`   | Canvas Sync   | Student submitted to Canvas (includes pending grading) |
| `in_progress` | **User Only** | Manually set by user, preserved during sync            |

#### Canvas Workflow State Mapping

Canvas provides these workflow states for submissions:

- `unsubmitted` → Maps to `not_started`
- `submitted` → Maps to `completed`
- `pending_review` → Maps to `completed` (student is done)
- `graded` → Maps to `completed`

**Key Rule**: If user marks assignment as `in_progress`, Canvas sync will **never** overwrite it, even if Canvas shows it as completed.

---

## Frontend Implementation

### Key Files

#### `/app/api/backend/[...path]/route.ts`

API proxy that:

1. Validates NextAuth session
2. Mints backend JWT
3. Forwards requests to FastAPI
4. Returns responses to client

#### `/app/test/page.tsx`

Test/demo page with full feature showcase:

- User profile management
- Canvas token configuration
- **Course selection UI** with checkboxes
- Assignment fetching
- Database sync
- Preferences management

### Course Selection UI Features

1. **Visual Selection**

   - Checkboxes for each course
   - Selected courses highlighted with blue border
   - Click anywhere on course card to toggle

2. **"Tracked" Badge**

   - Shows which courses are currently tracked
   - Blue badge on tracked courses

3. **Save Button**

   - Shows count of selected courses
   - Disabled when no courses selected
   - Updates tracking on click

4. **Smart State Management**
   - Auto-selects previously tracked courses
   - Persists selection across page refreshes
   - Updates immediately after saving

---

## Security Features

### Authentication

- ✅ Bcrypt password hashing (12 rounds)
- ✅ HTTP-only session cookies
- ✅ JWT with expiration (15 min for backend)
- ✅ Issuer/audience validation on JWTs

### API Security

- ✅ All user endpoints require authentication
- ✅ User data isolated by user_id
- ✅ Canvas tokens stored securely
- ✅ No direct database exposure to frontend

### CORS Configuration

- Allowed origins: `http://localhost:3000`, `http://127.0.0.1:3000`
- Credentials: Enabled
- Methods: All
- Headers: All

---

## Environment Variables

### Frontend (`.env.local`)

```bash
MONGODB_URI=mongodb+srv://...
DB_NAME=campusmind
NEXTAUTH_URL=http://localhost:3000/
NEXTAUTH_SECRET=<secret>
FASTAPI_INTERNAL_URL=http://localhost:8000
BACKEND_JWT_SECRET=<shared-secret>
```

### Backend (`.env`)

```bash
MONGODB_URI=mongodb+srv://...
DB_NAME=campusmind
BACKEND_JWT_SECRET=<shared-secret>
```

**Important**: `BACKEND_JWT_SECRET` must match between frontend and backend!

---

## User Flow Examples

### First-Time User Setup

1. **Sign Up**

   ```
   POST /api/signup
   → User created in campusmind.users
   ```

2. **Login**

   ```
   POST /api/auth/signin
   → NextAuth session created
   → Redirected to dashboard
   ```

3. **Complete Profile**

   ```
   PUT /api/backend/user/profile
   → Add name, university
   ```

4. **Add Canvas Token**

   ```
   POST /api/backend/canvas/token
   → Save Canvas PAT
   ```

5. **Select Courses**

   ```
   GET /api/backend/canvas/courses
   → Shows ALL courses

   User selects courses A, B, C

   PUT /api/backend/canvas/courses/track
   → Saves tracked courses
   ```

6. **Sync to Database**

   ```
   POST /api/backend/canvas/sync
   → Syncs courses A, B, C and their assignments to DB
   → Fetches submission status from Canvas automatically
   ```

7. **View & Manage Assignments**

   ```
   GET /api/backend/assignments
   → Shows synced assignments sorted by due date

   PUT /api/backend/assignments/{id}/status
   → Mark assignment as in_progress or completed
   → { "status": "in_progress" }
   ```

### Daily Usage Flow

1. User logs in (session restored)
2. Dashboard shows tracked courses only
3. View assignments: `GET /assignments`
4. Mark assignment as in progress: `PUT /assignments/{id}/status`
5. Periodic sync updates from Canvas (preserves in_progress status)

### Assignment Management Flow

**Typical workflow**:

```
1. User syncs from Canvas → POST /canvas/sync
2. View all assignments → GET /assignments?status=not_started
3. Start working on assignment → PUT /assignments/{id}/status {"status": "in_progress"}
4. Check upcoming assignments → GET /assignments?due_before=2025-01-15
5. Sync again from Canvas → POST /canvas/sync (preserves in_progress!)
6. Complete assignment in Canvas (submit)
7. Sync again → POST /canvas/sync (Canvas updates to completed)
```

---

## Error Handling

### Common Issues & Solutions

#### 404 Errors

- **Cause**: Double slash in URLs (e.g., `//user/profile`)
- **Fix**: Ensure `FASTAPI_INTERNAL_URL` has no trailing slash

#### 500 Errors on Profile

- **Cause**: User exists in multiple databases (test vs campusmind)
- **Fix**: NextAuth now uses `campusmind` database explicitly

#### Duplicate Key Error

- **Cause**: Trying to create user that already exists
- **Fix**: Backend now checks email first before creating

#### Invalid Token

- **Cause**: JWT secrets don't match or token expired
- **Fix**: Verify `BACKEND_JWT_SECRET` matches in both .env files

---

## Current Limitations & Future Enhancements

### Current Limitations

- Canvas token stored in plaintext (should encrypt)
- No course auto-refresh (manual fetch required)
- Assignment status changes don't sync back to Canvas
- No AI features implemented yet

### Implemented Features

- ✅ Canvas LMS integration with OAuth token
- ✅ Course tracking system (select which courses to track)
- ✅ Assignment sync from Canvas with submission status
- ✅ Smart assignment status management (preserves user's in_progress state)
- ✅ User preferences for study scheduling
- ✅ MongoDB database for data persistence

### Calendar System

#### Collections

**`calendar_events`**

```javascript
{
  _id: ObjectId,
  user_id: string (references users._id),
  title: string,
  description: string,
  start_time: datetime,
  end_time: datetime,
  location: string,
  event_type: string,  // "personal", "academic", "social", "wellness", "other"
  priority: string,    // "low", "medium", "high"
  is_recurring: boolean,
  recurrence_pattern: string,  // iCal RRULE format
  color: string,       // Hex color code
  notifications: [int], // Minutes before event
  created_at: datetime,
  updated_at: datetime
}
```

#### Calendar API Endpoints

**`POST /calendar/events`**
Create a single calendar event.

- **Auth**: Required
- **Body**: Event details with title, times, location, etc.
- **Returns**: Created event with ID

**`GET /calendar/events`**
Get calendar events with optional filters.

- **Auth**: Required
- **Query Params**:
  - `start_date` - Filter events starting from this date
  - `end_date` - Filter events until this date
  - `event_type` - Filter by event type
- **Returns**: Events list with total count

**`GET /calendar/events/{event_id}`**
Get specific event details.

- **Auth**: Required
- **Returns**: Event details

**`PUT /calendar/events/{event_id}`**
Update an existing event.

- **Auth**: Required
- **Body**: Fields to update
- **Returns**: Updated event

**`DELETE /calendar/events/{event_id}`**
Delete an event.

- **Auth**: Required
- **Returns**: 204 No Content

**`GET /calendar/events/upcoming`**
Get upcoming events for next X days.

- **Auth**: Required
- **Query Params**:
  - `days` - Number of days to look ahead (default: 7)
  - `limit` - Maximum events to return (default: 10)
- **Returns**: List of upcoming events

**`POST /calendar/classes`**
Bulk create recurring class events for an entire term.

- **Auth**: Required
- **Body**:
  ```javascript
  {
    "title": "Class Name",
    "description": "Class description",
    "location": "Room number",
    "days_of_week": ["monday", "wednesday"],
    "start_time": "14:00",
    "end_time": "15:30",
    "term_start_date": "2025-08-25T00:00:00Z",
    "term_end_date": "2025-12-10T00:00:00Z",
    "notifications": [15, 30],
    "priority": "high",
    "color": "#4285F4"
  }
  ```
- **Returns**: `{ success: true, message: string, events_created: int }`
- **Behavior**:
  - Automatically generates individual events for each class session
  - Handles recurring patterns based on days of week
  - Creates events only within the term date range

For complete documentation, see `backend/docs/calendar_api.md`.

### Planned Features

- AI study schedule generation
- Assignment priority recommendations
- Wellness check-ins
- Notification system
- Study session timer
- Two-way Canvas sync (update Canvas from app)

---

## Development Commands

### Start Backend

```bash
cd backend
python main.py
# or
uvicorn main:app --reload
```

### Start Frontend

```bash
cd frontend
npm run dev
```

### Access Points

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Test Page: http://localhost:3000/test

---

## Database Indexes

### Created Automatically

- `users.email` - Unique index for authentication
- Future: Will add indexes for performance as needed

---

## Testing

### Manual Testing via Test Page

1. Navigate to `/test`
2. Test each section:
   - User Profile CRUD
   - Canvas Token Management
   - Course Fetching & Selection
   - Assignment Retrieval
   - Database Sync
   - Preferences Management

### API Testing via Swagger

1. Navigate to `http://localhost:8000/docs`
2. Use "Authorize" button to add Bearer token
3. Test endpoints directly

---

## Troubleshooting

### Backend won't start

- Check MongoDB connection string
- Verify `.env` file exists
- Ensure port 8000 is available

### Frontend auth issues

- Clear browser cookies
- Check `NEXTAUTH_SECRET` is set
- Verify MongoDB connection

### Canvas integration fails

- Verify Canvas token is valid
- Check Canvas base URL is correct
- Ensure Canvas token has required permissions

### Course tracking not working

- Restart backend after code changes
- Check browser console for errors
- Verify tracked_course_ids saved in database

### Assignment status not updating

- Make sure to run POST /canvas/sync to sync from Canvas
- Use PUT /assignments/{id}/status to manually change status
- "in_progress" status is preserved during sync (by design)
- Check MongoDB `assignments` collection for actual status values

---

## Contributing

When adding new features:

1. Add API endpoint in backend (`/app/routers/`)
2. Define Pydantic schemas (`/app/models/schemas.py`)
3. Add frontend API call (`/app/test/page.tsx` or new component)
4. Test end-to-end flow
5. Update this documentation

---

_Last Updated: 2025-01-11_
