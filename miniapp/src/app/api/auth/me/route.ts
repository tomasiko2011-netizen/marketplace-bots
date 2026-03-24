import { NextResponse } from "next/server";
import { verifySession } from "@/lib/auth";

export async function GET(req: Request) {
  const cookie = req.headers.get("cookie") || "";
  const match = cookie.match(/session=([^;]+)/);
  if (!match) {
    return NextResponse.json({ authenticated: false }, { status: 401 });
  }
  try {
    const payload = await verifySession(match[1]);
    return NextResponse.json({ authenticated: true, user: payload });
  } catch {
    return NextResponse.json({ authenticated: false }, { status: 401 });
  }
}
