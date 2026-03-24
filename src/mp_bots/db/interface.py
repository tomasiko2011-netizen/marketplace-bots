"""Unified DB interface for skladprobot.

Provides a single API that delegates to either SQLite (dev) or Postgres (prod)
based on environment config. The bot imports from here instead of sqlite/postgres directly.

Usage:
    from mp_bots.db.interface import get_db
    db = get_db()  # auto-detects from DATABASE_URL / MP_BOTS_DB
    db.get_settings("kaspi-main")
"""
from __future__ import annotations

import os
from typing import Iterable

from mp_bots.core.models import Offer, PriceDecision


class DB:
    """Abstract interface matching both SQLite and Postgres backends."""

    def init(self) -> None:
        raise NotImplementedError

    def upsert_offers(self, store_key: str, offers: Iterable[Offer]) -> None:
        raise NotImplementedError

    def write_price_actions(self, store_key: str, actions: Iterable[PriceDecision]) -> None:
        raise NotImplementedError

    def get_price_actions(self, store_key: str, limit: int = 10) -> list:
        raise NotImplementedError

    def get_settings(self, store_key: str) -> tuple[int, bool]:
        raise NotImplementedError

    def set_settings(self, store_key: str, poll_interval_seconds: int | None = None, turbo_mode: bool | None = None) -> None:
        raise NotImplementedError

    def get_plan(self, store_key: str) -> tuple[str, int, bool, str | None]:
        raise NotImplementedError

    def set_plan(self, store_key: str, plan_code: str, max_skus: int, paid_active: bool, plan_started_at: str | None) -> None:
        raise NotImplementedError

    def get_rules(self, store_key: str) -> tuple[float | None, float | None, float | None]:
        raise NotImplementedError

    def set_rules(self, store_key: str, min_price=None, max_price=None, undercut_by=None) -> None:
        raise NotImplementedError

    def get_excluded_products(self, store_key: str) -> set[str]:
        raise NotImplementedError

    def set_excluded_products(self, store_key: str, skus: Iterable[str]) -> None:
        raise NotImplementedError

    def get_excluded_competitors(self, store_key: str) -> set[str]:
        raise NotImplementedError

    def set_excluded_competitors(self, store_key: str, competitors: Iterable[str]) -> None:
        raise NotImplementedError

    def get_session_store(self, chat_id: int) -> str | None:
        raise NotImplementedError

    def set_session_store(self, chat_id: int, store_key: str) -> None:
        raise NotImplementedError

    def get_pending_action(self, chat_id: int) -> str | None:
        raise NotImplementedError

    def set_pending_action(self, chat_id: int, action: str | None) -> None:
        raise NotImplementedError

    def get_run_count_checked(self, user_id: int, plan_started_at: str | None) -> int:
        raise NotImplementedError

    def increment_run_count(self, user_id: int, plan_started_at: str | None) -> int:
        raise NotImplementedError

    def reset_run_count(self, user_id: int) -> None:
        raise NotImplementedError

    def get_stores(self) -> list[dict]:
        raise NotImplementedError


