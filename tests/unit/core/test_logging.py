import logging
import subprocess
import sys
import textwrap
from pathlib import Path

from vnmarket.config import Config
from vnmarket.core.utils.logger import _DEFAULT_FORMAT, get_logger

ROOT = Path(__file__).resolve().parents[3]


def _own_handlers():
    """Handlers installed by vnmarket (pytest attaches its own to loggers too)."""
    return [
        h
        for h in logging.getLogger("vnmarket").handlers
        if h.formatter is not None and h.formatter._fmt == _DEFAULT_FORMAT
    ]


def test_module_logger_shares_the_package_handler():
    log = get_logger("vnmarket.tests.shared")
    assert log.handlers == []
    assert len(_own_handlers()) == 1
    assert logging.getLogger("vnmarket").propagate is False


def test_repeated_calls_never_stack_handlers():
    for _ in range(3):
        get_logger("vnmarket.tests.repeat")
    assert len(_own_handlers()) == 1


def test_follows_config_log_level():
    log = get_logger("vnmarket.tests.level")
    pkg = logging.getLogger("vnmarket")
    old = pkg.level
    try:
        pkg.setLevel(logging.ERROR)
        assert not log.isEnabledFor(logging.INFO)
        pkg.setLevel(Config.LOG_LEVEL)
        assert log.isEnabledFor(logging.INFO)
        assert not log.isEnabledFor(logging.DEBUG)
    finally:
        pkg.setLevel(old)


def test_custom_arguments_build_dedicated_logger():
    log = get_logger("vnmarket.tests.custom", level="WARNING")
    assert log.level == logging.WARNING
    assert len(log.handlers) == 1


def test_app_root_logging_does_not_duplicate_records():
    code = textwrap.dedent(
        """
        import logging, sys
        logging.basicConfig(stream=sys.stdout, format="ROOT:%(message)s")
        from vnmarket.core.utils.logger import get_logger
        get_logger("vnmarket.demo").error("once")
        """
    )
    out = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=60,
    )
    assert out.returncode == 0, out.stderr
    assert out.stderr.count("once") == 1  # package handler (stderr)
    assert "ROOT:" not in out.stdout  # root handler saw nothing
