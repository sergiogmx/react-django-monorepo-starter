from django.conf import settings
from django.core.checks import Warning, register


@register()
def auth0_settings_check(app_configs, **kwargs):
    missing = [
        name
        for name in ("AUTH0_DOMAIN", "AUTH0_AUDIENCE")
        if not getattr(settings, name)
    ]
    if not missing:
        return []
    return [
        Warning(
            f"Auth0 is not configured ({', '.join(missing)} empty). "
            "Protected endpoints will answer 401.",
            hint="Fill the variables in .env. See docs/auth0-setup.md.",
            id="auth.W001",
        )
    ]
