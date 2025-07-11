from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from accounts.models import Account

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
        # 創建用戶並加密密碼
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