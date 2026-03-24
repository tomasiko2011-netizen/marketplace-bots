from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from mp_bots.core.models import Offer, PriceDecision
from .base import MarketplaceAdapter


class KaspiAdapter(MarketplaceAdapter):
    code = "kaspi"

    def fetch_offers(self) -> List[Offer]:
        mode = self.config.get("mode", "live")
        if mode == "mock":
            return self._fetch_offers_mock()
        return self._fetch_offers_live()

    def update_prices(self, decisions: Iterable[PriceDecision]) -> None:
        mode = self.config.get("mode", "live")
        if mode == "mock":
            # In mock mode, we only log to stdout
            for d in decisions:
                print(f"[kaspi mock] update price sku={d.sku} {d.old_price} -> {d.new_price} ({d.reason})")
            return
        self._update_prices_live(decisions)

    def health_check(self) -> None:
        mode = self.config.get("mode", "live")
        if mode == "mock":
            return
        # Live health check placeholder
        api_base = self.config.get("api_base")
        if not api_base:
            raise RuntimeError("Kaspi live mode requires api_base in config")

    def _fetch_offers_mock(self) -> List[Offer]:
        input_path = self.config.get("input")
        if not input_path:
            raise RuntimeError("Kaspi mock mode requires input path to JSON offers")
        data = json.loads(Path(input_path).read_text(encoding="utf-8"))
        offers: List[Offer] = []
        for item in data.get("offers", []):
            offers.append(
                Offer(
                    sku=item["sku"],
                    title=item.get("title", ""),
                    price=float(item["price"]),
                    currency=item.get("currency", "KZT"),
                    ntin=item.get("ntin"),
                    available=bool(item.get("available", True)),
                    updated_at=datetime.utcnow(),
                )
            )
        return offers

    def _fetch_offers_live(self) -> List[Offer]:
        # Placeholder for official Kaspi API integration
        # Expected config keys (once you have API docs):
        # - api_base
        # - token or api_key
        # - store_id
        # - timeouts / pagination
        raise NotImplementedError("Kaspi live API not wired yet. Provide official API docs and credentials.")

    def _update_prices_live(self, decisions: Iterable[PriceDecision]) -> None:
        # Placeholder for official Kaspi API price update
        raise NotImplementedError("Kaspi live API not wired yet. Provide official API docs and credentials.")
