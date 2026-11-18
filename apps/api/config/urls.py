from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from config import container
from presentation.api.health import HealthView

urlpatterns = [
    path("admin/", admin.site.urls),
    # API documentation (OpenAPI 3 schema + Swagger UI).
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Endpoints. Use cases come from the container, never built in views.
    path(
        "api/health/",
        HealthView.as_view(check_health=container.check_health()),
        name="health",
    ),
]
