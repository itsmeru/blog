from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet

# 創建路由器
router = DefaultRouter()
router.register(r'', PostViewSet, basename='posts')

urlpatterns = [
    path('', include(router.urls)),
]
