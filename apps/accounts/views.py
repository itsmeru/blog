from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.exceptions import AuthenticationFailed

from apps.accounts.serializers import (
    AccountCreateSerializer,
    ForgotPasswordSerializer,
    ResetTokenSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
    ChangeUsernameSerializer,
    CustomTokenObtainPairSerializer
)
from .models import Account, PasswordResetToken
from apps.posts.models import Post
from apps.questions.models import Question
from apps.answers.models import Answer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200 and 'refresh' in response.data:
                response.set_cookie(
                    "refresh_token",
                    response.data['refresh'],
                    httponly=True,
                    max_age=60 * 60 * 24 * 7
                )
            return response
        except AuthenticationFailed:
            return Response({
                "message": "帳號或密碼錯誤"
            }, status=status.HTTP_401_UNAUTHORIZED)


class CustomTokenRefreshView(TokenRefreshView):
    def get(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({
                "error": "未提供 refresh token"
            }, status=status.HTTP_401_UNAUTHORIZED)
        token = RefreshToken(refresh_token)
        user_id = token.payload.get('user_id')
        if user_id:
            account = Account.objects.get(id=user_id)
            new_refresh = RefreshToken.for_user(account)
            new_access_token = str(new_refresh.access_token)
            new_refresh_token = str(new_refresh)
            response = Response({
                "access": new_access_token,
                "username": account.username
            })
            response.set_cookie(
                "refresh_token",
                new_refresh_token,
                httponly=True,
                max_age=60 * 60 * 24 * 7
            )
            return response
        else:
            return Response({
                "error": "Token 資料無效"
            }, status=status.HTTP_401_UNAUTHORIZED)


class RegisterView(GenericAPIView):
    serializer_class = AccountCreateSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = serializer.save()
        return Response({
            "message": "註冊成功",
            "username": account.username
        }, status=status.HTTP_201_CREATED)


class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({
            "message": "登出成功"
        })
        response.delete_cookie("refresh_token", path="/")
        return response


class ChangePasswordView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        if not user.check_password(old_password):
            return Response({
                "message": "舊密碼錯誤"
            }, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        response = Response({
            "message": "密碼更改成功，請重新登入",
            "require_relogin": True
        }, status=status.HTTP_200_OK)
        response.delete_cookie("refresh_token", path="/")
        return response


class ChangeUsernameView(GenericAPIView):
    serializer_class = ChangeUsernameSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_username = serializer.validated_data.get('new_username')
        if new_username:
            user = request.user
            user.username = new_username
            user.save()
            return Response({
                "message": "用戶名更改成功",
                "username": new_username
            }, status=status.HTTP_200_OK)


class ProfileStatsView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        posts_count = Post.objects.filter(author=user).count()
        questions_count = Question.objects.filter(author=user).count()
        answers_count = Answer.objects.filter(author=user).count()
        return Response({
            "posts_count": posts_count,
            "questions_count": questions_count,
            "answers_count": answers_count,
            "total_content": posts_count + questions_count + answers_count
        }, status=status.HTTP_200_OK)


class ForgotPasswordView(GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        reset_token = PasswordResetToken.create_token(email)
        reset_token.send_reset_email()
        return Response({
            "message": f"驗證碼已發送到 {email}，請檢查您的郵箱"
        }, status=status.HTTP_200_OK)


class VerifyResetTokenView(GenericAPIView):
    serializer_class = ResetTokenSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({
            "message": "驗證碼正確",
        }, status=status.HTTP_200_OK)


class ResetPasswordView(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "密碼重設成功，請使用新密碼登入"
        }, status=status.HTTP_200_OK)
