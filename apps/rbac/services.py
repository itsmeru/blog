from collections import defaultdict
from typing import List, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from core.app.api.exception import NotFoundError, ValidationError

from .models import Permission, Role, RolePermission
from .repositories import (
    PermissionRepository,
    RoleHierarchyRepository,
    RoleRepository,
    UserRepository,
)


class PermissionService:
    """權限服務層"""

    @staticmethod
    def get_all_permissions():
        """取得所有權限"""
        return PermissionRepository.all()

    @staticmethod
    def get_permission(pk):
        """取得單一權限"""
        permission = PermissionRepository.get_by_id(pk)
        if not permission:
            raise NotFoundError("權限不存在")
        return permission

    @staticmethod
    def create_permission(**kwargs):
        """建立權限"""
        try:
            return PermissionRepository.create(**kwargs)
        except Exception as e:
            raise ValidationError(str(e))

    @staticmethod
    def update_permission(pk, **kwargs):
        """更新權限"""
        permission = PermissionService.get_permission(pk)
        return PermissionRepository.update(permission, **kwargs)

    @staticmethod
    def delete_permission(pk):
        """刪除權限"""
        permission = PermissionService.get_permission(pk)
        PermissionRepository.delete(permission)

    @staticmethod
    def get_permission_by_api(api_url, method):
        """根據 API URL 和 HTTP 方法獲取權限"""
        try:
            return PermissionRepository.get_by_api_url(api_url, method)
        except Exception as e:
            raise ValidationError(f"獲取權限失敗: {str(e)}")

    @staticmethod
    def get_permissions_grouped(stage=None, is_active=None, function_zh_search=None):
        """取得分組的權限列表"""
        return PermissionRepository.get_permissions_grouped(
            stage=stage, is_active=is_active, function_zh_search=function_zh_search
        )

    @staticmethod
    @transaction.atomic
    def batch_update_permissions(permission_ids, is_active):
        """批次更新權限的啟用狀態"""
        permissions = PermissionRepository.filter(id__in=permission_ids)
        if len(permissions) != len(permission_ids):
            raise ValidationError("部分權限不存在")

        updated_count = PermissionRepository.batch_update_permissions(
            permission_ids=permission_ids, is_active=is_active
        )

        return updated_count


