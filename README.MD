# Full-Stack Boilerplate — React, TypeScript & Django

A production-minded monorepo starter with a React + TypeScript
frontend and a Django REST API backend, wired together with Docker
Compose. Built to clone, run, and start shipping a real feature
in minutes — not to reconfigure tooling for a day.

## What is included

- React + TypeScript + Vite frontend with Tailwind CSS
- Django + Django REST Framework API with PostgreSQL, structured
  with Clean Architecture (domain, application, infrastructure,
  presentation)
- Authentication with Auth0: sign up, log in, log out and password
  reset through Universal Login, protected routes in the web app,
  and JWT validation in the API (secure by default)
- Working catalog example: full CRUD with invented seed data
- Docker Compose setup for the web app, API, and database
- A `Makefile` as the single entry point: `make build`, `make up`,
  `make test`, and the rest of the daily commands
- Component documentation with Ladle: shared UI components in
  `packages/ui`, each with a CSF story, documented in `apps/docs`
- Design tokens in W3C format under `packages/tokens`
- Linting and basic tests on both sides, plus a GitHub Actions CI workflow
- Spec-driven workflow with OpenSpec 2.1.0: living specs under
  `openspec/specs/` and one reviewed change folder per feature
- Architecture notes and decision records under `docs/`

## Tech stack

Frontend: React, TypeScript, Vite, Tailwind CSS, React Router
Auth: Auth0 (`@auth0/auth0-react` on the web, PyJWT on the API)
Backend: Python, Django, Django REST Framework, drf-spectacular
(OpenAPI + Swagger UI)
Database: PostgreSQL
Tooling: Make, Docker Compose, ESLint, Prettier, Ruff, GitHub Actions,
OpenSpec 2.1.0, Ladle

## Project structure

    apps/web        React + TypeScript frontend
    apps/api        Django REST API, organized by Clean Architecture
    apps/docs       Component documentation, powered by Ladle
    packages/ui     Shared UI components, each with a CSF story
    packages/tokens Design tokens in W3C format
    openspec/       Living specs (specs/) and proposed changes (changes/)
    docs/           Architecture notes and decision records

## Getting started

Prerequisites: Docker, Make, and Node.js 20.19 or newer
(22 recommended, see `.nvmrc`). Python 3.13 is only needed to
run the API outside Docker.

1. Clone the repository:

   git clone <repo-url> && cd react-django-monorepo-starter

2. Run the first-time setup. It copies `.env.example` to `.env`
   (if missing), runs `npm install`, builds the images, starts
   the containers, and applies the migrations:

   make setup

3. Swagger UI opens in your browser as soon as the API answers,
   at http://localhost:8000/api/docs/. The web app runs at
   http://localhost:5173; it calls the API's health check and
   shows whether the API and the database are up.

4. Configure Auth0 to enable login: create an API and a
   Single Page Application in your Auth0 tenant, fill the
   `AUTH0_*` and `VITE_AUTH0_*` variables in `.env`, and run
   `make restart`. Step by step in
   [docs/auth0-setup.md](docs/auth0-setup.md). Until then the
   app runs, protected endpoints answer 401, and the web app
   shows a notice instead of the login button.

After that, `make up` and `make down` are all you need day to day.

## Daily commands with Make

The `Makefile` at the root is the single entry point for the
project. Use it instead of calling `docker compose`, `manage.py`,
or `npm` directly, so everyone runs the same commands the same
way. Run `make` (or `make help`) to list them all.

    make setup            First run: .env, install, build, up, migrate
    make install          npm install on the host
    make build            Build or rebuild all images
    make up               Start web, api, and db in the background,
                          then open Swagger UI (OPEN_BROWSER=0 skips it)
    make down             Stop the containers
    make restart          Restart everything
    make logs             Follow the logs of every service
    make ps               List running services

    make migrate          Apply Django migrations
    make makemigrations   Create new migrations
    make createsuperuser  Create a Django admin user
    make swagger          Wait for the API and open Swagger UI
    make api-schema       Validate the OpenAPI schema
    make shell-api        Open a shell in the api container
    make shell-db         Open psql in the db container

    make test             Run API and web tests
    make lint             Ruff, architecture contracts, ESLint,
                          Prettier check, and TypeScript
    make format           Ruff format and Prettier
    make typecheck        Type-check the TypeScript workspaces

    make tokens           Regenerate theme.css from tokens.json
    make docs             Start Ladle on http://localhost:61000
    make clean            Stop everything and delete volumes
                          (wipes the database)

