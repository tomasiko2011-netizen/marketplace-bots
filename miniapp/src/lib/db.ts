import { sql } from "@vercel/postgres";

// -- Schema init (idempotent, matches migrations/001_init.sql) --

export async function initSchema() {
  await sql`
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      email TEXT UNIQUE,
      password_hash TEXT,
      telegram_id TEXT UNIQUE,
      telegram_username TEXT,
      role TEXT NOT NULL DEFAULT 'user',
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
  `;
  await sql`
    CREATE TABLE IF NOT EXISTS stores (
      id SERIAL PRIMARY KEY,
      user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
      store_key TEXT NOT NULL UNIQUE,
      title TEXT NOT NULL DEFAULT '',
      marketplace TEXT NOT NULL DEFAULT 'kaspi',
      mode TEXT NOT NULL DEFAULT 'mock',
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
  `;
  await sql`
    CREATE TABLE IF NOT EXISTS store_settings (
      id SERIAL PRIMARY KEY,
      store_key TEXT NOT NULL UNIQUE,
      poll_interval_seconds INTEGER NOT NULL DEFAULT 120,
      turbo_mode BOOLEAN NOT NULL DEFAULT FALSE,
      plan_code TEXT NOT NULL DEFAULT 'start_100',
      max_skus INTEGER NOT NULL DEFAULT 100,
      paid_active BOOLEAN NOT NULL DEFAULT FALSE,
      plan_started_at TIMESTAMPTZ
    );
  `;
  await sql`
    CREATE TABLE IF NOT EXISTS price_rules (
      id SERIAL PRIMARY KEY,
      store_key TEXT NOT NULL,
      sku TEXT,
      min_price NUMERIC,
      max_price NUMERIC,
      undercut_by NUMERIC,
      priority INTEGER NOT NULL DEFAULT 0
    );
  `;
  await sql`
    CREATE TABLE IF NOT EXISTS price_actions (
      id SERIAL PRIMARY KEY,
      store_key TEXT NOT NULL,
      sku TEXT NOT NULL,
      old_price NUMERIC NOT NULL,
      new_price NUMERIC NOT NULL,
      reason TEXT NOT NULL DEFAULT '',
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
  `;
  await sql`
    CREATE TABLE IF NOT EXISTS usage_runs (
      id SERIAL PRIMARY KEY,
      user_id INTEGER NOT NULL UNIQUE,
      run_count INTEGER NOT NULL DEFAULT 0,
      period_start TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      last_run_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
  `;
  await sql`
    CREATE TABLE IF NOT EXISTS tariff_plans (
      code TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      max_skus INTEGER NOT NULL,
      price_kzt INTEGER NOT NULL,
      sort_order INTEGER NOT NULL DEFAULT 0
    );
  `;
}

// -- User queries --

export async function findUserByEmail(email: string) {
  const { rows } = await sql`SELECT * FROM users WHERE email = ${email} LIMIT 1;`;
  return rows[0] ?? null;
}

export async function findUserByTelegramId(telegramId: string) {
  const { rows } = await sql`SELECT * FROM users WHERE telegram_id = ${telegramId} LIMIT 1;`;
  return rows[0] ?? null;
}

export async function createUserWithEmail(email: string, passwordHash: string) {
  const { rows } = await sql`
    INSERT INTO users (email, password_hash)
    VALUES (${email}, ${passwordHash})
    RETURNING *;
  `;
  return rows[0];
}

export async function upsertTelegramUser(telegramId: string, username: string | null) {
  const { rows } = await sql`
    INSERT INTO users (telegram_id, telegram_username)
    VALUES (${telegramId}, ${username})
    ON CONFLICT (telegram_id)
    DO UPDATE SET telegram_username = EXCLUDED.telegram_username
    RETURNING *;
  `;
  return rows[0];
}

// -- Store queries --

export async function getStoresForUser(userId: number) {
  const { rows } = await sql`
    SELECT s.*, ss.poll_interval_seconds, ss.turbo_mode, ss.plan_code,
           ss.max_skus, ss.paid_active, ss.plan_started_at
    FROM stores s
    LEFT JOIN store_settings ss ON ss.store_key = s.store_key
    WHERE s.user_id = ${userId}
    ORDER BY s.created_at;
  `;
  return rows;
}

export async function getStoreSettings(storeKey: string) {
  const { rows } = await sql`
    SELECT * FROM store_settings WHERE store_key = ${storeKey} LIMIT 1;
  `;
  return rows[0] ?? null;
}

