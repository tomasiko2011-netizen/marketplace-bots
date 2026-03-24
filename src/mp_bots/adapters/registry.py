from __future__ import annotations

from typing import Dict, Type

from .base import MarketplaceAdapter
from .kaspi import KaspiAdapter


REGISTRY: Dict[str, Type[MarketplaceAdapter]] = {
    KaspiAdapter.code: KaspiAdapter,
}


def get_adapter(code: str) -> Type[MarketplaceAdapter]:
    if code not in REGISTRY:
        raise ValueError(f"Adapter not registered: {code}")
    return REGISTRY[code]
