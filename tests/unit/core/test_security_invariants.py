"""Static guards for the library's safety invariants."""

import ast
from pathlib import Path

import pytest

PKG = Path(__file__).resolve().parents[3] / "vnmarket"
HTTP_VERBS = {"get", "post", "put", "delete", "patch", "request"}
FORBIDDEN_IMPORTS = {
    "vnai",
    "psutil",
    "cryptography",
    "subprocess",
    "pickle",
    "marshal",
}
FILES = sorted(PKG.rglob("*.py"))


def _parse(path):
    return ast.parse(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(PKG)))
def test_every_requests_call_has_timeout(path):
    missing = [
        n.lineno
        for n in ast.walk(_parse(path))
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and isinstance(n.func.value, ast.Name)
        and n.func.value.id == "requests"
        and n.func.attr in HTTP_VERBS
        and not any(k.arg == "timeout" for k in n.keywords)
    ]
    assert not missing, f"requests call without timeout at lines {missing}"


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(PKG)))
def test_no_forbidden_imports_or_dynamic_exec(path):
    for n in ast.walk(_parse(path)):
        names = []
        if isinstance(n, ast.Import):
            names = [a.name.split(".")[0] for a in n.names]
        elif isinstance(n, ast.ImportFrom) and n.module:
            names = [n.module.split(".")[0]]
        assert not FORBIDDEN_IMPORTS & set(names), f"{path.name}:{n.lineno}"
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            assert n.func.id not in {"eval", "exec"}, f"{path.name}:{n.lineno}"


def test_no_verify_false():
    for path in FILES:
        assert "verify=False" not in path.read_text(encoding="utf-8"), path.name


def test_core_constants_importable():
    from vnmarket.core.constants import DEFAULT_TIMEOUT, DataSources

    assert DEFAULT_TIMEOUT > 0
    assert "kbs" in DataSources.ALL_SOURCES


# --- logging conventions -------------------------------------------------

# logger.py implements get_logger; market.py wires its own opt-in handler
# (enable_log); the rest print on purpose for the user (show_api, env info).
LOGGER_IMPL = {"core/utils/logger.py", "core/utils/market.py", "config.py"}
PRINT_OK = {"core/utils/env.py", "ui/helper.py", "core/utils/browser_profiles.py"}


def _rel(path):
    return path.relative_to(PKG).as_posix()


@pytest.mark.parametrize("path", FILES, ids=_rel)
def test_modules_use_project_get_logger(path):
    if _rel(path) in LOGGER_IMPL:
        pytest.skip("logger implementation")
    for n in ast.walk(_parse(path)):
        if isinstance(n, ast.Call):
            f = n.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
            assert name != "getLogger", f"use get_logger(__name__) at line {n.lineno}"


@pytest.mark.parametrize("path", FILES, ids=_rel)
def test_no_stray_print(path):
    if _rel(path) in PRINT_OK:
        pytest.skip("intentional user-facing output")
    lines = [
        n.lineno
        for n in ast.walk(_parse(path))
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "print"
    ]
    assert not lines, f"print() at lines {lines}; use the module logger"


def test_importing_package_is_silent():
    import subprocess
    import sys

    out = subprocess.run(
        [sys.executable, "-c", "import vnmarket"],
        capture_output=True,
        text=True,
        cwd=PKG.parent,
        timeout=60,
    )
    assert out.returncode == 0, out.stderr
    assert out.stdout == "" and out.stderr == ""
