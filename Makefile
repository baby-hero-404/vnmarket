# ==============================================================================
# vnmarket Development Makefile
# Best-practice automation for testing, linting, packaging, and dependencies.
# ==============================================================================

SHELL := /usr/bin/env bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

# ------------------------------------------------------------------------------
# Environment & Tooling Resolution
# ------------------------------------------------------------------------------
VENV ?= $(or $(and $(wildcard .venv/bin/python),.venv),\
             $(and $(wildcard $(HOME)/.venv/bin/python),$(HOME)/.venv),\
             $(VIRTUAL_ENV))
BIN  := $(if $(VENV),$(VENV)/bin/,)

PYTHON := $(if $(BIN),$(BIN)python,python3)
RUFF   := $(if $(BIN),$(BIN)ruff,ruff)
PYTEST := $(if $(BIN),$(BIN)pytest,pytest)
UV     := $(shell command -v uv 2>/dev/null)
PIP    := $(if $(UV),$(UV) pip,$(PYTHON) -m pip)
PIP_TARGET := $(if $(UV),--python $(PYTHON),)
LOCK   ?= requirements.lock

# Terminal Styling
BOLD   := \033[1m
GREEN  := \033[32m
CYAN   := \033[36m
YELLOW := \033[33m
RED    := \033[31m
RESET  := \033[0m

# ==============================================================================
##@ 🚀 General
# ==============================================================================
.PHONY: help
help: ## Display this interactive help menu
	@printf "$(BOLD)vnmarket Development Workflow Commands$(RESET)\n"
	@printf "Usage: make $(CYAN)<target>$(RESET)\n\n"
	@awk 'BEGIN {FS = ":.*##"; printf ""} \
		/^[a-zA-Z_-]+:.*?##/ { printf "  $(CYAN)%-16s$(RESET) %s\n", $$1, $$2 } \
		/^##@/ { printf "\n$(BOLD)%s$(RESET)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

# ==============================================================================
##@ 🔍 Code Quality & Formatting
# ==============================================================================
.PHONY: format format-check lint

format: ## Auto-format code and fix lint issues with Ruff
	@printf "$(GREEN)🎨 Formatting and auto-fixing code with Ruff...$(RESET)\n"
	$(RUFF) check --fix .
	$(RUFF) format .

format-check: ## Check code formatting without modifying files
	@printf "$(CYAN)🔍 Checking code formatting...$(RESET)\n"
	$(RUFF) format --check .

lint: ## Run linter checks (Ruff)
	@printf "$(CYAN)🔍 Running Ruff linter...$(RESET)\n"
	$(RUFF) check .

# ==============================================================================
##@ 🧪 Testing
# ==============================================================================
.PHONY: test test-cov test-live

test: ## Run unit and integration tests (mock-based, fast)
	@printf "$(GREEN)🧪 Running test suite...$(RESET)\n"
	PYTHONPATH=. $(PYTEST) tests/

test-cov: ## Run test suite with terminal coverage report
	@printf "$(GREEN)📊 Running tests with coverage report...$(RESET)\n"
	PYTHONPATH=. $(PYTEST) --cov=vnmarket --cov-report=term-missing tests/

test-live: ## Run live explorer tests against real endpoints (requires internet)
	@printf "$(YELLOW)🌐 Running live explorer tests (LIVE_TEST=1)...$(RESET)\n"
	LIVE_TEST=1 PYTHONPATH=. $(PYTEST) tests/

# ==============================================================================
##@ ✅ Verification & CI
# ==============================================================================
.PHONY: verify check

verify: format lint test ## Auto-format, lint, and run all tests
	@printf "\n$(GREEN)✅ All checks and tests passed successfully! Ready to commit / release.$(RESET)\n"

check: format-check lint test ## CI-safe check: verify formatting, lint, and tests without mutations
	@printf "\n$(GREEN)✅ CI verification passed!$(RESET)\n"

# ==============================================================================
##@ 📦 Build & Release
# ==============================================================================
.PHONY: build tag

build: clean ## Build sdist and wheel distribution packages
	@printf "$(GREEN)📦 Building source and wheel distributions...$(RESET)\n"
	$(if $(UV),$(UV) build,$(PYTHON) -m build)
	@printf "$(GREEN)✅ Build artifacts created in dist/$(RESET)\n"

tag: ## Show current version and helper commands to create a release tag
	@VERSION=$$(grep -E '^version\s*=' pyproject.toml | head -1 | tr -d ' "' | cut -d'=' -f2); \
	printf "$(BOLD)Current version in pyproject.toml:$(RESET) $(GREEN)v$$VERSION$(RESET)\n\n"; \
	printf "To create and push a release tag, run:\n"; \
	printf "  $(CYAN)git tag -a v$$VERSION -m 'Release v$$VERSION'$(RESET)\n"; \
	printf "  $(CYAN)git push origin v$$VERSION$(RESET)\n"

# ==============================================================================
##@ 🛠️ Dependencies & Maintenance
# ==============================================================================
.PHONY: install install-dev outdated upgrade clean

install: ## Install package in editable mode
	@printf "$(CYAN)📦 Installing vnmarket...$(RESET)\n"
	$(PIP) install $(PIP_TARGET) -e .

install-dev: ## Install package with development and testing dependencies
	@printf "$(CYAN)📦 Installing vnmarket with [dev,test] dependencies...$(RESET)\n"
	$(PIP) install $(PIP_TARGET) -e ".[dev]"

outdated: ## Check for outdated dependencies
	@printf "$(CYAN)📦 Checking for outdated dependencies...$(RESET)\n"
	@$(if $(UV),$(UV) pip list --outdated --python $(PYTHON),$(PYTHON) -m pip list --outdated)

upgrade: ## Upgrade dependencies, re-test, and rollback on failure
	@set -e; \
	backup=$$(mktemp); trap 'rm -f $$backup' EXIT; \
	$(PIP) freeze $(PIP_TARGET) | grep -v '^-e ' > $$backup; \
	printf "\n$(CYAN)📦 Current outdated packages:$(RESET)\n"; \
	$(MAKE) --no-print-directory outdated || true; \
	printf "\n$(CYAN)⬆️  Upgrading dependencies...$(RESET)\n"; \
	if $(PIP) install -U $(PIP_TARGET) -e ".[dev]" && $(MAKE) --no-print-directory lint test; then \
		$(PIP) freeze $(PIP_TARGET) | grep -v '^-e ' > $(LOCK); \
		printf "\n$(GREEN)✅ Upgrade successful. Versions pinned in $(LOCK)$(RESET)\n"; \
	else \
		printf "\n$(RED)❌ Upgrade checks failed — rolling back to previous state...$(RESET)\n"; \
		$(PIP) install $(PIP_TARGET) -r $$backup; \
		printf "$(YELLOW)↩️  Rolled back dependencies.$(RESET)\n"; exit 1; \
	fi

clean: ## Clean up cache, build artifacts, and compiled bytecode
	@printf "$(CYAN)🧹 Cleaning up build artifacts and caches...$(RESET)\n"
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov dist build *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	@printf "$(GREEN)✅ Cleaned.$(RESET)\n"
