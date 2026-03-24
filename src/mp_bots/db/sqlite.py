from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from mp_bots.core.models import Offer, PriceDecision


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS offers (
  store_key TEXT NOT NULL DEFAULT 'default',
  sku TEXT NOT NULL,
  title TEXT NOT NULL,
  ntin TEXT,
  price REAL NOT NULL,
  currency TEXT NOT NULL,
  available INTEGER NOT NULL,
  updated_at TEXT,
  PRIMARY KEY (store_key, sku)
);

CREATE TABLE IF NOT EXISTS store_settings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  store_key TEXT NOT NULL DEFAULT 'default',
  poll_interval_seconds INTEGER NOT NULL DEFAULT 120,
  turbo_mode INTEGER NOT NULL DEFAULT 0,
  plan_code TEXT NOT NULL DEFAULT 'start_100',
  max_skus INTEGER NOT NULL DEFAULT 100,
  paid_active INTEGER NOT NULL DEFAULT 0,
  plan_started_at TEXT
);

CREATE TABLE IF NOT EXISTS price_rules (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  store_key TEXT NOT NULL DEFAULT 'default',
  min_price REAL,
  max_price REAL,
  undercut_by REAL
);

CREATE TABLE IF NOT EXISTS excluded_products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  store_key TEXT NOT NULL DEFAULT 'default',
  sku TEXT NOT NULL,
  UNIQUE (store_key, sku)
);

CREATE TABLE IF NOT EXISTS excluded_competitors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  store_key TEXT NOT NULL DEFAULT 'default',
  competitor_id TEXT NOT NULL,
  UNIQUE (store_key, competitor_id)
);

CREATE TABLE IF NOT EXISTS bot_sessions (
  chat_id INTEGER PRIMARY KEY,
  store_key TEXT NOT NULL,
  pending_action TEXT
);

CREATE TABLE IF NOT EXISTS usage_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  chat_id INTEGER NOT NULL UNIQUE,
  run_count INTEGER NOT NULL DEFAULT 0,
  period_start TEXT,
  last_run_at TEXT
);

CREATE TABLE IF NOT EXISTS price_actions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sku TEXT NOT NULL,
  old_price REAL NOT NULL,
  new_price REAL NOT NULL,
  reason TEXT NOT NULL,
  created_at TEXT NOT NULL
);
"""


def init_db(db_path: str) -> None:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        # Lightweight migration for older dbs
        try:
            conn.execute("ALTER TABLE bot_sessions ADD COLUMN pending_action TEXT")
        except sqlite3.OperationalError:
            pass
        for table, column in (
            ("store_settings", "store_key"),
            ("price_rules", "store_key"),
            ("excluded_products", "store_key"),
            ("excluded_competitors", "store_key"),
        ):
            try:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} TEXT NOT NULL DEFAULT 'default'")
            except sqlite3.OperationalError:
                pass
        for column, default in (("plan_code", "start_100"), ("max_skus", "100")):
            try:
                conn.execute(
                    f"ALTER TABLE store_settings ADD COLUMN {column} "
                    f"{'TEXT' if column == 'plan_code' else 'INTEGER'} NOT NULL DEFAULT '{default}'"
                )
            except sqlite3.OperationalError:
                pass
        for column, default in (("paid_active", "0"), ("plan_started_at", "")):
            try:
                conn.execute(
                    f"ALTER TABLE store_settings ADD COLUMN {column} "
                    f"{'INTEGER' if column == 'paid_active' else 'TEXT'} NOT NULL DEFAULT '{default}'"
                )
            except sqlite3.OperationalError:
                pass
        try:
            conn.execute("ALTER TABLE offers ADD COLUMN store_key TEXT NOT NULL DEFAULT 'default'")
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute("ALTER TABLE offers ADD COLUMN ntin TEXT")
        except sqlite3.OperationalError:
            pass
        conn.commit()


def upsert_offers(db_path: str, store_key: str, offers: Iterable[Offer]) -> None:
    with sqlite3.connect(db_path) as conn:
        for offer in offers:
            conn.execute(
                """
                INSERT INTO offers (store_key, sku, title, ntin, price, currency, available, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(store_key, sku) DO UPDATE SET
                  title=excluded.title,
                  ntin=excluded.ntin,
                  price=excluded.price,
                  currency=excluded.currency,
                  available=excluded.available,
                  updated_at=excluded.updated_at
                """,
                (
                    store_key,
                    offer.sku,
                    offer.title,
                    offer.ntin,
                    offer.price,
                    offer.currency,
                    1 if offer.available else 0,
                    offer.updated_at.isoformat() if offer.updated_at else None,
                ),
            )
        conn.commit()


def write_price_actions(db_path: str, actions: Iterable[PriceDecision]) -> None:
    from datetime import datetime

    created_at = datetime.utcnow().isoformat()
    with sqlite3.connect(db_path) as conn:
        for action in actions:
            conn.execute(
                """
                INSERT INTO price_actions (sku, old_price, new_price, reason, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    action.sku,
                    action.old_price,
                    action.new_price,
                    action.reason,
                    created_at,
                ),
            )
        conn.commit()


