from collections import defaultdict
from typing import Optional

from django.contrib.auth.hashers import check_password
from rest_framework.exceptions import AuthenticationFailed, NotFound, ValidationError
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.rbac.repositories import PermissionRepository
from core.app.base.service import BaseService

from .models import User
from .repository import UserRepository


class UserService(BaseService[User]):
    """用戶服務層，處理所有用戶相關的業務邏輯"""

    repository_class = UserRepository

    @classmethod
    def _validate_email_unique(cls, email: str) -> None:
        """驗證郵箱唯一性

        Args:
            email: 待驗證的郵箱地址

        Raises:
            ValidationError: 當郵箱已存在時拋出
        """
        if cls.repository_class.get_by_email(email):
            raise ValidationError({"email": ["Email already exists"]})

    @classmethod
    def _validate_user_exists(cls, user_id: int) -> User:
        """驗證用戶存在性並返回用戶實例

        Args:
            user_id: 用戶ID

        Returns:
            User: 用戶實例

        Raises:
            NotFound: 當用戶不存在時拋出
        """
        user = cls.repository_class.get_by_id(user_id)
        if not user:
            raise NotFound("User not found")
        return user

    @classmethod
    def _validate_user_active(cls, user: User) -> None:
        """驗證用戶是否處於活躍狀態

        Args:
            user: 用戶實例

        Raises:
            ValidationError: 當用戶不處於活躍狀態時拋出
        """
        if not user.is_active:
            raise ValidationError({"detail": "User is not active"})

    @classmethod
    def register_user(
        cls, email: str, phone: str, nickname: str, password: str
    ) -> User:
        """註冊新用戶

        Args:
            email: 用戶郵箱
            phone: 用戶手機號
            nickname: 用戶暱稱
            password: 用戶密碼

        Returns:
            User: 新創建的用戶實例

        Raises:
            ValidationError: 當驗證失敗時拋出
        """
        try:
            cls._validate_email_unique(email)

            return cls.repository_class.create_user(
                email=email, phone=phone, nickname=nickname, password=password
            )
        except Exception as e:
            cls.handle_exception(e)

    @classmethod
    def authenticate(cls, account: str, password: str) -> User:
        """用戶認證

        Args:
            account: 用戶帳號（郵箱或手機號）
            password: 用戶密碼

        Returns:
            User: 認證成功的用戶實例

        Raises:
            AuthenticationFailed: 當認證失敗時拋出
            ValidationError: 當用戶未啟用時拋出
        """
        # 獲取用戶
        user = cls.repository_class.get_by_account(account)
        if not user:
            raise AuthenticationFailed("Invalid credentials")

        # 檢查用戶狀態
        if not user.is_active:
            raise AuthenticationFailed({"detail": "User is not active"})

        # 檢查密碼
        if not check_password(password, user.password):
            raise AuthenticationFailed("Invalid credentials")

        return user

    @classmethod
    def start_forgot_password(cls, account: str) -> Optional[User]:
        """開始忘記密碼流程

        Args:
            account: 用戶帳號（郵箱或手機號）

        Returns:
            Optional[User]: 如果找到用戶，返回用戶實例；否則返回 None

        Raises:
            NotFound: 當找不到用戶時拋出
        """
        user = cls.repository_class.get_by_email(
            account
        ) or cls.repository_class.get_by_phone(account)
        if not user:
            raise NotFound("User not found")

        # TODO: 發送重置密碼郵件或短信
        return user

    @classmethod
    def update_password(cls, user_id: int, new_password: str) -> User:
        """更新用戶密碼

        Args:
            user_id: 用戶ID
            new_password: 新密碼

        Returns:
            User: 更新後的用戶實例

        Raises:
            NotFound: 當用戶不存在時拋出
            ValidationError: 當密碼更新失敗時拋出
        """
        try:
            user = cls._validate_user_exists(user_id)
            return cls.repository_class.update_password(user, new_password)
        except Exception as e:
            cls.handle_exception(e)

    @classmethod
    def get_active_users(cls):
        """獲取所有活躍用戶

        Returns:
            QuerySet: 活躍用戶查詢集
        """
        try:
            return cls.repository_class.get_active_users()
        except Exception as e:
            cls.handle_exception(e)

    @classmethod
    def deactivate_user(cls, user_id: int) -> User:
        """停用用戶帳號

        Args:
            user_id: 用戶ID

        Returns:
            User: 更新後的用戶實例

        Raises:
            NotFound: 當用戶不存在時拋出
        """
        try:
            user = cls._validate_user_exists(user_id)
            return cls.repository_class.deactivate_user(user)
        except Exception as e:
            cls.handle_exception(e)

    @classmethod
    def activate_user(cls, user_id: int) -> User:
        """啟用用戶帳號

        Args:
            user_id: 用戶ID

        Returns:
            User: 更新後的用戶實例

        Raises:
            NotFound: 當用戶不存在時拋出
        """
        try:
            user = cls._validate_user_exists(user_id)
            return cls.repository_class.activate_user(user)
        except Exception as e:
            cls.handle_exception(e)

    @classmethod
    def refresh_token(cls, refresh_token: str) -> str:
        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token
            return {
                "access": str(access_token),
                "refresh": str(refresh),
            }
        except (InvalidToken, TokenError):
            raise ValidationError("Invalid refresh token")

    @classmethod
    def get_users_list(cls, department=None, is_active=None, search=None):
        """Get users list with filters."""
        try:
            return cls.repository_class.get_users_with_filters(
                department=department, is_active=is_active, search=search
            )
        except Exception as e:
            cls.handle_exception(e)

    @classmethod
    def get_user_detail(cls, user_id: int) -> User:
        """Get user detail with all related data."""
        try:
            user = cls.repository_class.get_user_by_id_with_relations(user_id)
            if not user:
                raise NotFound("User not found")
            return user
        except Exception as e:
            cls.handle_exception(e)

    @classmethod
    def create_user(cls, **kwargs) -> User:
        """Create a new user."""
        try:
            email = kwargs.get("email")
            username = kwargs.get("username")

            if email and cls.repository_class.get_by_email(email):
                raise ValidationError({"email": ["Email already exists"]})

            if username and cls.repository_class.filter(username=username).exists():
                raise ValidationError({"username": ["Username already exists"]})

            password = kwargs.pop("password")
            role_ids = kwargs.pop("roles", [])
            user = cls.repository_class.create(**kwargs)
            user.set_password(password)
            user.save()

            if role_ids:
                from apps.rbac.models import Role

                roles = Role.objects.filter(id__in=role_ids)
                user.roles.set(roles)

            return user
        except Exception as e:
            cls.handle_exception(e)

    @classmethod
    def delete_user(cls, user_id: int) -> None:
        """Hard delete a user."""
        try:
            user = cls._validate_user_exists(user_id)
            cls.repository_class.hard_delete_user(user)
        except Exception as e:
            cls.handle_exception(e)

    @classmethod
    def update_user(cls, user_id: int, **kwargs) -> User:
        """Update an existing user."""
        try:
            user = cls._validate_user_exists(user_id)

            # Validate unique constraints
            email = kwargs.get("email")
            username = kwargs.get("username")

            if email and email != user.email:
                if cls.repository_class.get_by_email(email):
                    raise ValidationError({"email": ["Email already exists"]})

            if username and username != user.username:
                if (
                    cls.repository_class.filter(username=username)
                    .exclude(id=user_id)
                    .exists()
                ):
                    raise ValidationError({"username": ["Username already exists"]})

            # Handle password update if provided
            password = kwargs.pop("password", None)
            role_ids = kwargs.pop("roles", None)

            # Update user fields
            for field, value in kwargs.items():
                setattr(user, field, value)

            if password:
                user.set_password(password)

            user.save()

            # Update roles if provided
            if role_ids is not None:
                from apps.rbac.models import Role

                roles = Role.objects.filter(id__in=role_ids)
                user.roles.set(roles)

            return user
        except Exception as e:
            cls.handle_exception(e)

    @classmethod
    def get_user_permission_groups(cls, user: User, stage=None, enabled=None):
        """Get user permission groups with enabled/disabled status."""
        try:
            permissions = PermissionRepository.get_all()

            # Filter by stage if provided
            if stage:
                permissions = permissions.filter(stage=stage)

            groups = defaultdict(list)

            for permission in permissions:
                key = (permission.category, permission.stage)
                is_enabled = cls._is_permission_enabled_for_user(user, permission)

                # Filter by enabled status if provided
                if enabled is not None and is_enabled != enabled:
                    continue

                groups[key].append(
                    {
                        "id": permission.id,
                        "function_zh": permission.function_zh,
                        "enabled": is_enabled,
                    }
                )

            result = []
            for (category, stage), perms in groups.items():
                result.append(
                    {"category": category, "stage": stage, "permissions": perms}
                )

            return result
        except Exception as e:
            cls.handle_exception(e)

    @classmethod
    def get_user_permission_stats(cls, user: User, stage=None, enabled=None):
        """Get user permission statistics."""
        try:
            from apps.rbac.models import Permission

            permissions_query = Permission.objects.all()

            # Filter by stage if provided
            if stage:
                permissions_query = permissions_query.filter(stage=stage)

            total_permissions = permissions_query.count()
            enabled_count = 0

            for permission in permissions_query:
                is_enabled = cls._is_permission_enabled_for_user(user, permission)

                if enabled is not None and is_enabled != enabled:
                    continue

                if is_enabled:
                    enabled_count += 1

            return {
                "total_permissions": total_permissions,
                "enabled_permissions_count": enabled_count,
            }
        except Exception as e:
            cls.handle_exception(e)

    @classmethod
    def _is_permission_enabled_for_user(cls, user: User, permission) -> bool:
        """Check if a permission is enabled for a user."""
        return permission.id not in user.disabled_permissions and (
            permission.id in user.enabled_permissions
            or user.permissions.filter(id=permission.id).exists()
            or any(
                role.permissions.filter(id=permission.id).exists()
                for role in user.roles.all()
            )
        )

    @classmethod
    def get_department_options(cls) -> list[dict]:
        """Get department options in label-value format."""
        from core.mixins.choices import DepartmentChoicesMixin

        return [
            {"label": choice[0], "value": choice[1]}
            for choice in DepartmentChoicesMixin.DEPARTMENT_CHOICES
        ]