A typical day is `make up`, work, `make test && make lint`,
and `make down`. Run `make build` again only when dependencies
or Dockerfiles change.

New commands go in the `Makefile` with a `## description`
comment, so they show up in `make help` automatically.

## API architecture: Clean Architecture

The API in `apps/api` follows Clean Architecture. Business
rules do not depend on Django, Django REST Framework, or
PostgreSQL; the framework and the database are details that
plug into the core, not the other way around.

The code is split into four layers, plus `config/` as the
composition root:

    apps/api/
      domain/          Entities, value objects, domain rules and
                       repository interfaces. Plain Python, no
                       Django imports.
      application/     Use cases (one per action, e.g.
                       CreateCatalogItem) and DTOs. Orchestrates
                       the domain through the interfaces it defines.
      infrastructure/  Django ORM models, migrations, repository
                       implementations, auth and external services.
      presentation/    DRF views, serializers and permissions.
                       Translates HTTP into use-case calls.
      config/          Django settings, URLs, and the dependency
                       container that wires use cases to their
                       implementations.

The dependency rule: dependencies point inward only.
`presentation` and `infrastructure` depend on `application`,
`application` depends on `domain`, and `domain` depends on
nothing. Concretely:

- Views never touch the ORM; they call a use case.
- Use cases receive repositories through their constructor
  (dependency injection) and only know the interfaces from
  `domain`.
- Django models live in `infrastructure` and are mapped to
  domain entities at the repository boundary; they never leak
  into `domain` or `application`.
- Domain and use-case tests run without a database or Django;
  infrastructure and API tests cover the adapters.

The API is documented with OpenAPI 3 through drf-spectacular:
the schema is at `/api/schema/` and Swagger UI at `/api/docs/`.
Every endpoint declares its responses with `@extend_schema` and
a serializer in `presentation`; `make lint` and CI fail if the
schema has warnings, so the docs cannot drift from the code.

These rules are enforced, not just documented: `import-linter`
contracts in `apps/api/pyproject.toml` run in `make lint` and in
CI, and the build fails if, for example, `domain` imports Django.

Every new feature in the API follows the same path: domain
first, then the use case, then the repository implementation,
and finally the endpoint. The `/api/health/` endpoint is the
reference example that walks through every layer. See
[docs/architecture.md](docs/architecture.md) and the decision
record [docs/decisions/0001-clean-architecture-api.md](docs/decisions/0001-clean-architecture-api.md).

## Component docs with Ladle

Shared components live in `packages/ui`, each with a story
in Component Story Format (CSF) next to the component, for
example `Button.tsx` and `Button.stories.tsx`. The stories
are documented with Ladle instead of Storybook: Ladle runs
on Vite, starts in under a second, and needs almost no
configuration. Because the stories are CSF, they also work
in Storybook if you ever need to migrate.

    make docs

Open http://localhost:61000 to browse the components in
isolation. Ladle lives in `apps/docs`; its config is in
`.ladle/config.mjs` and points at the stories in
`packages/ui`. Design tokens live in `packages/tokens` in
W3C format and are the single source for color, spacing,
and typography across the web app and the docs.

## How I work

This project is built spec-driven with OpenSpec 2.1.0.

The specs that describe how the system behaves today live in
`openspec/specs/`. Every feature starts as a change in
`openspec/changes/<name>/` with a `proposal.md` (why and what),
delta specs under `specs/` (ADDED / MODIFIED / REMOVED
requirements with concrete scenarios), a `design.md` (how),
and a `tasks.md` checklist. I review that plan before any
code is written.

The workflow is propose, apply, archive, driven by the
`openspec-*` skills — for example `/openspec-propose`, or
`$openspec-propose` in Codex. The old `/opsx:*` commands were
removed in OpenSpec 2.0. When a change is archived, its delta
specs merge into `openspec/specs/`, so the specs always match
the code.

To set it up from scratch:

    npm install -g @fission-ai/openspec@latest
    openspec init --scope project

An npm install needs Node.js 22.20.0 or newer. This repo uses
`--scope project` on purpose, so the skills live in
`.agents/skills/` inside the repo and anyone who clones it
gets the same setup. OpenSpec 2.1 installs skills globally
by default; use `openspec update` to change or refresh them.

## Roadmap

- [ ] Role-based permissions
- [ ] Pagination, search, and filters on the catalog
- [ ] Visual snapshot tests for Ladle stories with Playwright
- [ ] Deployment guide for a small VPS or PaaS

## License

MIT
