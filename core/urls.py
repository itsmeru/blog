from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from core import settings

API_VERSION = settings.API_VERSION

api_patterns = [
    path("users/", include("apps.users.urls")),
    path("posts/", include("apps.posts.urls")),
    path("questions/", include("apps.questions.urls")),
    path("answers/", include("apps.answers.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"api/{API_VERSION}/", include(api_patterns)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
