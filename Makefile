.DEFAULT_GOAL := help

COMPOSE := docker compose
API     := $(COMPOSE) exec api
MANAGE  := $(API) python manage.py

API_DOCS_URL := http://localhost:8000/api/docs/
# `make up` opens Swagger UI once the API answers. Disable with OPEN_BROWSER=0.
OPEN_BROWSER ?= 1

.PHONY: help setup install build up down restart logs ps \
        shell-api shell-db migrate makemigrations createsuperuser \
        test test-api test-web lint lint-api lint-web format typecheck \
        tokens docs swagger api-schema clean

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

# --- Setup & lifecycle -------------------------------------------------------

setup: ## First run: .env, npm install, build, start and migrate
	@test -f .env || cp .env.example .env
	$(MAKE) install
	$(MAKE) build
	$(MAKE) up OPEN_BROWSER=0
	$(MAKE) migrate
	@if [ "$(OPEN_BROWSER)" = "1" ]; then $(MAKE) --no-print-directory swagger; fi

install: ## Install JS dependencies on the host (editor, lint, docs)
	npm install

build: ## Build (or rebuild) all Docker images
	$(COMPOSE) build

up: ## Start web, api and db, then open Swagger UI (OPEN_BROWSER=0 to skip)
	$(COMPOSE) up -d
	@echo "Web: http://localhost:5173  |  API docs: $(API_DOCS_URL)"
	@if [ "$(OPEN_BROWSER)" = "1" ]; then $(MAKE) --no-print-directory swagger; fi

down: ## Stop and remove the containers
	$(COMPOSE) down

restart: down up ## Restart everything

logs: ## Follow the logs of every service
	$(COMPOSE) logs -f

ps: ## List running services
	$(COMPOSE) ps

# --- Backend -----------------------------------------------------------------

shell-api: ## Open a shell inside the api container
	$(API) sh

shell-db: ## Open psql inside the db container
	$(COMPOSE) exec db sh -c 'psql -U "$$POSTGRES_USER" "$$POSTGRES_DB"'

migrate: ## Apply Django migrations
	$(MANAGE) migrate

makemigrations: ## Create new Django migrations
	$(MANAGE) makemigrations

createsuperuser: ## Create a Django admin user
	$(MANAGE) createsuperuser

swagger: ## Wait for the API, then open Swagger UI in the browser
	@printf "Waiting for the API"; \
	for i in $$(seq 1 60); do \
		curl -sf -o /dev/null $(API_DOCS_URL) && break; \
		printf "."; sleep 1; \
	done; \
	if ! curl -sf -o /dev/null $(API_DOCS_URL); then \
		echo " not ready after 60s. Check 'make logs'."; exit 1; \
	fi; \
	echo " ready."; \
	if command -v open >/dev/null 2>&1; then open $(API_DOCS_URL); \
	elif command -v xdg-open >/dev/null 2>&1; then xdg-open $(API_DOCS_URL); \
	else echo "Open $(API_DOCS_URL) in your browser."; fi

api-schema: ## Validate the OpenAPI schema (fails on warnings)
	$(MANAGE) spectacular --validate --fail-on-warn --file /dev/null

# --- Quality -----------------------------------------------------------------

test: test-api test-web ## Run all tests

test-api: ## Run the API tests (inside the api container)
	$(MANAGE) test

test-web: ## Run the web and UI tests
	npm test

lint: lint-api lint-web ## Lint everything, including the architecture rules

lint-api: ## Ruff + Clean Architecture import contracts
	$(API) ruff check .
	$(API) ruff format --check .
	$(API) lint-imports
	$(MAKE) --no-print-directory api-schema

lint-web: ## ESLint, Prettier check and TypeScript
	npm run lint
	npm run format:check
	npm run typecheck

format: ## Format the API (Ruff) and the web (Prettier)
	$(API) ruff check --fix .
	$(API) ruff format .
	npm run format

typecheck: ## Type-check the TypeScript workspaces
	npm run typecheck

# --- Design system -----------------------------------------------------------

tokens: ## Regenerate packages/tokens/theme.css from tokens.json
	npm run tokens

docs: ## Start Ladle component docs on http://localhost:61000
	npm run docs

# --- Cleanup -----------------------------------------------------------------

clean: ## Stop everything and delete volumes (wipes the database)
	$(COMPOSE) down -v --remove-orphans
