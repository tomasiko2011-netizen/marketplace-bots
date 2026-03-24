"""Postgres data layer for skladprobot.

Mirrors the sqlite.py interface but uses psycopg2 and the unified
Postgres schema from migrations/001_init.sql.

Usage:
    from mp_bots.db.postgres import PostgresDB
    db = PostgresDB(os.environ["DATABASE_URL"])
    db.get_settings("my_store")
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Iterable

import psycopg2
import psycopg2.extras

from mp_bots.core.models import Offer, PriceDecision


class PostgresDB:
    def __init__(self, dsn: str | None = None):
        self.dsn = dsn or os.environ.get("DATABASE_URL", "")
        if not self.dsn:
            raise RuntimeError("DATABASE_URL not set")

    @contextmanager
    def _conn(self):
        conn = psycopg2.connect(self.dsn)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # -- Offers --

    def upsert_offers(self, store_key: str, offers: Iterable[Offer]) -> None:
        with self._conn() as conn:
            cur = conn.cursor()
            for o in offers:
                cur.execute(
                    """
                    INSERT INTO offers (store_key, sku, title, ntin, price, currency, available, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (store_key, sku) DO UPDATE SET
                      title=EXCLUDED.title, ntin=EXCLUDED.ntin, price=EXCLUDED.price,
                      currency=EXCLUDED.currency, available=EXCLUDED.available, updated_at=EXCLUDED.updated_at
                    """,
                    (store_key, o.sku, o.title, o.ntin, o.price, o.currency, o.available,
                     o.updated_at.isoformat() if o.updated_at else None),
                )

    # -- Price actions --

    def write_price_actions(self, store_key: str, actions: Iterable[PriceDecision]) -> None:
        now = datetime.utcnow()
        with self._conn() as conn:
            cur = conn.cursor()
            for a in actions:
                cur.execute(
                    "INSERT INTO price_actions (store_key, sku, old_price, new_price, reason, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (store_key, a.sku, a.old_price, a.new_price, a.reason, now),
                )

    def get_price_actions(self, store_key: str, limit: int = 10):
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT sku, old_price, new_price, reason, created_at "
                "FROM price_actions WHERE store_key=%s ORDER BY created_at DESC LIMIT %s",
                (store_key, limit),
            )
            return cur.fetchall()

    # -- Settings --

    def get_settings(self, store_key: str) -> tuple[int, bool]:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT poll_interval_seconds, turbo_mode FROM store_settings WHERE store_key=%s LIMIT 1",
                (store_key,),
            )
            row = cur.fetchone()
            if not row:
                return 120, False
            return int(row[0]), bool(row[1])

    def set_settings(self, store_key: str, poll_interval_seconds: int | None = None, turbo_mode: bool | None = None):
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, poll_interval_seconds, turbo_mode FROM store_settings WHERE store_key=%s", (store_key,))
            row = cur.fetchone()
            poll = poll_interval_seconds if poll_interval_seconds is not None else (row[1] if row else 120)
            turbo = turbo_mode if turbo_mode is not None else (bool(row[2]) if row else False)
            if row is None:
                cur.execute(
                    "INSERT INTO store_settings (store_key, poll_interval_seconds, turbo_mode) VALUES (%s, %s, %s)",
                    (store_key, poll, turbo),
                )
            else:
                cur.execute(
                    "UPDATE store_settings SET poll_interval_seconds=%s, turbo_mode=%s WHERE id=%s",
                    (poll, turbo, row[0]),
                )

    # -- Plan --

    def get_plan(self, store_key: str) -> tuple[str, int, bool, str | None]:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT plan_code, max_skus, paid_active, plan_started_at FROM store_settings WHERE store_key=%s LIMIT 1",
                (store_key,),
            )
            row = cur.fetchone()
            if not row:
                return "start_100", 100, False, None
            return str(row[0]), int(row[1]), bool(row[2]), str(row[3]) if row[3] else None

    def set_plan(self, store_key: str, plan_code: str, max_skus: int, paid_active: bool, plan_started_at: str | None):
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM store_settings WHERE store_key=%s", (store_key,))
            row = cur.fetchone()
            if row is None:
                cur.execute(
                    "INSERT INTO store_settings (store_key, plan_code, max_skus, paid_active, plan_started_at) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (store_key, plan_code, max_skus, paid_active, plan_started_at),
                )
            else:
                cur.execute(
                    "UPDATE store_settings SET plan_code=%s, max_skus=%s, paid_active=%s, plan_started_at=%s WHERE store_key=%s",
                    (plan_code, max_skus, paid_active, plan_started_at, store_key),
                )

    # -- Rules --

    def get_rules(self, store_key: str) -> tuple[float | None, float | None, float | None]:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT min_price, max_price, undercut_by FROM price_rules WHERE store_key=%s AND sku IS NULL LIMIT 1", (store_key,))
            row = cur.fetchone()
            if not row:
                return None, None, None
            return row[0], row[1], row[2]

    def set_rules(self, store_key: str, min_price=None, max_price=None, undercut_by=None):
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM price_rules WHERE store_key=%s AND sku IS NULL LIMIT 1", (store_key,))
            row = cur.fetchone()
            if row is None:
                cur.execute(
                    "INSERT INTO price_rules (store_key, min_price, max_price, undercut_by) VALUES (%s, %s, %s, %s)",
                    (store_key, min_price, max_price, undercut_by),
                )
            else:
                cur.execute(
                    "UPDATE price_rules SET min_price=%s, max_price=%s, undercut_by=%s WHERE id=%s",
                    (min_price, max_price, undercut_by, row[0]),
                )

    # -- Exclusions --

    def get_excluded_products(self, store_key: str) -> set[str]:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT sku FROM excluded_products WHERE store_key=%s", (store_key,))
            return {r[0] for r in cur.fetchall()}

    def set_excluded_products(self, store_key: str, skus: Iterable[str]):
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM excluded_products WHERE store_key=%s", (store_key,))
            for sku in skus:
                cur.execute("INSERT INTO excluded_products (store_key, sku) VALUES (%s, %s) ON CONFLICT DO NOTHING", (store_key, sku))

    def get_excluded_competitors(self, store_key: str) -> set[str]:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT competitor_id FROM excluded_competitors WHERE store_key=%s", (store_key,))
            return {r[0] for r in cur.fetchall()}

    def set_excluded_competitors(self, store_key: str, competitors: Iterable[str]):
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM excluded_competitors WHERE store_key=%s", (store_key,))
            for c in competitors:
                cur.execute("INSERT INTO excluded_competitors (store_key, competitor_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (store_key, c))

    # -- Sessions --

    def get_session_store(self, chat_id: int) -> str | None:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT store_key FROM bot_sessions WHERE chat_id=%s", (chat_id,))
            row = cur.fetchone()
            return row[0] if row else None

    def set_session_store(self, chat_id: int, store_key: str):
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO bot_sessions (chat_id, store_key) VALUES (%s, %s) "
                "ON CONFLICT (chat_id) DO UPDATE SET store_key=EXCLUDED.store_key",
                (chat_id, store_key),
            )

    def get_pending_action(self, chat_id: int) -> str | None:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT pending_action FROM bot_sessions WHERE chat_id=%s", (chat_id,))
            row = cur.fetchone()
            return row[0] if row else None

    def set_pending_action(self, chat_id: int, action: str | None):
        store = self.get_session_store(chat_id)
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO bot_sessions (chat_id, store_key, pending_action) VALUES (%s, %s, %s) "
                "ON CONFLICT (chat_id) DO UPDATE SET pending_action=EXCLUDED.pending_action",
                (chat_id, store or "default", action),
            )

    # -- Usage runs (per user_id) --

    def get_run_count_checked(self, user_id: int, plan_started_at: str | None) -> int:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, run_count, period_start FROM usage_runs WHERE user_id=%s", (user_id,))
            row = cur.fetchone()
            if not row:
                return 0
            run_id, run_count, period_start = row
            now = datetime.utcnow()
            reset = False

            if period_start:
                if (now - period_start).days >= 30:
                    reset = True
            else:
                reset = True

            if plan_started_at:
                try:
                    plan_dt = datetime.fromisoformat(str(plan_started_at))
                    if not period_start or plan_dt > period_start:
                        reset = True
                except Exception:
                    reset = True

            if reset:
                cur.execute("UPDATE usage_runs SET run_count=0, period_start=%s, last_run_at=%s WHERE id=%s", (now, now, run_id))
                return 0
            return int(run_count)

    def increment_run_count(self, user_id: int, plan_started_at: str | None) -> int:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, run_count, period_start FROM usage_runs WHERE user_id=%s", (user_id,))
            row = cur.fetchone()
            now = datetime.utcnow()
            if not row:
                cur.execute(
                    "INSERT INTO usage_runs (user_id, run_count, period_start, last_run_at) VALUES (%s, 1, %s, %s)",
                    (user_id, now, now),
                )
                return 1
            run_id, run_count, period_start = row
            reset = False
            if period_start:
                if (now - period_start).days >= 30:
                    reset = True
            else:
                reset = True
            if plan_started_at:
                try:
                    plan_dt = datetime.fromisoformat(str(plan_started_at))
                    if not period_start or plan_dt > period_start:
                        reset = True
                except Exception:
                    reset = True
            if reset:
                cur.execute("UPDATE usage_runs SET run_count=1, period_start=%s, last_run_at=%s WHERE id=%s", (now, now, run_id))
                return 1
            new_count = int(run_count) + 1
            cur.execute("UPDATE usage_runs SET run_count=%s, last_run_at=%s WHERE id=%s", (new_count, now, run_id))
            return new_count

    def reset_run_count(self, user_id: int):
        with self._conn() as conn:
            cur = conn.cursor()
            now = datetime.utcnow()
            cur.execute("SELECT id FROM usage_runs WHERE user_id=%s", (user_id,))
            row = cur.fetchone()
            if not row:
                cur.execute(
                    "INSERT INTO usage_runs (user_id, run_count, period_start, last_run_at) VALUES (%s, 0, %s, %s)",
                    (user_id, now, now),
                )
            else:
                cur.execute("UPDATE usage_runs SET run_count=0, period_start=%s, last_run_at=%s WHERE id=%s", (now, now, row[0]))
