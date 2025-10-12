import { NextRequest, NextResponse } from 'next/server';
import { getToken } from 'next-auth/jwt';
import { SignJWT } from 'jose';

export const runtime = 'nodejs';

const API_BASE = process.env.FASTAPI_INTERNAL_URL ?? 'http://localhost:8000';
const NEXTAUTH_SECRET = process.env.AUTH_SECRET || process.env.NEXTAUTH_SECRET;
const BACKEND_JWT_SECRET = process.env.BACKEND_JWT_SECRET!;
const ISS = 'nextapp';
const AUD = 'fastapi';

async function signBackendJWT(token: any) {
  const now = Math.floor(Date.now() / 1000);
  const secret = new TextEncoder().encode(BACKEND_JWT_SECRET);
  const sub = String(token.sub ?? token.userId ?? token.email ?? 'unknown');

  return new SignJWT({
    sub,
    email: token.email ?? null,
    name: token.name ?? null,
    picture: token.picture ?? null,
    iss: ISS,
    aud: AUD,
    iat: now,
  })
    .setProtectedHeader({ alg: 'HS256', typ: 'JWT' })
    .setExpirationTime(now + 15 * 60)
    .setIssuer(ISS)
    .setAudience(AUD)
    .setSubject(sub)
    .sign(secret);
}

export async function POST(request: NextRequest) {
  try {
    const sessionToken = await getToken({ req: request, secret: NEXTAUTH_SECRET });
    if (!sessionToken) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await request.json().catch(() => ({}));
    const canvasToken = body.canvas_token ?? body.token;
    const canvasBaseUrl = body.canvas_base_url ?? body.canvasUrl ?? undefined;

    if (!canvasToken) {
      return NextResponse.json(
        { error: 'Token is required' },
        { status: 400 }
      );
    }

    const payload = {
      canvas_token: canvasToken,
      ...(canvasBaseUrl ? { canvas_base_url: canvasBaseUrl } : {}),
    };

    const backendToken = await signBackendJWT(sessionToken);
    const baseUrl = API_BASE.endsWith('/') ? API_BASE.slice(0, -1) : API_BASE;

    // Forward the request to the backend server
    const backendResponse = await fetch(`${baseUrl}/canvas/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${backendToken}`,
      },
      body: JSON.stringify(payload),
    });

    if (!backendResponse.ok) {
      const errorData = await backendResponse.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData.detail || errorData.error || 'Failed to update Canvas token' },
        { status: backendResponse.status }
      );
    }

    const data = await backendResponse.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error updating Canvas token:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
