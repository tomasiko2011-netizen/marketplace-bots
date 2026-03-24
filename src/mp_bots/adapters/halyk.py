from __future__ import annotations

from typing import Iterable, List

from mp_bots.core.models import Offer, PriceDecision
from .base import MarketplaceAdapter


class HalykAdapter(MarketplaceAdapter):
    code = "halyk"

    def fetch_offers(self) -> List[Offer]:
        raise NotImplementedError("Live API not wired yet.")

    def update_prices(self, decisions: Iterable[PriceDecision]) -> None:
        raise NotImplementedError("Live API not wired yet.")

    def health_check(self) -> None:
        raise NotImplementedError("Live API not wired yet.")
