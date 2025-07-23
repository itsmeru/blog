from rest_framework import serializers
from .models import Permission, Role
from django.contrib.auth import get_user_model
from core.app.base.serializer import SuccessSerializer

User = get_user_model()

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = [
            'id', 'code', 'name', 'function_zh', 'is_active', 'action', 'resource',
            'category', 'api_url', 'method', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    class Meta:
        model = Role
        fields = [
            'id', 'code', 'name', 'name_zh', 'description', 'is_active', 'category',
            'permissions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class RoleUserSerializer(serializers.ModelSerializer):
    roles = serializers.StringRelatedField(many=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'roles']


PermissionListResponseSerializer = SuccessSerializer(
    PermissionSerializer(many=True), "PermissionListResponseSerializer"
)
PermissionSuccessResponseSerializer = SuccessSerializer(
    PermissionSerializer(), "PermissionSuccessResponseSerializer"
)
RoleListResponseSerializer = SuccessSerializer(
    RoleSerializer(many=True), "RoleListResponseSerializer"
)
RoleSuccessResponseSerializer = SuccessSerializer(
    RoleSerializer(), "RoleSuccessResponseSerializer"
)
RoleUserListResponseSerializer = SuccessSerializer(
    RoleUserSerializer(many=True), "RoleUserListResponseSerializer"
)
BaseSuccessResponseSerializer = SuccessSerializer(
    None, "BaseSuccessResponseSerializer"
)
