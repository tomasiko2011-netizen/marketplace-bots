-- skladprobot unified schema (Postgres)
-- Covers: auth users, stores, bot settings, pricing, usage tracking

BEGIN;

-- Users (web + telegram auth)
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  email TEXT UNIQUE,
  password_hash TEXT,
  telegram_id TEXT UNIQUE,
  telegram_username TEXT,
  role TEXT NOT NULL DEFAULT 'user',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Stores linked to user accounts
CREATE TABLE IF NOT EXISTS stores (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  store_key TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL DEFAULT '',
  marketplace TEXT NOT NULL DEFAULT 'kaspi',
  api_token_enc TEXT,
  mode TEXT NOT NULL DEFAULT 'mock',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Per-store settings (intervals, turbo, plan)
CREATE TABLE IF NOT EXISTS store_settings (
  id SERIAL PRIMARY KEY,
  store_key TEXT NOT NULL UNIQUE REFERENCES stores(store_key) ON DELETE CASCADE,
  poll_interval_seconds INTEGER NOT NULL DEFAULT 120,
  turbo_mode BOOLEAN NOT NULL DEFAULT FALSE,
  plan_code TEXT NOT NULL DEFAULT 'start_100',
  max_skus INTEGER NOT NULL DEFAULT 100,
  paid_active BOOLEAN NOT NULL DEFAULT FALSE,
  plan_started_at TIMESTAMPTZ
);

-- Pricing rules per store
CREATE TABLE IF NOT EXISTS price_rules (
  id SERIAL PRIMARY KEY,
  store_key TEXT NOT NULL REFERENCES stores(store_key) ON DELETE CASCADE,
  sku TEXT,
  min_price NUMERIC,
  max_price NUMERIC,
  undercut_by NUMERIC,
  priority INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_price_rules_store ON price_rules(store_key);

-- Product offers cache
CREATE TABLE IF NOT EXISTS offers (
  id SERIAL PRIMARY KEY,
  store_key TEXT NOT NULL REFERENCES stores(store_key) ON DELETE CASCADE,
  sku TEXT NOT NULL,
  title TEXT NOT NULL DEFAULT '',
  ntin TEXT,
  price NUMERIC NOT NULL,
  currency TEXT NOT NULL DEFAULT 'KZT',
  available BOOLEAN NOT NULL DEFAULT TRUE,
  updated_at TIMESTAMPTZ,
  UNIQUE (store_key, sku)
);

-- Excluded products
CREATE TABLE IF NOT EXISTS excluded_products (
  id SERIAL PRIMARY KEY,
  store_key TEXT NOT NULL REFERENCES stores(store_key) ON DELETE CASCADE,
  sku TEXT NOT NULL,
  UNIQUE (store_key, sku)
);

-- Excluded competitors
CREATE TABLE IF NOT EXISTS excluded_competitors (
  id SERIAL PRIMARY KEY,
  store_key TEXT NOT NULL REFERENCES stores(store_key) ON DELETE CASCADE,
  competitor_id TEXT NOT NULL,
  UNIQUE (store_key, competitor_id)
);

-- Price change history
CREATE TABLE IF NOT EXISTS price_actions (
  id SERIAL PRIMARY KEY,
  store_key TEXT NOT NULL REFERENCES stores(store_key) ON DELETE CASCADE,
  sku TEXT NOT NULL,
  old_price NUMERIC NOT NULL,
  new_price NUMERIC NOT NULL,
  reason TEXT NOT NULL DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_price_actions_store ON price_actions(store_key, created_at DESC);

-- Trial / usage run tracking (per user, not per store)
CREATE TABLE IF NOT EXISTS usage_runs (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  run_count INTEGER NOT NULL DEFAULT 0,
  period_start TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_run_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (user_id)
);

-- Bot sessions (telegram chat_id -> store mapping)
CREATE TABLE IF NOT EXISTS bot_sessions (
  chat_id BIGINT PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
  store_key TEXT REFERENCES stores(store_key) ON DELETE SET NULL,
  pending_action TEXT
);

-- Tariff plans reference
CREATE TABLE IF NOT EXISTS tariff_plans (
  code TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  max_skus INTEGER NOT NULL,
  price_kzt INTEGER NOT NULL,
  sort_order INTEGER NOT NULL DEFAULT 0
);

INSERT INTO tariff_plans (code, name, max_skus, price_kzt, sort_order) VALUES
  ('start_100',        'Start 100',        100,   1000, 1),
  ('base_500',         'Base 500',         500,   3000, 2),
  ('pro_2000',         'Pro 2000',        2000,   7000, 3),
  ('business_5000',    'Business 5000',   5000,  15000, 4),
  ('enterprise_20000', 'Enterprise 20000',20000,  30000, 5)
ON CONFLICT (code) DO NOTHING;

COMMIT;
