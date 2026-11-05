import { SignJWT, jwtVerify } from "jose";
import bcrypt from "bcryptjs";
import type { NextRequest } from "next/server";

const JWT_SECRET = process.env.JWT_SECRET || "";
// Роль admin выдаётся ТОЛЬКО по Telegram ID из подписанного initData.
// Email-вход/регистрация не подтверждают владение адресом, поэтому всегда role=user.
const ADMIN_TELEGRAM_IDS = new Set(
  (process.env.ADMIN_TELEGRAM_IDS || "")
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean)
);
const SESSION_TTL_SEC = Number(process.env.SESSION_TTL_SEC || "604800");

export async function hashPassword(password: string) {
  const salt = await bcrypt.genSalt(10);
  return bcrypt.hash(password, salt);
}

export async function verifyPassword(password: string, hash: string) {
  return bcrypt.compare(password, hash);
}

export async function signSession(payload: Record<string, string | number>) {
  if (!JWT_SECRET) throw new Error("JWT_SECRET missing");
  const secret = new TextEncoder().encode(JWT_SECRET);
  return new SignJWT(payload)
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime(Math.floor(Date.now() / 1000) + SESSION_TTL_SEC)
    .sign(secret);
}

export async function verifySession(token: string) {
  if (!JWT_SECRET) throw new Error("JWT_SECRET missing");
  const secret = new TextEncoder().encode(JWT_SECRET);
  const { payload } = await jwtVerify(token, secret);
  return payload;
}

export async function rotateSession(token: string) {
  const payload = await verifySession(token);
  const cleanPayload: Record<string, string | number> = {};
  for (const [key, value] of Object.entries(payload)) {
    if (["iat", "exp", "nbf", "jti"].includes(key)) continue;
    if (typeof value === "string" || typeof value === "number") {
      cleanPayload[key] = value;
    }
  }
  return signSession(cleanPayload);
}

export function resolveRoleByTelegramId(telegramId: string) {
  return ADMIN_TELEGRAM_IDS.has(String(telegramId || "")) ? "admin" : "user";
}

export function sessionCookieOptions() {
  return {
    httpOnly: true,
    sameSite: "lax" as const,
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: SESSION_TTL_SEC,
  };
}

export async function getSessionPayloadFromRequest(req: NextRequest) {
  const token = req.cookies.get("session")?.value;
  if (!token) return null;
  try {
    return await verifySession(token);
  } catch {
    return null;
  }
}

/**
 * Админ = role "admin" в подписанной сессии И telegram_id из ADMIN_TELEGRAM_IDS.
 * Вторая проверка отсекает старые сессии, выданные по email до этого исправления,
 * и снимает права сразу после удаления ID из ADMIN_TELEGRAM_IDS.
 */
export function isAdminPayload(payload: Record<string, unknown> | null | undefined) {
  if (!payload || payload.role !== "admin") return false;
  const telegramId = payload.telegram_id;
  if (typeof telegramId !== "string" || !telegramId) return false;
  return resolveRoleByTelegramId(telegramId) === "admin";
}

export async function requireAdmin(req: NextRequest) {
  const payload = await getSessionPayloadFromRequest(req);
  return isAdminPayload(payload);
}
