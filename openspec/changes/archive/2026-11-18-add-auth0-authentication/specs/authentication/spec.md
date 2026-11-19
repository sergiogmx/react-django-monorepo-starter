## Purpose

Lets people sign up, log in and log out of the web app through Auth0, and
ensures the API serves protected data only to callers holding a valid Auth0
access token, each of them backed by a local user profile.

## ADDED Requirements

### Requirement: Log in and sign up through Auth0

The web app SHALL let an anonymous user log in or sign up through Auth0
Universal Login, and SHALL show the user's identity once they are back.

#### Scenario: Anonymous user logs in

- **WHEN** an anonymous user clicks "Log in" on the home page
- **THEN** the browser is redirected to Auth0 Universal Login
- **AND** after a successful login the user returns to the web app
- **AND** the header shows the user's name or email and a "Log out" button

#### Scenario: New user signs up

- **WHEN** an anonymous user chooses "Sign up" on Auth0 Universal Login and
  completes it
- **THEN** the user returns to the web app logged in

#### Scenario: Session survives a page reload

- **WHEN** a logged-in user reloads the page
- **THEN** the user is still logged in without seeing the login page again

### Requirement: Log out

The web app SHALL end both the local session and the Auth0 session when the
user logs out.

#### Scenario: User logs out

- **WHEN** a logged-in user clicks "Log out"
- **THEN** the user is returned to the home page as an anonymous user
- **AND** visiting a protected page asks them to log in again

### Requirement: Protected pages in the web app

The web app SHALL require login for protected pages and SHALL return the
user to the page they asked for after logging in.

#### Scenario: Anonymous user opens a protected page

- **WHEN** an anonymous user opens `/profile`
- **THEN** the user is redirected to Auth0 Universal Login
- **AND** after logging in the user lands on `/profile`

#### Scenario: Logged-in user opens a protected page

- **WHEN** a logged-in user opens `/profile`
- **THEN** the page shows the profile returned by `GET /api/me/`

### Requirement: Web app sends the access token to the API

The web app SHALL send the Auth0 access token, issued for the API audience,
in the `Authorization: Bearer <token>` header of every request to a
protected API endpoint.

#### Scenario: Authenticated API call

- **WHEN** a logged-in user's page calls a protected API endpoint
- **THEN** the request carries `Authorization: Bearer <access token>`
- **AND** the token's audience is the configured `AUTH0_AUDIENCE`

### Requirement: API validates Auth0 access tokens

The API SHALL accept a request on a protected endpoint only when it carries
an access token signed with RS256 by the configured Auth0 tenant, issued
for the configured audience and not expired. Otherwise it SHALL respond
`401 Unauthorized`.

#### Scenario: Valid token

- **WHEN** a request to `GET /api/me/` carries a valid access token
- **THEN** the API responds `200`

#### Scenario: Missing token

- **WHEN** a request to `GET /api/me/` has no `Authorization` header
- **THEN** the API responds `401`

#### Scenario: Expired token

- **WHEN** a request carries a token whose `exp` is in the past
- **THEN** the API responds `401`

#### Scenario: Token for another audience

- **WHEN** a request carries a token whose `aud` does not include the
  configured audience
- **THEN** the API responds `401`

#### Scenario: Token from another issuer

- **WHEN** a request carries a token whose `iss` is not
  `https://<AUTH0_DOMAIN>/`
- **THEN** the API responds `401`

#### Scenario: Token with a forbidden algorithm or bad signature

- **WHEN** a request carries a token signed with `HS256`, with `alg: none`,
  or with a key that is not one of the tenant's signing keys
- **THEN** the API responds `401`

### Requirement: Public endpoints stay public

The API SHALL keep `/api/health/`, `/api/schema/` and `/api/docs/`
reachable without a token.

#### Scenario: Health check without a token

- **WHEN** a request to `GET /api/health/` has no `Authorization` header
- **THEN** the API responds with the health status, not `401`

### Requirement: Current user endpoint

The API SHALL expose `GET /api/me/`, which returns the authenticated user's
local profile: `id`, `subject` (the Auth0 `sub`), `email` (or `null`) and
`created_at`.

#### Scenario: Read own profile

- **WHEN** a user with a valid token calls `GET /api/me/`
- **THEN** the response contains their `subject` equal to the token's `sub`

### Requirement: Local user provisioning

The API SHALL create a local user profile the first time it sees a valid
token for a given Auth0 `sub`, and SHALL reuse it afterwards. The API SHALL
NOT store passwords.

#### Scenario: First authenticated request

- **WHEN** a valid token arrives for a `sub` with no local profile
- **THEN** a profile is created with that `sub` and returned

#### Scenario: Returning user

- **WHEN** a valid token arrives for a `sub` that already has a profile
- **THEN** the existing profile is returned and no new one is created

#### Scenario: Two first requests at the same time

- **WHEN** two requests for the same new `sub` are processed concurrently
- **THEN** exactly one profile exists afterwards and both requests succeed

### Requirement: Swagger UI can call protected endpoints

The OpenAPI schema SHALL declare a Bearer JWT security scheme for protected
endpoints and none for public ones, so Swagger UI shows an "Authorize"
button.

#### Scenario: Authorize in Swagger UI

- **WHEN** a developer pastes a valid access token in Swagger UI's
  "Authorize" dialog and calls `GET /api/me/`
- **THEN** the call succeeds with `200`

#### Scenario: Public endpoints are not marked as protected

- **WHEN** a developer reads `/api/health/` in Swagger UI
- **THEN** it shows no lock icon

### Requirement: The project runs without Auth0 configured

The project SHALL start and pass its tests when the Auth0 variables are
empty, and SHALL tell the developer what is missing.

#### Scenario: API without Auth0 settings

- **WHEN** the API starts with `AUTH0_DOMAIN` or `AUTH0_AUDIENCE` empty
- **THEN** `manage.py check` reports a warning naming the missing variables
- **AND** protected endpoints respond `401`
- **AND** public endpoints keep working

#### Scenario: Web app without Auth0 settings

- **WHEN** the web app starts with any `VITE_AUTH0_*` variable empty
- **THEN** the home page shows a notice explaining how to configure Auth0
  instead of the "Log in" button
