import { sql } from "@vercel/postgres";

export type StoreOverview = {
  store_key: string;
  title: string;
  marketplace: string;
  poll_interval_seconds: number;
  turbo_mode: boolean;
  plan_code: string;
  max_skus: number;
  paid_active: boolean;
  offer_count: number;
  last_run_at: string | null;
  run_count: number;
};

export type PriceAction = {
  sku: string;
  old_price: number;
  new_price: number;
  reason: string;
  created_at: string;
};

export type DashboardData = {
  generatedAt: string;
  stores: StoreOverview[];
  recentActions: PriceAction[];
  tariffs: { code: string; name: string; max_skus: number; price_kzt: number }[];
  trialRunsUsed: number;
  trialRunsLimit: number;
};

export async function getDashboardForUser(userId: number): Promise<DashboardData> {
  const [storesResult, tariffResult, usageResult] = await Promise.all([
    sql`
      SELECT s.store_key, s.title, s.marketplace,
             COALESCE(ss.poll_interval_seconds, 120) AS poll_interval_seconds,
             COALESCE(ss.turbo_mode, false) AS turbo_mode,
             COALESCE(ss.plan_code, 'start_100') AS plan_code,
             COALESCE(ss.max_skus, 100) AS max_skus,
             COALESCE(ss.paid_active, false) AS paid_active,
             COALESCE(oc.cnt, 0) AS offer_count
      FROM stores s
      LEFT JOIN store_settings ss ON ss.store_key = s.store_key
      LEFT JOIN (SELECT store_key, COUNT(*) AS cnt FROM offers GROUP BY store_key) oc ON oc.store_key = s.store_key
      WHERE s.user_id = ${userId}
      ORDER BY s.created_at;
    `,
    sql`SELECT * FROM tariff_plans ORDER BY sort_order;`,
    sql`SELECT run_count, last_run_at FROM usage_runs WHERE user_id = ${userId} LIMIT 1;`,
  ]);

  const stores: StoreOverview[] = storesResult.rows.map((r) => ({
    store_key: r.store_key,
    title: r.title || r.store_key,
    marketplace: r.marketplace,
    poll_interval_seconds: Number(r.poll_interval_seconds),
    turbo_mode: Boolean(r.turbo_mode),
    plan_code: r.plan_code,
    max_skus: Number(r.max_skus),
    paid_active: Boolean(r.paid_active),
    offer_count: Number(r.offer_count),
    last_run_at: r.last_run_at ?? null,
    run_count: 0,
  }));

  let recentActions: PriceAction[] = [];
  if (stores.length > 0) {
    const keysStr = stores.map((s) => s.store_key).join(",");
    const actionsResult = await sql.query(
      `SELECT sku, old_price, new_price, reason, created_at
       FROM price_actions
       WHERE store_key = ANY(string_to_array($1, ','))
       ORDER BY created_at DESC
       LIMIT 20`,
      [keysStr]
    );
    recentActions = actionsResult.rows.map((r) => ({
      sku: r.sku,
      old_price: Number(r.old_price),
      new_price: Number(r.new_price),
      reason: r.reason,
      created_at: r.created_at,
    }));
  }

  return {
    generatedAt: new Date().toISOString(),
    stores,
    recentActions,
    tariffs: tariffResult.rows.map((r) => ({
      code: r.code,
      name: r.name,
      max_skus: Number(r.max_skus),
      price_kzt: Number(r.price_kzt),
    })),
    trialRunsUsed: Number(usageResult.rows[0]?.run_count ?? 0),
    trialRunsLimit: 5,
  };
}
