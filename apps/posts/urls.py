from django.urls import path
from .views import PostCreateListView, PostDetailView

app_name = "posts"

urlpatterns = [
    path("", PostCreateListView.as_view(), name="post_list"),
    path("<int:post_id>/", PostDetailView.as_view(), name="post_detail"),
]
