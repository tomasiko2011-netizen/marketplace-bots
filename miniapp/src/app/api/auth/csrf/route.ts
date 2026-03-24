import { NextResponse } from "next/server";
import { CSRF_COOKIE, issueCsrfToken } from "@/lib/csrf";

export async function GET() {
  const token = issueCsrfToken();
  const res = NextResponse.json({ csrfToken: token });
  res.cookies.set(CSRF_COOKIE, token, {
    httpOnly: false,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60,
  });
  return res;
}
