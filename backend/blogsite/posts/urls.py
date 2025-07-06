from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("", views.posts_handler, name="posts_handler"),
]
