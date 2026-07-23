.PHONY: install lint format typecheck test clean setup

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

install: ## Create venv and install dependencies
	python3.13 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e "."
	$(PIP) install --group dev
	$(VENV)/bin/pre-commit install

setup: install ## Alias for install

lint: ## Run ruff linter
	$(VENV)/bin/ruff check .

format: ## Run ruff formatter
	$(VENV)/bin/ruff format .

typecheck: ## Run mypy type checker
	$(VENV)/bin/mypy .

test: ## Run pytest
	$(VENV)/bin/pytest

clean: ## Remove cache
	rm -rf .mypy_cache .ruff_cache .pytest_cache .coverage .codegraph htmlcov
	find scripts/ tests/ docs/ -type d -name "__pycache__" | xargs rm -rf

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