class SQLiteDB(DB):
    """Wraps the existing sqlite.py functions into the DB interface."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def init(self):
        from mp_bots.db.sqlite import init_db
        init_db(self.db_path)

    def upsert_offers(self, store_key, offers):
        from mp_bots.db.sqlite import upsert_offers
        upsert_offers(self.db_path, store_key, offers)

    def write_price_actions(self, store_key, actions):
        from mp_bots.db.sqlite import write_price_actions
        write_price_actions(self.db_path, actions)

    def get_price_actions(self, store_key, limit=10):
        from mp_bots.db.sqlite import get_price_actions
        return get_price_actions(self.db_path, limit)

    def get_settings(self, store_key):
        from mp_bots.db.sqlite import get_settings
        return get_settings(self.db_path, store_key)

    def set_settings(self, store_key, poll_interval_seconds=None, turbo_mode=None):
        from mp_bots.db.sqlite import set_settings
        set_settings(self.db_path, store_key, poll_interval_seconds=poll_interval_seconds, turbo_mode=turbo_mode)

    def get_plan(self, store_key):
        from mp_bots.db.sqlite import get_plan
        return get_plan(self.db_path, store_key)

    def set_plan(self, store_key, plan_code, max_skus, paid_active, plan_started_at):
        from mp_bots.db.sqlite import set_plan
        set_plan(self.db_path, store_key, plan_code, max_skus, paid_active, plan_started_at)

    def get_rules(self, store_key):
        from mp_bots.db.sqlite import get_rules
        return get_rules(self.db_path, store_key)

    def set_rules(self, store_key, min_price=None, max_price=None, undercut_by=None):
        from mp_bots.db.sqlite import set_rules
        set_rules(self.db_path, store_key, min_price=min_price, max_price=max_price, undercut_by=undercut_by)

    def get_excluded_products(self, store_key):
        from mp_bots.db.sqlite import get_excluded_products
        return get_excluded_products(self.db_path, store_key)

    def set_excluded_products(self, store_key, skus):
        from mp_bots.db.sqlite import set_excluded_products
        set_excluded_products(self.db_path, store_key, skus)

    def get_excluded_competitors(self, store_key):
        from mp_bots.db.sqlite import get_excluded_competitors
        return get_excluded_competitors(self.db_path, store_key)

    def set_excluded_competitors(self, store_key, competitors):
        from mp_bots.db.sqlite import set_excluded_competitors
        set_excluded_competitors(self.db_path, store_key, competitors)

    def get_session_store(self, chat_id):
        from mp_bots.db.sqlite import get_session_store
        return get_session_store(self.db_path, chat_id)

    def set_session_store(self, chat_id, store_key):
        from mp_bots.db.sqlite import set_session_store
        set_session_store(self.db_path, chat_id, store_key)

    def get_pending_action(self, chat_id):
        from mp_bots.db.sqlite import get_pending_action
        return get_pending_action(self.db_path, chat_id)

    def set_pending_action(self, chat_id, action):
        from mp_bots.db.sqlite import set_pending_action
        set_pending_action(self.db_path, chat_id, action)

    def get_run_count_checked(self, user_id, plan_started_at):
        from mp_bots.db.sqlite import get_run_count_checked
        return get_run_count_checked(self.db_path, user_id, plan_started_at)

    def increment_run_count(self, user_id, plan_started_at):
        from mp_bots.db.sqlite import increment_run_count
        return increment_run_count(self.db_path, user_id, plan_started_at)

    def reset_run_count(self, user_id):
        from mp_bots.db.sqlite import reset_run_count
        reset_run_count(self.db_path, user_id)

    def get_stores(self):
        return []


class PostgresDBAdapter(DB):
    """Wraps PostgresDB class into the DB interface."""

    def __init__(self, dsn: str):
        from mp_bots.db.postgres import PostgresDB
        self._pg = PostgresDB(dsn)

    def init(self):
        pass  # Postgres uses migrations

    def upsert_offers(self, store_key, offers):
        self._pg.upsert_offers(store_key, offers)

    def write_price_actions(self, store_key, actions):
        self._pg.write_price_actions(store_key, actions)

    def get_price_actions(self, store_key, limit=10):
        return self._pg.get_price_actions(store_key, limit)

    def get_settings(self, store_key):
        return self._pg.get_settings(store_key)

    def set_settings(self, store_key, poll_interval_seconds=None, turbo_mode=None):
        self._pg.set_settings(store_key, poll_interval_seconds=poll_interval_seconds, turbo_mode=turbo_mode)

    def get_plan(self, store_key):
        return self._pg.get_plan(store_key)

    def set_plan(self, store_key, plan_code, max_skus, paid_active, plan_started_at):
        self._pg.set_plan(store_key, plan_code, max_skus, paid_active, plan_started_at)

    def get_rules(self, store_key):
        return self._pg.get_rules(store_key)

    def set_rules(self, store_key, min_price=None, max_price=None, undercut_by=None):
        self._pg.set_rules(store_key, min_price=min_price, max_price=max_price, undercut_by=undercut_by)

    def get_excluded_products(self, store_key):
        return self._pg.get_excluded_products(store_key)

    def set_excluded_products(self, store_key, skus):
        self._pg.set_excluded_products(store_key, skus)

    def get_excluded_competitors(self, store_key):
        return self._pg.get_excluded_competitors(store_key)

    def set_excluded_competitors(self, store_key, competitors):
        self._pg.set_excluded_competitors(store_key, competitors)

    def get_session_store(self, chat_id):
        return self._pg.get_session_store(chat_id)

    def set_session_store(self, chat_id, store_key):
        self._pg.set_session_store(chat_id, store_key)

    def get_pending_action(self, chat_id):
        return self._pg.get_pending_action(chat_id)

    def set_pending_action(self, chat_id, action):
        self._pg.set_pending_action(chat_id, action)

    def get_run_count_checked(self, user_id, plan_started_at):
        return self._pg.get_run_count_checked(user_id, plan_started_at)

    def increment_run_count(self, user_id, plan_started_at):
        return self._pg.increment_run_count(user_id, plan_started_at)

    def reset_run_count(self, user_id):
        self._pg.reset_run_count(user_id)

    def get_stores(self):
        with self._pg._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT store_key, title, marketplace, mode FROM stores ORDER BY created_at"
            )
            return [
                {"key": r[0], "title": r[1] or r[0], "marketplace": r[2], "mode": r[3]}
                for r in cur.fetchall()
            ]


_db_instance: DB | None = None


def get_db() -> DB:
    """Return a singleton DB instance based on env config.

    - DATABASE_URL set -> Postgres
    - Otherwise -> SQLite at MP_BOTS_DB path
    """
    global _db_instance
    if _db_instance is not None:
        return _db_instance

    database_url = os.environ.get("DATABASE_URL", "")
    if database_url:
        _db_instance = PostgresDBAdapter(database_url)
    else:
        db_path = os.environ.get("MP_BOTS_DB", "tmp/dev.db")
        _db_instance = SQLiteDB(db_path)
        _db_instance.init()

    return _db_instance
