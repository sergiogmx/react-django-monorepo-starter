from functools import cache

from django.conf import settings
from jwt import PyJWKClient

from application.auth.ports import AccessTokenVerifier
from infrastructure.auth.jwt_verifier import (
    JwtAccessTokenVerifier,
    UnconfiguredVerifier,
)


@cache
def get_verifier() -> AccessTokenVerifier:
    """Build the verifier once from settings. JWKS keys are cached by PyJWT."""
    domain = settings.AUTH0_DOMAIN
    audience = settings.AUTH0_AUDIENCE
    if not domain or not audience:
        return UnconfiguredVerifier()

    jwks = PyJWKClient(f"https://{domain}/.well-known/jwks.json", cache_keys=True)
    return JwtAccessTokenVerifier(
        issuer=f"https://{domain}/",
        audience=audience,
        key_resolver=lambda token: jwks.get_signing_key_from_jwt(token).key,
        email_claim=settings.AUTH0_EMAIL_CLAIM,
    )
