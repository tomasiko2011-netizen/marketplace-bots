# Architecture: Marketplace Bots (KZ)

## Goals
- One core engine for pricing/monitoring across multiple marketplaces.
- Each marketplace integrates via a thin adapter (official APIs only).
- Clear audit trail for every price change.
- Scalable scheduling (jobs/queues) and safe retry logic.

## Components

### 1) Adapter Layer (per marketplace)
Each adapter implements a shared interface:
- `fetch_offers()` - list products/offer prices
- `fetch_orders()` - list recent orders
- `update_prices(price_updates)` - push price changes
- `health_check()` - validate credentials and API access

Adapters are registered in a registry so the core engine is marketplace-agnostic.

### 2) Core Engine
- Pricing rules engine (min/max/step/blacklist/whitelist)
- Decision trace (why a price changed)
- Rate-limiting and safe retries

### 3) Scheduler / Workers
- Cron-based polling
- Queue workers for heavy tasks
- Priority lanes for “turbo” SKUs

### 4) Data Layer
- Stores, credentials, products, offers, price history, rules
- Strict audit for every change

### 5) Admin / Ops
- Logs, metrics, and alerting
- Manual override tooling

## Adapter Flow (Pricing)
1) `fetch_offers()` -> raw offer list
2) `apply_rules()` -> proposed price changes
3) `update_prices()` -> push updates to marketplace
4) write `price_history` + `price_actions`

## Security / Compliance
- Use official APIs only
- Store tokens encrypted (KMS or vault)
- Least-privilege access per store
- Immutable audit logs for pricing actions

## Marketplaces (initial adapters)
- Kaspi
- Wildberries
- Ozon
- Halyk Market
- Jusan Market
- Forte Market
- Lamoda

Each marketplace has different API/partner policies; adapters should be enabled only if official access is confirmed.
