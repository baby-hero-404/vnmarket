"""Circuit breaker, block detection and retry policy."""

from types import SimpleNamespace

import pytest

from vnmarket.config import Config
from vnmarket.core.exceptions import DataSourceBlockedError, NetworkError
from vnmarket.core.utils import circuit as c
from vnmarket.core.utils.block_detect import parse_retry_after
from vnmarket.core.utils.retry import should_retry


@pytest.fixture(autouse=True)
def clean_circuit(monkeypatch):
    monkeypatch.delenv("VNMARKET_CIRCUIT_BREAKER", raising=False)
    monkeypatch.delenv("VNMARKET_DATA_CIRCUIT_BREAKER", raising=False)
    c.reset_circuit()
    yield
    c.reset_circuit()


def sig(kind="denied", retry_after=None):
    return SimpleNamespace(kind=kind, retry_after=retry_after)


class TestCircuitKey:
    def test_direct(self):
        assert c.circuit_key("https://API.Example.com/x") == "api.example.com|direct"

    def test_proxy_credentials_never_leak(self):
        key = c.circuit_key(
            "https://a.com/x", {"https": "http://user:secret@proxy.local:8080"}
        )
        assert key == "a.com|proxy.local"
        assert "secret" not in key


class TestCooldown:
    def test_retry_after_is_clamped(self):
        assert c.cooldown_for(sig(retry_after=10**9)) == Config.BLOCK_COOLDOWN_MAX
        assert c.cooldown_for(sig(retry_after=0.001)) == Config.BLOCK_COOLDOWN_MIN

    def test_kind_default(self):
        expected = max(
            Config.BLOCK_COOLDOWN_MIN,
            min(Config.BLOCK_COOLDOWN_RATE_LIMIT, Config.BLOCK_COOLDOWN_MAX),
        )
        assert c.cooldown_for(sig("rate_limit")) == expected


class TestBreaker:
    def test_open_then_reset(self):
        assert c.circuit_check("h|direct") is None
        c.circuit_trip("h|direct", sig(retry_after=60))
        assert c.circuit_check("h|direct") > 0
        assert "h|direct" in c.circuit_status()
        # reset takes a hostname and clears every egress route for it
        assert c.reset_circuit("H") == 1
        assert c.circuit_check("h|direct") is None

    def test_reset_all(self):
        c.circuit_trip("a|direct", sig(retry_after=60))
        c.circuit_trip("b|direct", sig(retry_after=60))
        assert c.reset_circuit() == 2
        assert c.circuit_status() == {}

    def test_longer_deadline_wins(self):
        c.circuit_trip("k", sig(retry_after=300))
        long_left = c.circuit_check("k")
        c.circuit_trip("k", sig(retry_after=Config.BLOCK_COOLDOWN_MIN))
        assert c.circuit_check("k") >= long_left - 1

    def test_expired_entry_is_dropped(self, monkeypatch):
        c.circuit_trip("k", sig(retry_after=60))
        base = c.time.monotonic()
        monkeypatch.setattr(c.time, "monotonic", lambda: base + 10_000)
        assert c.circuit_check("k") is None
        assert c.circuit_status() == {}

    @pytest.mark.parametrize("flag", ["0", "off", "FALSE", "no"])
    def test_env_switch_disables(self, monkeypatch, flag):
        monkeypatch.setenv("VNMARKET_CIRCUIT_BREAKER", flag)
        c.circuit_trip("k", sig(retry_after=60))
        assert c.circuit_check("k") is None

    def test_legacy_env_switch_disables(self, monkeypatch):
        monkeypatch.setenv("VNMARKET_DATA_CIRCUIT_BREAKER", "off")
        assert not c.circuit_enabled()

    def test_memory_is_bounded(self, monkeypatch):
        monkeypatch.setattr(Config, "CIRCUIT_MAX_ENTRIES", 5)
        for i in range(20):
            c.circuit_trip(f"k{i}", sig(retry_after=60))
        assert len(c.circuit_status()) <= 5


class TestRetryAfter:
    @pytest.mark.parametrize("raw", [None, "", "   ", "garbage"])
    def test_unreadable_is_none(self, raw):
        assert parse_retry_after(raw) is None

    def test_seconds(self):
        assert parse_retry_after("30") == 30.0

    def test_negative_clamped(self):
        assert parse_retry_after("-5") == 0.0

    def test_http_date_in_past_is_zero(self):
        assert parse_retry_after("Wed, 21 Oct 2015 07:28:00 GMT") == 0.0


class TestShouldRetry:
    def test_transient_retried(self):
        assert should_retry(ConnectionError())
        assert should_retry(OSError())
        assert should_retry(NetworkError("x"))

    def test_programming_errors_never_retried(self):
        assert not should_retry(ValueError())
        assert not should_retry(KeyError())

    def test_blocked_never_retried_even_though_it_is_a_connection_error(self):
        exc = DataSourceBlockedError.__new__(DataSourceBlockedError)
        assert isinstance(exc, ConnectionError)
        assert not should_retry(exc)
