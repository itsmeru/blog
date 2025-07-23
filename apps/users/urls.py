from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="user-register"),
    path("login/", views.LoginView.as_view(), name="user-login"),
    path("refresh/", views.RefreshTokenView.as_view(), name="user-refresh-token"),
    path(
        "forgot-password/",
        views.ForgotPasswordView.as_view(),
        name="user-forgot-password",
    ),
    path("me/", views.MeView.as_view(), name="user-me"),
    path("departments/", views.DepartmentListView.as_view(), name="department-list"),
    # User Management APIs
    path("", views.UserListView.as_view(), name="user-list"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="user-detail"),
]
