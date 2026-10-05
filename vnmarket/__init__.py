"""
vnmarket: Python toolkit for fetching and standardizing Vietnamese stock market data.
"""

# Lazy import Vnmarket to avoid circular import deadlock
_Vnmarket = None


def _get_vnmarket():
    """Lazy load Vnmarket class."""
    global _Vnmarket
    if _Vnmarket is None:
        from vnmarket.common.client import Vnmarket as _VnmarketClass

        _Vnmarket = _VnmarketClass
    return _Vnmarket


# Create a lazy proxy for Vnmarket
class Vnmarket:
    """Lazy proxy for vnmarket.common.client.Vnmarket to avoid circular import."""

    def __new__(cls, *args, **kwargs):
        actual_class = _get_vnmarket()
        return actual_class(*args, **kwargs)


# Load UI and helper classes
from vnmarket.ui import (  # noqa: E402
    Broker,
    Fundamental,
    Market,
    Reference,
    Retail,
    show_api,
    show_doc,
)

from .api.company import Company  # noqa: E402
from .api.financial import Finance  # noqa: E402
from .api.listing import Listing  # noqa: E402
from .api.quote import Quote  # noqa: E402
from .api.trading import Trading  # noqa: E402
from .explorer.fmarket import Fund  # noqa: E402

show_docs = show_doc  # Alias for better parity

# Market constants
from . import connector  # noqa: E402
from .constants import (  # noqa: E402
    EXCHANGES,
    INDEX_GROUPS,
    INDICES_INFO,
    INDICES_MAP,
    SECTOR_IDS,
)

# Load explorer modules to register providers (lazy to avoid deadlock)
_explorer_modules_loaded = False


def _ensure_explorer_modules_loaded():
    """Lazy load explorer modules to avoid circular import deadlock."""
    global _explorer_modules_loaded
    if _explorer_modules_loaded:
        return
    try:
        from .explorer import kbs, msn, vci  # noqa: F401

        _explorer_modules_loaded = True
    except Exception as e:
        _explorer_modules_loaded = True  # Mark as loaded to avoid retry loops
        import warnings

        warnings.warn(f"Failed to load explorer modules: {e}", stacklevel=2)


__all__ = [
    "Vnmarket",
    "Quote",
    "Listing",
    "Company",
    "Finance",
    "Trading",
    "Fund",
    "ui",
    "show_api",
    "show_doc",
    "show_docs",
    "Reference",
    "Market",
    "Fundamental",
    "Retail",
    "Broker",
    "connector",
    "INDICES_INFO",
    "INDICES_MAP",
    "INDEX_GROUPS",
    "SECTOR_IDS",
    "EXCHANGES",
]
