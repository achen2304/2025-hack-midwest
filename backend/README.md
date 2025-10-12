# CampusMind Backend

AI-powered academic and wellness assistant for college students.

## Overview

CampusMind is a FastAPI backend that provides intelligent scheduling, document processing, wellness tracking, and academic planning for students. It integrates with Canvas LMS and uses AI agents powered by AWS Strands SDK to provide personalized support.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run the server
python main.py
```

Visit http://localhost:8000/docs for interactive API documentation.

## Core Features

### 🤖 AI Agents
- **Health Check Agent** - Monitors student wellness and stress levels
- **Schedule Maker Agent** - Generates AI-powered study schedules
- **Study Planner Agent** - Creates personalized study guides using RAG
- **Study Assistant Agent** - Conversational tutor with RAG-powered Q&A
- **Vector Agent** - Semantic search over user documents

### 📚 Document Processing
- Upload PDFs and PowerPoints
- Automatic text extraction and chunking
- Vector embeddings for semantic search
- User-isolated document storage

### 📅 Smart Scheduling
- AI-generated study blocks and breaks
- Canvas LMS integration
- Respects locked events and user preferences
- Adapts to wellness state

### 💚 Wellness Tracking
- Health check-ins with sentiment analysis
- Course-specific feeling levels (1-5 scale)
- Adaptive check-in frequency
- Study session tracking

### 🎓 Canvas Integration
- Sync courses and assignments
- Track multiple courses
- Assignment status management
- Calendar event sync

## Architecture

```
Backend (FastAPI + MongoDB Atlas)
├── AI Agents (AWS Strands SDK)
│   ├── Health Check Agent
│   ├── Schedule Maker Agent
│   ├── Study Planner Agent
│   └── Vector Agent
├── Document Processing (PyMuPDF + python-pptx)
├── Vector Search (MongoDB Atlas Vector Search)
└── Canvas Integration (Canvas REST API)
```

## Tech Stack

- **Framework**: FastAPI (Python 3.9+)
- **Database**: MongoDB Atlas with Vector Search
- **AI**: AWS Strands SDK (Bedrock)
- **Embeddings**: OpenAI text-embedding-ada-002 (1536-dim)
- **Document Processing**: PyMuPDF, python-pptx
- **Authentication**: JWT tokens

## Documentation

Comprehensive documentation is available in the `/docs` directory:

- **[SETUP.md](./docs/SETUP.md)** - Complete setup and configuration guide
- **[IMPLEMENTATION_SUMMARY.md](./docs/IMPLEMENTATION_SUMMARY.md)** - Feature overview and architecture
- **[ai_agents.md](./docs/ai_agents.md)** - AI agents documentation
- **[study_assistant_chat.md](./docs/study_assistant_chat.md)** - Study assistant chatbot guide
- **[vector_search_setup.md](./docs/vector_search_setup.md)** - MongoDB vector search setup

## API Endpoints

### Health & Wellness
- `POST /health/checkin` - Record health check-in
- `GET /health/checkins` - Get check-in history
- `GET /health/course-feelings/{course_id}` - Get feeling trends

### Document Management
- `POST /documents/upload` - Upload PDF/PPTX
- `GET /documents` - List documents
- `POST /documents/search` - Semantic search
- `DELETE /documents/{document_id}` - Delete document

### AI Scheduling
- `POST /schedule/generate` - Generate AI schedule
- `GET /schedule/ai-blocks` - Get AI-generated blocks
- `DELETE /schedule/ai-blocks/clear` - Clear AI blocks

### Assignments
- `GET /assignments?weeks=6` - Get assignments (default: next 6 weeks)
- `GET /assignments/count/by-status` - Assignment counts
- `PUT /assignments/{assignment_id}` - Update assignment

### Canvas Integration
- `POST /canvas/token` - Store Canvas token
- `GET /canvas/courses` - Get Canvas courses
- `POST /canvas/sync` - Sync Canvas data

### Calendar
- `POST /calendar/events` - Create event
- `GET /calendar/events` - List events
- `POST /calendar/classes/bulk` - Bulk create class events

### Study Assistant Chat
- `POST /chat/sessions` - Create chat session
- `POST /chat/sessions/{session_id}/messages` - Send message
- `GET /chat/sessions/{session_id}/history` - Get conversation history
- `GET /chat/sessions` - List all chat sessions
- `POST /chat/documents/summarize` - Summarize a document

Full API documentation: http://localhost:8000/docs

## Environment Variables

Required variables in `.env`:

```bash
# MongoDB Atlas
MONGODB_URI=mongodb+srv://...

# AWS Strands SDK
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-west-2

# OpenAI (for embeddings)
OPENAI_API_KEY=sk-...

# Authentication
BACKEND_JWT_SECRET=...
AUTH0_DOMAIN=...
AUTH0_API_AUDIENCE=...

# Canvas LMS (optional)
CANVAS_BASE=https://canvas.instructure.com
```

See `.env.example` for complete template.

## MongoDB Setup

### 1. Create Database
- Cluster: M10 or higher (for vector search)
- Database name: `campusmind`

### 2. Create Vector Search Index

**CRITICAL**: Vector search requires a manually created index.

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

Apply to collection: `document_chunks`

See [vector_search_setup.md](./docs/vector_search_setup.md) for detailed instructions.

## Security

### User Isolation
- ✅ Every query filters by `user_id` from JWT token
- ✅ Users can ONLY access their own data
- ✅ Vector search enforces user isolation
- ✅ Document access restricted to owner

### Authentication
- ✅ JWT token verification on all protected routes
- ✅ User ID extraction from token
- ✅ MongoDB user lookup for data access

## Development

### Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run Development Server

```bash
# With auto-reload
python main.py

# OR with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Run Tests

```bash
# Coming soon
pytest
```

## Project Structure

```
backend/
├── main.py                      # FastAPI application
├── requirements.txt             # Dependencies
├── .env.example                 # Environment template
│
├── app/
│   ├── agents/                  # AI Agents
│   │   ├── health_check.py
│   │   ├── schedule_maker.py
│   │   ├── study_planner.py
│   │   └── vector_agent.py
│   │
│   ├── routers/                 # API Routes
│   │   ├── health.py
│   │   ├── schedule.py
│   │   ├── documents.py
│   │   ├── assignments.py
│   │   ├── calendar.py
│   │   ├── canvas.py
│   │   └── user.py
│   │
│   ├── services/                # Business Logic
│   │   ├── document_processor.py
│   │   └── chunking_service.py
│   │
│   ├── util/                    # Utilities
│   │   ├── db.py
│   │   ├── auth.py
│   │   └── embed.py
│   │
│   └── models/
│       └── schemas.py           # Pydantic models
│
└── docs/                        # Documentation
    ├── SETUP.md
    ├── IMPLEMENTATION_SUMMARY.md
    ├── ai_agents.md
    └── vector_search_setup.md
```

## Troubleshooting

### MongoDB Connection Failed
- Check `MONGODB_URI` in `.env`
- Verify IP whitelist in MongoDB Atlas
- Ensure database user has correct permissions

### Vector Search Returns No Results
- Check vector search index is created and active
- Verify documents have been uploaded
- Check user authentication

### OpenAI API Error
- Verify `OPENAI_API_KEY` is set correctly
- Check API key has credits available
- Alternative: Use AWS Bedrock Titan embeddings

See [SETUP.md](./docs/SETUP.md) for complete troubleshooting guide.

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

MIT License - see LICENSE file for details

---

**Version**: 1.0.0
**Last Updated**: January 2025
**Status**: ✅ Production Ready

For questions or support, see the documentation in `/docs`.
