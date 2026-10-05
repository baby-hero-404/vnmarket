"""Offline tests for exchange rate explorer (HTTP mocked)."""

import base64
from io import BytesIO
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

from vnmarket.core.exceptions import DataFetchError
from vnmarket.explorer.misc import exchange_rate as fx


def _resp(status=200, payload=None):
    r = MagicMock(status_code=status, text="x")
    r.json.return_value = payload
    return r


def _excel_payload():
    rows = (
        [["h"] * 5, ["h"] * 5] + [["USD", "US Dollar", 1, 2, 3]] * 2 + [["f"] * 5] * 4
    )
    buf = BytesIO()
    pd.DataFrame(rows, columns=list("abcde")).to_excel(
        buf, sheet_name="ExchangeRate", index=False
    )
    return {"Data": base64.b64encode(buf.getvalue()).decode()}


class TestVcb:
    def test_bad_date_raises(self):
        with pytest.raises(ValueError):
            fx.vcb_exchange_rate("26-12-2023")

    def test_http_error(self):
        with patch.object(fx.requests, "get", return_value=_resp(500)):
            with pytest.raises(DataFetchError):
                fx.vcb_exchange_rate("2023-12-26")

    def test_network_error(self):
        with patch.object(fx.requests, "get", side_effect=requests.Timeout):
            with pytest.raises(DataFetchError):
                fx.vcb_exchange_rate("2023-12-26")

    def test_bad_payload(self):
        with patch.object(fx.requests, "get", return_value=_resp(200, {})):
            with pytest.raises(DataFetchError):
                fx.vcb_exchange_rate("2023-12-26")

    def test_success(self):
        with patch.object(
            fx.requests, "get", return_value=_resp(200, _excel_payload())
        ):
            df = fx.vcb_exchange_rate("2023-12-26")
        assert len(df) == 2
        assert (df["date"] == "2023-12-26").all()
        assert "currency_code" in df.columns

    def test_blank_date_means_today(self):
        with patch.object(
            fx.requests, "get", return_value=_resp(200, _excel_payload())
        ) as g:
            fx.vcb_exchange_rate()
        assert "date=" in g.call_args.args[0] and "date=&" not in g.call_args.args[0]
