"""Issue real RS256 tokens with a key generated locally, so auth tests run
offline and exercise the actual validation code."""

import time
from typing import Any

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

from infrastructure.auth.jwt_verifier import JwtAccessTokenVerifier

ISSUER = "https://tenant.test/"
AUDIENCE = "https://api.test"
EMAIL_CLAIM = "https://starter.local/email"

_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_FOREIGN_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)


def issue_token(
    *,
    key: Any = _PRIVATE_KEY,
    algorithm: str = "RS256",
    **claims: Any,
) -> str:
    """A valid token by default. Override claims; pass None to drop one."""
    now = int(time.time())
    payload = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": "auth0|ana",
        "iat": now,
        "exp": now + 300,
        **claims,
    }
    payload = {name: value for name, value in payload.items() if value is not None}
    return jwt.encode(payload, key, algorithm=algorithm)


def foreign_key() -> Any:
    return _FOREIGN_KEY


def make_verifier() -> JwtAccessTokenVerifier:
    public_key = _PRIVATE_KEY.public_key()
    return JwtAccessTokenVerifier(
        issuer=ISSUER,
        audience=AUDIENCE,
        key_resolver=lambda token: public_key,
        email_claim=EMAIL_CLAIM,
    )
