import { NextRequest, NextResponse } from "next/server";
import { getAdminData, toCsv } from "@/lib/admin";
import { requireAdmin } from "@/lib/auth";

export async function GET(req: NextRequest) {
  const allowed = await requireAdmin(req);
  if (!allowed) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }
  const url = new URL(req.url);
  const type = (url.searchParams.get("type") ?? "users").toLowerCase();
  const limit = Number(url.searchParams.get("limit") ?? "500");
  const search = url.searchParams.get("search") ?? "";

  const data = await getAdminData(limit, search);

  let rows: Record<string, unknown>[] = [];
  if (type === "stores") rows = data.stores;
  else rows = data.users;

  const csv = toCsv(rows);
  const filename = `${type}_${new Date().toISOString().slice(0, 10)}.csv`;

  return new NextResponse(csv, {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": `attachment; filename=${filename}`,
    },
  });
}
