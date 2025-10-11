# Backend Setup Instructions

## Quick Install

Run this command to install all dependencies:

```bash
cd backend
pip install -r requirements.txt
```

## Individual Install (if requirements.txt fails)

If the requirements.txt installation fails, run this single command:

```bash
pip install fastapi==0.119.0 uvicorn[standard]==0.37.0 python-multipart==0.0.20 motor==3.7.1 pymongo==4.15.3 pyjwt[crypto]==2.10.1 cryptography==46.0.2 python-jose[cryptography]==3.3.0 httpx==0.28.1 python-dotenv==1.1.1 strands-agents==1.12.0 strands-agents-tools==0.2.11 boto3==1.40.50 numpy==2.2.6 pydantic==2.12.0 pydantic-settings==2.11.0
```

## Quick Fix for Auth Issues

If you're getting JWT/cryptography errors, just install these (compatible with strands-agents-tools):

```bash
pip install cryptography==46.0.2 "pyjwt[crypto]>=2.10.1" python-jose[cryptography]==3.3.0
```

## Start the Server

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Setup

Make sure you have a `.env` file in the backend directory with:

```env
MONGODB_URI=your_mongodb_uri
DB_NAME=campusmind
CLERK_PUBLISHABLE_KEY=your_clerk_key
CLERK_SECRET_KEY=your_clerk_secret
CLERK_JWKS_URL=your_clerk_jwks_url
CANVAS_API_TOKEN=your_canvas_token
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

## Verify Installation

Test the server is running:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","database":"connected","version":"1.0.0"}
```
