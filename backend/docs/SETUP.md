# CampusMind Backend Setup Guide

Complete setup guide for the CampusMind AI-powered academic assistant backend.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Environment Setup](#environment-setup)
3. [Dependencies Installation](#dependencies-installation)
4. [MongoDB Atlas Setup](#mongodb-atlas-setup)
5. [Vector Search Setup](#vector-search-setup)
6. [Running the Application](#running-the-application)
7. [Testing Endpoints](#testing-endpoints)
8. [Architecture Overview](#architecture-overview)

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment variables
cp .env.example .env
# Edit .env with your credentials

# 3. Create MongoDB Atlas vector search index (see vector_search_setup.md)

# 4. Run the server
python main.py
# OR
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Environment Setup

### Required Environment Variables

Create a `.env` file in the backend directory:

```bash
# MongoDB Atlas
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/campusmind?retryWrites=true&w=majority

# AWS Credentials (for Strands AI SDK & Bedrock)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-west-2

# OpenAI (for embeddings)
OPENAI_API_KEY=sk-your_openai_api_key

# Auth0 or JWT Configuration
AUTH0_DOMAIN=your-auth0-domain.auth0.com
AUTH0_API_AUDIENCE=https://api.campusmind.com
AUTH0_ISSUER=https://your-auth0-domain.auth0.com/

# Optional: Canvas LMS
CANVAS_BASE_URL=https://canvas.instructure.com
```

### Alternative: Use AWS Bedrock for Embeddings

If you prefer using AWS Bedrock Titan embeddings instead of OpenAI:

1. Remove or comment out `OPENAI_API_KEY`
2. Update `app/util/embed.py` to use AWS Bedrock Titan
3. Change vector index dimensions from 1536 to 1024

---

## Dependencies Installation

### Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### Key Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework |
| `motor` | Async MongoDB driver |
| `pymupdf` | PDF text extraction |
| `python-pptx` | PowerPoint text extraction |
| `httpx` | Async HTTP client |
| `boto3` | AWS SDK (for Strands AI) |
| `numpy` | Vector operations |
| `pyjwt` | JWT authentication |

---

## MongoDB Atlas Setup

### 1. Create MongoDB Atlas Cluster

1. Sign up at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster (M10 or higher for vector search)
3. Create a database user with read/write permissions
4. Whitelist your IP address (or use 0.0.0.0/0 for development)
5. Get your connection string

### 2. Database Structure

The application will automatically create these collections on startup:

- `users` - User profiles and preferences
- `canvas_courses` - Canvas LMS course data
- `assignments` - Assignment tracking
- `calendar_events` - Calendar events and AI-generated schedule blocks
- `health_checkins` - Wellness check-ins with feeling levels
- `study_sessions` - Study session tracking
- `documents` - Uploaded course materials (PDFs, PPTXs)
- `document_chunks` - Vectorized document chunks for RAG
- `user_preferences` - User scheduling preferences

### 3. Indexes

Recommended indexes for performance:

```javascript
// users collection
db.users.createIndex({ "email": 1 }, { unique: true })

// assignments collection
db.assignments.createIndex({ "user_id": 1, "due_date": 1 })
db.assignments.createIndex({ "user_id": 1, "status": 1 })

// calendar_events collection
db.calendar_events.createIndex({ "user_id": 1, "start_time": 1 })
db.calendar_events.createIndex({ "user_id": 1, "source": 1, "start_time": 1 })

// health_checkins collection
db.health_checkins.createIndex({ "user_id": 1, "created_at": -1 })

// documents collection
db.documents.createIndex({ "user_id": 1, "course_id": 1 })

// document_chunks collection (CRITICAL for vector search)
db.document_chunks.createIndex({ "user_id": 1, "document_id": 1 })
db.document_chunks.createIndex({ "user_id": 1, "course_id": 1 })
```

---

## Vector Search Setup

**CRITICAL**: Vector search is required for document RAG functionality.

### Create Vector Search Index

See [`vector_search_setup.md`](./vector_search_setup.md) for complete instructions.

**Quick setup:**

1. Go to MongoDB Atlas → Search → Create Search Index
2. Choose JSON Editor
3. Use this configuration:

```json
{
  "name": "vector_search_index",
  "type": "vectorSearch",
  "definition": {
    "fields": [
      {
        "type": "vector",
        "path": "embedding",
        "numDimensions": 1536,
        "similarity": "cosine"
      },
      {
        "type": "filter",
        "path": "user_id"
      },
      {
        "type": "filter",
        "path": "course_id"
      }
    ]
  }
}
```

4. Select database: `campusmind`, collection: `document_chunks`
5. Wait for index to build (usually 1-5 minutes)

**IMPORTANT**: The `user_id` filter is **mandatory** for security. It ensures users can only search their own documents.

---

## Running the Application

### Development Mode

```bash
# Start with auto-reload (recommended for development)
python main.py

# OR with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Use multiple workers for better performance
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Optional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Testing Endpoints

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

### 2. Protected Route (Authentication Test)

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/protected
```

### 3. Upload Document

```bash
curl -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@lecture_notes.pdf" \
  -F "course_id=CS101" \
  -F "document_type=lecture_notes"
```

### 4. Search Documents (Vector Search)

```bash
curl -X POST http://localhost:8000/documents/search \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is recursion?",
    "course_id": "CS101",
    "limit": 5
  }'
```

### 5. Health Check-In (Wellness Tracking)

```bash
curl -X POST http://localhost:8000/health/checkin \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Feeling stressed about the upcoming midterm",
    "current_course_id": "CS101",
    "feeling_level": 4
  }'
```

### 6. Generate AI Schedule

```bash
curl -X POST http://localhost:8000/schedule/generate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prioritize_courses": ["CS101", "MATH201"],
    "regenerate": true
  }'
```

### 7. Start Chat with Study Assistant ✨ NEW

```bash
curl -X POST http://localhost:8000/chat/sessions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": "CS101",
    "initial_message": "What is recursion?"
  }'
```

### 8. Ask Follow-Up Question ✨ NEW

```bash
curl -X POST http://localhost:8000/chat/sessions/SESSION_ID/messages \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you give me an example?"
  }'
```

---

## Architecture Overview

### AI Agents System

The backend implements four specialized AI agents using **AWS Strands SDK**:

#### 1. **Health Check Agent** (`app/agents/health_check.py`)
- Monitors student wellness and stress levels
- Analyzes sentiment from check-ins
- Tracks feeling levels (1-5 scale) for each course
- Adjusts check-in frequency based on wellness state
- **Endpoints**: `/health/checkin`, `/health/checkins`, `/health/course-feelings/{course_id}`

#### 2. **Schedule Maker Agent** (`app/agents/schedule_maker.py`)
- Generates AI-powered study schedules
- Implements Read-Wipe-Write workflow
- Respects locked events and user preferences
- Creates study blocks and break periods
- Adapts to wellness state (stressed users get lighter schedules)
- **Endpoints**: `/schedule/generate`, `/schedule/ai-blocks`, `/schedule/ai-blocks/clear`

#### 3. **Study Planner Agent** (`app/agents/study_planner.py`)
- Creates personalized study guides
- Uses RAG (Retrieval-Augmented Generation) with user's documents
- Generates study plans based on assignments and exams
- Provides topic breakdowns and study strategies
- **Usage**: Called by Schedule Maker Agent

#### 4. **Vector Agent** (`app/agents/vector_agent.py`)
- Provides semantic search over user documents
- **CRITICAL**: Enforces user isolation (users can ONLY access their own documents)
- Performs vector similarity search using MongoDB Atlas
- Used by Study Planner for RAG context
- **Usage**: Called by other agents and `/documents/search` endpoint

### Document Processing Pipeline

**Flow**: Upload → Extract → Chunk → Embed → Store → Search

1. **Upload** (`POST /documents/upload`)
   - User uploads PDF or PPTX
   - Validates file type and size (max 50MB)
   - Authenticates user via JWT

2. **Extract** (`app/services/document_processor.py`)
   - PDF: Uses PyMuPDF (fitz) to extract text
   - PPTX: Uses python-pptx to extract text from slides
   - Preserves page/slide numbers

3. **Chunk** (`app/services/chunking_service.py`)
   - Splits text into 512-token chunks with 50-token overlap
   - Uses recursive splitting (paragraphs → sentences → words)
   - Preserves context across chunks

4. **Embed** (`app/util/embed.py`)
   - Generates 1536-dimension embeddings using OpenAI text-embedding-ada-002
   - Alternative: AWS Bedrock Titan (1024 dimensions)

5. **Store** (MongoDB Atlas)
   - Stores document record in `documents` collection
   - Stores chunks with embeddings in `document_chunks` collection
   - **CRITICAL**: Always tags with `user_id` for isolation

6. **Search** (`POST /documents/search`)
   - Generates query embedding
   - Performs vector similarity search using MongoDB `$vectorSearch`
   - **CRITICAL**: Always filters by `user_id` (prevents data leakage)
   - Returns top K most relevant chunks

### Security Model

**User Isolation**: EVERY query is filtered by `user_id` from JWT token.

```python
# CORRECT ✅
match_filter = {"user_id": user_id}  # ALWAYS filter by user_id
pipeline = [
    {"$vectorSearch": {...}},
    {"$match": match_filter}  # User isolation
]

# WRONG ❌ - DATA LEAKAGE!
match_filter = {}  # No user filter - returns ALL users' data!
```

This pattern is enforced in:
- `app/routers/documents.py` - All document endpoints
- `app/agents/vector_agent.py` - Vector search methods
- All other data access layers

### Canvas LMS Integration

- Sync courses: `POST /canvas/sync`
- Track courses: `POST /canvas/track-courses`
- Sync assignments: `POST /canvas/sync-assignments`
- Get assignments: `GET /assignments?weeks=6`

**Note**: Assignments default to next 6 weeks (configurable via `weeks` parameter).

---

## API Documentation

Once running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Interactive API documentation is automatically generated by FastAPI.

---

## Troubleshooting

### Common Issues

#### 1. MongoDB Connection Failed

**Error**: `Failed to connect to database`

**Solution**:
- Check `MONGODB_URI` in `.env`
- Verify IP whitelist in MongoDB Atlas
- Ensure database user has correct permissions

#### 2. Vector Search Returns No Results

**Possible causes**:
- Vector search index not created or not active
- No documents uploaded yet
- Wrong user_id filter

**Solution**:
- Check index status in MongoDB Atlas (Search tab)
- Upload some documents first
- Verify user authentication

#### 3. OpenAI API Key Error

**Error**: `OpenAI API error: 401`

**Solution**:
- Check `OPENAI_API_KEY` in `.env`
- Verify API key is valid and has credits
- Alternative: Use AWS Bedrock Titan embeddings

#### 4. Import Error: "No module named 'fitz'"

**Solution**:
```bash
pip install pymupdf
```

#### 5. AWS Strands SDK Not Found

**Solution**:
- Verify AWS credentials are correct
- Check if Strands SDK is installed
- May need to install from specific source (not PyPI)

---

## Next Steps

1. **Create MongoDB Atlas vector search index** (see `vector_search_setup.md`)
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Configure `.env`** with your credentials
4. **Run the application**: `python main.py`
5. **Test endpoints** using the provided curl commands
6. **Integrate with frontend** at http://localhost:3000

For detailed information:
- **AI Agents**: See [`ai_agents.md`](./ai_agents.md)
- **Vector Search**: See [`vector_search_setup.md`](./vector_search_setup.md)

---

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the comprehensive documentation in `/docs`
- Verify all environment variables are set correctly

---

**Last Updated**: January 2025
