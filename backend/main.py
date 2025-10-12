"""
CampusMind FastAPI Application - Simplified Auth/User Setup
Basic user authentication and management API
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from app.util.db import get_database

# Load environment variables
load_dotenv()

# Import database manager
from app.util.db import db_manager

# Import auth utilities
from app.util.auth import verify_backend_token

# Import routers
from app.routers import user, canvas, assignments, calendar, documents, health, schedule, chat, assignments_vector_simple

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting CampusMind API...")
    try:
        await db_manager.connect()
        await db_manager.create_collections()
        print("Database connection established")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        raise

    yield

    # Shutdown
    print("Shutting down CampusMind API...")
    await db_manager.disconnect()

# Create FastAPI application
app = FastAPI(
    title="CampusMind API",
    description="AI-powered academic and wellness assistant for college students",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to CampusMind API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db_status = "not connected"
        if db_manager.client is not None:
            try:
                await db_manager.client.admin.command("ping")
                db_status = "connected"
            except:
                db_status = "error"

        return {
            "status": "healthy",
            "database": db_status,
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


import asyncio
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorClient
from pymongo.operations import SearchIndexModel

INDEX_NAME = "assignments_vs"
NUM_DIMS = 384  # MiniLM-L6-v2
@app.get("/protected")
async def protected_route(user=Depends(verify_backend_token), db=Depends(get_database)):

    MONGODB_URI = os.getenv("MONGODB_URI")
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client["campusmind"]
    collection = db["assignments"]
    model = SearchIndexModel(
        definition={
            "fields": [
                {"type": "vector", "path": "embedding", "numDimensions": NUM_DIMS, "similarity": "cosine"},
                {"type": "filter", "path": "user_id"},
                {"type": "filter", "path": "course_id"},
                {"type": "filter", "path": "status"},
                {"type": "filter", "path": "due_date"},
            ]
        },
        name=INDEX_NAME,
        type="vectorSearch",
    )

    # CREATE (await!)
    name = await collection.create_search_index(model=model)
    print(f"New vector index named '{name}' is building.")

    # POLL (await async cursor)
    print("Polling to check if the index is ready (up to ~1–2 minutes).")
    while True:
        cursor = collection.list_search_indexes(name)     # async cursor
        indexes = await cursor.to_list(length=None)       # ✅ await
        if indexes and indexes[0].get("queryable") is True:
            break
        await asyncio.sleep(5)

    print(f"'{name}' is ready for querying.")

    
    return {
        "ok": True,
        "sub": user.get("sub"),
        "email": user.get("email"),
        "name": user.get("name"),
    }

# Include routers
app.include_router(user.router)
app.include_router(canvas.router)
app.include_router(assignments.router)
app.include_router(calendar.router)
app.include_router(documents.router)
app.include_router(health.router)
app.include_router(schedule.router)
app.include_router(chat.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )