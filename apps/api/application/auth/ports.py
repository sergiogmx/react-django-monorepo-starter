from typing import Protocol

from domain.users import Identity


class InvalidAccessToken(Exception):
    """The token is missing a claim, expired, forged or for someone else."""


class AccessTokenVerifier(Protocol):
    def verify(self, token: str) -> Identity:
        """Return the caller's identity or raise InvalidAccessToken."""
        ...
