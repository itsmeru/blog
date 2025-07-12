import jwt
from rest_framework import serializers
from django.conf import settings

from accounts.models import Account, PasswordResetToken


class EmailValidationMixin:
    def validate_email_exists(self, value):
        if not Account.objects.filter(email=value).exists():
            raise serializers.ValidationError("該電子郵件地址未註冊")
        return value
    
    def validate_email_unique(self, value):
        if Account.objects.filter(email=value).exists():
            raise serializers.ValidationError("此信箱已被使用")
        return value

class UsernameValidationMixin:
    def validate_username_unique(self, value):
        if Account.objects.filter(username=value).exists():
            raise serializers.ValidationError("該用戶名已被使用")
        return value
    
class PasswordValidationMixin:
    def validate_password_length(self, value, min_length=6):
        if len(value) < min_length:
            raise serializers.ValidationError(f"密碼至少需要{min_length}個字符")
        return value

class TokenValidationMixin:
    def validate_reset_token(self, email, token):
        try:
            reset_token = PasswordResetToken.objects.get(email=email, token=token)
            if not reset_token.is_valid():
                raise serializers.ValidationError("驗證碼已過期或已使用")
            return reset_token
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("驗證碼錯誤")


class AccountCreateSerializer(serializers.Serializer, EmailValidationMixin, UsernameValidationMixin, PasswordValidationMixin):
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(max_length=100, write_only=True)

    def validate_username(self, value):
        return self.validate_username_unique(value)
    
    def validate_email(self, value):
        return self.validate_email_unique(value)
    
    def validate_password(self, value):
        return self.validate_password_length(value, 8)
    
    def create(self, validated_data):
        account = Account.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        account.set_password(validated_data['password'])
        return account

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']

class ForgotPasswordSerializer(serializers.Serializer, EmailValidationMixin):
    email = serializers.EmailField()

    def validate_email(self, value):
        return self.validate_email_exists(value)

class ResetTokenSerializer(serializers.Serializer, EmailValidationMixin, TokenValidationMixin):
    email = serializers.EmailField()
    token = serializers.CharField(max_length=6)

    def validate(self, data):
        data['reset_token'] = self.validate_reset_token(data['email'], data['token'])
        return data

class ResetPasswordSerializer(serializers.Serializer, EmailValidationMixin, TokenValidationMixin, PasswordValidationMixin):
    email = serializers.EmailField()
    token = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=6)

    def validate(self, data):
        data['reset_token'] = self.validate_reset_token(data['email'], data['token'])
        return data

    def validate_new_password(self, value):
        return self.validate_password_length(value, 6)

    def save(self):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']
        reset_token = self.validated_data['reset_token']
        
        account = Account.objects.get(email=email)
        account.set_password(new_password)
        account.save()
        
        reset_token.mark_as_used()
        
        return account

class AccountUpdateSerializer(serializers.Serializer, UsernameValidationMixin, PasswordValidationMixin):
    old_password = serializers.CharField(required=False)
    new_password = serializers.CharField(min_length=6, required=False)
    new_username = serializers.CharField(min_length=2, required=False)

    def validate(self, data):
        if not any([data.get('new_password'), data.get('new_username')]):
            raise serializers.ValidationError("請提供要更新的欄位")
        return data

    def validate_new_password(self, value):
        if value:
            return self.validate_password_length(value, 6)
        return value

    def validate_new_username(self, value):
        if value:
            return self.validate_username_unique(value)
        return value

class LoginSerializer(serializers.Serializer, EmailValidationMixin):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return self.validate_email_exists(value)

    def validate(self, data):
        email = data['email']
        password = data['password']
        
        try:
            account = Account.objects.get(email=email)
        except Account.DoesNotExist:
            raise serializers.ValidationError("用戶不存在")
        
        if not account.check_password(password):
            raise serializers.ValidationError("用戶名或密碼錯誤")
        
        data['account'] = account
        return data

class RefreshTokenSerializer(serializers.Serializer):
    def validate(self, data):
        refresh_token = self.context['request'].COOKIES.get("refresh_token")
        
        if not refresh_token:
            raise serializers.ValidationError("No refresh token")
        
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])            
            user_id = payload.get("user_id")            
            account = Account.objects.get(id=user_id)
            data['account'] = account
            return data
        except Account.DoesNotExist:
            raise serializers.ValidationError("User not found")
        except (
            jwt.ExpiredSignatureError,
            jwt.InvalidTokenError,
            jwt.DecodeError,
            jwt.InvalidSignatureError,
        ):
            raise serializers.ValidationError("Invalid or expired token")
