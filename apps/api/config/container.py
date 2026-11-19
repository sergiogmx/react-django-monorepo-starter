"""Dependency container: the only place that knows concrete implementations.

Each factory builds a use case with the infrastructure it needs. Views receive
use cases from here (via config/urls.py) and never construct them themselves.
"""

from application.health.check_health import CheckHealth
from application.users.get_current_user import GetCurrentUser
from infrastructure.health.django_database_probe import DjangoDatabaseProbe
from infrastructure.users.repository import DjangoUserProfileRepository


def check_health() -> CheckHealth:
    return CheckHealth(database=DjangoDatabaseProbe())


def get_current_user() -> GetCurrentUser:
    return GetCurrentUser(profiles=DjangoUserProfileRepository())
