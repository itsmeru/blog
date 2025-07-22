from django.urls import path
from .views import PostCreateView, PostDetailView, PostDeleteView

app_name = 'posts'

urlpatterns = [
    path('', PostCreateView.as_view(), name='post_create'),
    path('<int:post_id>/', PostDetailView.as_view(), name='post_detail'),
    path('delete/<int:post_id>/', PostDeleteView.as_view(), name='post_delete'),
]
