## Context

The API follows Clean Architecture with enforced import contracts
(`docs/decisions/0001-clean-architecture-api.md`): `domain` and
`application` must not import Django, DRF or any vendor SDK. The web app is
a Vite SPA that talks to the API through Vite's `/api` proxy. There is no
router and no user model yet.

Auth0 setup (tenant, SPA application, API) is done by hand in the Auth0
dashboard and documented in `docs/auth0-setup.md`.

## Goals / Non-Goals

**Goals:**

- Login, sign up and logout via Auth0 Universal Login.
- The API trusts only valid Auth0 access tokens for its own audience.
- A local profile per Auth0 user, so future features can own data.
- Auth0 stays an infrastructure detail: replacing it later touches
  `infrastructure/auth` and the web provider, not use cases.
- Tests and CI run without network access to Auth0.

**Non-Goals:**

- Roles and permissions (RBAC). Planned as a separate change.
- Machine-to-machine clients.
- A custom login UI or embedded login.
- The OAuth2 login flow inside Swagger UI; pasting a token is enough.
- Syncing profile data (name, picture) from Auth0 into the API.

## Decisions

### D1. Web: `@auth0/auth0-react` with refresh tokens in local storage

Authorization Code + PKCE through the official SDK. `Auth0Provider` uses
`useRefreshTokens: true` and `cacheLocation: 'localstorage'`.

- *Why*: without a custom Auth0 domain, silent authentication relies on a
  third-party cookie that Safari and Brave block, so users would be logged
  out on every reload. Rotating refresh tokens avoid that.
- *Trade-off*: tokens in local storage are readable by injected scripts
  (XSS). Mitigated by short access-token lifetime and refresh-token
  rotation. Production deployments with a custom domain can switch to
  `cacheLocation: 'memory'`; documented in the decision record.
- Requires, in the Auth0 dashboard: **Refresh Token Rotation** on the SPA
  application and **Allow Offline Access** on the API.

### D2. Web: React Router v7 with a `RequireAuth` wrapper

`react-router` v7 in declarative mode (`BrowserRouter` + `Routes`), not
framework mode: the app stays a plain Vite SPA.

Routes: `/` (public: health status, Log in / Log out) and `/profile`
(protected). `RequireAuth` reads the app's own `useAuth()` (see D3) and,
for anonymous users, calls `login({ returnTo })`, which stores the target
path in `appState.returnTo`; `Auth0Provider.onRedirectCallback` navigates
there after login.

*Changed during implementation*: `RequireAuth` does not use Auth0's
`withAuthenticationRequired`, so it also handles the "not configured"
state and stays testable without the SDK.

- *Why*: the most widely known React router, the simplest option for a
  starter other people will clone, and it works with Auth0's
  `withAuthenticationRequired` without extra wiring.
- *Alternative considered*: TanStack Router, for type-safe routes and
  search params (useful for the catalog's pagination and filters). Not
  chosen, to keep the starter on the more familiar tool; search params
  will be validated by hand where needed.

### D3. Web: the SDK behind `useAuth()`, one authenticated fetch helper

`src/auth/AuthContext.ts` defines the app's own auth state (`status`,
`user`, `error`, `login`, `logout`, `getAccessToken`). `AuthProvider`
fills it from `@auth0/auth0-react`, or with an "unconfigured" state when
the variables are missing. Components and tests only use `useAuth()`.

`src/api/client.ts` exposes `useApiFetch()`, which wraps `fetch` and adds
the token from `getAccessToken()`. The audience is set once on
`Auth0Provider`. Feature functions in `src/api/` receive the fetch
function, so components never handle tokens.

### D4. API: token validation with PyJWT, behind a port

- `application/auth/ports.py` defines `AccessTokenVerifier` (Protocol):
  `verify(token: str) -> Identity`, raising `InvalidAccessToken`.
- `domain/users.py` defines `Identity` (`subject`, `email | None`).
- `infrastructure/auth/jwt_verifier.py` implements it with PyJWT:
  algorithms fixed to `["RS256"]`, `issuer=https://<domain>/`,
  `audience=<audience>`, required claims `exp`, `iss`, `aud`, `sub`,
  10 seconds of leeway.
- The signing key comes from a **key resolver** passed to the constructor.
  Production uses `PyJWKClient(https://<domain>/.well-known/jwks.json)`,
  which caches keys and refetches on an unknown `kid`. Tests pass a
  resolver backed by an RSA key generated in the test, so every rejection
  scenario (expired, wrong audience, wrong issuer, HS256, `alg: none`,
  foreign key) is tested for real, offline.
