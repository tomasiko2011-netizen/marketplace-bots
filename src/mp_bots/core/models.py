from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Offer:
    sku: str
    title: str
    price: float
    currency: str = "KZT"
    ntin: str | None = None
    available: bool = True
    updated_at: Optional[datetime] = None


@dataclass
class PriceRule:
    sku: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    undercut_by: Optional[float] = None
    priority: int = 0


@dataclass
class PriceDecision:
    sku: str
    old_price: float
    new_price: float
    reason: str
