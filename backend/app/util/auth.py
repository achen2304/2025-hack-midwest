"""
Authentication utilities for CampusMind API
"""
import os
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError

SECRET = os.environ.get("BACKEND_JWT_SECRET", "dev-secret")
ALGS = ["HS256"]
ISS = "nextapp"
AUD = "fastapi"

security = HTTPBearer()

def verify_backend_token(creds: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token from Next.js frontend"""
    token = creds.credentials
    try:
        payload = jwt.decode(
            token,
            SECRET,
            algorithms=ALGS,
            audience=AUD,
            issuer=ISS,
        )
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return payload  # contains sub, email, name, picture, iat, exp, iss, aud
