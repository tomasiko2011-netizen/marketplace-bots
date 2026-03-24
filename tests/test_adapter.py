"""Tests for adapter contract (mock/live boundary)."""
import json
import os
import tempfile

import pytest

from mp_bots.adapters.kaspi import KaspiAdapter
from mp_bots.adapters.base import MarketplaceAdapter
from mp_bots.adapters.registry import get_adapter
from mp_bots.core.models import Offer, PriceDecision


class TestAdapterRegistry:
    def test_kaspi_registered(self):
        cls = get_adapter("kaspi")
        assert cls is KaspiAdapter

    def test_unknown_adapter_raises(self):
        with pytest.raises(ValueError, match="Adapter not registered"):
            get_adapter("nonexistent")


class TestKaspiMockAdapter:
    def _mock_offers_file(self, offers):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        with open(path, "w") as f:
            json.dump({"offers": offers}, f)
        return path

    def test_fetch_offers_mock(self):
        path = self._mock_offers_file([
            {"sku": "KSP-001", "title": "Product A", "price": 5000, "available": True},
            {"sku": "KSP-002", "title": "Product B", "price": 3000, "ntin": "7700000000001"},
        ])
        adapter = KaspiAdapter(mode="mock", input=path)
        offers = adapter.fetch_offers()
        assert len(offers) == 2
        assert offers[0].sku == "KSP-001"
        assert offers[0].price == 5000.0
        assert offers[1].ntin == "7700000000001"

    def test_fetch_offers_mock_empty(self):
        path = self._mock_offers_file([])
        adapter = KaspiAdapter(mode="mock", input=path)
        offers = adapter.fetch_offers()
        assert offers == []

    def test_update_prices_mock_no_crash(self):
        adapter = KaspiAdapter(mode="mock")
        decisions = [
            PriceDecision(sku="KSP-001", old_price=5000, new_price=4850, reason="test"),
        ]
        adapter.update_prices(decisions)  # should not raise

    def test_health_check_mock(self):
        adapter = KaspiAdapter(mode="mock")
        adapter.health_check()  # should not raise


class TestKaspiLiveAdapter:
    def test_fetch_live_not_implemented(self):
        adapter = KaspiAdapter(mode="live", api_base="https://example.com")
        with pytest.raises(NotImplementedError):
            adapter.fetch_offers()

    def test_update_live_not_implemented(self):
        adapter = KaspiAdapter(mode="live", api_base="https://example.com")
        with pytest.raises(NotImplementedError):
            adapter.update_prices([])

    def test_health_check_live_requires_api_base(self):
        adapter = KaspiAdapter(mode="live")
        with pytest.raises(RuntimeError, match="api_base"):
            adapter.health_check()


class TestAdapterContract:
    """Verify the adapter base class contract."""

    def test_base_class_is_abstract(self):
        assert hasattr(MarketplaceAdapter, "fetch_offers")
        assert hasattr(MarketplaceAdapter, "update_prices")
        assert hasattr(MarketplaceAdapter, "health_check")

    def test_kaspi_implements_interface(self):
        adapter = KaspiAdapter(mode="mock")
        assert hasattr(adapter, "fetch_offers")
        assert hasattr(adapter, "update_prices")
        assert hasattr(adapter, "health_check")
        assert adapter.code == "kaspi"
