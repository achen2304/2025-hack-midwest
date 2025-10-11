# Authentication Guide

Complete guide to authentication in CampusMind using Clerk.

## Table of Contents

- [Overview](#overview)
- [Clerk Setup](#clerk-setup)
- [Development Testing](#development-testing)
- [Production Setup](#production-setup)
- [Frontend Integration](#frontend-integration)
- [Troubleshooting](#troubleshooting)

## Overview

CampusMind uses **Clerk** for user authentication with JWT tokens. The system supports:

- ✅ Email/Password authentication
- ✅ OAuth providers (Google, GitHub, etc.)
- ✅ JWT token validation
- ✅ Router-level authentication
- ✅ Dev mode for testing without Clerk

### Architecture

```
Client Request
    ↓
[Bearer Token in Authorization header]
    ↓
[Auth Middleware] → Validates JWT
    ↓
[Extracts user info] → Stores in request.state.user
    ↓
[Protected Endpoint] → Accesses user_id from request
```

## Clerk Setup

### 1. Create Clerk Account

1. Go to [clerk.com](https://clerk.com)
2. Sign up for free
3. Create a new application
   - **Name:** CampusMind
   - **Sign-in methods:** Email, Google (recommended)

### 2. Get API Keys

In Clerk Dashboard → **API Keys**:

```bash
# Copy these to backend/.env
CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxx
CLERK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxx
```

### 3. Get JWKS URL (Production)

In Clerk Dashboard → **JWT Templates**:

```bash
# Copy JWKS endpoint to backend/.env
CLERK_JWKS_URL=https://your-app.clerk.accounts.dev/.well-known/jwks.json
```

### 4. Configure Environment

Edit `backend/.env`:

```bash
# Clerk Authentication
CLERK_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
CLERK_SECRET_KEY=sk_test_YOUR_KEY_HERE
CLERK_JWKS_URL=https://your-app.clerk.accounts.dev/.well-known/jwks.json
```

### 5. Restart Server

```bash
cd backend
uvicorn main:app --reload
```

## Development Testing

For testing without setting up Clerk:

### Option 1: Dev Token Endpoint

Comment out Clerk keys in `.env`:

```bash
# CLERK_SECRET_KEY=sk_test_xxxxx  # Commented = dev mode
```

Get a test token:

```bash
curl -X POST http://localhost:8000/auth/dev-token \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "email": "test@campusmind.com",
    "name": "Test User"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1Qi...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "user_id": "test_user_123",
    "email": "test@campusmind.com",
    "name": "Test User"
  }
}
```

Use the token:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/canvas/courses
```

### Option 2: Postman Collection

1. **Get Token:**
   - POST to `http://localhost:8000/auth/dev-token`
   - Copy `access_token` from response

2. **Configure Postman:**
   - Authorization tab
   - Type: **Bearer Token**
   - Paste token

3. **Test Endpoints:**
   - All `/canvas/*` endpoints
   - All `/calendar/*` endpoints
   - All `/sync/*` endpoints

### Dev Token Features

- ✅ Valid for 24 hours
- ✅ Customizable user info
- ✅ Works exactly like real Clerk tokens
- ✅ Automatically disabled when Clerk is configured

## Production Setup

### Backend Configuration

1. **Set Clerk keys in `.env`:**

```bash
CLERK_PUBLISHABLE_KEY=pk_live_xxxxx
CLERK_SECRET_KEY=sk_live_xxxxx
CLERK_JWKS_URL=https://your-app.clerk.accounts.dev/.well-known/jwks.json
```

2. **Restart server**

3. **Test with real Clerk tokens**

### Getting Real Tokens

**Method 1: Clerk Dashboard**

1. Clerk Dashboard → Users
2. Create test user
3. Click user → "Sign in as user"
4. Browser DevTools → Console:
```javascript
await Clerk.session.getToken()
```

**Method 2: Frontend (Production)**

```typescript
import { useAuth } from '@clerk/nextjs';

function MyComponent() {
  const { getToken } = useAuth();

  const makeRequest = async () => {
    const token = await getToken();

    const response = await fetch('http://localhost:8000/canvas/courses', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
  };
}
```

## Frontend Integration

### Install Clerk

```bash
cd frontend
npm install @clerk/nextjs
```

### Configure Next.js

**`frontend/.env.local`:**
```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxx
CLERK_SECRET_KEY=sk_test_xxxxx
```

**`app/layout.tsx`:**
```typescript
import { ClerkProvider } from '@clerk/nextjs';

export default function RootLayout({ children }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}
```

### Making Authenticated Requests

```typescript
import { useAuth } from '@clerk/nextjs';
import { useEffect, useState } from 'react';

function CoursesPage() {
  const { getToken } = useAuth();
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    const fetchCourses = async () => {
      const token = await getToken();

      const response = await fetch('http://localhost:8000/canvas/courses', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();
      setCourses(data);
    };

    fetchCourses();
  }, [getToken]);

  return (
    <div>
      {courses.map(course => (
        <div key={course.id}>{course.name}</div>
      ))}
    </div>
  );
}
```

### Protected Routes

```typescript
import { auth } from '@clerk/nextjs';
import { redirect } from 'next/navigation';

export default async function ProtectedPage() {
  const { userId } = auth();

  if (!userId) {
    redirect('/sign-in');
  }

  return <div>Protected Content</div>;
}
```

## How It Works

### Backend Auth Flow

1. **Client sends request with Bearer token**
   ```
   GET /canvas/courses
   Authorization: Bearer eyJ0eXAi...
   ```

2. **Router-level dependency checks auth**
   ```python
   router = APIRouter(
       prefix="/canvas",
       dependencies=[Depends(get_current_user)]
   )
   ```

3. **Middleware validates token**
   - Verifies JWT signature (JWKS or secret key)
   - Checks expiration
   - Extracts user info

4. **User info stored in request.state**
   ```python
   request.state.user = {
       "user_id": "user_123",
       "email": "user@example.com",
       "name": "User Name"
   }
   ```

5. **Endpoint accesses user info**
   ```python
   from ..util.auth_helpers import get_user_id

   @router.get("/courses")
   async def get_courses(request: Request):
       user_id = get_user_id(request)
       # Use user_id to fetch user-specific data
   ```

### Token Validation Logic

**`backend/app/middleware/auth.py`:**

```python
async def verify_token(token: str):
    # Method 1: JWKS (Production - Most Secure)
    if self.clerk_jwks_url:
        jwks_client = PyJWKClient(self.clerk_jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        data = jwt.decode(token, signing_key.key, algorithms=["RS256"])

    # Method 2: Secret Key (Simpler)
    elif self.clerk_secret_key:
        data = jwt.decode(token, self.clerk_secret_key, algorithms=["HS256"])

    # Method 3: Dev Mode (Testing Only - INSECURE!)
    else:
        data = jwt.decode(token, "dev_secret", algorithms=["HS256"])

    return {
        "user_id": data.get("sub"),
        "email": data.get("email"),
        "name": data.get("name")
    }
```

## Troubleshooting

### "Not authenticated" Error

**Problem:** 401 Unauthorized

**Solutions:**
- Verify `Authorization: Bearer YOUR_TOKEN` header is set
- Check token hasn't expired (Clerk tokens expire after 1 hour)
- Get fresh token from Clerk or `/auth/dev-token`

### "Invalid token" Error

**Problem:** Token validation fails

**Solutions:**
- Verify `CLERK_SECRET_KEY` or `CLERK_JWKS_URL` in `.env`
- Ensure token is from same Clerk application
- Check for extra spaces in token
- Restart server after `.env` changes

### Dev Token Not Working

**Problem:** `/auth/dev-token` returns 403

**Solution:**
- Dev token endpoint is disabled when `CLERK_SECRET_KEY` is set
- Comment out `CLERK_SECRET_KEY` in `.env` to enable dev mode

### Token Expired

**Problem:** Token works then stops working

**Solutions:**
- Clerk tokens expire after 1 hour by default
- Get new token from Clerk
- Or configure longer expiration in Clerk dashboard

### CORS Issues

**Problem:** Frontend can't reach backend

**Solution:**
Update CORS in `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Security Best Practices

### Production

✅ **DO:**
- Use JWKS URL for token verification
- Use `sk_live_` secret keys (not `sk_test_`)
- Enable HTTPS for all requests
- Set short token expiration (1 hour)
- Rotate secrets regularly

❌ **DON'T:**
- Commit `.env` file to git
- Use dev tokens in production
- Disable token expiration
- Share secret keys publicly

### Development

✅ **DO:**
- Use dev token endpoint for quick testing
- Use `sk_test_` keys from Clerk
- Test with multiple user IDs

❌ **DON'T:**
- Use dev mode in production
- Skip authentication testing
- Hardcode tokens in code

## API Reference

### Get Dev Token

```http
POST /auth/dev-token
Content-Type: application/json

{
  "user_id": "test_user_123",
  "email": "test@example.com",
  "name": "Test User"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1Qi...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "user_id": "test_user_123",
    "email": "test@example.com",
    "name": "Test User"
  }
}
```

### Use Token

```http
GET /canvas/courses
Authorization: Bearer eyJ0eXAiOiJKV1Qi...
```

## Next Steps

- [ ] Set up Clerk account
- [ ] Configure environment variables
- [ ] Test with Postman
- [ ] Integrate with frontend
- [ ] Deploy to production

## Resources

- [Clerk Documentation](https://clerk.com/docs)
- [Clerk FastAPI Guide](https://clerk.com/docs/backend-requests/handling/python)
- [JWT.io Debugger](https://jwt.io) - Debug JWTs
- [Clerk Next.js Guide](https://clerk.com/docs/quickstarts/nextjs)
