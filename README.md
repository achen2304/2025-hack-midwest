# CampusMind 🧠

**AI-powered academic and wellness assistant for college students**

CampusMind is a comprehensive full-stack application that leverages AI agents to provide personalized academic guidance and wellness support for college students. Built with FastAPI, Next.js, MongoDB Atlas with Vector Search, and the Strands Agents SDK.

## 🚀 Features

### Academic Support

- **AI Study Coach**: Personalized study planning and academic guidance
- **Assignment Tracker**: Canvas LMS integration for assignment management
- **Study Plans**: AI-generated study schedules based on courses and preferences
- **Performance Analytics**: Track academic progress and identify improvement areas

### Wellness & Mental Health

- **Wellness Companion**: AI-powered mental health support
- **Mood Tracking**: Track emotional patterns and get insights
- **Journal System**: Safe space for self-reflection and emotional expression
- **Wellness Activities**: Personalized suggestions for mental health maintenance

### Smart Context

- **Vector Search**: Semantic search through notes, assignments, and journal entries
- **Context Enrichment**: AI agents use historical data to provide better responses
- **Multi-modal Support**: Text, mood, and behavioral pattern analysis

## 🏗️ Architecture

```
CampusMind/
├── backend/          # FastAPI Python backend
├── frontend/         # Next.js 14 TypeScript frontend
├── infra/           # Infrastructure configuration
└── README.md
```

### Backend Architecture

- **FastAPI**: Modern Python web framework
- **MongoDB Atlas**: Database with vector search capabilities
- **Strands Agents SDK**: AI agent orchestration
- **Vector Embeddings**: OpenAI embeddings for semantic search

### Frontend Architecture

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Responsive Design**: Mobile-first approach

## 🛠️ Tech Stack

### Backend

- **FastAPI** - Web framework
- **MongoDB Atlas** - Database with vector search
- **Motor** - Async MongoDB driver
- **Strands Agents SDK** - AI agent framework
- **OpenAI API** - Embeddings generation
- **Pydantic** - Data validation

### Frontend

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **React Hook Form** - Form handling

### Infrastructure

- **MongoDB Atlas Vector Search** - Semantic search
- **Canvas LMS API** - Academic data integration
- **Postman** - API testing

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- MongoDB Atlas account
- OpenAI API key (optional, for embeddings)

### Backend Setup

1. **Navigate to backend directory**

   ```bash
   cd backend
   ```

2. **Create virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install fastapi uvicorn[standard] motor pymongo python-dotenv httpx numpy strands-agents-sdk
   ```

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB URI and other configurations
   ```

5. **Start the backend server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**

   ```bash
   cd frontend
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Start the development server**

   ```bash
   npm run dev
   ```

4. **Open your browser**
   ```
   http://localhost:3000
   ```

## 📊 API Documentation

Once the backend is running, visit:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Health Check

```
GET /health
```

#### Journal Management

```
POST /journal/entries          # Create journal entry
GET /journal/entries          # Get user's journal entries
GET /journal/mood-trends      # Get mood analytics
```

#### Study Plans

```
POST /plan/plans              # Create study plan
GET /plan/plans               # Get user's study plans
POST /plan/generate           # Generate AI study plan
```

#### AI Actions

```
POST /actions/academic        # Academic coaching
POST /actions/wellness        # Wellness support
```

#### Canvas Integration

```
GET /canvas/courses           # Get Canvas courses
GET /canvas/assignments       # Get Canvas assignments
POST /canvas/sync             # Sync Canvas data
POST /canvas/calendar/sync    # Sync Canvas calendar events
```

#### Calendar Management

```
POST /calendar/events         # Create individual calendar event
GET /calendar/events          # Get calendar events with filters
GET /calendar/events/{id}     # Get specific calendar event
PUT /calendar/events/{id}     # Update calendar event
DELETE /calendar/events/{id}  # Delete calendar event
POST /calendar/classes        # Bulk create recurring class events
GET /calendar/events/upcoming # Get upcoming events
```

## 🤖 AI Agents

### Academic Coach

- Analyzes study patterns
- Creates personalized study plans
- Provides academic improvement suggestions
- Integrates with Canvas LMS

### Wellness Companion

- Monitors mood patterns
- Suggests wellness activities
- Provides emotional support
- Tracks mental health trends

### Context Enricher

- Uses vector search to find relevant context
- Enriches agent responses with historical data
- Maintains user context across sessions

### Action Agent

- Executes specific actions (Canvas sync, notifications)
- Manages integrations with external services
- Handles calendar and communication tasks

## 🗄️ Database Schema

### Collections

- **users**: User profiles and preferences
- **journal_entries**: Mood tracking and reflections
- **assignments**: Academic assignments and deadlines
- **study_plans**: AI-generated study schedules
- **canvas_courses**: Canvas LMS course data
- **vector_embeddings**: Embeddings for semantic search

### Vector Search Indexes

- **notes_vector_search**: Semantic search for notes and journal entries
- **assignments_vector_search**: Semantic search for assignments and course content

## 🔧 Configuration

### Environment Variables

#### Backend (.env)

```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=campusmind
CANVAS_BASE=https://your-university.instructure.com
CANVAS_CLIENT_ID=your_canvas_client_id
CANVAS_CLIENT_SECRET=your_canvas_client_secret
CANVAS_REDIRECT_URI=http://localhost:8000/canvas/callback
OPENAI_API_KEY=your_openai_api_key
```

### MongoDB Atlas Setup

1. **Create a cluster** on MongoDB Atlas
2. **Create vector search indexes** using the configurations in `infra/atlas_indexes/`
3. **Configure network access** to allow connections from your application
4. **Create database user** with read/write permissions

## 🧪 Testing

### API Testing

Import the Postman collection from `infra/postman/smoke_tests.json` to test basic API functionality.

### Running Tests

```bash
# Backend tests (when implemented)
cd backend
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

## 🚀 Deployment

### Backend Deployment

1. **Set up production environment variables**
2. **Deploy to cloud platform** (Railway, Heroku, AWS, etc.)
3. **Configure MongoDB Atlas** for production
4. **Set up monitoring and logging**

### Frontend Deployment

1. **Build the application**
   ```bash
   npm run build
   ```
2. **Deploy to Vercel, Netlify, or similar platform**
3. **Configure environment variables** for production

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests** for new functionality
5. **Submit a pull request**

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Strands** for the Agents SDK
- **OpenAI** for embedding models
- **Canvas** for LMS integration
- **MongoDB** for vector search capabilities

## 📞 Support

For support and questions:

- Create an issue in the GitHub repository
- Contact the development team

---

**Built with ❤️ for college students everywhere**
