from django.apps import AppConfig


class InfrastructureConfig(AppConfig):
    name = "infrastructure"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        # Registered on import: the system check and the OpenAPI extension.
        from infrastructure.auth import checks, openapi  # noqa: F401
