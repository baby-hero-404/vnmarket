class Broker:
    """
    Brokerage Connectors.
    """

    @property
    def dnse(self):
        from vnmarket.ui.domains.broker.dnse import DNSEBroker

        return DNSEBroker()
