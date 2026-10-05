from typing import Any

from vnmarket.ui._base import BaseUI


class Retail(BaseUI):
    """Retail market data (Exchange Rates)."""

    def exchange_rate(self, date: str = "") -> Any:
        """Get exchange rate from Vietcombank."""
        return self._dispatch("retail", "exchange_rate", date=date)
