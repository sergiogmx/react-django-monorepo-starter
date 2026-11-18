from django.test import TestCase
from rest_framework.test import APIRequestFactory

from application.health.check_health import CheckHealth
from presentation.api.health import HealthView
from tests.application.test_check_health import FakeDatabaseProbe


class HealthEndpointTests(TestCase):
    """End to end through the real container and the real test database."""

    def test_reports_ok_when_everything_is_up(self) -> None:
        response = self.client.get("/api/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "database": "up"})


class HealthViewTests(TestCase):
    """The view with an injected use case, to cover the degraded path."""

    def test_returns_503_when_database_is_down(self) -> None:
        view = HealthView.as_view(
            check_health=CheckHealth(database=FakeDatabaseProbe(available=False))
        )

        response = view(APIRequestFactory().get("/api/health/"))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data, {"status": "error", "database": "down"})
