## Why

The starter has no authentication yet, and almost every real feature
(starting with the catalog) needs to know who the user is. Building sign
up, login, password reset and token refresh ourselves is slow and easy to
get wrong. Auth0 provides all of that through its hosted Universal Login,
so the starter can focus on validating identities instead of managing
credentials.

## What Changes

- The web app gets **Log in / Sign up / Log out** through Auth0 Universal
  Login (Authorization Code + PKCE), using `@auth0/auth0-react`.
- The web app gets client-side routing (`react-router`) with a public home
  page and a protected `/profile` page.
- Every API call from the web app sends the Auth0 access token as a
  `Bearer` token.
- The API validates Auth0 access tokens (RS256, issuer, audience, expiry)
  and rejects anything else with `401`.
- New protected endpoint **`GET /api/me/`** returns the current user's
  local profile. A profile is created automatically on the first
  authenticated request, keyed by the Auth0 `sub`. No passwords are stored.
- Swagger UI gets an **Authorize** button (Bearer JWT) to call protected
  endpoints.
- Public endpoints stay public: `/api/health/`, `/api/schema/`,
  `/api/docs/`.
- If Auth0 is not configured, the project still starts: the API reports a
  Django system-check warning and the web app shows a notice instead of a
  login button.
- **README**: the "token-based authentication" bullet becomes Auth0, and
  the roadmap item "Refresh tokens and password reset" is removed, since
  Auth0 covers both.

## Capabilities

### New Capabilities

- `authentication`: login and logout in the web app, protected routes,
  access-token validation in the API, the current-user endpoint, and local
  user provisioning.

### Modified Capabilities

None. There are no living specs yet.

## Impact

- **apps/web**: new dependencies `@auth0/auth0-react` and `react-router`;
  `Auth0Provider` and router in `main.tsx`; API client attaches tokens.
- **apps/api**: new dependency `PyJWT[crypto]`; new code in every layer
  (`domain/users`, `application/users`, `infrastructure/auth`,
  `infrastructure/users`, `presentation/api/me.py`, `config`); one new
  migration for the user profile table.
- **Configuration**: new variables `AUTH0_DOMAIN`, `AUTH0_AUDIENCE`
  (API) and `VITE_AUTH0_DOMAIN`, `VITE_AUTH0_CLIENT_ID`,
  `VITE_AUTH0_AUDIENCE` (web). None of them are secrets.
- **docker-compose.yml**: the `web` service reads `.env`.
- **CI**: no Auth0 credentials needed; tests use locally generated keys.
- **Docs**: `docs/auth0-setup.md` (dashboard steps), decision record
  `docs/decisions/0003-auth0.md`, README and `docs/architecture.md`.
