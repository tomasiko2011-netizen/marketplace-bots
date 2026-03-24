import { NextResponse } from "next/server";
import { NextRequest } from "next/server";
import { initSchema, findUserByEmail, createUserWithEmail } from "@/lib/db";
import { hashPassword, signSession, resolveRoleByEmail, sessionCookieOptions } from "@/lib/auth";
import { getClientIp, takeRateLimit } from "@/lib/rate-limit";
import { validateCsrf } from "@/lib/csrf";

export async function POST(req: NextRequest) {
  const ip = getClientIp(req.headers);
  const rl = takeRateLimit(`register:${ip}`, 10, 15 * 60 * 1000);
  if (!rl.ok) {
    return NextResponse.json({ error: "Too many requests" }, { status: 429 });
  }
  if (!validateCsrf(req)) {
    return NextResponse.json({ error: "CSRF validation failed" }, { status: 403 });
  }
  await initSchema();
  const { email, password } = await req.json();
  if (!email || !password) {
    return NextResponse.json({ error: "Missing email or password" }, { status: 400 });
  }

  const existing = await findUserByEmail(email);
  if (existing) {
    return NextResponse.json({ error: "User exists" }, { status: 409 });
  }

  const passwordHash = await hashPassword(password);
  const user = await createUserWithEmail(email, passwordHash);
  const token = await signSession({ sub: String(user.id), email: user.email, role: resolveRoleByEmail(user.email) });

  const res = NextResponse.json({ ok: true });
  res.cookies.set("session", token, sessionCookieOptions());
  return res;
}
