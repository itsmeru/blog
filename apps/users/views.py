from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import FormParser, JSONParser

from core.app.base.serializer import BaseErrorSerializer

from .serializers import (
    ChangePasswordSerializer,
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


class RegisterView(GenericAPIView):
    permission_classes = [AllowAny]
    parser_classes = (FormParser,)

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: RegisterSuccessResponseSerializer,
            400: BaseErrorSerializer,
        },
        summary="註冊新用戶",
        tags=["Users"],
    )
    def post(self, request, *args, **kwargs):
        register_data = UserService.register_user(request.data)
        return Response(
            {
                "success": True,
                "message": register_data["message"],
                "data": {
                    "user_id": register_data["user"].id,
                    "nickname": register_data["user"].nickname,
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
        summary="使用者登入",
        tags=["Users"],
    )
    def post(self, request):
        login_data = UserService.login_user(request.data)
        response = Response(
            {
                "success": True,
                "message": login_data["message"],
                "data": {
                    "access": login_data["access"],
                    "user_id": login_data["user"].id,
                    "nickname": login_data["user"].nickname,
                },
            }
        )
        response.set_cookie(
            "refresh_token",
            login_data["refresh"],
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
        summary="使用者登出",
        tags=["Users"],
    )
    def post(self, request):
        logout_data = UserService.logout_user()
        response = Response(
            {
                "success": True,
                "message": logout_data["message"],
                "data": {},
            },
            status=204,
        )
        response.delete_cookie("refresh_token", path="/")
        return response


class ChangePasswordView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (FormParser,)

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: ChangePasswordSuccessResponseSerializer,
            400: BaseErrorSerializer,
        },
        summary="變更密碼",
        tags=["Users"],
    )
    def post(self, request):
        change_data = UserService.change_password(request.user, request.data)
        response = Response(
            {
                "success": True,
                "message": change_data["message"],
                "data": {"require_relogin": True},
            }
        )
        response.delete_cookie("refresh_token", path="/")
        return response


class ForgotPasswordView(GenericAPIView):
    permission_classes = [AllowAny]
    parser_classes = (FormParser, JSONParser)

    @extend_schema(
        request=ForgotPasswordSerializer,
        responses={
            200: ForgotPasswordSuccessResponseSerializer,
            404: BaseErrorSerializer,
        },
        summary="忘記密碼發送驗證碼",
        tags=["Users"],
    )
    def post(self, request):
        forgot_data = UserService.forgot_password(request.data)
        return Response(
            {
                "success": True,
                "message": forgot_data["message"],
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
        summary="重設密碼",
        tags=["Users"],
    )
    def post(self, request):
        reset_data = UserService.reset_password(request.data)
        return Response(
            {
                "success": True,
                "message": reset_data["message"],
                "data": {},
            }
        )


class RefreshTokenView(GenericAPIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={
            200: RefreshTokenResponseSerializer,
            400: BaseErrorSerializer,
        },
        summary="刷新 Access Token",
        tags=["Users"],
    )
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        data = UserService.validate_refresh_token(refresh_token)

        response = Response(
            {
                "success": True,
                "message": data["message"],
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
