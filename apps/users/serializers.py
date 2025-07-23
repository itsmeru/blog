from rest_framework import serializers

from apps.rbac.models import Role
from core.app.base.serializer import SuccessSerializer
from core.mixins.choices import DepartmentChoicesMixin

from .models import User


class UserBaseSerializer(serializers.ModelSerializer):
    """用戶基本信息序列化器"""

    class Meta:
        model = User
        fields = ["email", "phone", "nickname"]


class RegisterSerializer(UserBaseSerializer):
    """註冊序列化器"""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + ["password"]

    def validate_email(self, value):
        """驗證 email 是否已存在"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value


class LoginSerializer(serializers.Serializer):
    """登入序列化器"""

    account = serializers.CharField(help_text="Email 或 Phone")
    password = serializers.CharField(write_only=True)


class ForgotPasswordSerializer(serializers.Serializer):
    """忘記密碼序列化器"""

    account = serializers.CharField(help_text="Email 或 Phone")


class UserProfileSerializer(UserBaseSerializer):
    """用戶資料序列化器"""

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + ["id", "is_active", "created_at"]


class LoginSuccessDataSerializer(serializers.Serializer):
    token = serializers.CharField(help_text="JWT token (兼容欄位)")
    access = serializers.CharField(help_text="JWT access token")
    refresh = serializers.CharField(help_text="JWT refresh token")
    user_id = serializers.IntegerField(help_text="用戶ID")
    nickname = serializers.CharField(help_text="暱稱")


LoginSuccessResponseSerializer = SuccessSerializer(
    LoginSuccessDataSerializer(), "LoginSuccessResponseSerializer"
)


class ForgotPasswordDataSerializer(serializers.Serializer):
    message = serializers.CharField(help_text="重設密碼流程啟動訊息")
    user_found = serializers.BooleanField(help_text="是否找到用戶")


ForgotPasswordResponseSerializer = SuccessSerializer(
    ForgotPasswordDataSerializer(), "ForgotPasswordResponseSerializer"
)


class MeDataSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(help_text="用戶ID")
    email = serializers.EmailField(help_text="Email")
    phone = serializers.CharField(help_text="電話", allow_null=True)
    nickname = serializers.CharField(help_text="暱稱")


MeResponseSerializer = SuccessSerializer(MeDataSerializer(), "MeResponseSerializer")


class RefreshTokenSerializer(serializers.Serializer):
    """刷新令牌序列化器"""

    refresh = serializers.CharField(help_text="Refresh token")


class RefreshTokenResponseDataSerializer(serializers.Serializer):
    access = serializers.CharField(help_text="新的 access token")
    refresh = serializers.CharField(help_text="新的 refresh token")


RefreshTokenResponseSerializer = SuccessSerializer(
    RefreshTokenResponseDataSerializer(), "RefreshTokenResponseSerializer"
)


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "name_zh"]


class UserListSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "nickname", "department", "roles", "username", "is_active"]


class PermissionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    function_zh = serializers.CharField()
    enabled = serializers.BooleanField()


class PermissionGroupSerializer(serializers.Serializer):
    category = serializers.CharField()
    stage = serializers.CharField()
    permissions = PermissionSerializer(many=True)


class UserDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nickname = serializers.CharField()
    department = serializers.CharField()
    is_active = serializers.BooleanField()
    roles = RoleSerializer(many=True)
    username = serializers.CharField()
    email = serializers.EmailField()
    permission_groups = PermissionGroupSerializer(many=True)
    total_permissions = serializers.IntegerField()
    enabled_permissions_count = serializers.IntegerField()


class UserCreateSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=50)
    department = serializers.ChoiceField(
        choices=DepartmentChoicesMixin.DEPARTMENT_CHOICES,
        required=False,
        allow_null=True,
    )
    roles = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )
    username = serializers.CharField(max_length=50, required=False, allow_null=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_null=True)
    is_active = serializers.BooleanField(default=True)
    enabled_permissions = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True, default=list
    )
    disabled_permissions = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True, default=list
    )


class UserUpdateSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=50, required=False)
    department = serializers.ChoiceField(
        choices=DepartmentChoicesMixin.DEPARTMENT_CHOICES,
        required=False,
        allow_null=True,
    )
    roles = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )
    username = serializers.CharField(max_length=50, required=False, allow_null=True)
    password = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False)
    enabled_permissions = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )
    disabled_permissions = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )


class UserPatchSerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=True)


# Pagination Response Serializer
class PaginationDataSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = UserListSerializer(many=True)


class UserListPaginationResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    message = serializers.CharField(default="ok")
    data = PaginationDataSerializer()


# Response Serializers with SuccessSerializer wrapper
UserDetailResponseSerializer = SuccessSerializer(
    UserDetailSerializer(), "UserDetailResponseSerializer"
)

UserCreateResponseSerializer = SuccessSerializer(
    UserListSerializer(), "UserCreateResponseSerializer"
)

UserUpdateResponseSerializer = SuccessSerializer(
    UserListSerializer(), "UserUpdateResponseSerializer"
)


class DepartmentOptionSerializer(serializers.Serializer):
    label = serializers.CharField()
    value = serializers.CharField()


DepartmentListResponseSerializer = SuccessSerializer(
    DepartmentOptionSerializer(many=True), "DepartmentListResponseSerializer"
)
