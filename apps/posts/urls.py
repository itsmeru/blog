from django.urls import path
from .views import PostListCreateView, PostDetailView

app_name = 'posts'

urlpatterns = [
    path('', PostListCreateView.as_view(), name='post_create_list'),
    path('<int:post_id>/', PostDetailView.as_view(), name='post_detail'),
]
