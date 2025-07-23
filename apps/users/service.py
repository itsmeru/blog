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


class UserService:
    @staticmethod
    def register_user(email, phone, nickname, password):
        if UserRepository.get_by_email(email):
            raise ValidationError({"email": ["Email already exists"]})

        return UserRepository.create_user(
            email=email, phone=phone, nickname=nickname, password=password
        )

    @staticmethod
    def authenticate(account, password):
        user = UserRepository.get_by_account(account)
        if not user:
            raise AuthenticationFailed("Invalid credentials")

        if not user.is_active:
            raise AuthenticationFailed({"detail": "User is not active"})

        if not check_password(password, user.password):
            raise AuthenticationFailed("Invalid credentials")

        return user

    @staticmethod
    def refresh_token(refresh_token):
        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token
            return {
                "access": str(access_token),
                "refresh": str(refresh),
            }
        except (InvalidToken, TokenError):
            raise ValidationError("Invalid refresh token")

    @staticmethod
    def update_password(user, new_password):
        return UserRepository.update_password(user, new_password)

    @staticmethod
    def forgot_password(email):
        user = UserRepository.get_by_email(email)
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
        except Exception as e:
            cache.delete(cache_key)
            raise ValidationError("郵件發送失敗，請稍後再試")

        return {"email": email, "expires_at": datetime.now() + timedelta(hours=1)}

    @staticmethod
    def reset_password(email, verification_code, new_password):
        user = UserRepository.get_by_email(email)
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

        return user