def get_price_actions(db_path: str, limit: int = 10) -> list[tuple[str, float, float, str, str]]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT sku, old_price, new_price, reason, created_at FROM price_actions "
            "ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return rows


def set_settings(
    db_path: str,
    store_key: str,
    poll_interval_seconds: int | None = None,
    turbo_mode: bool | None = None,
) -> None:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT id, poll_interval_seconds, turbo_mode FROM store_settings WHERE store_key=? LIMIT 1",
            (store_key,),
        ).fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO store_settings (store_key, poll_interval_seconds, turbo_mode) VALUES (?, ?, ?)",
                (
                    store_key,
                    poll_interval_seconds if poll_interval_seconds is not None else 120,
                    1 if turbo_mode else 0,
                ),
            )
        else:
            current_id, current_poll, current_turbo = row
            conn.execute(
                "UPDATE store_settings SET poll_interval_seconds=?, turbo_mode=? WHERE id=?",
                (
                    poll_interval_seconds if poll_interval_seconds is not None else current_poll,
                    1 if turbo_mode else current_turbo,
                    current_id,
                ),
            )
        conn.commit()


def get_settings(db_path: str, store_key: str) -> tuple[int, bool]:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT poll_interval_seconds, turbo_mode FROM store_settings WHERE store_key=? LIMIT 1",
            (store_key,),
        ).fetchone()
        if row is None:
            return 120, False
        poll_interval_seconds, turbo_mode = row
        return int(poll_interval_seconds), bool(turbo_mode)


def get_plan(db_path: str, store_key: str) -> tuple[str, int, bool, str | None]:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT plan_code, max_skus, paid_active, plan_started_at FROM store_settings WHERE store_key=? LIMIT 1",
            (store_key,),
        ).fetchone()
        if row is None:
            return "start_100", 100, False, None
        return str(row[0]), int(row[1]), bool(row[2]), row[3]


def set_plan(
    db_path: str,
    store_key: str,
    plan_code: str,
    max_skus: int,
    paid_active: bool,
    plan_started_at: str | None,
) -> None:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT id FROM store_settings WHERE store_key=? LIMIT 1",
            (store_key,),
        ).fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO store_settings (store_key, poll_interval_seconds, turbo_mode, plan_code, max_skus, paid_active, plan_started_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (store_key, 120, 0, plan_code, max_skus, 1 if paid_active else 0, plan_started_at),
            )
        else:
            conn.execute(
                "UPDATE store_settings SET plan_code=?, max_skus=?, paid_active=?, plan_started_at=? WHERE store_key=?",
                (plan_code, max_skus, 1 if paid_active else 0, plan_started_at, store_key),
            )
        conn.commit()


def set_excluded_products(db_path: str, store_key: str, skus: Iterable[str]) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM excluded_products WHERE store_key=?", (store_key,))
        for sku in skus:
            conn.execute(
                "INSERT OR IGNORE INTO excluded_products (store_key, sku) VALUES (?, ?)",
                (store_key, sku),
            )
        conn.commit()


def get_excluded_products(db_path: str, store_key: str) -> set[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT sku FROM excluded_products WHERE store_key=?", (store_key,)).fetchall()
        return {r[0] for r in rows}


def set_excluded_competitors(db_path: str, store_key: str, competitors: Iterable[str]) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM excluded_competitors WHERE store_key=?", (store_key,))
        for comp in competitors:
            conn.execute(
                "INSERT OR IGNORE INTO excluded_competitors (store_key, competitor_id) VALUES (?, ?)",
                (store_key, comp),
            )
        conn.commit()


def get_excluded_competitors(db_path: str, store_key: str) -> set[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT competitor_id FROM excluded_competitors WHERE store_key=?",
            (store_key,),
        ).fetchall()
        return {r[0] for r in rows}


def set_rules(
    db_path: str,
    store_key: str,
    min_price: float | None = None,
    max_price: float | None = None,
    undercut_by: float | None = None,
) -> None:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT id FROM price_rules WHERE store_key=? LIMIT 1", (store_key,)).fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO price_rules (store_key, min_price, max_price, undercut_by) VALUES (?, ?, ?, ?)",
                (store_key, min_price, max_price, undercut_by),
            )
        else:
            rule_id = row[0]
            conn.execute(
                "UPDATE price_rules SET min_price=?, max_price=?, undercut_by=? WHERE id=?",
                (min_price, max_price, undercut_by, rule_id),
            )
        conn.commit()


def get_rules(db_path: str, store_key: str) -> tuple[float | None, float | None, float | None]:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT min_price, max_price, undercut_by FROM price_rules WHERE store_key=? LIMIT 1",
            (store_key,),
        ).fetchone()
        if row is None:
            return None, None, None
        return row[0], row[1], row[2]


