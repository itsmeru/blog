from rest_framework import serializers
from .models import Permission, Role
from django.contrib.auth import get_user_model
from core.app.base.serializer import SuccessSerializer

User = get_user_model()


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = [
            "id",
            "code",
            "name",
            "function_zh",
            "is_active",
            "action",
            "resource",
            "category",
            "api_url",
            "method",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PermissionSimpleSerializer(serializers.ModelSerializer):
    enabled = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = ["id", "function_zh", "enabled"]

    def get_enabled(self, obj):
        return obj.is_active


class RoleSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name_zh", "is_active"]


class RoleDetailSerializer(serializers.ModelSerializer):
    permission_groups = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ["id", "code", "name_zh", "permission_groups"]

    def get_permission_groups(self, obj):
        permissions = obj.permissions.all()
        return [
            {"permissions": PermissionSimpleSerializer(permissions, many=True).data}
        ]


class RoleUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nickname = serializers.CharField()
    email = serializers.EmailField()
    is_active = serializers.BooleanField()


class RoleUsersDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name_zh = serializers.CharField()
    total_user = serializers.IntegerField()
    users = RoleUserSerializer(many=True)


class RoleUsersUpdateSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.IntegerField(), help_text="使用者ID列表", allow_empty=True
    )


class PermissionBatchUpdateSerializer(serializers.Serializer):
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(), help_text="權限ID列表", allow_empty=True
    )
    is_active = serializers.BooleanField(help_text="啟用狀態")


PermissionListResponseSerializer = SuccessSerializer(
    PermissionSerializer(many=True), "PermissionListResponseSerializer"
)
PermissionSuccessResponseSerializer = SuccessSerializer(
    PermissionSerializer(), "PermissionSuccessResponseSerializer"
)
RoleListResponseSerializer = SuccessSerializer(
    serializers.SerializerMethodField(), "RoleListResponseSerializer"
)
RoleDetailResponseSerializer = SuccessSerializer(
    RoleDetailSerializer(), "RoleDetailResponseSerializer"
)
RoleUserListResponseSerializer = SuccessSerializer(
    RoleUserSerializer(many=True), "RoleUserListResponseSerializer"
)
BaseSuccessResponseSerializer = SuccessSerializer(None, "BaseSuccessResponseSerializer")
