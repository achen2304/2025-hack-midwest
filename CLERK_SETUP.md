# Clerk Authentication Setup Guide

This guide will help you set up Clerk authentication for CampusMind.

## Why Clerk?

- Zero custom auth code needed
- Built-in OAuth providers (Google, GitHub, etc.)
- User management dashboard
- JWT token handling
- Free tier for development

## Step 1: Create a Clerk Account

1. Go to [https://clerk.com](https://clerk.com)
2. Sign up for a free account
3. Create a new application
   - Name: "CampusMind" (or your choice)
   - Choose your sign-in methods (Email, Google, etc.)

## Step 2: Get Your API Keys

1. In Clerk Dashboard, go to **API Keys**
2. Copy the following values:

   - **Publishable Key** (starts with `pk_test_` or `pk_live_`)
   - **Secret Key** (starts with `sk_test_` or `sk_live_`)

3. Add these to your `backend/.env` file:

```bash
CLERK_PUBLISHABLE_KEY=pk_test_XXXXXXXXXXXXXXXXX
CLERK_SECRET_KEY=sk_test_XXXXXXXXXXXXXXXXX
```

## Step 3: Get JWKS URL (Recommended for Production)

1. In Clerk Dashboard, go to **JWT Templates**
2. Click on **Convex** template (or create custom)
3. Copy the **JWKS Endpoint URL**
4. Add to your `backend/.env`:

```bash
CLERK_JWKS_URL=https://your-app.clerk.accounts.dev/.well-known/jwks.json
```

> **Note**: For development, you can skip this step. The auth system will fall back to less secure verification using just the secret key.

## Step 4: Configure Authentication Backend (DONE ✅)

The backend is already configured to use Clerk! Here's what was set up:

### Router-Level Authentication

All API endpoints are protected with router-level auth:

```python
# Example from canvas.py
router = APIRouter(
    prefix="/canvas",
    tags=["canvas"],
    dependencies=[Depends(get_current_user)]  # 🔒 All routes protected
)
```

### How to Get User Info in Endpoints

```python
from ..util.auth_helpers import get_user_id

@router.get("/my-data")
async def get_my_data(request: Request):
    user_id = get_user_id(request)
    # user_id is extracted from JWT token
    # Now fetch user-specific data
    ...
```

## Step 5: Frontend Setup (Next.js)

When you're ready to add the frontend, install Clerk:

```bash
cd frontend
npm install @clerk/nextjs
```

Then wrap your app with Clerk provider (`frontend/app/layout.tsx`):

```tsx
import { ClerkProvider } from "@clerk/nextjs";

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

Add environment variables to `frontend/.env.local`:

```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_XXXXXXXXXX
CLERK_SECRET_KEY=sk_test_XXXXXXXXXX
```

## Step 6: Testing with Postman/cURL

### 1. Get a Session Token

**Option A: Via Clerk Dashboard (Development)**

1. Go to Clerk Dashboard → Users
2. Create a test user
3. Click on the user → **Sign in as user**
4. Open browser DevTools → Console
5. Run: `await Clerk.session.getToken()`
6. Copy the token

**Option B: Via Frontend (Production)**

```typescript
// In your Next.js app
import { useAuth } from "@clerk/nextjs";

function MyComponent() {
  const { getToken } = useAuth();

  const makeRequest = async () => {
    const token = await getToken();

    const response = await fetch("http://localhost:8000/canvas/courses", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  };
}
```

### 2. Make API Requests

**Using cURL:**

```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     http://localhost:8000/canvas/courses
```

**Using Postman:**

1. Create a new request
2. Select **Authorization** tab
3. Type: **Bearer Token**
4. Token: Paste your Clerk session token
5. Send request

## Step 7: Development Mode (No Auth)

For quick local testing without Clerk setup, you can temporarily disable auth:

**Option 1:** Comment out the dependency in routers:

```python
router = APIRouter(
    prefix="/canvas",
    tags=["canvas"],
    # dependencies=[Depends(get_current_user)]  # Temporarily disabled
)
```

**Option 2:** Use a fake token (auth.py already handles this):

If `CLERK_SECRET_KEY` is not set, the auth middleware runs in dev mode and accepts any JWT without verification (INSECURE - dev only!).

## Protected Routes

All routes except these require authentication:

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - API documentation
- `GET /openapi.json` - OpenAPI spec

## User ID in Requests

**Before Auth:**

```python
# Had to pass user_id manually
GET /canvas/courses?user_id=123
```

**After Auth (Current):**

```python
# user_id extracted from JWT automatically
GET /canvas/courses
Authorization: Bearer YOUR_TOKEN
```

## Troubleshooting

### "Not authenticated" Error

- Check that your Authorization header is set: `Authorization: Bearer YOUR_TOKEN`
- Verify token hasn't expired (Clerk tokens expire after 1 hour by default)
- Get a fresh token from Clerk

### "Invalid token" Error

- Verify `CLERK_SECRET_KEY` or `CLERK_JWKS_URL` is set correctly in `.env`
- Check that the token is from the same Clerk application
- Ensure no extra spaces in the token

### Can't Get Token from Clerk Dashboard

- Make sure you're signed into Clerk Dashboard
- Use "Sign in as user" feature
- Alternatively, set up the frontend to get tokens properly

## Next Steps

1. Set up Clerk application
2. Add API keys to `.env`
3. Test with Postman using Clerk tokens
4. (Later) Add Clerk to Next.js frontend
5. (Later) Add user profile UI

## Resources

- [Clerk Documentation](https://clerk.com/docs)
- [Clerk FastAPI Guide](https://clerk.com/docs/backend-requests/handling/python)
- [Clerk Next.js Quickstart](https://clerk.com/docs/quickstarts/nextjs)
- [JWT Token Reference](https://clerk.com/docs/backend-requests/resources/session-tokens)
