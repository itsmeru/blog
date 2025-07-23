from typing import List, Optional

from django.db import transaction

from ..models import Permission
from ..repositories import PermissionRepository
from .base import BaseService


class PermissionService(BaseService):
    """權限服務"""

    def __init__(self):
        super().__init__(Permission)
        self.repository = PermissionRepository()

    def get_by_code(self, code: str) -> Optional[Permission]:
        """根據代碼獲取權限"""
        return self.repository.get_by_code(code)

    def get_by_codes(self, codes: List[str]) -> List[Permission]:
        """根據多個代碼獲取權限"""
        return self.repository.get_by_codes(codes)

    def get_by_category(self, category: str) -> List[Permission]:
        """根據分類獲取權限"""
        return self.repository.get_by_category(category)

    def get_by_module(self, module: str) -> List[Permission]:
        """根據模組獲取權限"""
        return self.repository.get_by_module(module)

    def get_by_action(self, action: str) -> List[Permission]:
        """根據操作獲取權限"""
        return self.repository.get_by_action(action)

    def get_by_resource(self, resource: str) -> List[Permission]:
        """根據資源獲取權限"""
        return self.repository.get_by_resource(resource)

    def get_by_level(self, level: int) -> List[Permission]:
        """根據層級獲取權限"""
        return self.repository.get_by_level(level)

    def get_by_parent(self, parent_id: int) -> List[Permission]:
        """根據父權限獲取子權限"""
        return self.repository.get_by_parent(parent_id)

    def get_children(self, permission_id: int) -> List[Permission]:
        """獲取子權限"""
        return self.repository.get_children(permission_id)

    def get_descendants(self, permission_id: int) -> List[Permission]:
        """獲取所有後代權限"""
        return self.repository.get_descendants(permission_id)

    def get_ancestors(self, permission_id: int) -> List[Permission]:
        """獲取所有祖先權限"""
        return self.repository.get_ancestors(permission_id)

    def get_tree(self, permission_id: Optional[int] = None) -> List[Permission]:
        """獲取權限樹"""
        return self.repository.get_tree(permission_id)

    @transaction.atomic
    def create_with_parent(self, parent_id: Optional[int], **kwargs) -> Permission:
        """建立帶有父權限的新權限"""
        parent = self.get_by_id(parent_id) if parent_id else None
        if parent_id and not parent:
            raise ValueError(f"Parent permission with id {parent_id} not found")

        permission = self.create(**kwargs)
        if parent:
            permission.parent = parent
            permission.save()

        return permission

    @transaction.atomic
    def move_to_parent(
        self, permission_id: int, new_parent_id: Optional[int]
    ) -> Permission:
        """移動權限到新的父權限"""
        permission = self.get_by_id(permission_id)
        if not permission:
            raise ValueError(f"Permission with id {permission_id} not found")

        new_parent = self.get_by_id(new_parent_id) if new_parent_id else None
        if new_parent_id and not new_parent:
            raise ValueError(f"New parent permission with id {new_parent_id} not found")

        # 檢查是否會形成循環
        if new_parent and new_parent in self.get_descendants(permission_id):
            raise ValueError("Cannot move permission to its descendant")

        permission.parent = new_parent
        permission.save()
        return permission
