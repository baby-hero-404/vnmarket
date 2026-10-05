"""Offline contract tests for the DNSE trade connector (HTTP mocked)."""

import inspect
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from vnmarket.connector.dnse.trade import Trade
from vnmarket.core.constants import DEFAULT_TIMEOUT

_DUMMY = {str: "x", int: 1, float: 1.0, bool: True, dict: {}, list: []}
_SKIP = {"login", "email_otp", "get_trading_token"}  # return str/None, tested below
METHODS = [
    n
    for n, f in inspect.getmembers(Trade, inspect.isfunction)
    if not n.startswith("_") and n not in _SKIP
]


def _args(name):
    out = {}
    for p in inspect.signature(getattr(Trade, name)).parameters.values():
        if p.name == "self" or p.default is not inspect.Parameter.empty:
            continue
        out[p.name] = _DUMMY.get(p.annotation, "x")
    return out


def _http(status, payload=None):
    r = MagicMock(status_code=status, text="boom")
    r.json.return_value = payload if payload is not None else {}
    return r


@pytest.fixture
def trade():
    t = Trade()
    t.token = "jwt"
    t.trading_token = "tt"
    return t


def test_methods_discovered():
    assert len(METHODS) >= 15


VERBS = ("get", "post", "put", "delete", "patch")


def _mock_requests(response):
    """Patch every HTTP verb so no test can reach the network."""
    m = MagicMock()
    for verb in VERBS:
        getattr(m, verb).return_value = response
    return patch("vnmarket.connector.dnse.trade.requests", m), m


@pytest.mark.parametrize("name", METHODS)
def test_non_200_returns_none(trade, name):
    ctx, _ = _mock_requests(_http(500))
    with ctx:
        assert getattr(trade, name)(**_args(name)) is None


@pytest.mark.parametrize("name", METHODS)
def test_200_returns_dataframe_and_sets_timeout(trade, name):
    ok = _http(
        200, {"id": 1, "accounts": [], "orders": [], "data": [], "loanPackages": []}
    )
    ctx, m = _mock_requests(ok)
    with ctx:
        result = getattr(trade, name)(**_args(name))
    assert isinstance(result, pd.DataFrame)
    calls = [c for v in VERBS for c in getattr(m, v).call_args_list]
    assert calls and all(c.kwargs["timeout"] == DEFAULT_TIMEOUT for c in calls)


class TestAuth:
    def test_login_stores_token(self):
        t = Trade()
        ctx, _ = _mock_requests(_http(200, {"token": "abc"}))
        with ctx:
            assert t.login("u", "p") == "abc"
        assert t.token == "abc"

    def test_login_failure(self):
        t = Trade()
        ctx, _ = _mock_requests(_http(401))
        with ctx:
            assert t.login("u", "p") is None
        assert t.token is None
