# 0002. Makefile as the single entry point

- Status: accepted
- Date: 2026-11-18

## Context

Running the project involves Docker Compose, `manage.py` inside a
container, npm workspaces and the token generator. Each has its own
syntax, and people end up with slightly different commands in their
shell history.

## Decision

The root `Makefile` is the documented way to run anything: `make setup`
once, then `make up`, `make test`, `make lint` and so on. Every target has
a `## description` so `make help` lists it. The README and docs refer to
`make` targets, not to the underlying tools.

## Consequences

- One command to learn per task, the same for everyone and for CI-like
  checks run locally.
- Make is required on the host (preinstalled on macOS and most Linux;
  on Windows, use WSL).
- The underlying commands still work for anyone who needs them; the
  Makefile is a thin wrapper, not a build system.
