from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from application.auth.ports import InvalidAccessToken
from domain.users import Identity
from infrastructure.auth.factory import get_verifier


class AuthenticatedPrincipal:
    """What DRF puts in request.user. Views read `.identity` and nothing else."""

    is_authenticated = True
    is_anonymous = False

    def __init__(self, identity: Identity) -> None:
        self.identity = identity

    def __str__(self) -> str:
        return self.identity.subject


class Auth0BearerAuthentication(BaseAuthentication):
    """Authenticates `Authorization: Bearer <Auth0 access token>`."""

    def authenticate(
        self, request: Request
    ) -> tuple[AuthenticatedPrincipal, str] | None:
        parts = get_authorization_header(request).split()
        if not parts or parts[0].lower() != b"bearer":
            return None  # No credentials: let permissions decide (401 if needed).
        if len(parts) != 2:
            raise AuthenticationFailed("Malformed Authorization header.")

        try:
            token = parts[1].decode()
            identity = get_verifier().verify(token)
        except (UnicodeError, InvalidAccessToken) as exc:
            raise AuthenticationFailed("Invalid or expired access token.") from exc

        return AuthenticatedPrincipal(identity), token

    def authenticate_header(self, request: Request) -> str:
        # Makes DRF answer 401 (not 403) when credentials are missing.
        return 'Bearer realm="api"'
