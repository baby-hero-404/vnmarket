class Retail:
    """
    Retail Data Layer for vnmarket (Exchange Rates).
    """

    def __init__(self):
        from vnmarket.ui.domains.retail.commodity import Retail as RetailDomain

        self._retail = RetailDomain()

    def exchange_rate(self, date: str = ""):
        """Access exchange rate data."""
        return self._retail.exchange_rate(date=date)
