from rest_framework import serializers

from core.app.base.serializer import SuccessSerializer

from .models import Permission, Role, RoleHierarchy, RolePermission


class PermissionSerializer(serializers.ModelSerializer):
    """權限序列化器"""

    class Meta:
        model = Permission
        fields = [
            "id",
            "code",
            "name",
            "category",
            "module",
            "action",
            "resource",
            "api_url",
            "method",
            "level",
            "is_active",
            "created_at",
            "updated_at",
            "function_zh",
            "sort_order",
            "description",
            "parent",
            "stage",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


PermissionListResponseSerializer = SuccessSerializer(
    PermissionSerializer(many=True), "PermissionListResponseSerializer"
)


PermissionDetailResponseSerializer = SuccessSerializer(
    PermissionSerializer(), "PermissionDetailResponseSerializer"
)


class RoleSerializer(serializers.ModelSerializer):
    """角色序列化器"""

    class Meta:
        model = Role
        fields = [
            "id",
            "code",
            "name",
            "name_zh",
            "description",
            "category",
            "level",
            "is_active",
            "stage",
            "special_conditions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RoleListSerializer(serializers.ModelSerializer):
    """角色列表序列化器"""

    total_apply_users = serializers.IntegerField(read_only=True)

    class Meta:
        model = Role
        fields = [
            "id",
            "name_zh",
            "stage",
            "total_apply_users",
            "is_active",
        ]


class RoleCreateSerializer(serializers.Serializer):
    """角色建立序列化器"""

    name_zh = serializers.CharField(max_length=100, help_text="角色中文名稱")
    stage = serializers.ChoiceField(
        choices=[("frontstage", "前台"), ("backstage", "後台")], help_text="權限位置"
    )
    is_active = serializers.BooleanField(default=True, help_text="角色狀態")
    special_conditions = serializers.CharField(
        max_length=200, required=False, allow_blank=True, help_text="特殊條件"
    )
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, help_text="權限ID列表"
    )


class RoleUpdateSerializer(serializers.Serializer):
    """角色更新序列化器"""

    name_zh = serializers.CharField(max_length=100, help_text="角色中文名稱")
    stage = serializers.ChoiceField(
        choices=[("frontstage", "前台"), ("backstage", "後台")], help_text="權限位置"
    )
    is_active = serializers.BooleanField(help_text="角色狀態")
    special_conditions = serializers.CharField(
        max_length=200, required=False, allow_blank=True, help_text="特殊條件"
    )
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, help_text="權限ID列表"
    )

    def __init__(self, *args, **kwargs):
        self.role_id = kwargs.pop("role_id", None)
        super().__init__(*args, **kwargs)


class RoleDetailPermissionSerializer(serializers.Serializer):
    """角色詳情權限序列化器"""

    id = serializers.IntegerField()
    function_zh = serializers.CharField()
    enabled = serializers.BooleanField()


class RoleDetailPermissionGroupSerializer(serializers.Serializer):
    """角色詳情權限群組序列化器"""

    category = serializers.CharField()
    stage = serializers.CharField()
    permissions = RoleDetailPermissionSerializer(many=True)


class RoleDetailSerializer(serializers.Serializer):
    """角色詳情序列化器 - 純序列化層，不包含業務邏輯"""

    id = serializers.IntegerField()
    name_zh = serializers.CharField()
    is_active = serializers.BooleanField()
    permission_groups = RoleDetailPermissionGroupSerializer(many=True)
    total_permissions = serializers.IntegerField()
    total_apply_users = serializers.IntegerField()
    enabled_permissions = serializers.IntegerField()