- *Alternative considered*: Authlib (Auth0's Django quickstart). PyJWT is
  smaller, already standard, and enough for validation only.

### D5. API: where the DRF pieces live

- `infrastructure/auth/drf_authentication.py`: `Auth0BearerAuthentication`
  (`BaseAuthentication`). Parses `Authorization: Bearer`, calls the
  verifier, and sets `request.user` to an `AuthenticatedPrincipal` that
  wraps the `Identity` and has `is_authenticated = True`. DRF builds
  authentication classes without arguments, so the class gets its verifier
  from `infrastructure.auth.factory.get_verifier()`, built once from
  settings. This keeps `presentation` free of `config` imports.
- It returns `WWW-Authenticate: Bearer` so missing tokens yield `401`,
  not `403`.
- Set as `DEFAULT_AUTHENTICATION_CLASSES` with `IsAuthenticated` as the
  default permission. Public views (health, schema, Swagger) opt out
  explicitly with `AllowAny` and no authentication classes. Secure by
  default: a new view is protected unless someone decides otherwise.

### D6. API: user profile, not `django.contrib.auth.User`

- `domain/users.py`: `UserProfile` entity (`id`, `subject`, `email`,
  `created_at`) and `UserProfileRepository` port with
  `get_or_create(identity) -> UserProfile`.
- `application/users/get_current_user.py`: `GetCurrentUser` use case.
- `infrastructure/users/models.py`: `UserProfileModel` with a unique
  `subject`. The repository uses Django's `get_or_create`, which already
  catches the `IntegrityError` of a concurrent insert and re-reads the
  row. `email` is stored as `""` when unknown (Django convention) and
  mapped to `None` in the entity. The email is refreshed when a token
  brings a new one.
- *Why not `contrib.auth.User`*: it carries passwords, usernames and
  permissions we don't want to duplicate from Auth0. `contrib.auth` stays
  only for Django Admin superusers.

### D7. Email claim is optional

Auth0 access tokens don't include the email by default. The verifier reads
it from a configurable namespaced claim (`AUTH0_EMAIL_CLAIM`, default
`https://starter.local/email`) and leaves it `null` when absent.
`docs/auth0-setup.md` includes the optional Auth0 Action that adds it.

### D8. Swagger: Bearer scheme through a drf-spectacular extension

An `OpenApiAuthenticationExtension` for `Auth0BearerAuthentication`
declares an HTTP Bearer JWT scheme. Views without authentication classes
get no security requirement, so public endpoints show no lock.
`make api-schema` keeps validating with `--fail-on-warn`.

### D9. Missing configuration degrades, it does not crash

- API: a Django system check (`auth.W001`) lists the empty `AUTH0_*`
  variables. `get_verifier()` returns a verifier that rejects every token,
  so protected endpoints answer `401` and public ones keep working.
- Web: `src/auth/config.ts` reads the `VITE_AUTH0_*` variables; if any is
  empty, the app renders without `Auth0Provider` and the home page shows a
  "Configure Auth0" notice pointing to `docs/auth0-setup.md`.

### D10. Configuration lives in the root `.env`

- `.env.example` gets `AUTH0_DOMAIN`, `AUTH0_AUDIENCE`,
  `AUTH0_EMAIL_CLAIM`, `VITE_AUTH0_DOMAIN`, `VITE_AUTH0_CLIENT_ID`,
  `VITE_AUTH0_AUDIENCE`. None are secrets.
- `apps/web/vite.config.ts` sets `envDir` to the repo root, so `npm run
  dev` on the host and the Docker container read the same file.
- *Changed during implementation*: no `env_file` for the `web` service.
  The container mounts the repo root, so `envDir` already finds `.env`.

## Layer map

    domain/users.py                      Identity, UserProfile, UserProfileRepository
    application/auth/ports.py            AccessTokenVerifier, InvalidAccessToken
    application/users/get_current_user.py
    infrastructure/auth/jwt_verifier.py  PyJWT implementation
    infrastructure/auth/drf_authentication.py
    infrastructure/auth/factory.py       verifier from settings
    infrastructure/auth/checks.py        auth.W001
    infrastructure/auth/openapi.py       drf-spectacular extension
    infrastructure/users/models.py       UserProfileModel + migration
    infrastructure/users/repository.py   DjangoUserProfileRepository
    presentation/api/me.py               MeView + UserProfileSerializer
    config/container.py, config/urls.py  wiring

`import-linter` contracts stay unchanged and must keep passing.

## Risks / Trade-offs

- **Tokens in local storage (XSS)** → short-lived access tokens, rotation,
  documented switch to memory storage with a custom domain.
- **JWKS endpoint unreachable** → keys are cached by `PyJWKClient`; a cold
  start during an Auth0 outage returns `401`, which is the safe failure.
- **A profile per M2M token** if someone calls the API with a
  client-credentials token (its `sub` ends in `@clients`) → acceptable in
  development; M2M is a non-goal.
- **Profiles are never deleted** when a user is removed from Auth0 → out
  of scope; a future change can add a cleanup.

## Migration Plan

1. One new migration in `infrastructure` creates the profile table.
   `make migrate` applies it; it is additive.
2. Developers run `make build` (new Python and npm dependencies), fill the
   Auth0 variables in `.env`, and `make up`.
3. Rollback: revert the change and roll back the migration with
   `manage.py migrate infrastructure zero`.

## Open Questions

- Final audience identifier and email claim namespace, once the Auth0
  tenant exists. The defaults above are placeholders.
