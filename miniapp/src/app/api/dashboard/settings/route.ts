import { NextRequest, NextResponse } from "next/server";
import { getSessionPayloadFromRequest } from "@/lib/auth";
import {
  getStoreSettings,
  upsertStoreSettings,
  getPriceRules,
  upsertGlobalRule,
  getStoresForUser,
  getPriceHistory,
  getExcludedProducts,
  getExcludedCompetitors,
  setExcludedProducts,
  setExcludedCompetitors,
} from "@/lib/db";

async function verifyStoreAccess(req: NextRequest, storeKey: string) {
  const payload = await getSessionPayloadFromRequest(req);
  if (!payload?.sub) return null;
  const stores = await getStoresForUser(Number(payload.sub));
  const match = stores.find((s) => s.store_key === storeKey);
  if (!match && payload.role !== "admin") return null;
  return payload;
}

export async function GET(req: NextRequest) {
  const storeKey = req.nextUrl.searchParams.get("store");
  if (!storeKey) {
    return NextResponse.json({ error: "Missing store param" }, { status: 400 });
  }
  const payload = await verifyStoreAccess(req, storeKey);
  if (!payload) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const [settings, rules, history, excludedSkus, excludedCompetitors] = await Promise.all([
    getStoreSettings(storeKey),
    getPriceRules(storeKey),
    getPriceHistory(storeKey, 20),
    getExcludedProducts(storeKey),
    getExcludedCompetitors(storeKey),
  ]);

  return NextResponse.json({ settings, rules, history, excludedSkus, excludedCompetitors });
}

export async function POST(req: NextRequest) {
  const body = await req.json();
  const storeKey = body.store_key;
  if (!storeKey) {
    return NextResponse.json({ error: "Missing store_key" }, { status: 400 });
  }
  const payload = await verifyStoreAccess(req, storeKey);
  if (!payload) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  if (body.settings) {
    await upsertStoreSettings(storeKey, body.settings);
  }
  if (body.rule) {
    await upsertGlobalRule(
      storeKey,
      body.rule.min_price ?? null,
      body.rule.max_price ?? null,
      body.rule.undercut_by ?? null
    );
  }
  if (body.excluded_skus !== undefined) {
    const skus = (body.excluded_skus as string)
      .split(",")
      .map((s: string) => s.trim())
      .filter(Boolean);
    await setExcludedProducts(storeKey, skus);
  }
  if (body.excluded_competitors !== undefined) {
    const comps = (body.excluded_competitors as string)
      .split(",")
      .map((s: string) => s.trim())
      .filter(Boolean);
    await setExcludedCompetitors(storeKey, comps);
  }

  return NextResponse.json({ ok: true });
}
