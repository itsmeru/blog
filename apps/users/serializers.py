from rest_framework import serializers

from core.app.base.serializer import SuccessSerializer

from .models import User


class UserBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "phone", "nickname"]


class RegisterSerializer(UserBaseSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + ["password"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value


class LoginSerializer(serializers.Serializer):
    account = serializers.CharField(help_text="Email 或 Phone")
    password = serializers.CharField(write_only=True)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="電子郵件")
    old_password = serializers.CharField(
        write_only=True, required=False, help_text="舊密碼"
    )
    new_password = serializers.CharField(
        write_only=True, required=False, help_text="新密碼"
    )

    def validate(self, attrs):
        if "old_password" not in attrs and "new_password" not in attrs:
            return attrs

        if "old_password" not in attrs or "new_password" not in attrs:
            raise serializers.ValidationError("變更密碼需要提供舊密碼和新密碼")

        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="電子郵件")
    verification_code = serializers.CharField(max_length=6, help_text="6位數驗證碼")
    new_password = serializers.CharField(min_length=6, help_text="新密碼")


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(help_text="Refresh token")


class LoginSuccessDataSerializer(serializers.Serializer):
    access = serializers.CharField(help_text="JWT access token")
    user_id = serializers.IntegerField(help_text="用戶ID")
    nickname = serializers.CharField(help_text="暱稱")


class RegisterSuccessDataSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(help_text="用戶ID")
    nickname = serializers.CharField(help_text="暱稱")


class LogoutSuccessDataSerializer(serializers.Serializer):
    message = serializers.CharField(help_text="登出成功訊息")


class ChangePasswordSuccessDataSerializer(serializers.Serializer):
    message = serializers.CharField(help_text="密碼變更成功訊息")
    require_relogin = serializers.BooleanField(help_text="是否需要重新登入")


class ForgotPasswordSuccessDataSerializer(serializers.Serializer):
    message = serializers.CharField(help_text="驗證碼發送成功訊息")


class RefreshTokenResponseDataSerializer(serializers.Serializer):
    access = serializers.CharField(help_text="新的 access token")


class ResetPasswordSuccessDataSerializer(serializers.Serializer):
    message = serializers.CharField(help_text="密碼重置成功訊息")


LoginSuccessResponseSerializer = SuccessSerializer(
    LoginSuccessDataSerializer(), "LoginSuccessResponseSerializer"
)

RegisterSuccessResponseSerializer = SuccessSerializer(
    RegisterSuccessDataSerializer(), "RegisterSuccessResponseSerializer"
)

LogoutSuccessResponseSerializer = SuccessSerializer(
    LogoutSuccessDataSerializer(), "LogoutSuccessResponseSerializer"
)

ChangePasswordSuccessResponseSerializer = SuccessSerializer(
    ChangePasswordSuccessDataSerializer(), "ChangePasswordSuccessResponseSerializer"
)

ForgotPasswordSuccessResponseSerializer = SuccessSerializer(
    ForgotPasswordSuccessDataSerializer(), "ForgotPasswordSuccessResponseSerializer"
)

ResetPasswordSuccessResponseSerializer = SuccessSerializer(
    ResetPasswordSuccessDataSerializer(), "ResetPasswordSuccessResponseSerializer"
)

RefreshTokenResponseSerializer = SuccessSerializer(
    RefreshTokenResponseDataSerializer(), "RefreshTokenResponseSerializer"
)
