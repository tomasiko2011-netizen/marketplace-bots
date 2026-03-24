"""Tests for core models."""
from mp_bots.core.models import Offer, PriceDecision, PriceRule


def test_offer_creation():
    o = Offer(sku="KSP-001", title="Test Product", price=5000.0)
    assert o.sku == "KSP-001"
    assert o.price == 5000.0
    assert o.currency == "KZT"
    assert o.ntin is None
    assert o.available is True


def test_offer_with_ntin():
    o = Offer(sku="KSP-002", title="With NTIN", price=3000.0, ntin="7700000000001")
    assert o.ntin == "7700000000001"


def test_price_decision():
    d = PriceDecision(sku="KSP-001", old_price=5000.0, new_price=4850.0, reason="undercut_by=150")
    assert d.new_price < d.old_price


def test_price_rule_defaults():
    r = PriceRule()
    assert r.sku is None
    assert r.min_price is None
    assert r.priority == 0