class RoleService:
    """角色服務層"""

    @staticmethod
    def get_all_roles():
        """取得所有角色"""
        return RoleRepository.all()

    @staticmethod
    def get_role(pk):
        """取得單一角色"""
        role = RoleRepository.get_by_id(pk)
        if not role:
            raise NotFoundError("角色不存在")
        return role

    @staticmethod
    @transaction.atomic
    def create_role(**kwargs):
        """建立角色"""
        try:
            role = RoleRepository.create(**kwargs)

            # 預設啟動所有權限
            all_permissions = PermissionRepository.filter(is_active=True)
            permission_ids = [permission.id for permission in all_permissions]
            if permission_ids:
                RoleRepository.set_role_permissions(role.id, permission_ids)

            return role
        except Exception as e:
            raise ValidationError(str(e))

    @staticmethod
    def update_role(pk, **kwargs):
        """更新角色"""
        role = RoleService.get_role(pk)
        return RoleRepository.update(role, **kwargs)

    @staticmethod
    def delete_role(pk):
        """刪除角色"""
        role = RoleService.get_role(pk)
        RoleRepository.delete(role)

    @staticmethod
    def get_role_permissions(role_id):
        """取得角色的權限列表"""
        try:
            role = RoleService.get_role(role_id)
            return role.permissions.all()
        except Exception as e:
            raise ValidationError(str(e))

    @staticmethod
    @transaction.atomic
    def set_role_permissions(role_id, permission_ids):
        """設定角色的權限"""
        role = RoleService.get_role(role_id)

        # 驗證權限是否存在
        permissions = PermissionRepository.filter(id__in=permission_ids)
        if len(permissions) != len(permission_ids):
            raise ValidationError("部分權限不存在")

        # 刪除現有的權限關聯
        RolePermission.objects.filter(role=role).delete()

        # 建立新的權限關聯
        role_permissions = []
        for permission in permissions:
            role_permissions.append(
                RolePermission(role=role, permission=permission, is_active=True)
            )
        RolePermission.objects.bulk_create(role_permissions)

        return role

    # 新增角色管理 API 專用方法
    @staticmethod
    def get_roles_with_user_count() -> List[Role]:
        """獲取角色列表並包含使用者數量"""
        return RoleRepository.get_roles_with_user_count()

    @staticmethod
    def get_role_with_user_count(role_id: int) -> Optional[Role]:
        """獲取單一角色並包含使用者數量"""
        return RoleRepository.get_role_with_user_count(role_id)

    @staticmethod
    def _validate_role_code(code: str, role_id: int = None) -> None:
        """驗證角色代碼唯一性"""
        role = RoleRepository.filter(code=code)
        if role_id:
            role = role.exclude(id=role_id)
        if role.exists():
            raise ValidationError("此角色代碼已存在")

    @staticmethod
    @transaction.atomic
    def create_role_with_permissions(data: dict) -> Role:
        """建立角色並設定權限"""
        code = data.get("code") or data.get("name_zh")
        data["code"] = code
        RoleService._validate_role_code(code)

        permission_ids = data.pop("permission_ids", None)
        role = RoleRepository.create(**data)

        # 取得所有啟用的權限
        if not permission_ids:
            all_permissions = PermissionRepository.filter(
                is_active=True, stage=data["stage"]
            )
            permission_ids = [permission.id for permission in all_permissions]
        # 設定權限
        RoleRepository.set_role_permissions(role.id, permission_ids)

        return role

    @staticmethod
    @transaction.atomic
    def update_role_with_permissions(role_id: int, data: dict) -> Role:
        """更新角色並設定權限"""
        role = RoleService.get_role(role_id)
        if not role:
            raise NotFoundError(f"角色ID不存在:{role_id}")

        code = data.get("code") or data.get("name_zh")
        data["code"] = code
        permission_ids = data.pop("permission_ids", None)
        if code:
            RoleService._validate_role_code(code, role_id)

        if data:
            role = RoleRepository.update(role, **data)

        # 更新權限
        if permission_ids:
            RoleRepository.set_role_permissions(role_id, permission_ids)

        return role

    @staticmethod
    @transaction.atomic
    def delete_role_safe(role_id: int) -> None:
        """安全刪除角色 - 檢查是否仍有使用者綁定"""
        role = RoleService.get_role(role_id)
        if not role:
            raise NotFoundError(f"角色ID不存在:{role_id}")

        if not RoleRepository.can_delete_role(role_id):
            raise ValidationError("無法刪除角色：仍有使用者綁定此角色")

        RoleRepository.delete(role)

    @staticmethod
    def get_role_permission_groups(
        role_id: int, stage=None, is_active=None
    ) -> List[dict]:
        """獲取角色的權限群組資料"""
        # Repository layer calls
        role = RoleService.get_role(role_id)
        permission_groups = RoleRepository.get_permissions_grouped_by_category_stage(
            stage=stage or role.stage
        )
        role_permission_ids = RoleRepository.get_role_permission_ids(role_id)

        # Business logic - format data for serializer
        result = []
        for (category, stage_key), permissions in permission_groups.items():
            permission_data = []
            for permission in permissions:
                enabled = permission.id in role_permission_ids
                permission_data.append(
                    {
                        "id": permission.id,
                        "function_zh": permission.function_zh,
                        "enabled": enabled,
                    }
                )
            # 如果 is_active 為 False，則顯示 disabled 的權限
            # 如果 is_active 為 True，則顯示 enabled 的權限
            # 如果 is_active 為 None，則顯示所有權限
            if is_active is not None:
                permission_data = [
                    permission
                    for permission in permission_data
                    if permission["enabled"] == is_active
                ]

            result.append(
                {
                    "category": category,
                    "stage": stage_key,
                    "permissions": permission_data,
                }
            )

        return result

    @staticmethod
    def get_role_permission_stats(role_id: int, stage=None) -> dict:
        """獲取角色權限統計資料"""
        role = RoleService.get_role(role_id)
        # Repository layer calls
        filter_params = {"stage": stage or role.stage}
        filter_params["is_active"] = True
        total_permissions = PermissionRepository.filter(**filter_params).count()
        role_permission_ids = RoleRepository.get_role_permission_ids(role_id)

        return {
            "total_permissions": total_permissions,
            "enabled_permissions": len(role_permission_ids),
        }


