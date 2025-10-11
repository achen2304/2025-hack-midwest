"""
Authentication endpoints for CampusMind
DEV-ONLY: Provides test token generation when Clerk is not configured
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import jwt
import os
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["auth"])


class DevTokenRequest(BaseModel):
    user_id: str = "test_user_123"
    email: str = "test@campusmind.com"
    name: str = "Test User"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


@router.post("/dev-token", response_model=TokenResponse)
async def get_dev_token(request: DevTokenRequest):
    """
    🚨 DEV ONLY: Generate a test JWT token for Postman testing

    This endpoint only works when CLERK_SECRET_KEY is NOT set in .env
    Once you set up Clerk, this endpoint will be disabled.

    Usage:
    1. POST to /auth/dev-token with optional user details
    2. Copy the access_token from response
    3. Use in Postman: Authorization → Bearer Token
    """
    # Only allow in dev mode (no Clerk configured)
    if os.getenv("CLERK_SECRET_KEY"):
        raise HTTPException(
            status_code=403,
            detail="Dev token endpoint is disabled when Clerk is configured. Use Clerk authentication instead."
        )

    # Generate a simple JWT token for testing
    # Using HS256 since we're not using Clerk
    secret = "dev_secret_key_for_testing_only"

    expires_at = datetime.utcnow() + timedelta(hours=24)

    payload = {
        "sub": request.user_id,  # Clerk uses 'sub' for user ID
        "email": request.email,
        "name": request.name,
        "email_verified": True,
        "iat": datetime.utcnow(),
        "exp": expires_at
    }

    token = jwt.encode(payload, secret, algorithm="HS256")

    return TokenResponse(
        access_token=token,
        expires_in=86400,  # 24 hours
        user={
            "user_id": request.user_id,
            "email": request.email,
            "name": request.name
        }
    )


@router.get("/me")
async def get_current_user_info():
    """
    Get current authenticated user info
    Requires valid JWT token in Authorization header
    """
    # This will be handled by the auth middleware
    # Just a placeholder to show how to get user info
    return {
        "message": "This endpoint requires authentication",
        "note": "Add Authorization: Bearer YOUR_TOKEN header"
    }


@router.post("/sync-user")
async def sync_user(request: Request):
    """
    Sync user data from Clerk to MongoDB
    This should be called by the frontend after user authentication
    """
    try:
        from ..services.user_service import user_service
        from ..util.auth_helpers import get_user_id
        
        user_id = get_user_id(request)
        
        # Get user info from request state (set by auth middleware)
        user_info = request.state.user
        
        result = await user_service.ensure_user_exists(
            user_id=user_id,
            email=user_info.get("email", ""),
            name=user_info.get("name", "Unknown User"),
            university=None
        )
        
        return {
            "success": True,
            "message": f"User {result['action']} successfully",
            "data": {"user_id": user_id, "action": result["action"]}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))