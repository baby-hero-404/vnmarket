"""Outbound calls must forward DEFAULT_TIMEOUT to requests."""

from unittest.mock import MagicMock, patch

from vnmarket.connector.dnse.trade import Trade
from vnmarket.core.constants import DEFAULT_TIMEOUT


def test_dnse_login_forwards_timeout():
    resp = MagicMock(status_code=200)
    resp.json.return_value = {"token": "t"}
    with patch("vnmarket.connector.dnse.trade.requests.post", return_value=resp) as p:
        assert Trade().login("u", "p") == "t"
    assert p.call_args.kwargs["timeout"] == DEFAULT_TIMEOUT