class RolePermissionSerializer(serializers.ModelSerializer):
    """角色權限關聯序列化器"""

    class Meta:
        model = RolePermission
        fields = ["id", "role", "permission", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class RoleSetPermissionSerializer(serializers.Serializer):
    permissions = serializers.ListField(
        child=serializers.IntegerField(), help_text="權限ID列表"
    )


class RoleHierarchySerializer(serializers.ModelSerializer):
    """角色階層關係序列化器"""

    class Meta:
        model = RoleHierarchy
        fields = ["id", "parent_role", "child_role", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, data):
        """驗證父角色和子角色不能相同"""
        if data["parent_role"] == data["child_role"]:
            raise serializers.ValidationError("父角色和子角色不能相同")
        return data


RoleListResponseSerializer = SuccessSerializer(
    RoleSerializer(many=True), "RoleListResponseSerializer"
)


RoleDetailResponseSerializer = SuccessSerializer(
    RoleSerializer(), "RoleDetailResponseSerializer"
)


class PermissionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = [
            "id",
            "name",
            "function_zh",
            "is_active",
            "method",
            "api_url",
        ]


class PermissionGroupSerializer(serializers.Serializer):
    stage = serializers.CharField()
    category = serializers.CharField()
    permissions = PermissionListSerializer(many=True)


class PermissionListResponseSerializer(serializers.Serializer):
    groups = PermissionGroupSerializer(many=True)
    total_permissions = serializers.IntegerField()
    active_permissions = serializers.IntegerField()


class PermissionBatchUpdateSerializer(serializers.Serializer):
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(), help_text="權限ID列表"
    )
    is_active = serializers.BooleanField(help_text="是否啟用")


class PermissionBatchUpdateOkSerializer(serializers.Serializer):
    updated_count = serializers.IntegerField()
    message = serializers.CharField()


PermissionBatchUpdateOkResponseSerializer = SuccessSerializer(
    PermissionBatchUpdateOkSerializer(), "PermissionBatchUpdateOkResponseSerializer"
)


# 角色管理 API 回應序列化器
class RoleListResponseDataSerializer(serializers.Serializer):
    """角色列表回應資料序列化器"""

    roles = RoleListSerializer(many=True)
    total = serializers.IntegerField()


# 使用 SuccessSerializer 包裝，供 Swagger 文件使用
RoleManagementListResponseSerializer = SuccessSerializer(
    RoleListResponseDataSerializer(), "RoleManagementListResponseSerializer"
)

RoleManagementDetailResponseSerializer = SuccessSerializer(
    RoleDetailSerializer(), "RoleManagementDetailResponseSerializer"
)


# Role Users API Serializers
class RoleUserSerializer(serializers.Serializer):
    """角色使用者序列化器"""

    id = serializers.IntegerField(help_text="使用者ID")
    nickname = serializers.CharField(help_text="使用者暱稱")
    email = serializers.EmailField(help_text="使用者郵箱")
    is_active = serializers.BooleanField(help_text="是否啟用")


class RoleUsersDetailSerializer(serializers.Serializer):
    """角色使用者詳情序列化器"""

    id = serializers.IntegerField(help_text="角色ID")
    name = serializers.CharField(help_text="角色名稱")
    total_user = serializers.IntegerField(help_text="總使用者數")
    users = RoleUserSerializer(many=True, help_text="使用者列表")


class RoleUsersUpdateSerializer(serializers.Serializer):
    """角色使用者更新序列化器"""

    user_ids = serializers.ListField(
        child=serializers.IntegerField(), help_text="使用者ID列表", allow_empty=True
    )


class RoleUserListSerializer(serializers.Serializer):
    """角色使用者列表序列化器"""

    id = serializers.IntegerField(help_text="使用者ID")
    nickname = serializers.CharField(help_text="使用者暱稱")
    department = serializers.CharField(help_text="部門")
    email = serializers.EmailField(help_text="使用者郵箱")
    is_active = serializers.BooleanField(help_text="是否啟用")


# Response Serializers
RoleUsersDetailResponseSerializer = SuccessSerializer(
    RoleUsersDetailSerializer(), "RoleUsersDetailResponseSerializer"
)

RoleUserListResponseSerializer = SuccessSerializer(
    RoleUserListSerializer(many=True), "RoleUserListResponseSerializer"
)
