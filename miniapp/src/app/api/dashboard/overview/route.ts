import { NextRequest, NextResponse } from "next/server";
import { getSessionPayloadFromRequest } from "@/lib/auth";
import { getDashboardForUser } from "@/lib/dashboard";

export async function GET(req: NextRequest) {
  const payload = await getSessionPayloadFromRequest(req);
  if (!payload?.sub) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }
  const data = await getDashboardForUser(Number(payload.sub));
  return NextResponse.json(data);
}
