from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from application.health.check_health import CheckHealth


class HealthSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["ok", "error"])
    database = serializers.ChoiceField(choices=["up", "down"])


class HealthView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    # Injected by config/urls.py through HealthView.as_view(check_health=...).
    check_health: CheckHealth | None = None

    @extend_schema(
        summary="Check API health",
        description="Reports whether the API can reach its database.",
        tags=["health"],
        responses={200: HealthSerializer, 503: HealthSerializer},
    )
    def get(self, request: Request) -> Response:
        assert self.check_health is not None, "check_health use case not injected"
        report = self.check_health.execute()
        body = HealthSerializer(
            {
                "status": "ok" if report.is_healthy else "error",
                "database": report.database.value,
            }
        ).data
        return Response(
            body,
            status=status.HTTP_200_OK
            if report.is_healthy
            else status.HTTP_503_SERVICE_UNAVAILABLE,
        )
