"""
User profile management routes
"""
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from bson import ObjectId

from app.util.db import get_database
from app.util.auth import verify_backend_token
from app.models.schemas import (
    UserProfileResponse,
    UserProfileUpdate,
    UserPreferences,
    UserPreferencesResponse,
    BlockedTime
)

router = APIRouter(prefix="/user", tags=["User"])

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Get current user's profile"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        print(f"[DEBUG] Fetching profile for user_id={user_id}, email={email}")

        # Try to find user by MongoDB _id first
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
            print(f"[DEBUG] Found user by ObjectId: {user_doc is not None}")
        except Exception as e:
            print(f"[DEBUG] ObjectId lookup failed: {e}, trying email")

        # If not found by ObjectId, try email
        if not user_doc:
            user_doc = await db.users.find_one({"email": email})
            print(f"[DEBUG] Found user by email: {user_doc is not None}")

        if not user_doc:
            print(f"[DEBUG] User not found, creating new user")
            # Create user profile if it doesn't exist
            new_user = {
                "email": email,
                "name": user.get("name"),
                "image": user.get("picture"),
                "university": None,
                "created_at": datetime.utcnow()
            }
            result = await db.users.insert_one(new_user)
            user_doc = await db.users.find_one({"_id": result.inserted_id})
            print(f"[DEBUG] Created new user with _id={result.inserted_id}")

        return UserProfileResponse(
            id=str(user_doc["_id"]),
            email=user_doc["email"],
            name=user_doc.get("name"),
            university=user_doc.get("university"),
            image=user_doc.get("image"),
            created_at=user_doc.get("created_at", datetime.utcnow())
        )

    except Exception as e:
        print(f"[ERROR] Failed to fetch user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user profile: {str(e)}"
        )

@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Update current user's profile"""
    try:
        user_id = user.get("sub")

        # Build update document
        update_data = {}
        if profile_update.name is not None:
            update_data["name"] = profile_update.name
        if profile_update.university is not None:
            update_data["university"] = profile_update.university
        if profile_update.image is not None:
            update_data["image"] = profile_update.image

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        # Try to update by MongoDB _id first
        result = None
        try:
            result = await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
        except:
            pass

        # If not found by ObjectId, try email
        if not result or result.matched_count == 0:
            result = await db.users.update_one(
                {"email": user.get("email")},
                {"$set": update_data}
            )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Fetch updated user
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass

        if not user_doc:
            user_doc = await db.users.find_one({"email": user.get("email")})

        return UserProfileResponse(
            id=str(user_doc["_id"]),
            email=user_doc["email"],
            name=user_doc.get("name"),
            university=user_doc.get("university"),
            image=user_doc.get("image"),
            created_at=user_doc.get("created_at", datetime.utcnow())
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user profile: {str(e)}"
        )

@router.get("/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Get user's scheduling preferences"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Try to find preferences by user ID
        prefs_doc = None
        try:
            prefs_doc = await db.user_preferences.find_one({"user_id": user_id})
        except:
            pass

        # If not found, get user by email first to get MongoDB ID
        if not prefs_doc:
            user_doc = await db.users.find_one({"email": email})
            if user_doc:
                prefs_doc = await db.user_preferences.find_one({"user_id": str(user_doc["_id"])})

        if not prefs_doc:
            # Return default preferences
            return UserPreferencesResponse(
                user_id=user_id,
                study_block_duration=60,
                break_duration=15,
                travel_duration=10,
                recurring_blocked_times=[]
            )

        return UserPreferencesResponse(
            user_id=str(prefs_doc.get("user_id")),
            study_block_duration=prefs_doc.get("study_block_duration", 60),
            break_duration=prefs_doc.get("break_duration", 15),
            travel_duration=prefs_doc.get("travel_duration", 10),
            recurring_blocked_times=[
                BlockedTime(**blocked_time)
                for blocked_time in prefs_doc.get("recurring_blocked_times", [])
            ]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user preferences: {str(e)}"
        )

@router.put("/preferences", response_model=UserPreferencesResponse)
async def update_user_preferences(
    preferences: UserPreferences,
    user=Depends(verify_backend_token),
    db=Depends(get_database)
):
    """Update user's scheduling preferences"""
    try:
        user_id = user.get("sub")
        email = user.get("email")

        # Get user's MongoDB ID
        user_doc = None
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass

        if not user_doc:
            user_doc = await db.users.find_one({"email": email})

        if user_doc:
            db_user_id = str(user_doc["_id"])
        else:
            db_user_id = user_id  # Fallback to JWT sub

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Convert blocked times to dict
        blocked_times_dict = [bt.model_dump() for bt in preferences.recurring_blocked_times]

        # Upsert preferences
        await db.user_preferences.update_one(
            {"user_id": db_user_id},
            {
                "$set": {
                    "user_id": db_user_id,
                    "study_block_duration": preferences.study_block_duration,
                    "break_duration": preferences.break_duration,
                    "travel_duration": preferences.travel_duration,
                    "recurring_blocked_times": blocked_times_dict,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )

        return UserPreferencesResponse(
            user_id=db_user_id,
            study_block_duration=preferences.study_block_duration,
            break_duration=preferences.break_duration,
            travel_duration=preferences.travel_duration,
            recurring_blocked_times=preferences.recurring_blocked_times
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user preferences: {str(e)}"
        )
