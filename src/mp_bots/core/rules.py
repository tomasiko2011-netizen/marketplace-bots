from __future__ import annotations

from typing import Iterable

from .models import Offer, PriceDecision, PriceRule


def apply_rules(offer: Offer, rules: Iterable[PriceRule]) -> PriceDecision | None:
    """
    Apply a simple rule set to a single offer.
    Priority: higher rule priority wins when multiple match.
    """
    matched = [r for r in rules if r.sku is None or r.sku == offer.sku]
    if not matched:
        return None

    matched.sort(key=lambda r: r.priority, reverse=True)
    rule = matched[0]

    new_price = offer.price
    reason_parts = []

    if rule.undercut_by is not None:
        new_price = max(0.0, offer.price - rule.undercut_by)
        reason_parts.append(f"undercut_by={rule.undercut_by}")

    if rule.min_price is not None and new_price < rule.min_price:
        new_price = rule.min_price
        reason_parts.append("min_price")

    if rule.max_price is not None and new_price > rule.max_price:
        new_price = rule.max_price
        reason_parts.append("max_price")

    if new_price == offer.price:
        return None

    reason = ",".join(reason_parts) if reason_parts else "rule_applied"
    return PriceDecision(sku=offer.sku, old_price=offer.price, new_price=new_price, reason=reason)
