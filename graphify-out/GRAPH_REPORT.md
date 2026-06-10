# Graph Report - .  (2026-06-11)

## Corpus Check
- Corpus is ~17,574 words - fits in a single context window. You may not need a graph.

## Summary
- 539 nodes · 1073 edges · 46 communities (31 shown, 15 thin omitted)
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 204 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Marketplace Adapter Base|Marketplace Adapter Base]]
- [[_COMMUNITY_Telegram Bot Commands|Telegram Bot Commands]]
- [[_COMMUNITY_Auth & CSRF Middleware|Auth & CSRF Middleware]]
- [[_COMMUNITY_Kaspi Adapter & Registry|Kaspi Adapter & Registry]]
- [[_COMMUNITY_PostgreSQL Database Layer|PostgreSQL Database Layer]]
- [[_COMMUNITY_CLI Entry & SQLite Init|CLI Entry & SQLite Init]]
- [[_COMMUNITY_Dashboard Data & DB Access|Dashboard Data & DB Access]]
- [[_COMMUNITY_MiniApp Package Config|MiniApp Package Config]]
- [[_COMMUNITY_Database Interface Tests|Database Interface Tests]]
- [[_COMMUNITY_DB Abstract Interface|DB Abstract Interface]]
- [[_COMMUNITY_SQLite DB Implementation|SQLite DB Implementation]]
- [[_COMMUNITY_MiniApp TypeScript Config|MiniApp TypeScript Config]]
- [[_COMMUNITY_Architecture Docs & MiniApp Deployment|Architecture Docs & MiniApp Deployment]]
- [[_COMMUNITY_DB Adapter Offer & Plan Methods|DB Adapter Offer & Plan Methods]]
- [[_COMMUNITY_DB Adapter Exclusion & Rules Methods|DB Adapter Exclusion & Rules Methods]]
- [[_COMMUNITY_Admin Routes & Export|Admin Routes & Export]]
- [[_COMMUNITY_Dashboard UI Page|Dashboard UI Page]]
- [[_COMMUNITY_Domain Model Unit Tests|Domain Model Unit Tests]]
- [[_COMMUNITY_App Layout & Fonts|App Layout & Fonts]]
- [[_COMMUNITY_App Pages Navigation|App Pages Navigation]]
- [[_COMMUNITY_DB Interface Module Root|DB Interface Module Root]]
- [[_COMMUNITY_Telegram Runner Entry Point|Telegram Runner Entry Point]]
- [[_COMMUNITY_Login & Telegram Auth Page|Login & Telegram Auth Page]]
- [[_COMMUNITY_Claude Local Settings|Claude Local Settings]]
- [[_COMMUNITY_KZ Regions Geo Data|KZ Regions Geo Data]]
- [[_COMMUNITY_MiniApp Next.js Config|MiniApp Next.js Config]]
- [[_COMMUNITY_Proxy Config|Proxy Config]]
- [[_COMMUNITY_Sample Stores Config|Sample Stores Config]]
- [[_COMMUNITY_Kaspi Mock Offers Example|Kaspi Mock Offers Example]]
- [[_COMMUNITY_Pricing Rules Example|Pricing Rules Example]]
- [[_COMMUNITY_MiniApp ESLint Config|MiniApp ESLint Config]]
- [[_COMMUNITY_MiniApp PostCSS Config|MiniApp PostCSS Config]]

## God Nodes (most connected - your core abstractions)
1. `Offer` - 56 edges
2. `PriceDecision` - 55 edges
3. `MarketplaceAdapter` - 43 edges
4. `DB` - 37 edges
5. `SQLiteDB` - 37 edges
6. `PostgresDB` - 31 edges
7. `PostgresDBAdapter` - 29 edges
8. `KaspiAdapter` - 26 edges
9. `PriceRule` - 20 edges
10. `DEFAULT_TYPE` - 19 edges

## Surprising Connections (you probably didn't know these)
- `TestAdapterContract` --uses--> `MarketplaceAdapter`  [INFERRED]
  tests/test_adapter.py → src/mp_bots/adapters/base.py
- `TestAdapterRegistry` --uses--> `MarketplaceAdapter`  [INFERRED]
  tests/test_adapter.py → src/mp_bots/adapters/base.py
- `TestKaspiLiveAdapter` --uses--> `MarketplaceAdapter`  [INFERRED]
  tests/test_adapter.py → src/mp_bots/adapters/base.py
- `TestKaspiMockAdapter` --uses--> `MarketplaceAdapter`  [INFERRED]
  tests/test_adapter.py → src/mp_bots/adapters/base.py
- `TestAdapterContract` --uses--> `Offer`  [INFERRED]
  tests/test_adapter.py → src/mp_bots/core/models.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Core pricing loop: scheduler triggers engine, engine calls adapter to fetch offers and push price updates** — architecture_scheduler, architecture_pricing_rules_engine, architecture_adapter_layer [INFERRED]
- **Turbo mode triad: SkladProBot 30s cycle requires priority scheduling lane in the scheduler** — docs_requirements_turbo_mode, docs_requirements_skladprobot, architecture_scheduler [INFERRED]
- **Telegram mini-app auth: JWT validates Telegram initData to grant admin access via the bot** — miniapp_miniapp, miniapp_jwt, readme_telegram_bot [INFERRED]

## Communities (46 total, 15 thin omitted)

### Community 0 - "Marketplace Adapter Base"
Cohesion: 0.05
Nodes (45): ABC, MarketplaceAdapter, ForteAdapter, HalykAdapter, JusanAdapter, LamodaAdapter, OzonAdapter, WildberriesAdapter (+37 more)

