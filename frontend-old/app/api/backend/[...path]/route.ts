// app/api/backend/[...path]/route.ts
import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import { SignJWT } from "jose";

export const runtime = "nodejs";

const API_BASE = process.env.FASTAPI_INTERNAL_URL!;             // e.g. http://localhost:8000
const NEXTAUTH_SECRET = process.env.AUTH_SECRET || process.env.NEXTAUTH_SECRET;
const BACKEND_JWT_SECRET = process.env.BACKEND_JWT_SECRET!;
const ISS = "nextapp";
const AUD = "fastapi";

async function signBackendJWT(t: any) {
  const now = Math.floor(Date.now() / 1000);
  const secret = new TextEncoder().encode(BACKEND_JWT_SECRET);

  const sub = String(t.sub ?? t.userId ?? t.email ?? "unknown");

  return await new SignJWT({
    sub,
    email: t.email ?? null,
    name: t.name ?? null,
    picture: t.picture ?? null,
    iss: ISS,
    aud: AUD,
    iat: now,
  })
    .setProtectedHeader({ alg: "HS256", typ: "JWT" })
    .setExpirationTime(now + 15 * 60) // 15 min
    .setIssuer(ISS)
    .setAudience(AUD)
    .setSubject(sub)
    .sign(secret);
}

async function proxy(req: NextRequest, path: string[]) {
  // 1) Authenticate via NextAuth cookie
  const token = await getToken({ req, secret: NEXTAUTH_SECRET });
  console.log("as token?", !!token);
  if (!token) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  // 2) Mint backend JWT and attach header
  const backendToken = await signBackendJWT(token);
  const headers = new Headers();
  headers.set("Authorization", `Bearer ${backendToken}`);
  const ct = req.headers.get("content-type");
  if (ct) headers.set("content-type", ct);

  // 3) Build target URL + forward
  const url = `${API_BASE}/${path.join("/")}${req.nextUrl.search}`;
  console.log("forwarding to", url);
  console.log("auth header present?", headers.has("Authorization"));

  const method = req.method.toUpperCase();
  const init: RequestInit = {
    method,
    headers,
    ...(method !== "GET" && method !== "HEAD"
      ? { body: req.body as any, duplex: "half" as any }
      : {}),
  };

  const res = await fetch(url, init);
  return new NextResponse(res.body, {
    status: res.status,
    headers: { "content-type": res.headers.get("content-type") ?? "application/json" },
  });
}

export const GET = (req: NextRequest, ctx: any) => proxy(req, ctx.params.path);
export const POST = (req: NextRequest, ctx: any) => proxy(req, ctx.params.path);
export const PUT = (req: NextRequest, ctx: any) => proxy(req, ctx.params.path);
export const PATCH = (req: NextRequest, ctx: any) => proxy(req, ctx.params.path);
export const DELETE = (req: NextRequest, ctx: any) => proxy(req, ctx.params.path);
