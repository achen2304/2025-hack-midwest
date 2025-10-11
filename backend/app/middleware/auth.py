"""
Authentication middleware for CampusMind
Validates Clerk JWT tokens and extracts user information
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.requests import Request
from typing import Optional, Dict
import httpx
import os
from functools import lru_cache
import jwt
from jwt import PyJWKClient
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


class ClerkAuth:
    """Clerk authentication handler"""

    def __init__(self):
        self.clerk_secret_key = os.getenv("CLERK_SECRET_KEY")
        self.clerk_publishable_key = os.getenv("CLERK_PUBLISHABLE_KEY")
        self.clerk_jwks_url = None

        if self.clerk_publishable_key:
            # Extract instance ID from publishable key (format: pk_test_xxxxx or pk_live_xxxxx)
            # JWKS URL format: https://clerk.{instance}.lcl.dev/.well-known/jwks.json (for test)
            # or use the provided CLERK_JWKS_URL env var
            self.clerk_jwks_url = os.getenv("CLERK_JWKS_URL")

    @lru_cache(maxsize=1)
    def get_jwks_client(self) -> Optional[PyJWKClient]:
        """Get JWKS client for token verification"""
        if not self.clerk_jwks_url:
            return None
        return PyJWKClient(self.clerk_jwks_url)

    async def verify_token(self, token: str) -> Dict:
        """Verify Clerk JWT token and return user info"""
        try:
            # Method 1: Verify using JWKS (production-ready)
            if self.clerk_jwks_url:
                jwks_client = self.get_jwks_client()
                signing_key = jwks_client.get_signing_key_from_jwt(token)

                data = jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=["RS256"],
                    options={"verify_exp": True}
                )

                return {
                    "user_id": data.get("sub"),  # Clerk user ID
                    "email": data.get("email"),
                    "name": data.get("name"),
                    "email_verified": data.get("email_verified", False),
                    "clerk_data": data
                }

            # Method 2: Verify using secret key (simpler, less secure)
            elif self.clerk_secret_key:
                data = jwt.decode(
                    token,
                    self.clerk_secret_key,
                    algorithms=["HS256"],
                    options={"verify_exp": True}
                )

                return {
                    "user_id": data.get("sub"),
                    "email": data.get("email"),
                    "name": data.get("name"),
                    "email_verified": data.get("email_verified", False),
                    "clerk_data": data
                }

            else:
                # Development mode - use simple secret
                # This works with tokens from /auth/dev-token endpoint
                logger.warning("⚠️  Running in DEV mode - Using dev secret for JWT verification")

                dev_secret = "dev_secret_key_for_testing_only"

                try:
                    # Try to decode with dev secret first
                    data = jwt.decode(
                        token,
                        dev_secret,
                        algorithms=["HS256"],
                        options={"verify_exp": True}
                    )
                except:
                    # Fall back to no verification for any other JWT
                    logger.warning("⚠️  DEV mode - Accepting unverified JWT")
                    data = jwt.decode(token, options={"verify_signature": False})

                return {
                    "user_id": data.get("sub", "dev_user"),
                    "email": data.get("email", "dev@campusmind.com"),
                    "name": data.get("name", "Dev User"),
                    "email_verified": True,
                    "clerk_data": data
                }

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

    async def get_user_from_clerk_api(self, user_id: str) -> Dict:
        """Fetch full user details from Clerk API"""
        if not self.clerk_secret_key:
            return {}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.clerk.com/v1/users/{user_id}",
                    headers={"Authorization": f"Bearer {self.clerk_secret_key}"}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch user from Clerk API: {e}")
            return {}


# Global auth instance
clerk_auth = ClerkAuth()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    FastAPI dependency to get current authenticated user
    Stores user info in request.state for easy access
    Automatically creates user in database if not exists

    Usage in routes:
        @router.get("/protected")
        async def protected_route(current_user: Dict = Depends(get_current_user)):
            user_id = current_user["user_id"]
            ...

        Or with router-level dependency:
        router = APIRouter(dependencies=[Depends(get_current_user)])

        def get_user_id(request: Request) -> str:
            return request.state.user["user_id"]
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    token = credentials.credentials
    user_info = await clerk_auth.verify_token(token)

    # Ensure user exists in database
    try:
        from ..services.user_service import user_service
        await user_service.ensure_user_exists(
            user_id=user_info["user_id"],
            email=user_info.get("email", ""),
            name=user_info.get("name", "Unknown User"),
            university=None  # Can be updated later
        )
    except Exception as e:
        logger.warning(f"Failed to ensure user exists in database: {e}")
        # Don't fail auth if user creation fails, just log it

    # Store in request.state for router-level dependency access
    request.state.user = user_info

    return user_info


async def get_optional_user(
    request: Request
) -> Optional[Dict]:
    """
    Optional auth - returns user if authenticated, None otherwise
    Use for routes that work with or without auth
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]

    try:
        user_info = await clerk_auth.verify_token(token)
        return user_info
    except:
        return None
