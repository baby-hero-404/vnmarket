from typing import Any

from vnmarket.ui._base import BaseUI


class Misc(BaseUI):
    """Miscellaneous market tools."""

    def exchange_rate(self, date: str = "") -> Any:
        return self._dispatch("misc", "exchange_rate", date=date)
