from __future__ import annotations

from typing import Iterable, List

from .models import Offer, PriceDecision, PriceRule
from .rules import apply_rules


def evaluate_offers(offers: Iterable[Offer], rules: Iterable[PriceRule]) -> List[PriceDecision]:
    decisions: List[PriceDecision] = []
    for offer in offers:
        decision = apply_rules(offer, rules)
        if decision:
            decisions.append(decision)
    return decisions