class RoleHierarchyService:
    """角色階層服務層"""

    @staticmethod
    def create_hierarchy(parent_role_id, child_role_id):
        """建立角色階層關係"""
        parent_role = RoleRepository.get_by_id(parent_role_id)
        child_role = RoleRepository.get_by_id(child_role_id)

        # 檢查是否會形成循環依賴
        children = RoleHierarchyRepository.get_all_children(child_role)
        if parent_role.id in children:
            raise ValidationError("不能建立循環依賴的角色階層關係")

        try:
            return RoleHierarchyRepository.create(parent_role, child_role)
        except Exception as e:
            raise ValidationError(f"建立角色階層關係失敗: {str(e)}")

    @staticmethod
    def delete_hierarchy(parent_role_id, child_role_id):
        """刪除角色階層關係"""
        parent_role = RoleRepository.get_by_id(parent_role_id)
        child_role = RoleRepository.get_by_id(child_role_id)
        hierarchy = RoleHierarchyRepository.get_by_parent(parent_role).get(
            child_role=child_role
        )
        try:
            RoleHierarchyRepository.delete(hierarchy)
        except Exception as e:
            raise ValidationError(f"刪除角色階層關係失敗: {str(e)}")

    @staticmethod
    def get_role_hierarchy(role_id):
        """獲取角色的階層關係"""
        role = RoleRepository.get_by_id(role_id)
        try:
            return RoleRepository.get_role_hierarchy(role)
        except Exception as e:
            raise ValidationError(f"獲取角色階層關係失敗: {str(e)}")


class RoleUserService:
    """角色使用者服務層"""

    @staticmethod
    def get_role_users(role_id: int) -> dict:
        """獲取角色的使用者列表"""
        role = RoleService.get_role(role_id)
        if not role:
            raise NotFoundError("角色不存在")

        users = UserRepository.get_all_users_by_role(role)

        return {
            "id": role.id,
            "name": role.name_zh,
            "total_user": users.count(),
            "users": [
                {
                    "id": user.id,
                    "nickname": user.nickname,
                    "email": user.email,
                    "is_active": user.is_active,
                }
                for user in users
            ],
        }

    @staticmethod
    @transaction.atomic
    def update_role_users(role_id: int, user_ids: List[int]) -> None:
        """更新角色的使用者列表"""
        role = RoleService.get_role(role_id)
        if not role:
            raise NotFoundError("角色不存在")

        # 驗證使用者是否存在
        if user_ids:
            existing_users = UserRepository.get_users_by_ids(user_ids)
            if existing_users.count() != len(user_ids):
                raise ValidationError("部分使用者不存在")

        # 清除角色現有的使用者關聯
        role.users.clear()

        # 添加新的使用者關聯
        if user_ids:
            users = UserRepository.get_users_by_ids(user_ids)
            role.users.set(users)

    @staticmethod
    def get_role_users_list(search=None, department=None, page=1, page_size=20) -> dict:
        """獲取角色使用者列表 (分頁)"""
        queryset = UserRepository.search_users(search=search, department=department)

        # 分頁
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        users = queryset[start:end]

        return {
            "results": [
                {
                    "id": user.id,
                    "nickname": user.nickname,
                    "department": user.get_department_display(),
                    "email": user.email,
                    "is_active": user.is_active,
                }
                for user in users
            ],
            "count": total,
            "next": f"?page={page + 1}" if end < total else None,
            "previous": f"?page={page - 1}" if page > 1 else None,
        }
