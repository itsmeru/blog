import secrets
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.hashers import check_password
from rest_framework.exceptions import AuthenticationFailed, NotFound, ValidationError
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .repository import UserRepository
from .serializers import (
    RegisterSerializer, LoginSerializer, ChangePasswordSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
)


class UserService:
    repository_class = UserRepository

    @classmethod
    def register_user(cls, data):
        serializer = RegisterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = cls.repository_class.create_user(
            email=serializer.validated_data["email"],
            phone=serializer.validated_data.get("phone"),
            nickname=serializer.validated_data["nickname"],
            password=serializer.validated_data["password"],
        )
        return {
            "user": user,
            "message": "註冊成功，請登入"
        }

    @classmethod
    def login_user(cls, data):
        serializer = LoginSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        account = serializer.validated_data["account"]
        password = serializer.validated_data["password"]
        user = cls.authenticate(account, password)
        refresh = RefreshToken.for_user(user)
        return {
            "user": user,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "message": "登入成功"
        }

    @classmethod
    def refresh_token(cls, refresh_token):
        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token
            return {
                "access": str(access_token),
                "refresh": str(refresh),
                "message": "Token 刷新成功"
            }
        except (InvalidToken, TokenError):
            raise ValidationError("Invalid refresh token")

    @classmethod
    def validate_refresh_token(cls, refresh_token):
        if not refresh_token:
            raise ValidationError("未找到 refresh token")
        
        return cls.refresh_token(refresh_token)

    @classmethod
    def update_password(cls, user, new_password):
        return cls.repository_class.update_password(user, new_password)

    @classmethod
    def change_password(cls, user, data):
        serializer = ChangePasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]
        if not user.check_password(old_password):
            raise ValidationError("舊密碼錯誤")

        cls.repository_class.update_password(user, new_password)
        return {"message": "密碼更改成功，請重新登入"}

    @classmethod
    def forgot_password(cls, data):
        serializer = ForgotPasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = cls.repository_class.get_by_email(email)
        if not user:
            raise NotFound("User not found")
        verification_code = str(secrets.randbelow(1000000)).zfill(6)
        cache_key = f"password_reset_{email}"
        cache.set(cache_key, verification_code, 3600)
        subject = "密碼重置驗證碼"
        message = f"""
        您好 {user.nickname}，

        您正在重置密碼，驗證碼為：{verification_code}

        此驗證碼將在1小時後過期。
        如果您沒有請求重置密碼，請忽略此郵件。

        謝謝！
        """
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception:
            cache.delete(cache_key)
            raise ValidationError("郵件發送失敗，請稍後再試")
        return {
            "email": email,
            "expires_at": datetime.now() + timedelta(hours=1),
            "message": f"驗證碼已發送到 {email}，請檢查您的郵箱"
        }

    @classmethod
    def reset_password(cls, data):
        serializer = ResetPasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        verification_code = serializer.validated_data["verification_code"]
        new_password = serializer.validated_data["new_password"]
        user = cls.repository_class.get_by_email(email)
        if not user:
            raise NotFound("User not found")
        cache_key = f"password_reset_{email}"
        stored_code = cache.get(cache_key)
        if not stored_code:
            raise ValidationError("驗證碼已過期，請重新申請")
        if stored_code != verification_code:
            raise ValidationError("驗證碼錯誤")
        user.set_password(new_password)
        user.save()
        cache.delete(cache_key)
        return {
            "user": user,
            "message": "密碼重置成功，請使用新密碼登入"
        }

    @classmethod
    def logout_user(cls):
        return {"message": "登出成功"}
