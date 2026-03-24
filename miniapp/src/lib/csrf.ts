import crypto from "crypto";
import { NextRequest } from "next/server";

export const CSRF_COOKIE = "csrf_token";

export function issueCsrfToken() {
  return crypto.randomBytes(24).toString("hex");
}

export function validateCsrf(req: NextRequest) {
  const cookieToken = req.cookies.get(CSRF_COOKIE)?.value || "";
  const headerToken = req.headers.get("x-csrf-token") || "";
  if (!cookieToken || !headerToken) return false;
  try {
    return crypto.timingSafeEqual(Buffer.from(cookieToken), Buffer.from(headerToken));
  } catch {
    return false;
  }
}
