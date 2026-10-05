"""
Integration tests for Vnmarket main client interface.

Tests end-to-end workflows using the Vnmarket class.
"""

import pytest

from vnmarket.common.client import Vnmarket


@pytest.mark.integration
class TestVnmarketClient:
    """Test suite for Vnmarket main client."""

    def test_vnmarket_instantiation(self):
        """Test Vnmarket can be instantiated."""
        stock = Vnmarket(show_log=False)
        assert stock is not None

    def test_vnmarket_stock_method(self):
        """Test Vnmarket.stock() method."""
        stock = Vnmarket(show_log=False)
        acb = stock.stock("ACB", source="VCI")
        assert acb is not None
        assert hasattr(acb, "quote")
        assert hasattr(acb, "company")
        assert hasattr(acb, "finance")

    def test_vnmarket_stock_components_quote(self):
        """Test StockComponents has working quote component."""
        stock = Vnmarket(show_log=False)
        acb = stock.stock("ACB", source="VCI")
        assert hasattr(acb.quote, "history")

    def test_vnmarket_stock_components_company(self):
        """Test StockComponents has working company component."""
        stock = Vnmarket(show_log=False)
        acb = stock.stock("ACB", source="VCI")
        assert hasattr(acb.company, "overview")
        assert hasattr(acb.company, "profile")

    def test_vnmarket_stock_components_finance(self):
        """Test StockComponents has working finance component."""
        stock = Vnmarket(show_log=False)
        acb = stock.stock("ACB", source="VCI")
        assert hasattr(acb.finance, "balance_sheet")
        assert hasattr(acb.finance, "income_statement")
        assert hasattr(acb.finance, "cash_flow")

    def test_vnmarket_supported_sources(self):
        """Test Vnmarket supports expected sources."""
        expected_sources = ["KBS", "VCI", "MSN"]
        assert Vnmarket.SUPPORTED_SOURCES == expected_sources

    @pytest.mark.parametrize("source", ["VCI", "KBS"])
    def test_vnmarket_stock_with_different_sources(self, source):
        """Test Vnmarket.stock() works with different sources."""
        stock = Vnmarket(show_log=False)
        acb = stock.stock("ACB", source=source)
        assert acb is not None
        assert acb.source.upper() == source

    def test_vnmarket_fx_method(self):
        """Test Vnmarket.fx() method for forex data."""
        stock = Vnmarket(show_log=False)
        fx = stock.fx("USDVND", source="MSN")
        assert fx is not None
        assert hasattr(fx, "quote")

    def test_vnmarket_crypto_method(self):
        """Test Vnmarket.crypto() method."""
        stock = Vnmarket(show_log=False)
        btc = stock.crypto("BTC")
        assert btc is not None
        assert hasattr(btc, "quote")

    def test_vnmarket_world_index_method(self):
        """Test Vnmarket.world_index() method."""
        stock = Vnmarket(show_log=False)
        dji = stock.world_index("DJI")
        assert dji is not None
        assert hasattr(dji, "quote")
