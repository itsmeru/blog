from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="user-register"),
    path("login/", views.LoginView.as_view(), name="user-login"),
    path("refresh/", views.RefreshTokenView.as_view(), name="user-refresh-token"),
    path("logout/", views.LogoutView.as_view(), name="user-logout"),
    path(
        "change-password/",
        views.ChangePasswordView.as_view(),
        name="user-change-password",
    ),
    path(
        "forgot-password/",
        views.ForgotPasswordView.as_view(),
        name="user-forgot-password",
    ),
    path(
        "reset-password/", views.ResetPasswordView.as_view(), name="user-reset-password"
    ),
]
