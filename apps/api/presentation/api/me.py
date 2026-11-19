from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from application.users.get_current_user import GetCurrentUser
from domain.users import Identity


class UserProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    subject = serializers.CharField(help_text="Auth0 user id (the token's `sub`).")
    email = serializers.EmailField(allow_null=True)
    created_at = serializers.DateTimeField()


class MeView(APIView):
    # Protected by the defaults in settings (Auth0 bearer + IsAuthenticated).

    # Injected by config/urls.py through MeView.as_view(get_current_user=...).
    get_current_user: GetCurrentUser | None = None

    @extend_schema(
        summary="Get the current user",
        description="Returns the caller's profile, creating it on first use.",
        tags=["users"],
        responses={200: UserProfileSerializer},
    )
    def get(self, request: Request) -> Response:
        assert self.get_current_user is not None, "get_current_user not injected"
        identity: Identity = request.user.identity
        profile = self.get_current_user.execute(identity)
        return Response(UserProfileSerializer(profile).data)
