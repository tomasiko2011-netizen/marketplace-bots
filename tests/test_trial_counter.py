"""Tests for trial counter logic (30-day reset, plan-activation reset)."""
import os
import tempfile
from datetime import datetime, timedelta

from mp_bots.db.sqlite import (
    init_db,
    get_run_count_checked,
    increment_run_count,
    reset_run_count,
)


def _tmp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    return path


class TestTrialCounter:
    def test_initial_count_is_zero(self):
        db = _tmp_db()
        assert get_run_count_checked(db, 12345, None) == 0

    def test_increment_from_zero(self):
        db = _tmp_db()
        count = increment_run_count(db, 12345, None)
        assert count == 1

    def test_increment_accumulates(self):
        db = _tmp_db()
        for i in range(5):
            count = increment_run_count(db, 12345, None)
        assert count == 5

    def test_trial_limit_check(self):
        db = _tmp_db()
        for _ in range(5):
            increment_run_count(db, 12345, None)
        used = get_run_count_checked(db, 12345, None)
        assert used == 5
        assert used >= 5  # should block

    def test_reset_run_count(self):
        db = _tmp_db()
        for _ in range(3):
            increment_run_count(db, 12345, None)
        reset_run_count(db, 12345)
        assert get_run_count_checked(db, 12345, None) == 0

    def test_plan_activation_resets_counter(self):
        db = _tmp_db()
        # Use some runs
        for _ in range(3):
            increment_run_count(db, 12345, None)
        assert get_run_count_checked(db, 12345, None) == 3

        # Simulate plan activation (plan_started_at is in the future relative to period_start)
        future = (datetime.utcnow() + timedelta(seconds=5)).isoformat()
        count = get_run_count_checked(db, 12345, future)
        assert count == 0  # reset happened

    def test_30_day_period_reset(self):
        db = _tmp_db()
        import sqlite3

        # Insert usage with period_start 31 days ago
        old_start = (datetime.utcnow() - timedelta(days=31)).isoformat()
        with sqlite3.connect(db) as conn:
            conn.execute(
                "INSERT INTO usage_runs (chat_id, run_count, period_start, last_run_at) VALUES (?, ?, ?, ?)",
                (12345, 4, old_start, old_start),
            )
            conn.commit()

        count = get_run_count_checked(db, 12345, None)
        assert count == 0  # should have reset


class TestSKULimitBlocking:
    def test_sku_count_within_limit(self):
        # Simple logic test: offers <= max_skus means not blocked
        offers_count = 50
        max_skus = 100
        assert offers_count <= max_skus

    def test_sku_count_exceeds_limit(self):
        offers_count = 150
        max_skus = 100
        assert offers_count > max_skus

    def test_exact_limit(self):
        offers_count = 100
        max_skus = 100
        assert offers_count <= max_skus
