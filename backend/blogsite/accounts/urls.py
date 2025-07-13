from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "accounts"

router = DefaultRouter()
router.register(r'', views.AccountViewSet, basename='account')

urlpatterns = router.urls
