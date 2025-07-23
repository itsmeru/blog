from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import FormParser
from rest_framework.exceptions import ValidationError

from core.app.base.serializer import BaseErrorSerializer

from .serializers import (
    ForgotPasswordSerializer,
    LoginSerializer,
    LoginSuccessResponseSerializer,
    RegisterSuccessResponseSerializer,
    LogoutSuccessResponseSerializer,
    ChangePasswordSuccessResponseSerializer,
    ForgotPasswordSuccessResponseSerializer,
    ResetPasswordSuccessResponseSerializer,
    RefreshTokenResponseSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
)
from .service import UserService
from apps.users.models import User


class RegisterView(GenericAPIView):
    permission_classes = [AllowAny]
    parser_classes = (FormParser,)

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: RegisterSuccessResponseSerializer,
            400: BaseErrorSerializer,
        },
        description="註冊新用戶",
        tags=["Users"],
    )
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService.register_user(
            email=serializer.validated_data["email"],
            phone=serializer.validated_data.get("phone"),
            nickname=serializer.validated_data["nickname"],
            password=serializer.validated_data["password"],
        )
        return Response(
            {
                "success": True,
                "message": "註冊成功，請登入",
                "data": {
                    "user_id": user.id,
                    "nickname": user.nickname,
                },
            },
            status=201,
        )


class LoginView(GenericAPIView):
    permission_classes = [AllowAny]
    parser_classes = (FormParser,)

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: LoginSuccessResponseSerializer,
            400: BaseErrorSerializer,
        },
        description="使用者登入",
        tags=["Users"],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService.authenticate(
            account=serializer.validated_data["account"],
            password=serializer.validated_data["password"],
        )
        refresh = RefreshToken.for_user(user)

        response = Response(
            {
                "success": True,
                "message": "登入成功",
                "data": {
                    "access": str(refresh.access_token),
                    "user_id": user.id,
                    "nickname": user.nickname,
                },
            }
        )

        response.set_cookie(
            "refresh_token",
            str(refresh),
            httponly=True,
            samesite="Lax",
            max_age=60 * 60 * 24 * 7,
        )

        return response


class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            204: LogoutSuccessResponseSerializer,
            403: BaseErrorSerializer,
        },
        description="使用者登出",
        tags=["Users"],
    )
    def post(self, request):
        response = Response(
            {"success": True, "message": "登出成功", "data": {}}, status=204
        )
        response.delete_cookie("refresh_token", path="/")
        return response


class ChangePasswordView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (FormParser,)
    serializer_class = ForgotPasswordSerializer

    @extend_schema(
        request=ForgotPasswordSerializer,
        responses={
            200: ChangePasswordSuccessResponseSerializer,
            400: BaseErrorSerializer,
        },
        description="變更密碼",
        tags=["Users"],
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        if not user.check_password(old_password):
            return Response(
                {"success": False, "message": "舊密碼錯誤", "data": {}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()
        response = Response(
            {
                "success": True,
                "message": "密碼更改成功，請重新登入",
                "data": {"require_relogin": True},
            }
        )
        response.delete_cookie("refresh_token", path="/")
        return response


class ForgotPasswordView(GenericAPIView):
    permission_classes = [AllowAny]
    parser_classes = (FormParser,)

    @extend_schema(
        request=ForgotPasswordSerializer,
        responses={
            200: ForgotPasswordSuccessResponseSerializer,
            404: BaseErrorSerializer,
        },
        description="忘記密碼發送驗證碼",
        tags=["Users"],
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        reset_data = UserService.forgot_password(email)
        return Response(
            {
                "success": True,
                "message": f"驗證碼已發送到 {email}，請檢查您的郵箱",
                "data": {},
            }
        )


class ResetPasswordView(GenericAPIView):
    permission_classes = [AllowAny]
    parser_classes = (FormParser,)

    @extend_schema(
        request=ResetPasswordSerializer,
        responses={
            200: ResetPasswordSuccessResponseSerializer,
            400: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        description="重置密碼",
        tags=["Users"],
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        verification_code = serializer.validated_data["verification_code"]
        new_password = serializer.validated_data["new_password"]

        UserService.reset_password(email, verification_code, new_password)
        return Response(
            {"success": True, "message": "密碼重置成功，請使用新密碼登入", "data": {}}
        )


class RefreshTokenView(GenericAPIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={
            200: RefreshTokenResponseSerializer,
            400: BaseErrorSerializer,
        },
        description="刷新 Access Token",
        tags=["Users"],
    )
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"success": False, "message": "未找到 refresh token", "data": {}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = UserService.refresh_token(refresh_token)

        response = Response(
            {
                "success": True,
                "message": "Token 刷新成功",
                "data": {"access": data["access"]},
            }
        )

        response.set_cookie(
            "refresh_token",
            data["refresh"],
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=60 * 60 * 24 * 7,
        )

        return response
