VENV_BIN ?= $(shell if [ -d "$$HOME/.venv/bin" ]; then echo "$$HOME/.venv/bin"; elif [ -d ".venv/bin" ]; then echo ".venv/bin"; else echo ""; fi)
RUFF = $(if $(VENV_BIN),$(VENV_BIN)/ruff,ruff)
PYTEST = $(if $(VENV_BIN),$(VENV_BIN)/pytest,pytest)
PYTHON = $(if $(VENV_BIN),$(VENV_BIN)/python,python)
UV := $(shell command -v uv 2>/dev/null)
# Prefer uv (fast, works in venvs without pip); fall back to pip.
PIP = $(if $(UV),$(UV) pip --quiet,$(PYTHON) -m pip --quiet)
PIP_TARGET = $(if $(UV),--python $(PYTHON),)
LOCK ?= requirements.lock

.PHONY: help format lint test test-live verify clean outdated upgrade

help:
	@echo "🚀 vnmarket Development Workflow Commands:"
	@echo "----------------------------------------------------------------"
	@echo "make verify      : 🌟 Run everything: format, lint, and test."
	@echo "make format      : 🎨 Auto-format and auto-fix code using Ruff."
	@echo "make lint        : 🔍 Check code style and errors using Ruff."
	@echo "make test        : 🧪 Run all Pytest suites (Core & Unified UI)."
	@echo "make outdated    : 📦 List dependencies that have a newer release."
	@echo "make upgrade     : ⬆️  Upgrade all deps, re-check lint+tests, auto-rollback on failure."
	@echo "make clean       : 🧹 Clean up cache and compiled files."
	@echo "----------------------------------------------------------------"

format:
	@echo "\n🎨 Formatting and Auto-fixing code with Ruff..."
	$(RUFF) check --fix .
	$(RUFF) format .

lint:
	@echo "\n🔍 Running Linter..."
	$(RUFF) check .

test:
	@echo "\n🧪 Running Test Suites..."
	PYTHONPATH=. $(PYTEST) tests/

test-live:
	@echo "\n🌐 Running Live Explorer Tests (requires internet)..."
	LIVE_TEST=1 PYTHONPATH=. $(PYTEST) tests/

verify: format lint test
	@echo "\n✅ Vượt qua toàn bộ bài kiểm tra! Mã nguồn của bạn đã sạch, an toàn và sẵn sàng để Commit / Release."

outdated:
	@echo "\n📦 Outdated dependencies:"
	@$(if $(UV),$(UV) pip list --outdated --python $(PYTHON),$(PYTHON) -m pip list --outdated)

# Upgrade -> lint -> test. If anything fails, the previous environment is
# restored from a snapshot, so a bad release can never leave the venv broken.
# On success, the resolved versions are written to $(LOCK) for reproducibility.
upgrade:
	@set -e; \
	backup=$$(mktemp); trap 'rm -f $$backup' EXIT; \
	$(PIP) freeze $(PIP_TARGET) | grep -v '^-e ' > $$backup; \
	echo "\n📦 Before:"; $(MAKE) --no-print-directory outdated || true; \
	echo "\n⬆️  Upgrading dependencies..."; \
	if $(PIP) install -U $(PIP_TARGET) -e ".[dev]" && $(MAKE) --no-print-directory lint test; then \
		$(PIP) freeze $(PIP_TARGET) | grep -v '^-e ' > $(LOCK); \
		echo "\n✅ Upgrade OK. Versions pinned in $(LOCK)"; \
	else \
		echo "\n❌ Upgrade or checks failed - rolling back..."; \
		$(PIP) install $(PIP_TARGET) -r $$backup; \
		echo "↩️  Rolled back to previous versions."; exit 1; \
	fi

clean:
	@echo "\n🧹 Cleaning up caches..."
	rm -rf .pytest_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "Done!"

