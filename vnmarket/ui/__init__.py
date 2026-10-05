"""
UI Module - Unified Interface for vnmarket
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from vnmarket.ui.broker import Broker
    from vnmarket.ui.fundamental import Fundamental
    from vnmarket.ui.market import Market
    from vnmarket.ui.reference import Reference
    from vnmarket.ui.retail import Retail

__all__ = ["Reference", "Market", "Fundamental", "Retail", "Broker"]


def __getattr__(name: str) -> Any:
    """
    Lazy load UI modules using PEP 562.
    Allows IDE autocomplete and type hints to work correctly.
    """
    if name == "Reference":
        from vnmarket.ui.reference import Reference as _Reference

        return _Reference
    elif name == "Market":
        from vnmarket.ui.market import Market as _Market

        return _Market
    elif name == "Fundamental":
        from vnmarket.ui.fundamental import Fundamental as _Fundamental

        return _Fundamental
    elif name == "Retail":
        from vnmarket.ui.retail import Retail as _Retail

        return _Retail
    elif name == "Broker":
        from vnmarket.ui.broker import Broker as _Broker

        return _Broker
    elif name == "show_api":
        from vnmarket.ui.helper import show_api as _show_api

        return _show_api
    elif name == "show_doc":
        from vnmarket.ui.helper import show_doc as _show_doc

        return _show_doc

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