export async function upsertStoreSettings(
  storeKey: string,
  settings: {
    poll_interval_seconds?: number;
    turbo_mode?: boolean;
    plan_code?: string;
    max_skus?: number;
    paid_active?: boolean;
  }
) {
  const current = await getStoreSettings(storeKey);
  const poll = settings.poll_interval_seconds ?? current?.poll_interval_seconds ?? 120;
  const turbo = settings.turbo_mode ?? current?.turbo_mode ?? false;
  const plan = settings.plan_code ?? current?.plan_code ?? "start_100";
  const maxSkus = settings.max_skus ?? current?.max_skus ?? 100;
  const paid = settings.paid_active ?? current?.paid_active ?? false;

  const { rows } = await sql`
    INSERT INTO store_settings (store_key, poll_interval_seconds, turbo_mode, plan_code, max_skus, paid_active)
    VALUES (${storeKey}, ${poll}, ${turbo}, ${plan}, ${maxSkus}, ${paid})
    ON CONFLICT (store_key)
    DO UPDATE SET
      poll_interval_seconds = EXCLUDED.poll_interval_seconds,
      turbo_mode = EXCLUDED.turbo_mode,
      plan_code = EXCLUDED.plan_code,
      max_skus = EXCLUDED.max_skus,
      paid_active = EXCLUDED.paid_active
    RETURNING *;
  `;
  return rows[0];
}

// -- Price rules --

export async function getPriceRules(storeKey: string) {
  const { rows } = await sql`
    SELECT * FROM price_rules WHERE store_key = ${storeKey} ORDER BY priority DESC;
  `;
  return rows;
}

export async function upsertGlobalRule(
  storeKey: string,
  minPrice: number | null,
  maxPrice: number | null,
  undercutBy: number | null
) {
  const { rows: existing } = await sql`
    SELECT id FROM price_rules WHERE store_key = ${storeKey} AND sku IS NULL LIMIT 1;
  `;
  if (existing.length) {
    await sql`
      UPDATE price_rules SET min_price = ${minPrice}, max_price = ${maxPrice}, undercut_by = ${undercutBy}
      WHERE id = ${existing[0].id};
    `;
  } else {
    await sql`
      INSERT INTO price_rules (store_key, min_price, max_price, undercut_by)
      VALUES (${storeKey}, ${minPrice}, ${maxPrice}, ${undercutBy});
    `;
  }
}

// -- Exclusions --

export async function getExcludedProducts(storeKey: string) {
  const { rows } = await sql`
    SELECT sku FROM excluded_products WHERE store_key = ${storeKey} ORDER BY sku;
  `;
  return rows.map((r) => r.sku as string);
}

export async function setExcludedProducts(storeKey: string, skus: string[]) {
  await sql`DELETE FROM excluded_products WHERE store_key = ${storeKey};`;
  for (const sku of skus) {
    await sql`
      INSERT INTO excluded_products (store_key, sku) VALUES (${storeKey}, ${sku})
      ON CONFLICT DO NOTHING;
    `;
  }
}

export async function getExcludedCompetitors(storeKey: string) {
  const { rows } = await sql`
    SELECT competitor_id FROM excluded_competitors WHERE store_key = ${storeKey} ORDER BY competitor_id;
  `;
  return rows.map((r) => r.competitor_id as string);
}

export async function setExcludedCompetitors(storeKey: string, competitors: string[]) {
  await sql`DELETE FROM excluded_competitors WHERE store_key = ${storeKey};`;
  for (const c of competitors) {
    await sql`
      INSERT INTO excluded_competitors (store_key, competitor_id) VALUES (${storeKey}, ${c})
      ON CONFLICT DO NOTHING;
    `;
  }
}

// -- Price history --

export async function getPriceHistory(storeKey: string, limit = 20) {
  const { rows } = await sql`
    SELECT sku, old_price, new_price, reason, created_at
    FROM price_actions
    WHERE store_key = ${storeKey}
    ORDER BY created_at DESC
    LIMIT ${limit};
  `;
  return rows;
}

// -- Usage / trial --

export async function getUsageRuns(userId: number) {
  const { rows } = await sql`
    SELECT * FROM usage_runs WHERE user_id = ${userId} LIMIT 1;
  `;
  return rows[0] ?? null;
}

// -- Tariffs --

export async function getTariffPlans() {
  const { rows } = await sql`SELECT * FROM tariff_plans ORDER BY sort_order;`;
  return rows;
}
