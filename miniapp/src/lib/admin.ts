import { sql } from "@vercel/postgres";

export type AdminUser = {
  id: number;
  email: string;
  telegramId: string;
  telegramUsername: string;
  role: string;
  createdAt: string;
};

export type AdminStore = {
  storeKey: string;
  title: string;
  marketplace: string;
  userId: number;
  planCode: string;
  maxSkus: number;
  paidActive: boolean;
  offerCount: number;
};

export type AdminData = {
  generatedAt: string;
  users: AdminUser[];
  stores: AdminStore[];
};

const esc = (v: unknown) => String(v ?? "").replace(/"/g, '""');

export function toCsv(rows: Record<string, unknown>[]): string {
  if (!rows.length) return "";
  const header = Object.keys(rows[0]);
  const body = rows.map((r) => header.map((h) => `"${esc(r[h])}"`).join(","));
  return [header.join(","), ...body].join("\n");
}

export async function getAdminData(limit = 50, search = ""): Promise<AdminData> {
  const lim = Math.min(Math.max(Number(limit) || 50, 1), 500);
  const s = `%${search.trim()}%`;

  try {
    const usersQuery = search.trim()
      ? sql`
          SELECT id, email, telegram_id, telegram_username, role, created_at
          FROM users
          WHERE COALESCE(email,'') ILIKE ${s}
             OR COALESCE(telegram_id,'') ILIKE ${s}
             OR COALESCE(telegram_username,'') ILIKE ${s}
          ORDER BY created_at DESC
          LIMIT ${lim}
        `
      : sql`
          SELECT id, email, telegram_id, telegram_username, role, created_at
          FROM users
          ORDER BY created_at DESC
          LIMIT ${lim}
        `;

    const storesQuery = sql`
      SELECT s.store_key, s.title, s.marketplace, s.user_id,
             COALESCE(ss.plan_code, 'start_100') AS plan_code,
             COALESCE(ss.max_skus, 100) AS max_skus,
             COALESCE(ss.paid_active, false) AS paid_active,
             COALESCE(oc.cnt, 0) AS offer_count
      FROM stores s
      LEFT JOIN store_settings ss ON ss.store_key = s.store_key
      LEFT JOIN (SELECT store_key, COUNT(*) AS cnt FROM offers GROUP BY store_key) oc ON oc.store_key = s.store_key
      ORDER BY s.created_at DESC
      LIMIT ${lim}
    `;

    const [usersRes, storesRes] = await Promise.all([usersQuery, storesQuery]);

    return {
      generatedAt: new Date().toISOString(),
      users: usersRes.rows.map((r) => ({
        id: Number(r.id),
        email: String(r.email ?? ""),
        telegramId: String(r.telegram_id ?? ""),
        telegramUsername: String(r.telegram_username ?? ""),
        role: String(r.role ?? "user"),
        createdAt: String(r.created_at ?? ""),
      })),
      stores: storesRes.rows.map((r) => ({
        storeKey: String(r.store_key),
        title: String(r.title ?? ""),
        marketplace: String(r.marketplace ?? "kaspi"),
        userId: Number(r.user_id),
        planCode: String(r.plan_code),
        maxSkus: Number(r.max_skus),
        paidActive: Boolean(r.paid_active),
        offerCount: Number(r.offer_count),
      })),
    };
  } catch {
    return { generatedAt: new Date().toISOString(), users: [], stores: [] };
  }
}
