class Misc:
    """
    Miscellaneous market tools.
    """

    def __init__(self):
        from vnmarket.ui.domains.misc.tools import Misc as MiscDomain

        self._misc = MiscDomain()

    def exchange_rate(self, date: str = ""):
        return self._misc.exchange_rate(date=date)
