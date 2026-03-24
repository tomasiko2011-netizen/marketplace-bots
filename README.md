# Marketplace Bots (KZ) - Skeleton

This is a pragmatic, API-first skeleton for marketplace bots in Kazakhstan. It uses an adapter pattern so each marketplace integrates via a small, isolated module while the core logic remains the same.

Status:
- Architecture and DB schema are included.
- A working **Kaspi adapter in mock mode** is included so you can run end-to-end without API keys.
- Live API calls are stubbed and ready to be filled once you obtain official API access.

## Structure
- `docs/architecture.md` - system architecture and adapter design
- `docs/db_schema.sql` - database schema (PostgreSQL flavored SQL)
- `src/mp_bots` - core service code
- `examples/` - sample config and mock offers

## Quick start (mock run)
```
python3 -m mp_bots.cli init-db --db /Users/guldana/Documents/New\ project/marketplace-bots/tmp/dev.db
python3 -m mp_bots.cli sync --marketplace kaspi --mode mock --input /Users/guldana/Documents/New\ project/marketplace-bots/examples/kaspi_mock_offers.json --db /Users/guldana/Documents/New\ project/marketplace-bots/tmp/dev.db
```

Notes:
- This uses SQLite locally for convenience. The schema file is PostgreSQL-flavored for production.
- Replace mock with live once you have official API details and credentials.

## Turbo + exclusions (mock)
```
python3 -m mp_bots.cli set-exclusions --db /Users/guldana/Documents/New\ project/marketplace-bots/tmp/dev.db --skus KSP-003
python3 -m mp_bots.cli run --marketplace kaspi --mode mock --input /Users/guldana/Documents/New\ project/marketplace-bots/examples/kaspi_mock_offers.json --rules /Users/guldana/Documents/New\ project/marketplace-bots/examples/rules.json --db /Users/guldana/Documents/New\ project/marketplace-bots/tmp/dev.db --turbo --iterations 3
```

## Telegram bot (admin)
Requirements:
- `python-telegram-bot` (v20+)

Run:
```
export TELEGRAM_BOT_TOKEN=...          # do not commit tokens
export ADMIN_CHAT_IDS=123456789        # comma-separated chat IDs (optional)
export MP_BOTS_DB=/Users/guldana/Documents/New\ project/marketplace-bots/tmp/dev.db
export MP_BOTS_STORES=/Users/guldana/Documents/New\ project/marketplace-bots/config/stores.sample.json
python3 -m mp_bots.bot.telegram_bot
```

## skladprobot requirements
See `docs/requirements.md` for the Russian-language requirements and cycle description.
