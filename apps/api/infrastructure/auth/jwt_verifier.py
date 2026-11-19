from collections.abc import Callable
from typing import Any

import jwt

from application.auth.ports import InvalidAccessToken
from domain.users import Identity

# Given the raw token, return the public key that should have signed it.
KeyResolver = Callable[[str], Any]


class JwtAccessTokenVerifier:
    """Implements AccessTokenVerifier for RS256 JWTs (Auth0 access tokens)."""

    ALGORITHMS = ["RS256"]  # Never accept HS256 or "none".
    REQUIRED_CLAIMS = ["exp", "iss", "aud", "sub"]

    def __init__(
        self,
        *,
        issuer: str,
        audience: str,
        key_resolver: KeyResolver,
        email_claim: str,
        leeway_seconds: int = 10,
    ) -> None:
        self._issuer = issuer
        self._audience = audience
        self._key_resolver = key_resolver
        self._email_claim = email_claim
        self._leeway = leeway_seconds

    def verify(self, token: str) -> Identity:
        try:
            claims = jwt.decode(
                token,
                key=self._key_resolver(token),
                algorithms=self.ALGORITHMS,
                audience=self._audience,
                issuer=self._issuer,
                leeway=self._leeway,
                options={"require": self.REQUIRED_CLAIMS},
            )
        except (jwt.PyJWTError, ValueError) as exc:
            raise InvalidAccessToken(str(exc)) from exc

        email = claims.get(self._email_claim)
        return Identity(
            subject=claims["sub"],
            email=email if isinstance(email, str) else None,
        )


class UnconfiguredVerifier:
    """Used when Auth0 settings are missing: every token is rejected."""

    def verify(self, token: str) -> Identity:
        raise InvalidAccessToken("Auth0 is not configured on this server.")
