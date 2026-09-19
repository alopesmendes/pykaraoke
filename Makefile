.DEFAULT_GOAL := help
.PHONY: help install dev migrate superuser test cov lint fmt audit check db-up db-down clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Create the venv, install every dependency group, activate the local git hooks
	uv sync --all-groups
	uv run pre-commit install

dev: ## Run the local dev server
	uv run python manage.py runserver

migrate: ## Apply database migrations
	uv run python manage.py migrate

superuser: ## Create a Django admin superuser
	uv run python manage.py createsuperuser

test: ## Run the test suite
	uv run pytest

cov: ## Run the test suite with a coverage report
	uv run pytest --cov

lint: ## Ruff check + format check (no changes made)
	uv run ruff check .
	uv run ruff format --check .

fmt: ## Ruff check --fix + format (rewrites files)
	uv run ruff check --fix .
	uv run ruff format .

# bandit does not auto-discover pyproject.toml — without -c it ignores
# [tool.bandit] exclude_dirs entirely and crawls .venv's thousands of files.
#
# No --fail-level here: this runs against the real, local .env, where
# DEBUG=True and a placeholder key are correct for development and produce
# expected warnings. The strict version — --fail-level WARNING against a
# production-shaped environment — lives in tests/test_smoke.py (via
# pytest-env) and in security.yml (chunk 7), not in everyday local dev.
audit: ## Security checks: bandit, pip-audit, Django's own deploy check
	uv run bandit -qr . -c pyproject.toml
	uv run pip-audit
	uv run python manage.py check --deploy --tag security

check: lint test audit ## The full local gate — run before every PR

db-up: ## Start local Postgres + mailpit (docker-compose.yml, chunk 5)
	docker compose up -d

db-down: ## Stop local Postgres + mailpit
	docker compose down

clean: ## Remove caches and generated files
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -not -path './.venv/*' -exec rm -rf {} +
