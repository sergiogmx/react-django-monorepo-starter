# Auth0 setup

The web app logs users in with Auth0 Universal Login, and the API accepts
only Auth0 access tokens issued for it. This is a one-time setup in the
Auth0 dashboard. None of the values below are secrets.

## 1. Tenant

Create a tenant for development (the free plan is enough). Its domain looks
like `dev-xxxxxxxx.us.auth0.com`.

## 2. API (the audience)

**Applications → APIs → Create API**

| Field             | Value                                                   |
| ----------------- | ------------------------------------------------------- |
| Name              | `Starter API`                                           |
| Identifier        | `https://api.starter.local` (any URL-like string; it is never called and cannot be changed later) |
| Signing algorithm | RS256                                                   |

Then, in the API's **Settings**, turn on **Allow Offline Access** (needed
for refresh tokens).

After creating the application in step 3, come back to this API, open
**Application Access**, and authorize the SPA for **User Access** (or set
the user access policy to *Allow*). Recent tenants block it by default.

> Do not use the **Auth0 Management API** (`https://<tenant>/api/v2/`) as
> the audience. That API manages your tenant; ours needs its own.

## 3. Application (the web app)

**Applications → Applications → Create Application → Single Page Application**

In **Settings**:

| Field                 | Value                   |
| --------------------- | ----------------------- |
| Allowed Callback URLs | `http://localhost:5173` |
| Allowed Logout URLs   | `http://localhost:5173` |
| Allowed Web Origins   | `http://localhost:5173` |

Under **Refresh Token Rotation**, turn on **Rotation**. Save.

## 4. Fill `.env`

```
AUTH0_DOMAIN=<tenant domain, without https://>
AUTH0_AUDIENCE=<API identifier>
VITE_AUTH0_DOMAIN=<same tenant domain>
VITE_AUTH0_CLIENT_ID=<the application's Client ID>
VITE_AUTH0_AUDIENCE=<same API identifier>
```

Then `make restart`. `docker compose exec api python manage.py check`
must not show `auth.W001`.

## 5. Optional: email in the access token

Auth0 access tokens don't carry the user's email by default, so
`GET /api/me/` returns `"email": null`. To include it, create an Action in
**Actions → Library → Create Action** (trigger: *Login / Post Login*):

```js
exports.onExecutePostLogin = async (event, api) => {
  if (event.user.email) {
    api.accessToken.setCustomClaim('https://starter.local/email', event.user.email);
  }
};
```

Deploy it and add it to the **Login** flow. The claim name must match
`AUTH0_EMAIL_CLAIM` in `.env`.

## Testing the API from Swagger UI

Open http://localhost:8000/api/docs/, click **Authorize**, and paste an
access token. The easiest way to get one is to log in to the web app,
open the browser's dev tools, and copy the `Authorization` header of the
`/api/me/` request (without `Bearer `).

## Troubleshooting

| Symptom                                        | Likely cause                                                     |
| ---------------------------------------------- | ---------------------------------------------------------------- |
| "Callback URL mismatch" on the Auth0 page      | `http://localhost:5173` missing in Allowed Callback URLs         |
| "Service not found" after login                | `VITE_AUTH0_AUDIENCE` doesn't match an API identifier            |
| "Client … is not authorized to access resource server" | The SPA is not authorized for User Access in the API's **Application Access** tab |
| Logged out on every reload                     | Refresh Token Rotation or Allow Offline Access is off            |
| `/api/me/` answers 401 with a token            | `AUTH0_AUDIENCE` / `AUTH0_DOMAIN` differ from the web's values, or `make restart` not run |
| "Auth0 is not configured" notice               | A `VITE_AUTH0_*` variable is empty; restart after filling it     |
