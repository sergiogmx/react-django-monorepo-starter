# Architecture

## Overview

    Browser ──▶ web (Vite, :5173) ──/api proxy──▶ api (Django, :8000) ──▶ db (PostgreSQL)

The browser only talks to Vite. Vite forwards every `/api` request to
Django, so there is no CORS setup in development. Docker Compose runs the
three services; the `Makefile` is the entry point for all of them.

## Frontend

- `apps/web`: the React + TypeScript app. Talks to the API through small
  functions in `src/api/`; components never call `fetch` directly.
- `packages/ui`: shared components. Each one has a CSF story next to it
  and a Vitest test.
- `packages/tokens`: design tokens in W3C format (`tokens.json`).
  `make tokens` generates `theme.css`, a Tailwind v4 `@theme` block that
  both the web app and Ladle import. CI fails if it is out of date.
- `apps/docs`: Ladle, pointed at the stories in `packages/ui`.

## Backend: Clean Architecture

`apps/api` is split into layers. Dependencies point inward only:

    config ──▶ presentation ─┐
           └─▶ infrastructure ┴─▶ application ──▶ domain

| Layer            | Holds                                                     | May import                     |
| ---------------- | --------------------------------------------------------- | ------------------------------ |
| `domain`         | Entities, value objects, rules, ports (`Protocol`s)       | Nothing (standard library)     |
| `application`    | Use cases, one class per action, with an `execute` method | `domain`                       |
| `infrastructure` | Django models, migrations, repository implementations     | `application`, `domain`        |
| `presentation`   | DRF views, serializers, permissions                       | `application`, `domain`        |
| `config`         | Settings, URLs, dependency container                      | Everything (composition root)  |

`presentation` and `infrastructure` do not import each other. Views get
their use case injected by `config/urls.py`, which takes it from
`config/container.py`.

These rules are enforced by `import-linter` (contracts in
`apps/api/pyproject.toml`), run by `make lint` and by CI.

### The health check as the reference example

The `/api/health/` endpoint walks through every layer and is the template
to copy for new features:

1. `domain/health.py`: `HealthReport` entity and the `DatabaseProbe` port.
2. `application/health/check_health.py`: the `CheckHealth` use case.
3. `infrastructure/health/django_database_probe.py`: the port implemented
   with Django's connection.
4. `presentation/api/health.py`: `HealthView`, which only calls the use
   case and maps the result to HTTP, and `HealthSerializer`, which shapes
   the response and documents it in OpenAPI via `@extend_schema`.
5. `config/container.py` and `config/urls.py`: the wiring.

### Tests

- `tests/application/`: use cases with fake ports. Plain `unittest`, no
  Django, no database.
- `tests/presentation/`: endpoints through Django's test client, plus
  views with injected fakes for the edge cases.
