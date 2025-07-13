from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet

app_name = 'posts'

router = DefaultRouter()
router.register(r'', PostViewSet, basename='posts')

urlpatterns = router.urls
