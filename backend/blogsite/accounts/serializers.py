from rest_framework import serializers

from accounts.models import Account, PasswordResetToken

class AccountCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(max_length=100, write_only=True)

    def validate_username(self, value):
        if Account.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long")
        return value
    
    def validate_email(self, value):
        if Account.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        return value
    
    def create(self, validated_data):
        account = Account.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        account.set_password(validated_data['password'])
        account.save()
        return account

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not Account.objects.filter(email=value).exists():
            raise serializers.ValidationError("該電子郵件地址未註冊")
        return value

class VerifyResetTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            reset_token = PasswordResetToken.objects.get(
                email=data['email'], 
                token=data['token']
            )
            if not reset_token.is_valid():
                raise serializers.ValidationError("驗證碼已過期或已使用")
            data['reset_token'] = reset_token
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("驗證碼錯誤")
        return data

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=6)

    def validate(self, data):
        try:
            reset_token = PasswordResetToken.objects.get(
                email=data['email'], 
                token=data['token']
            )
            if not reset_token.is_valid():
                raise serializers.ValidationError("驗證碼已過期或已使用")
            data['reset_token'] = reset_token
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("驗證碼錯誤")
        return data

    def save(self):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']
        reset_token = self.validated_data['reset_token']
        
        account = Account.objects.get(email=email)
        account.set_password(new_password)
        account.save()
        
        reset_token.mark_as_used()
        
        return account

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=6)

    def validate_new_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("新密碼至少需要6個字符")
        return value

class ChangeUsernameSerializer(serializers.Serializer):
    new_username = serializers.CharField(min_length=2)

    def validate_new_username(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("用戶名至少需要2個字符")
        return value
