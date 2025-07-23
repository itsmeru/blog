from typing import List, Optional

from django.db import transaction

from ..models import Permission, Role
from ..repositories import (
    RoleHierarchyRepository,
    RolePermissionRepository,
    RoleRepository,
)
from .base import BaseService


class RoleService(BaseService):
    """角色服務"""

    def __init__(self):
        super().__init__(Role)
        self.role_repository = RoleRepository()
        self.role_permission_repository = RolePermissionRepository()
        self.role_hierarchy_repository = RoleHierarchyRepository()

    def get_by_code(self, code: str) -> Optional[Role]:
        """根據代碼獲取角色"""
        return self.role_repository.get_by_code(code)

    def get_by_codes(self, codes: List[str]) -> List[Role]:
        """根據多個代碼獲取角色"""
        return self.role_repository.get_by_codes(codes)

    def get_by_category(self, category: str) -> List[Role]:
        """根據分類獲取角色"""
        return self.role_repository.get_by_category(category)

    def get_by_level(self, level: int) -> List[Role]:
        """根據層級獲取角色"""
        return self.role_repository.get_by_level(level)

    def get_by_parent(self, parent_id: int) -> List[Role]:
        """根據父角色獲取子角色"""
        return self.role_repository.get_by_parent(parent_id)

    def get_children(self, role_id: int) -> List[Role]:
        """獲取子角色"""
        return self.role_repository.get_children(role_id)

    def get_descendants(self, role_id: int) -> List[Role]:
        """獲取所有後代角色"""
        return self.role_repository.get_descendants(role_id)

    def get_ancestors(self, role_id: int) -> List[Role]:
        """獲取所有祖先角色"""
        return self.role_repository.get_ancestors(role_id)

    def get_tree(self, role_id: Optional[int] = None) -> List[Role]:
        """獲取角色樹"""
        return self.role_repository.get_tree(role_id)

    def get_permissions(self, role_id: int) -> List[Permission]:
        """獲取角色的權限"""
        return self.role_permission_repository.get_permissions(role_id)

    def get_inherited_permissions(self, role_id: int) -> List[Permission]:
        """獲取角色繼承的權限"""
        return self.role_permission_repository.get_inherited_permissions(role_id)

    def get_all_permissions(self, role_id: int) -> List[Permission]:
        """獲取角色的所有權限（包括繼承的）"""
        return self.role_permission_repository.get_all_permissions(role_id)

    @transaction.atomic
    def create_with_parent(self, parent_id: Optional[int], **kwargs) -> Role:
        """建立帶有父角色的新角色"""
        parent = self.get_by_id(parent_id) if parent_id else None
        if parent_id and not parent:
            raise ValueError(f"Parent role with id {parent_id} not found")

        role = self.create(**kwargs)
        if parent:
            role.parent = parent
            role.save()

        return role

    @transaction.atomic
    def move_to_parent(self, role_id: int, new_parent_id: Optional[int]) -> Role:
        """移動角色到新的父角色"""
        role = self.get_by_id(role_id)
        if not role:
            raise ValueError(f"Role with id {role_id} not found")

        new_parent = self.get_by_id(new_parent_id) if new_parent_id else None
        if new_parent_id and not new_parent:
            raise ValueError(f"New parent role with id {new_parent_id} not found")

        # 檢查是否會形成循環
        if new_parent and new_parent in self.get_descendants(role_id):
            raise ValueError("Cannot move role to its descendant")

        role.parent = new_parent
        role.save()
        return role

    @transaction.atomic
    def assign_permissions(self, role_id: int, permission_ids: List[int]) -> None:
        """分配權限給角色"""
        role = self.get_by_id(role_id)
        if not role:
            raise ValueError(f"Role with id {role_id} not found")

        # 移除現有的權限
        self.role_permission_repository.remove_all_permissions(role_id)

        # 添加新的權限
        for permission_id in permission_ids:
            self.role_permission_repository.add_permission(role_id, permission_id)

    @transaction.atomic
    def add_permission(self, role_id: int, permission_id: int) -> None:
        """添加單個權限給角色"""
        role = self.get_by_id(role_id)
        if not role:
            raise ValueError(f"Role with id {role_id} not found")

        self.role_permission_repository.add_permission(role_id, permission_id)

    @transaction.atomic
    def remove_permission(self, role_id: int, permission_id: int) -> None:
        """移除角色的權限"""
        role = self.get_by_id(role_id)
        if not role:
            raise ValueError(f"Role with id {role_id} not found")

        self.role_permission_repository.remove_permission(role_id, permission_id)

    @transaction.atomic
    def remove_all_permissions(self, role_id: int) -> None:
        """移除角色的所有權限"""
        role = self.get_by_id(role_id)
        if not role:
            raise ValueError(f"Role with id {role_id} not found")

        self.role_permission_repository.remove_all_permissions(role_id)
