from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List

from mp_bots.core.models import Offer, PriceDecision


class MarketplaceAdapter(ABC):
    code: str

    def __init__(self, **kwargs):
        self.config = kwargs

    @abstractmethod
    def fetch_offers(self) -> List[Offer]:
        raise NotImplementedError

    @abstractmethod
    def update_prices(self, decisions: Iterable[PriceDecision]) -> None:
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> None:
        raise NotImplementedError
