# AI Agents Documentation

CampusMind uses AI agents powered by **AWS Strands SDK** to provide intelligent academic and wellness support for students.

## Table of Contents

- [Overview](#overview)
- [Agent Architecture](#agent-architecture)
- [Individual Agents](#individual-agents)
  - [Health Check Agent](#health-check-agent)
  - [Schedule Maker Agent](#schedule-maker-agent)
  - [Study Planner Agent](#study-planner-agent)
  - [Vector Agent](#vector-agent)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Data Flow Examples](#data-flow-examples)
- [Development Guide](#development-guide)

---

## Overview

The AI agent system provides four specialized agents that work together to support students:

| Agent                    | Purpose                                                             | Status                       |
| ------------------------ | ------------------------------------------------------------------- | ---------------------------- |
| **Health Check Agent**   | Monitors wellness, analyzes sentiment, adjusts check-in frequency   | ✅ Active                    |
| **Schedule Maker Agent** | Generates optimal study schedules based on assignments and wellness | ✅ Active                    |
| **Study Planner Agent**  | Creates personalized study guides using RAG                         | 🚧 Requires course materials |
| **Vector Agent**         | Provides contextual data via MongoDB vector search                  | 🚧 Requires vector index     |

---

## Agent Architecture

### Technology Stack

- **Strands SDK**: AI agent framework with AWS Bedrock integration
- **AWS Bedrock**: Hosts the underlying LLM
- **MongoDB Atlas**: Stores user data, check-ins, and schedules
- **FastAPI**: Async Python backend framework

### File Structure

```
app/
├── agents/
│   ├── __init__.py           # Exports all agents
│   ├── health_check.py       # HealthCheckAgent
│   ├── schedule_maker.py     # ScheduleMakerAgent
│   ├── study_planner.py      # StudyPlannerAgent
│   └── vector_agent.py       # VectorAgent
├── routers/
│   ├── health.py            # Health & wellness endpoints
│   └── schedule.py          # Schedule generation endpoints
└── models/
    └── schemas.py           # Pydantic models
```

### Agent Initialization

Agents are initialized as **singletons** when first accessed:

```python
# In app/agents/health_check.py
_health_check_agent = None

def get_health_check_agent() -> HealthCheckAgent:
    global _health_check_agent
    if _health_check_agent is None:
        _health_check_agent = HealthCheckAgent()
    return _health_check_agent
```

This ensures only one instance exists per agent, reducing overhead.

---

## Individual Agents

### Health Check Agent

**File**: `app/agents/health_check.py`

**Purpose**: Monitors student emotional well-being and provides adaptive wellness support.

#### Capabilities

- Analyzes sentiment from student messages
- Detects stress indicators: "overwhelmed", "anxious", "tired", "can't focus"
- Detects positive indicators: "good", "confident", "ready", "motivated"
- Adjusts check-in frequency based on wellness state
- Tracks feelings per course (1-5 scale)

#### Sentiment Analysis

```python
agent = get_health_check_agent()
analysis = await agent.analyze_checkin(
    user_message="I'm really struggling with calculus derivatives",
    current_course="Calculus II",
    recent_feelings=[{"feeling_level": 4, "recorded_at": "..."}]
)

# Returns:
{
    "sentiment": "stressed",
    "next_checkin_minutes": 30,
    "suggestions": "Take a short break and try working through example problems step by step.",
    "needs_break": False
}
```

#### Check-in Frequency Rules

| Sentiment        | Next Check-in               |
| ---------------- | --------------------------- |
| Positive/Neutral | 60-120 minutes              |
| Negative         | 45 minutes                  |
| Stressed         | 30 minutes                  |
| Overwhelmed      | Immediate break recommended |

#### Database Storage

Data stored in `health_checkins` collection:

```javascript
{
  _id: ObjectId,
  user_id: string,
  message: string,
  sentiment: string,  // "positive", "neutral", "negative", "stressed", "overwhelmed"
  current_study_context: string,  // Course name
  course_feelings: [
    {
      course_id: string,
      course_name: string,
      feeling_level: int,  // 1-5 (1=great, 5=overwhelmed)
      recorded_at: datetime
    }
  ],
  next_checkin_minutes: int,
  needs_break: boolean,
  ai_suggestions: string,
  created_at: datetime
}
```

---

### Schedule Maker Agent

**File**: `app/agents/schedule_maker.py`

**Purpose**: Generates AI-powered study schedules that adapt to student needs and wellness state.

#### Capabilities

- Creates study blocks for assignments based on deadlines
- Respects locked events (classes, exams, personal appointments)
- Adds breaks between study sessions
- Includes travel time buffers
- Prioritizes specified courses
- Adapts to wellness state (more breaks if stressed)

#### Scheduling Algorithm

The agent follows the **Read-Wipe-Write** workflow:

1. **Read "Pillars"**: Fetch all fixed events (classes, exams, locked events)
2. **Wipe AI Blocks**: Delete all previous AI-generated `STUDY_BLOCK` and `BREAK` events
3. **Plan with Priority**: Allocate more study time to prioritized courses
4. **Write Schedule**: Insert new schedule blocks into database

#### Usage Example

```python
agent = get_schedule_maker_agent()
result = await agent.generate_schedule(
    assignments=[
        {
            "id": "123",
            "title": "Math Homework",
            "course_id": "calc_101",
            "due_date": "2025-01-20T23:59:00Z",
            "status": "not_started"
        }
    ],
    existing_events=[...],  # Classes, exams, locked events
    user_preferences={
        "study_block_duration": 60,  # minutes
        "break_duration": 15,
        "travel_duration": 10,
        "recurring_blocked_times": [
            {"day_of_week": "monday", "start": "12:00", "end": "13:00"}
        ]
    },
    prioritize_courses=["calc_101"],
    wellness_state="stressed"  # "normal", "good", "stressed"
)

# Returns:
{
    "success": True,
    "schedule": [
        {
            "type": "STUDY_BLOCK",
            "title": "Study: Math Homework",
            "course_id": "calc_101",
            "assignment_id": "123",
            "start_time": "2025-01-15T14:00:00Z",
            "end_time": "2025-01-15T15:00:00Z",
            "is_locked": False
        },
        {
            "type": "BREAK",
            "title": "Break",
            "start_time": "2025-01-15T15:00:00Z",
            "end_time": "2025-01-15T15:15:00Z",
            "is_locked": False
        }
    ],
    "message": "Generated 2 schedule blocks"
}
```

#### Scheduling Rules

- **Study blocks**: Use user's preferred duration (default 60 min)
- **Breaks**: Use user's preferred duration (default 15 min)
- **Travel buffers**: Use user's preferred duration (default 10 min)
- **Never schedule over locked events**
- **Schedule intensive sessions early in the day**
- **Leave evenings lighter if student is stressed**

#### Database Storage

AI-generated events stored in `calendar_events` collection:

```javascript
{
  _id: ObjectId,
  user_id: string,
  title: string,
  start_time: datetime,
  end_time: datetime,
  event_type: "other",  // AI-generated blocks use "other" type
  source: "CAMPUSMIND_AI",  // Identifies AI-generated events
  ai_generated: true,
  block_type: string,  // "STUDY_BLOCK" or "BREAK"
  course_id: string,
  assignment_id: string,
  is_locked: boolean,  // User can lock to prevent rescheduling
  color: string,  // Green for study, blue for break
  created_at: datetime,
  updated_at: datetime
}
```

---

### Study Planner Agent

**File**: `app/agents/study_planner.py`

**Purpose**: Creates personalized study guides using Retrieval-Augmented Generation (RAG).

**Status**: 🚧 Requires course materials to be uploaded and indexed

#### Capabilities

- Analyzes uploaded course materials (notes, slides, readings)
- Uses vector search to find relevant content
- Generates comprehensive study guides for exams
- Breaks down topics into manageable sections
- Recommends time allocation and practice strategies

#### Future Usage

```python
from app.agents import create_study_planner_agent
from app.agents.vector_agent import create_vector_agent

vector_agent = create_vector_agent(db, embedding_service)
study_planner = create_study_planner_agent(vector_agent)

result = await study_planner.create_study_guide(
    exam_info={
        "title": "Midterm Exam",
        "course_name": "Calculus II",
        "date": "2025-02-15"
    },
    course_materials=[...]  # Retrieved from vector search
)
```

---

### Vector Agent

**File**: `app/agents/vector_agent.py`

**Purpose**: Provides contextual data to other agents via MongoDB Atlas Vector Search.

**Status**: 🚧 Requires MongoDB Atlas vector search index

#### Capabilities

- Performs semantic similarity searches on course materials
- Retrieves relevant documents based on queries
- Provides context to Study Planner Agent
- Helps prioritize topics based on content analysis

#### Future Usage

```python
from app.agents import create_vector_agent

vector_agent = create_vector_agent(db, embedding_service)

results = await vector_agent.search_documents(
    query="derivatives chain rule",
    user_id="user_123",
    course_id="calc_101",
    limit=5
)
```

---

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# AWS Credentials for Strands SDK
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-west-2

# MongoDB (for data storage)
MONGODB_URI=mongodb+srv://...
DB_NAME=campusmind
```

### AWS Bedrock Setup

The Strands SDK automatically connects to AWS Bedrock using your credentials. Ensure:

1. AWS credentials have Bedrock permissions
2. Bedrock is available in your region
3. You have access to the required model (Claude, etc.)

---

## API Endpoints

### Health & Wellness Endpoints

**Base URL**: `/health`

#### `POST /health/checkin`

Record a health check-in with feeling level for the current course.

**Request:**

```json
{
  "message": "I'm feeling stressed about calculus",
  "current_course_id": "calc_101",
  "feeling_level": 4
}
```

**Response:**

```json
{
  "id": "checkin_123",
  "user_id": "user_456",
  "message": "I'm feeling stressed about calculus",
  "sentiment": "stressed",
  "current_study_context": "Calculus II",
  "course_feelings": [
    {
      "course_id": "calc_101",
      "course_name": "Calculus II",
      "feeling_level": 4,
      "recorded_at": "2025-01-15T14:30:00Z"
    }
  ],
  "created_at": "2025-01-15T14:30:00Z",
  "next_checkin_minutes": 30
}
```

#### `GET /health/checkins`

Get check-in history.

**Query Parameters:**

- `limit` (int, default: 20)
- `course_id` (string, optional)

#### `GET /health/course-feelings/{course_id}`

Get feeling level trends for a specific course.

**Query Parameters:**

- `days` (int, default: 30)

**Response:**

```json
{
  "course_id": "calc_101",
  "feelings_count": 15,
  "average_feeling_level": 3.2,
  "trend": "improving",
  "feelings": [
    {
      "feeling_level": 4,
      "recorded_at": "2025-01-15T14:30:00Z",
      "sentiment": "stressed"
    }
  ]
}
```

#### `POST /health/study-session`

Start a new study session.

**Request:**

```json
{
  "course_id": "calc_101",
  "assignment_id": "assignment_123",
  "planned_duration": 60
}
```

#### `PUT /health/study-session/{session_id}`

End a study session with feelings.

**Request:**

```json
{
  "actual_duration": 45,
  "feeling_before": 3,
  "feeling_after": 2,
  "completed": true,
  "notes": "Made good progress on derivatives"
}
```

---

### Schedule Generation Endpoints

**Base URL**: `/schedule`

#### `POST /schedule/generate`

Generate an AI-powered study schedule.

**Request:**

```json
{
  "prioritize_courses": ["calc_101", "chem_201"],
  "start_date": "2025-01-15T00:00:00Z",
  "end_date": "2025-01-29T00:00:00Z",
  "regenerate": true
}
```

**Response:**

```json
{
  "success": true,
  "message": "Successfully generated schedule with 20 study blocks and 10 breaks",
  "study_blocks_created": 20,
  "break_blocks_created": 10
}
```

#### `GET /schedule/ai-blocks`

Get all AI-generated study blocks and breaks.

**Query Parameters:**

- `start_date` (datetime, optional)
- `end_date` (datetime, optional)

#### `DELETE /schedule/ai-blocks/clear`

Clear all AI-generated blocks in a date range.

#### `PUT /schedule/ai-blocks/{block_id}/lock`

Lock or unlock a block to prevent it from being rescheduled.

**Request:**

```json
{
  "lock": true
}
```

---

## Data Flow Examples

### Example 1: Student Check-in During Study Session

```
1. Student starts studying Calculus
   POST /health/study-session
   { course_id: "calc_101", planned_duration: 60 }

2. 30 minutes in, student feels stressed
   POST /health/checkin
   {
     message: "I don't understand derivatives",
     current_course_id: "calc_101",
     feeling_level: 4  // stressed
   }

   → Health Check Agent analyzes
   → Returns: sentiment="stressed", next_checkin=30min
   → Stored in MongoDB with course feeling data

3. Student ends session
   PUT /health/study-session/{id}
   {
     feeling_after: 3,  // slightly better
     actual_duration: 45,
     completed: true
   }
```

### Example 2: AI Schedule Generation

```
1. User has 3 assignments due next week
   - Math HW (due Monday)
   - Chemistry Lab (due Wednesday)
   - Essay (due Friday)

2. User requests schedule with priority on Math
   POST /schedule/generate
   {
     prioritize_courses: ["math_101"],
     start_date: "2025-01-13",
     end_date: "2025-01-20",
     regenerate: true
   }

3. Schedule Maker Agent:
   → Reads: All classes, exams, locked events
   → Wipes: Previous AI-generated blocks
   → Checks: Recent wellness state (finds "stressed" from health check)
   → Plans: More breaks, prioritizes Math
   → Writes: 15 study blocks + 8 breaks to database

4. User sees schedule in calendar
   → Can lock specific blocks
   → Can drag/drop to adjust
   → Regenerating respects locked blocks
```

### Example 3: Wellness State Influences Schedule

```
1. Student has been stressed (multiple check-ins with feeling_level 4-5)

2. When generating schedule:
   → Health Check Agent recorded: sentiment="stressed"
   → Schedule Maker Agent receives: wellness_state="stressed"
   → AI adjusts:
     - Shorter study blocks (45min instead of 60min)
     - More frequent breaks (every 45min instead of 60min)
     - Lighter evening schedule
     - No back-to-back study blocks

3. As student's wellness improves:
   → Future check-ins show: feeling_level 2-3
   → Next schedule generation uses: wellness_state="normal"
   → Longer study blocks returned
```

---

## Development Guide

### Adding a New Agent

1. **Create agent file** in `app/agents/new_agent.py`

```python
from strands import Agent

class NewAgent:
    def __init__(self):
        self.agent = Agent(
            name="NewAgent",
            system_prompt="Your agent's instructions here"
        )

    async def perform_task(self, input_data):
        prompt = f"Process this: {input_data}"
        response = await self.agent.run_async(prompt)
        return self._parse_response(response)

    def _parse_response(self, response):
        # Extract and parse agent response
        pass

# Singleton getter
_new_agent = None

def get_new_agent():
    global _new_agent
    if _new_agent is None:
        _new_agent = NewAgent()
    return _new_agent
```

2. **Export in `__init__.py`**

```python
from app.agents.new_agent import NewAgent, get_new_agent

__all__ = [..., "NewAgent", "get_new_agent"]
```

3. **Use in router**

```python
from app.agents import get_new_agent

@router.post("/endpoint")
async def endpoint(user=Depends(verify_backend_token)):
    agent = get_new_agent()
    result = await agent.perform_task(data)
    return result
```

### Testing Agents Locally

```python
# Test health check agent
from app.agents import get_health_check_agent

agent = get_health_check_agent()
result = await agent.analyze_checkin(
    user_message="I'm feeling great!",
    current_course="Math 101"
)
print(result)
```

### Debugging Agent Responses

Add logging to see raw AI responses:

```python
response = await self.agent.run_async(prompt)
print(f"Raw response: {response}")  # Debug output
result = self._parse_response(response)
```

---

## Future Enhancements

- [ ] **Agent-to-Agent Communication**: Health Check triggers schedule regeneration
- [ ] **Document Upload System**: Enable Study Planner with course materials
- [ ] **Vector Search Index**: Set up MongoDB Atlas vector search
- [ ] **Proactive Check-ins**: Schedule-based wellness monitoring
- [ ] **Learning Analytics**: Track which study strategies work best
- [ ] **Multi-modal Support**: Image/diagram analysis in study materials

---

## Troubleshooting

### Agent Not Responding

**Issue**: Agent calls timeout or return errors

**Solutions**:

1. Check AWS credentials are valid: `echo $AWS_ACCESS_KEY_ID`
2. Verify Bedrock access in AWS region
3. Check network connectivity to AWS
4. Review agent logs for error messages

### JSON Parsing Errors

**Issue**: Agent response cannot be parsed as JSON

**Solutions**:

1. Check agent's `system_prompt` includes "Respond in JSON format"
2. Add better JSON extraction in `_parse_response()`:
   ```python
   import re
   json_match = re.search(r'\{.*\}', content, re.DOTALL)
   if json_match:
       return json.loads(json_match.group())
   ```
3. Add fallback responses for unparseable content

### Wellness State Not Updating

**Issue**: Schedule doesn't reflect recent check-ins

**Solutions**:

1. Verify check-ins are being stored: query `health_checkins` collection
2. Check sentiment analysis is working correctly
3. Ensure schedule generation reads most recent check-in:
   ```python
   recent_checkin = await db.health_checkins.find_one(
       {"user_id": user_id},
       sort=[("created_at", -1)]
   )
   ```

---

**Last Updated**: January 2025
