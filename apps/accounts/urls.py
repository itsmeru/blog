from django.urls import path
from .views import (
    RegisterView, LogoutView, ChangePasswordView, ChangeUsernameView,
    ProfileStatsView, ForgotPasswordView, VerifyResetTokenView, ResetPasswordView,
    CustomTokenObtainPairView, CustomTokenRefreshView
)

app_name = "accounts"

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('change_username/', ChangeUsernameView.as_view(), name='change_username'),
    path('profile_stats/', ProfileStatsView.as_view(), name='profile_stats'),
    path('forgot_password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('verify_reset_token/', VerifyResetTokenView.as_view(), name='verify_reset_token'),
    path('reset_password/', ResetPasswordView.as_view(), name='reset_password'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]
