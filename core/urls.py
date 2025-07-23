from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from core import settings
from django.conf import settings
from django.conf.urls.static import static

API_VERSION = settings.API_VERSION

api_patterns = [
    path("users/", include("apps.users.urls")),
    path("posts/", include("apps.posts.urls")),
    path("questions/", include("apps.questions.urls")),
    path("answers/", include("apps.answers.urls")),
    path("rbac/", include("apps.rbac.urls")),
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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
