"""Tests for rules engine and price decisions."""
from mp_bots.core.models import Offer, PriceRule
from mp_bots.core.rules import apply_rules
from mp_bots.core.engine import evaluate_offers


def _offer(sku="KSP-001", price=5000.0):
    return Offer(sku=sku, title="Test", price=price)


class TestApplyRules:
    def test_no_rules_no_change(self):
        result = apply_rules(_offer(), [])
        assert result is None

    def test_undercut_basic(self):
        rule = PriceRule(undercut_by=150, priority=0)
        result = apply_rules(_offer(price=5000), [rule])
        assert result is not None
        assert result.new_price == 4850.0

    def test_undercut_respects_min_price(self):
        rules = [PriceRule(undercut_by=200, min_price=4900, priority=0)]
        result = apply_rules(_offer(price=5000), rules)
        assert result is not None
        assert result.new_price == 4900.0

    def test_max_price_cap(self):
        rules = [PriceRule(max_price=3000, priority=0)]
        result = apply_rules(_offer(price=5000), rules)
        assert result is not None
        assert result.new_price == 3000.0

    def test_no_change_returns_none(self):
        rules = [PriceRule(min_price=1000, max_price=10000, priority=0)]
        result = apply_rules(_offer(price=5000), rules)
        assert result is None

    def test_undercut_below_zero_floors_at_zero(self):
        rules = [PriceRule(undercut_by=10000, priority=0)]
        result = apply_rules(_offer(price=5000), rules)
        assert result is not None
        assert result.new_price == 0.0

    def test_sku_specific_rule_matches(self):
        rules = [
            PriceRule(sku="KSP-001", undercut_by=100, priority=1),
            PriceRule(undercut_by=50, priority=0),
        ]
        result = apply_rules(_offer(sku="KSP-001", price=5000), rules)
        assert result.new_price == 4900.0

    def test_sku_specific_rule_no_match(self):
        rules = [PriceRule(sku="KSP-999", undercut_by=100, priority=1)]
        result = apply_rules(_offer(sku="KSP-001", price=5000), rules)
        assert result is None

    def test_higher_priority_wins(self):
        rules = [
            PriceRule(undercut_by=50, priority=0),
            PriceRule(undercut_by=200, priority=5),
        ]
        result = apply_rules(_offer(price=5000), rules)
        assert result.new_price == 4800.0


class TestEvaluateOffers:
    def test_multiple_offers(self):
        offers = [_offer("A", 5000), _offer("B", 3000), _offer("C", 1000)]
        rules = [PriceRule(undercut_by=100, priority=0)]
        decisions = evaluate_offers(offers, rules)
        assert len(decisions) == 3
        assert all(d.new_price == d.old_price - 100 for d in decisions)

    def test_no_decisions_when_no_change(self):
        offers = [_offer("A", 5000)]
        rules = [PriceRule(min_price=1000, priority=0)]
        decisions = evaluate_offers(offers, rules)
        assert len(decisions) == 0
