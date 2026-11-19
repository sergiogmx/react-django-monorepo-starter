from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class Identity:
    """Who is calling, as asserted by the identity provider."""

    subject: str
    email: str | None = None


@dataclass(frozen=True)
class UserProfile:
    """Our own record of a user. Never holds credentials."""

    id: int
    subject: str
    email: str | None
    created_at: datetime


class UserProfileRepository(Protocol):
    def get_or_create(self, identity: Identity) -> UserProfile:
        """Return the profile for this identity, creating it the first time.

        Must be safe when two calls for the same new subject run concurrently.
        """
        ...
