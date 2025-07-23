from typing import List

from django.contrib.auth import get_user_model
from django.db import transaction

from ..models import Permission, Role
from ..repositories import (
    RoleHierarchyRepository,
    RolePermissionRepository,
    UserPermissionRepository,
)
from .base import BaseService

User = get_user_model()


class UserPermissionService(BaseService):
    """使用者權限服務"""

    def __init__(self):
        super().__init__(User)
        self.user_permission_repository = UserPermissionRepository()
        self.role_permission_repository = RolePermissionRepository()
        self.role_hierarchy_repository = RoleHierarchyRepository()

    def get_direct_permissions(self, user_id: int) -> List[Permission]:
        """獲取使用者的直接權限"""
        return self.user_permission_repository.get_direct_permissions(user_id)

    def get_role_permissions(self, user_id: int) -> List[Permission]:
        """獲取使用者透過角色獲得的權限"""
        return self.user_permission_repository.get_role_permissions(user_id)

    def get_all_permissions(self, user_id: int) -> List[Permission]:
        """獲取使用者的所有權限（包括角色權限）"""
        return self.user_permission_repository.get_all_permissions(user_id)

    def get_roles(self, user_id: int) -> List[Role]:
        """獲取使用者的角色"""
        return self.user_permission_repository.get_roles(user_id)

    def has_permission(self, user_id: int, permission_code: str) -> bool:
        """檢查使用者是否擁有指定權限"""
        return self.user_permission_repository.has_permission(user_id, permission_code)

    def has_any_permission(self, user_id: int, permission_codes: List[str]) -> bool:
        """檢查使用者是否擁有任一指定權限"""
        return self.user_permission_repository.has_any_permission(
            user_id, permission_codes
        )

    def has_all_permissions(self, user_id: int, permission_codes: List[str]) -> bool:
        """檢查使用者是否擁有所有指定權限"""
        return self.user_permission_repository.has_all_permissions(
            user_id, permission_codes
        )

    @transaction.atomic
    def assign_direct_permissions(
        self, user_id: int, permission_ids: List[int]
    ) -> None:
        """分配直接權限給使用者"""
        user = self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        # 移除現有的直接權限
        self.user_permission_repository.remove_all_direct_permissions(user_id)

        # 添加新的直接權限
        for permission_id in permission_ids:
            self.user_permission_repository.add_direct_permission(
                user_id, permission_id
            )

    @transaction.atomic
    def add_direct_permission(self, user_id: int, permission_id: int) -> None:
        """添加單個直接權限給使用者"""
        user = self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        self.user_permission_repository.add_direct_permission(user_id, permission_id)

    @transaction.atomic
    def remove_direct_permission(self, user_id: int, permission_id: int) -> None:
        """移除使用者的直接權限"""
        user = self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        self.user_permission_repository.remove_direct_permission(user_id, permission_id)

    @transaction.atomic
    def remove_all_direct_permissions(self, user_id: int) -> None:
        """移除使用者的所有直接權限"""
        user = self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        self.user_permission_repository.remove_all_direct_permissions(user_id)

    @transaction.atomic
    def assign_roles(self, user_id: int, role_ids: List[int]) -> None:
        """分配角色給使用者"""
        user = self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        # 移除現有的角色
        self.user_permission_repository.remove_all_roles(user_id)

        # 添加新的角色
        for role_id in role_ids:
            self.user_permission_repository.add_role(user_id, role_id)

    @transaction.atomic
    def add_role(self, user_id: int, role_id: int) -> None:
        """添加單個角色給使用者"""
        user = self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        self.user_permission_repository.add_role(user_id, role_id)

    @transaction.atomic
    def remove_role(self, user_id: int, role_id: int) -> None:
        """移除使用者的角色"""
        user = self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        self.user_permission_repository.remove_role(user_id, role_id)

    @transaction.atomic
    def remove_all_roles(self, user_id: int) -> None:
        """移除使用者的所有角色"""
        user = self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        self.user_permission_repository.remove_all_roles(user_id)
