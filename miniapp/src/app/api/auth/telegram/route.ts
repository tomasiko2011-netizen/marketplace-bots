import { NextResponse } from "next/server";
import { NextRequest } from "next/server";
import { initSchema, upsertTelegramUser } from "@/lib/db";
import { signSession, resolveRoleByTelegramId, sessionCookieOptions } from "@/lib/auth";
import { validateTelegramInitData } from "@/lib/telegram";
import { getClientIp, takeRateLimit } from "@/lib/rate-limit";
import { validateCsrf } from "@/lib/csrf";

export async function POST(req: NextRequest) {
  const ip = getClientIp(req.headers);
  const rl = takeRateLimit(`telegram_login:${ip}`, 30, 15 * 60 * 1000);
  if (!rl.ok) {
    return NextResponse.json({ error: "Too many requests" }, { status: 429 });
  }
  if (!validateCsrf(req)) {
    return NextResponse.json({ error: "CSRF validation failed" }, { status: 403 });
  }
  await initSchema();
  const { initData } = await req.json();
  const botToken = process.env.TELEGRAM_BOT_TOKEN || "";
  if (!botToken) {
    return NextResponse.json({ error: "TELEGRAM_BOT_TOKEN missing" }, { status: 500 });
  }
  if (!initData || !validateTelegramInitData(initData, botToken)) {
    return NextResponse.json({ error: "Invalid initData" }, { status: 401 });
  }

  const params = new URLSearchParams(initData);
  const userRaw = params.get("user");
  if (!userRaw) {
    return NextResponse.json({ error: "No user data" }, { status: 400 });
  }

  const user = JSON.parse(userRaw);
  const telegramId = String(user.id);
  const username = user.username || null;

  const dbUser = await upsertTelegramUser(telegramId, username);
  const token = await signSession({
    sub: String(dbUser.id),
    telegram_id: telegramId,
    role: resolveRoleByTelegramId(telegramId),
  });

  const res = NextResponse.json({ ok: true });
  res.cookies.set("session", token, sessionCookieOptions());
  return res;
}
