import bcrypt from "bcryptjs";
import clientPromise from "@/lib/mongo/client";

export async function POST(req: Request) {
  try {
    const { email, password, name } = await req.json();

    if (!email || !password) {
      return new Response(JSON.stringify({ error: "Missing fields" }), { status: 400 });
    }

    const client = await clientPromise;
    const db = client.db();
    const existing = await db.collection("users").findOne({ email });

    if (existing) {
      return new Response(JSON.stringify({ error: "Email already in use" }), { status: 400 });
    }

    const hashedPassword = await bcrypt.hash(password, 12);
    await db.collection("users").insertOne({
      email,
      name,
      hashedPassword,
    });

    return new Response(JSON.stringify({ ok: true }), { status: 201 });
  } catch (err) {
    console.error("Signup error:", err);
    return new Response(JSON.stringify({ error: "Internal server error" }), { status: 500 });
  }
}
