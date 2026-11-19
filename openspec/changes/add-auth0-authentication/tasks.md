## 1. Auth0 setup and configuration

- [x] 1.1 Write `docs/auth0-setup.md`: tenant, SPA application (callback,
      logout and web-origin URLs, Refresh Token Rotation), API (identifier,
      RS256, Allow Offline Access), optional Action for the email claim
- [x] 1.2 Add `AUTH0_DOMAIN`, `AUTH0_AUDIENCE`, `AUTH0_EMAIL_CLAIM`,
      `VITE_AUTH0_DOMAIN`, `VITE_AUTH0_CLIENT_ID`, `VITE_AUTH0_AUDIENCE` to
      `.env.example`
- [x] 1.3 Set `envDir` to the repo root in `apps/web/vite.config.ts` (no
      `env_file` needed: the container mounts the repo root)

## 2. API: domain and application

- [x] 2.1 `domain/users.py`: `Identity`, `UserProfile`,
      `UserProfileRepository`
- [x] 2.2 `application/auth/ports.py`: `AccessTokenVerifier`,
      `InvalidAccessToken`
- [x] 2.3 `application/users/get_current_user.py`: `GetCurrentUser`
- [x] 2.4 Unit tests for `GetCurrentUser` with a fake repository
      (new user, returning user)

## 3. API: infrastructure

- [x] 3.1 Add `PyJWT[crypto]` to `requirements.txt`
- [x] 3.2 `infrastructure/auth/jwt_verifier.py` with an injectable key
      resolver; tests with a locally generated RSA key for valid, expired,
      wrong audience, wrong issuer, HS256, `alg: none` and foreign key
- [x] 3.3 `infrastructure/auth/factory.py` and the reject-all verifier when
      settings are missing
- [x] 3.4 `infrastructure/auth/checks.py`: system check `auth.W001`
- [x] 3.5 `infrastructure/auth/drf_authentication.py`:
      `Auth0BearerAuthentication` and `AuthenticatedPrincipal`
- [x] 3.6 `infrastructure/users/models.py`, migration, and
      `DjangoUserProfileRepository` (get_or_create, which handles the
      concurrent `IntegrityError`); tests including the lost-race path

## 4. API: presentation and wiring

- [x] 4.1 `presentation/api/me.py`: `MeView` and `UserProfileSerializer`
      with `@extend_schema`
- [x] 4.2 Settings: default authentication class and `IsAuthenticated`
      default permission; `HealthView` and the schema/Swagger views stay
      public explicitly
- [x] 4.3 `config/container.py` and `config/urls.py`: wire
      `GetCurrentUser` and `/api/me/`
- [x] 4.4 `infrastructure/auth/openapi.py`: Bearer JWT security scheme;
      `make api-schema` passes with `--fail-on-warn`
- [x] 4.5 API tests: `/api/me/` with valid token (200), no token (401),
      invalid token (401); `/api/health/` without token stays public;
      schema marks `/api/me/` as protected and `/api/health/` as public
- [x] 4.6 `make lint-api` passes, including the import-linter contracts

## 5. Web

- [x] 5.1 Add `@auth0/auth0-react` and `react-router`
- [x] 5.2 `src/auth/config.ts` (reads and validates `VITE_AUTH0_*`) and
      `AuthProvider` (Auth0Provider with refresh tokens, local storage,
      `onRedirectCallback` to `returnTo`)
- [x] 5.3 Router with `/` and `/profile`; `RequireAuth` wrapper
- [x] 5.4 Header with Log in / Log out and the user's name or email;
      "Configure Auth0" notice when not configured
- [x] 5.5 `src/api/client.ts` (`useApiFetch` adds the Bearer token) and
      `src/api/me.ts`
- [x] 5.6 `/profile` page showing the result of `GET /api/me/`
- [x] 5.7 Tests with a fake `AuthContext`: anonymous header, logged-in
      header, not-configured notice, profile page sends the token and
      renders the profile

## 6. Docs

- [x] 6.1 `docs/decisions/0003-auth0.md` (including the local-storage
      trade-off)
- [x] 6.2 Update `docs/architecture.md` with the auth flow and layer map
- [x] 6.3 README: Auth0 in "What is included" and "Tech stack", Auth0 step
      in "Getting started", remove "Refresh tokens and password reset" from
      the roadmap

## 7. Verification

- [x] 7.1 `make test` and `make lint` pass
- [x] 7.2 Manual check against the real tenant: sign up, log in, reload,
      open `/profile`, log out, open `/profile` again
- [x] 7.3 Manual check in Swagger UI: Authorize with a token and call
      `/api/me/`
