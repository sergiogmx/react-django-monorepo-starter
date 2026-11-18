# 0001. Clean Architecture for the API

- Status: accepted
- Date: 2026-11-18

## Context

Django encourages putting business logic in models and views. That is fast
at first, but the logic becomes hard to test without a database and hard
to change without touching the framework. This starter is meant to grow
into real products, so the API's core rules should outlive any framework
choice.

## Decision

The API in `apps/api` follows Clean Architecture with four layers
(`domain`, `application`, `infrastructure`, `presentation`) plus `config`
as the composition root. Dependencies point inward only. Domain and
application code must not import Django, DRF or database drivers.

The rules are enforced, not just documented: `import-linter` contracts in
`apps/api/pyproject.toml` run in `make lint` and in CI, and the build fails
on any violation.

## Consequences

- Use cases are tested with fakes in milliseconds, without a database.
- Each feature costs a bit more code: an entity, a port, a use case, an
  implementation and a view, instead of a model and a `ModelViewSet`.
- Django models live in `infrastructure` and are mapped to domain entities
  at the repository boundary. We give up some ORM conveniences (passing
  querysets around) in exchange for a core that does not depend on them.
- Django Admin keeps working, because it reads the models in
  `infrastructure` directly.
