from drf_spectacular.extensions import OpenApiAuthenticationExtension


class Auth0BearerScheme(OpenApiAuthenticationExtension):
    """Shows an "Authorize" button in Swagger UI for protected endpoints."""

    target_class = "infrastructure.auth.drf_authentication.Auth0BearerAuthentication"
    name = "Auth0Bearer"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Auth0 access token issued for this API's audience.",
        }
