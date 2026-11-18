"""Use-case tests: plain unittest, fake ports, no Django and no database."""

from unittest import TestCase

from application.health.check_health import CheckHealth
from domain.health import ComponentStatus


class FakeDatabaseProbe:
    def __init__(self, available: bool) -> None:
        self.available = available

    def is_available(self) -> bool:
        return self.available


class CheckHealthTests(TestCase):
    def test_healthy_when_database_is_available(self) -> None:
        report = CheckHealth(database=FakeDatabaseProbe(available=True)).execute()

        self.assertEqual(report.database, ComponentStatus.UP)
        self.assertTrue(report.is_healthy)

    def test_unhealthy_when_database_is_down(self) -> None:
        report = CheckHealth(database=FakeDatabaseProbe(available=False)).execute()

        self.assertEqual(report.database, ComponentStatus.DOWN)
        self.assertFalse(report.is_healthy)
