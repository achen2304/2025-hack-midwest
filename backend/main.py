"""
CampusMind FastAPI Application
AI-powered academic and wellness assistant for college students
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from app.routers import ingest, journal, plan, canvas, actions, calendar, sync, auth

# Import database manager
from app.util.db import db_manager

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

# Include routers
app.include_router(auth.router)  # Auth endpoints (no auth required)
app.include_router(ingest.router)
app.include_router(journal.router)
app.include_router(plan.router)
app.include_router(canvas.router)
app.include_router(calendar.router)
app.include_router(sync.router)
app.include_router(actions.router)

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
        db = db_manager.get_database()
        await db.command("ping")
        
        return {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