### Community 1 - "Telegram Bot Commands"
Cohesion: 0.19
Nodes (37): Any, build_adapter(), cmd_admin_reset_runs(), cmd_admin_set_plan(), cmd_exclude_sku(), cmd_interval(), cmd_rules(), cmd_run_once() (+29 more)

### Community 2 - "Auth & CSRF Middleware"
Cohesion: 0.15
Nodes (27): GET(), ADMIN_EMAILS, ADMIN_TELEGRAM_IDS, hashPassword(), resolveRoleByEmail(), resolveRoleByTelegramId(), rotateSession(), SESSION_TTL_SEC (+19 more)

### Community 3 - "Kaspi Adapter & Registry"
Cohesion: 0.11
Nodes (11): KaspiAdapter, get_adapter(), Offer, PriceDecision, MarketplaceAdapter, Tests for adapter contract (mock/live boundary)., Verify the adapter base class contract., TestAdapterContract (+3 more)

### Community 4 - "PostgreSQL Database Layer"
Cohesion: 0.13
Nodes (4): PostgresDB, Postgres data layer for skladprobot.  Mirrors the sqlite.py interface but uses p, Offer, PriceDecision

### Community 5 - "CLI Entry & SQLite Init"
Cohesion: 0.12
Nodes (13): init_db(), cmd_init_db(), cmd_run(), _cmd_set_exclusions(), cmd_sync(), _load_rules(), main(), Namespace (+5 more)

### Community 6 - "Dashboard Data & DB Access"
Cohesion: 0.16
Nodes (19): getSessionPayloadFromRequest(), DashboardData, getDashboardForUser(), PriceAction, StoreOverview, getExcludedCompetitors(), getExcludedProducts(), getPriceHistory() (+11 more)

### Community 7 - "MiniApp Package Config"
Cohesion: 0.08
Nodes (25): dependencies, bcryptjs, jose, next, react, react-dom, @vercel/postgres, devDependencies (+17 more)

### Community 8 - "Database Interface Tests"
Cohesion: 0.13
Nodes (9): Tests for the unified DB interface (SQLite backend)., TestExclusions, TestOffers, TestPlan, TestPriceActions, TestRules, TestSessions, TestSettings (+1 more)

### Community 11 - "MiniApp TypeScript Config"
Cohesion: 0.10
Nodes (19): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+11 more)

### Community 12 - "Architecture Docs & MiniApp Deployment"
Cohesion: 0.12
Nodes (18): Adapter Layer (per-marketplace), Immutable Audit Trail, Data Layer, Halyk Market, Ozon, Pricing Rules Engine, Scheduler / Workers, Wildberries (+10 more)

### Community 15 - "Admin Routes & Export"
Cohesion: 0.30
Nodes (8): GET(), GET(), AdminData, AdminStore, AdminUser, getAdminData(), toCsv(), requireAdmin()

### Community 16 - "Dashboard UI Page"
Cohesion: 0.22
Nodes (5): DashboardData, PriceAction, Store, StoreDetail, Tariff

### Community 18 - "App Layout & Fonts"
Cohesion: 0.40
Nodes (3): geistMono, geistSans, metadata

### Community 19 - "App Pages Navigation"
Cohesion: 0.40
Nodes (3): portfolio, products, stats

### Community 20 - "DB Interface Module Root"
Cohesion: 0.40
Nodes (3): get_db(), Unified DB interface for skladprobot.  Provides a single API that delegates to e, Return a singleton DB instance based on env config.      - DATABASE_URL set -> P

### Community 21 - "Telegram Runner Entry Point"
Cohesion: 0.40
Nodes (4): MP_BOTS_DB, MP_BOTS_STORES, PYTHONPATH, run_telegram.sh script

## Knowledge Gaps
- **86 isolated node(s):** `allow`, `stores`, `offers`, `rules`, `eslintConfig` (+81 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Offer` connect `Marketplace Adapter Base` to `Kaspi Adapter & Registry`, `PostgreSQL Database Layer`, `Database Interface Tests`, `DB Abstract Interface`, `DB Adapter Offer & Plan Methods`, `DB Adapter Exclusion & Rules Methods`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **Why does `DB` connect `DB Abstract Interface` to `Marketplace Adapter Base`, `Telegram Bot Commands`, `PostgreSQL Database Layer`, `DB Adapter Offer & Plan Methods`, `DB Adapter Exclusion & Rules Methods`, `DB Interface Module Root`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `PriceDecision` connect `Marketplace Adapter Base` to `Kaspi Adapter & Registry`, `PostgreSQL Database Layer`, `Database Interface Tests`, `DB Abstract Interface`, `DB Adapter Offer & Plan Methods`, `DB Adapter Exclusion & Rules Methods`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Are the 53 inferred relationships involving `Offer` (e.g. with `MarketplaceAdapter` and `ForteAdapter`) actually correct?**
  _`Offer` has 53 INFERRED edges - model-reasoned connections that need verification._
- **Are the 51 inferred relationships involving `PriceDecision` (e.g. with `MarketplaceAdapter` and `ForteAdapter`) actually correct?**
  _`PriceDecision` has 51 INFERRED edges - model-reasoned connections that need verification._
- **Are the 28 inferred relationships involving `MarketplaceAdapter` (e.g. with `Offer` and `PriceDecision`) actually correct?**
  _`MarketplaceAdapter` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `DB` (e.g. with `Any` and `Scheduler`) actually correct?**
  _`DB` has 10 INFERRED edges - model-reasoned connections that need verification._