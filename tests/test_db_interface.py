"""Tests for the unified DB interface (SQLite backend)."""
import os
import tempfile
from datetime import datetime

from mp_bots.db.interface import SQLiteDB
from mp_bots.core.models import Offer, PriceDecision


def _tmp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = SQLiteDB(path)
    db.init()
    return db


class TestSettings:
    def test_default_settings(self):
        db = _tmp_db()
        poll, turbo = db.get_settings("store1")
        assert poll == 120
        assert turbo is False

    def test_set_and_get_settings(self):
        db = _tmp_db()
        db.set_settings("store1", poll_interval_seconds=60, turbo_mode=True)
        poll, turbo = db.get_settings("store1")
        assert poll == 60
        assert turbo is True

    def test_partial_update(self):
        db = _tmp_db()
        db.set_settings("store1", poll_interval_seconds=90)
        db.set_settings("store1", turbo_mode=True)
        poll, turbo = db.get_settings("store1")
        assert poll == 90
        assert turbo is True


class TestPlan:
    def test_default_plan(self):
        db = _tmp_db()
        code, skus, paid, started = db.get_plan("store1")
        assert code == "start_100"
        assert skus == 100
        assert paid is False

    def test_set_plan(self):
        db = _tmp_db()
        db.set_plan("store1", "pro_2000", 2000, True, "2026-01-01T00:00:00")
        code, skus, paid, started = db.get_plan("store1")
        assert code == "pro_2000"
        assert skus == 2000
        assert paid is True


class TestRules:
    def test_default_rules(self):
        db = _tmp_db()
        mn, mx, uc = db.get_rules("store1")
        assert mn is None
        assert mx is None
        assert uc is None

    def test_set_rules(self):
        db = _tmp_db()
        db.set_rules("store1", min_price=2000, max_price=10000, undercut_by=150)
        mn, mx, uc = db.get_rules("store1")
        assert mn == 2000
        assert mx == 10000
        assert uc == 150


class TestExclusions:
    def test_excluded_products_empty(self):
        db = _tmp_db()
        assert db.get_excluded_products("store1") == set()

    def test_set_excluded_products(self):
        db = _tmp_db()
        db.set_excluded_products("store1", ["KSP-001", "KSP-002"])
        result = db.get_excluded_products("store1")
        assert result == {"KSP-001", "KSP-002"}

    def test_replace_excluded_products(self):
        db = _tmp_db()
        db.set_excluded_products("store1", ["A", "B"])
        db.set_excluded_products("store1", ["C"])
        assert db.get_excluded_products("store1") == {"C"}

    def test_excluded_competitors(self):
        db = _tmp_db()
        db.set_excluded_competitors("store1", ["C001", "C002"])
        assert db.get_excluded_competitors("store1") == {"C001", "C002"}


class TestSessions:
    def test_no_session(self):
        db = _tmp_db()
        assert db.get_session_store(12345) is None

    def test_set_session(self):
        db = _tmp_db()
        db.set_session_store(12345, "store1")
        assert db.get_session_store(12345) == "store1"

    def test_pending_action(self):
        db = _tmp_db()
        db.set_session_store(12345, "store1")
        assert db.get_pending_action(12345) is None
        db.set_pending_action(12345, "rules")
        assert db.get_pending_action(12345) == "rules"
        db.set_pending_action(12345, None)
        assert db.get_pending_action(12345) is None


class TestOffers:
    def test_upsert_offers(self):
        db = _tmp_db()
        offers = [
            Offer(sku="KSP-001", title="A", price=5000.0, updated_at=datetime.utcnow()),
            Offer(sku="KSP-002", title="B", price=3000.0),
        ]
        db.upsert_offers("store1", offers)
        # no assertion — just verify no crash


class TestPriceActions:
    def test_write_and_read(self):
        db = _tmp_db()
        actions = [
            PriceDecision(sku="KSP-001", old_price=5000, new_price=4850, reason="undercut"),
        ]
        db.write_price_actions("store1", actions)
        rows = db.get_price_actions("store1", limit=5)
        assert len(rows) == 1
        assert rows[0][0] == "KSP-001"
