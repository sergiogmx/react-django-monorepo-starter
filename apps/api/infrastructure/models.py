# Django discovers models through <app>/models.py; each feature keeps its
# models in its own package and re-exports them here.
from infrastructure.users.models import UserProfileModel

__all__ = ["UserProfileModel"]
