from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import (
    TokenVerifyView,
)
from accounts.views import CustomTokenObtainPairView, CustomTokenRefreshView

api_patterns = [
    path("accounts/", include("accounts.urls")),
    path("posts/", include("posts.urls")),
    path("questions/", include("questions.urls")),
    path("answers/", include("answers.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),

    # API URLs
    path("api/", include(api_patterns)),
    
    # Simple JWT URLs
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    
    # Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
