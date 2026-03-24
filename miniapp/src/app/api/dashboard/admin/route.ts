import { NextRequest, NextResponse } from "next/server";
import { getAdminData } from "@/lib/admin";
import { requireAdmin } from "@/lib/auth";

export async function GET(req: NextRequest) {
  const allowed = await requireAdmin(req);
  if (!allowed) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }
  const url = new URL(req.url);
  const limit = Number(url.searchParams.get("limit") ?? "50");
  const search = url.searchParams.get("search") ?? "";
  const data = await getAdminData(limit, search);
  return NextResponse.json(data);
}