def set_session_store(db_path: str, chat_id: int, store_key: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO bot_sessions (chat_id, store_key) VALUES (?, ?) "
            "ON CONFLICT(chat_id) DO UPDATE SET store_key=excluded.store_key",
            (chat_id, store_key),
        )
        conn.commit()


def get_session_store(db_path: str, chat_id: int) -> str | None:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT store_key FROM bot_sessions WHERE chat_id=?", (chat_id,)).fetchone()
        return row[0] if row else None


def set_pending_action(db_path: str, chat_id: int, action: str | None) -> None:
    current_store = get_session_store(db_path, chat_id)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO bot_sessions (chat_id, store_key, pending_action) VALUES (?, ?, ?) "
            "ON CONFLICT(chat_id) DO UPDATE SET pending_action=excluded.pending_action",
            (chat_id, current_store or "default", action),
        )
        conn.commit()


def get_pending_action(db_path: str, chat_id: int) -> str | None:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT pending_action FROM bot_sessions WHERE chat_id=?", (chat_id,)).fetchone()
        return row[0] if row else None


def get_run_count(db_path: str, chat_id: int) -> int:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT run_count FROM usage_runs WHERE chat_id=?", (chat_id,)).fetchone()
        return int(row[0]) if row else 0


def get_run_count_checked(db_path: str, chat_id: int, plan_started_at: str | None) -> int:
    from datetime import datetime

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT id, run_count, period_start FROM usage_runs WHERE chat_id=?",
            (chat_id,),
        ).fetchone()
        if row is None:
            return 0
        run_id, run_count, period_start = row
        now = datetime.utcnow()
        reset_needed = False
        if period_start:
            try:
                from datetime import datetime as dt
                start_dt = dt.fromisoformat(period_start)
                if (now - start_dt).days >= 30:
                    reset_needed = True
            except Exception:
                reset_needed = True
        else:
            reset_needed = True

        if plan_started_at:
            try:
                from datetime import datetime as dt
                plan_dt = dt.fromisoformat(plan_started_at)
                if not period_start or plan_dt > dt.fromisoformat(period_start):
                    reset_needed = True
            except Exception:
                reset_needed = True

        if reset_needed:
            conn.execute(
                "UPDATE usage_runs SET run_count=?, period_start=?, last_run_at=? WHERE id=?",
                (0, now.isoformat(), now.isoformat(), run_id),
            )
            conn.commit()
            return 0

        return int(run_count)


def increment_run_count(db_path: str, chat_id: int, plan_started_at: str | None) -> int:
    from datetime import datetime

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT id, run_count, period_start FROM usage_runs WHERE chat_id=?",
            (chat_id,),
        ).fetchone()
        now = datetime.utcnow()
        if row is None:
            conn.execute(
                "INSERT INTO usage_runs (chat_id, run_count, period_start, last_run_at) VALUES (?, ?, ?, ?)",
                (chat_id, 1, now.isoformat(), now.isoformat()),
            )
            conn.commit()
            return 1
        run_id, run_count, period_start = row
        reset_needed = False
        if period_start:
            try:
                from datetime import datetime as dt
                start_dt = dt.fromisoformat(period_start)
                if (now - start_dt).days >= 30:
                    reset_needed = True
            except Exception:
                reset_needed = True
        else:
            reset_needed = True

        if plan_started_at:
            try:
                from datetime import datetime as dt
                plan_dt = dt.fromisoformat(plan_started_at)
                if not period_start or plan_dt > dt.fromisoformat(period_start):
                    reset_needed = True
            except Exception:
                reset_needed = True

        if reset_needed:
            conn.execute(
                "UPDATE usage_runs SET run_count=?, period_start=?, last_run_at=? WHERE id=?",
                (1, now.isoformat(), now.isoformat(), run_id),
            )
            conn.commit()
            return 1

        new_count = int(run_count) + 1
        conn.execute(
            "UPDATE usage_runs SET run_count=?, last_run_at=? WHERE id=?",
            (new_count, now.isoformat(), run_id),
        )
        conn.commit()
        return new_count


def reset_run_count(db_path: str, chat_id: int) -> None:
    from datetime import datetime

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT id FROM usage_runs WHERE chat_id=?",
            (chat_id,),
        ).fetchone()
        now = datetime.utcnow().isoformat()
        if row is None:
            conn.execute(
                "INSERT INTO usage_runs (chat_id, run_count, period_start, last_run_at) VALUES (?, ?, ?, ?)",
                (chat_id, 0, now, now),
            )
        else:
            run_id = row[0]
            conn.execute(
                "UPDATE usage_runs SET run_count=?, period_start=?, last_run_at=? WHERE id=?",
                (0, now, now, run_id),
            )
        conn.commit()
