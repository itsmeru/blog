from collections import defaultdict

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django.db.models import Count, Q

# from core.app.base.repository import BaseRepository

from .models import Permission, Role, RoleHierarchy, RolePermission


class PermissionRepository:
    """權限資料存取層"""

    model_class = Permission

    @classmethod
    def get_by_id(cls, permission_id):
        """根據 ID 獲取權限"""
        return super().get_by_id(permission_id)

    @staticmethod
    def get_by_code(code):
        """根據權限代碼獲取權限"""
        return Permission.objects.get(code=code)

    @staticmethod
    def get_by_codes(codes):
        """根據多個權限代碼獲取權限"""
        return Permission.objects.filter(code__in=codes)

    @staticmethod
    def get_all():
        """獲取所有權限"""
        return Permission.objects.all()

    @staticmethod
    def get_active():
        """獲取所有啟用的權限"""
        return Permission.objects.filter(is_active=True)

    @staticmethod
    def get_by_module(module):
        """獲取指定模組的權限"""
        return Permission.objects.filter(module=module)

    @staticmethod
    def get_by_action(action):
        """根據操作獲取權限"""
        return Permission.objects.filter(action=action)

    @staticmethod
    def get_by_resource(resource):
        """根據資源獲取權限"""
        return Permission.objects.filter(resource=resource)

    @staticmethod
    def get_by_category(category):
        """根據分類獲取權限"""
        return Permission.objects.filter(category=category)

    @staticmethod
    def get_by_level(level):
        """根據層級獲取權限"""
        return Permission.objects.filter(level=level)

    @staticmethod
    def get_by_parent(parent):
        """根據父權限獲取子權限"""
        return Permission.objects.filter(parent=parent)

    @staticmethod
    def get_children(permission):
        """獲取子權限"""
        return Permission.objects.filter(parent=permission)

    @staticmethod
    def get_ancestors(permission):
        """獲取所有祖先權限"""
        ancestors = set()
        current = permission
        while current.parent:
            ancestors.add(current.parent)
            current = current.parent
        return ancestors

    @staticmethod
    def get_descendants(permission):
        """獲取所有後代權限"""
        descendants = set()
        children = Permission.objects.filter(parent=permission)
        for child in children:
            descendants.add(child)
            descendants.update(PermissionRepository.get_descendants(child))
        return descendants

    @staticmethod
    def get_tree(category=None):
        """獲取權限樹"""
        if category:
            permissions = Permission.objects.filter(category=category)
        else:
            permissions = Permission.objects.all()

        tree = {}
        for permission in permissions:
            if not permission.parent:
                tree[permission] = PermissionRepository._build_tree(permission)
        return tree

    @staticmethod
    def _build_tree(permission):
        """構建權限樹"""
        children = Permission.objects.filter(parent=permission)
        tree = {}
        for child in children:
            tree[child] = PermissionRepository._build_tree(child)
        return tree

    @staticmethod
    def create(**kwargs):
        """建立新權限"""
        return Permission.objects.create(**kwargs)

    @staticmethod
    def update(permission, **kwargs):
        """更新權限"""
        for key, value in kwargs.items():
            setattr(permission, key, value)
        permission.save()
        return permission

    @staticmethod
    def delete(permission):
        """刪除權限"""
        permission.delete()

    @classmethod
    def get_permissions_grouped(
        cls, stage=None, is_active=None, function_zh_search=None
    ):
        """取得分組的權限列表"""
        queryset = cls.all()

        if stage:
            queryset = queryset.filter(stage=stage)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        if function_zh_search:
            queryset = queryset.filter(Q(function_zh__icontains=function_zh_search))

        permissions = queryset.order_by("category", "sort_order", "id")

        grouped_data = defaultdict(list)
        for permission in permissions:
            grouped_data[permission.category].append(permission)

        groups = []
        for category, perms in grouped_data.items():
            groups.append(
                {
                    "category": category,
                    "stage": perms[0].stage,
                    "permissions": perms,
                }
            )

        total_permissions = queryset.count()
        active_permissions = queryset.filter(is_active=True).count()

        return {
            "groups": groups,
            "total_permissions": total_permissions,
            "active_permissions": active_permissions,
        }

    @classmethod
    def batch_update_permissions(cls, permission_ids, is_active):
        """批次更新權限的啟用狀態"""
        return cls.filter(id__in=permission_ids).update(is_active=is_active)


class RoleRepository:
    """角色資料存取層"""

    model_class = Role

    @classmethod
    def get_by_id(cls, role_id):
        """根據 ID 獲取角色"""
        return super().get_by_id(role_id)

    @staticmethod
    def get_by_code(code):
        """根據角色代碼獲取角色"""
        try:
            return Role.objects.get(code=code)
        except Role.DoesNotExist:
            return None

    @staticmethod
    def get_by_codes(codes):
        """根據多個角色代碼獲取角色"""
        return Role.objects.filter(code__in=codes)

    @staticmethod
    def get_all():
        """獲取所有角色"""
        return Role.objects.all()

    @staticmethod
    def get_active():
        """獲取所有啟用的角色"""
        return Role.objects.filter(is_active=True)

    @staticmethod
    def get_by_category(category):
        """根據分類獲取角色"""
        return Role.objects.filter(category=category)

    @staticmethod
    def get_by_level(level):
        """根據層級獲取角色"""
        return Role.objects.filter(level=level)

    @staticmethod
    def get_by_parent(parent):
        """根據父角色獲取子角色"""
        return Role.objects.filter(parents__parent_role=parent)

    @staticmethod
    def get_children(role):
        """獲取子角色"""
        return Role.objects.filter(parents__parent_role=role)

    @staticmethod
    def get_ancestors(role):
        """獲取所有祖先角色"""
        if isinstance(role, int):
            role = Role.objects.get(id=role)
        ancestors = set()
        current = role
        while current.parents.exists():
            parent = current.parents.first().parent_role
            ancestors.add(parent)
            current = parent
        return ancestors

    @staticmethod
    def get_descendants(role):
        """獲取所有後代角色"""
        descendants = set()
        children = Role.objects.filter(parents__parent_role=role)
        for child in children:
            descendants.add(child)
            descendants.update(RoleRepository.get_descendants(child))
        return descendants

    @staticmethod
    def get_tree(category=None):
        """獲取角色樹"""
        if category:
            roles = Role.objects.filter(category=category)
        else:
            roles = Role.objects.all()

        tree = []
        for role in roles:
            if not role.parents.exists():
                tree.append(RoleRepository._build_tree_node(role))
        return tree

    @staticmethod
    def _build_tree_node(role):
        """構建角色樹節點"""
        children = Role.objects.filter(parents__parent_role=role)
        return {
            "id": role.id,
            "children": [RoleRepository._build_tree_node(child) for child in children],
        }

    @staticmethod
    def get_permissions(role):
        """獲取角色的權限"""
        if isinstance(role, int):
            role = Role.objects.get(id=role)
        return Permission.objects.filter(
            id__in=RolePermission.objects.filter(role=role, is_active=True).values_list(
                "permission_id", flat=True
            ),
            is_active=True,
        )

    @staticmethod
    def get_inherited_permissions(role):
        """獲取角色繼承的權限"""
        if isinstance(role, int):
            role = Role.objects.get(id=role)
        permissions = set()
        ancestors = RoleRepository.get_ancestors(role)
        for ancestor in ancestors:
            ancestor_permissions = Permission.objects.filter(
                id__in=RolePermission.objects.filter(
                    role=ancestor, is_active=True
                ).values_list("permission_id", flat=True),
                is_active=True,
            )
            permissions.update(ancestor_permissions)
        return permissions

    @staticmethod
    def get_all_permissions(role):
        """獲取角色的所有權限（包括繼承的）"""
        if isinstance(role, int):
            role = Role.objects.get(id=role)
        direct_permissions = set(RoleRepository.get_permissions(role))
        inherited_permissions = RoleRepository.get_inherited_permissions(role)
        return direct_permissions | inherited_permissions

    @staticmethod
    def create(**kwargs):
        """建立新角色"""
        return Role.objects.create(**kwargs)

    @staticmethod
    def update(role, **kwargs):
        """更新角色"""
        for key, value in kwargs.items():
            setattr(role, key, value)
        role.save()
        return role

    @staticmethod
    def delete(role):
        """刪除角色"""
        role.delete()

    @staticmethod
    def get_user_roles(user):
        """獲取用戶的所有角色"""
        return user.roles.filter(is_active=True)

    @staticmethod
    def get_role_permissions(role):
        """獲取角色的所有權限"""
        return role.permissions.filter(is_active=True)

    @staticmethod
    def get_role_hierarchy(role):
        """獲取角色的階層關係"""
        return {
            "parents": Role.objects.filter(children__child_role=role),
            "children": Role.objects.filter(parents__parent_role=role),
        }

    @staticmethod
    def get_roles_with_user_count():
        """獲取角色列表並包含使用者數量"""
        return Role.objects.annotate(
            total_apply_users=Count("users", distinct=True)
        ).all()

    @staticmethod
    def get_role_with_user_count(role_id):
        """獲取單一角色並包含使用者數量"""
        try:
            return Role.objects.annotate(
                total_apply_users=Count("users", distinct=True)
            ).get(id=role_id)
        except Role.DoesNotExist:
            return None

    @staticmethod
    def can_delete_role(role_id):
        """檢查角色是否可以刪除（沒有綁定使用者）"""
        try:
            role = Role.objects.get(id=role_id)
            return not role.users.exists()
        except Role.DoesNotExist:
            return False

    @staticmethod
    def set_role_permissions(role_id, permission_ids):
        """設定角色權限"""
        role = Role.objects.get(id=role_id)
        role.permissions.clear()
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            role.permissions.set(permissions)
        return role

    @staticmethod
    def get_permissions_grouped_by_category_stage(stage=None):
        """獲取所有權限並按 category 和 stage 分組"""
        permissions = Permission.objects.filter(is_active=True)
        if stage:
            permissions = permissions.filter(stage=stage)
        permissions = permissions.order_by("category", "stage", "function_zh")

        groups = {}
        for permission in permissions:
            key = (permission.category, permission.stage)
            if key not in groups:
                groups[key] = []
            groups[key].append(permission)

        return groups

    @staticmethod
    def get_role_permission_ids(role_id):
        """獲取角色的權限ID列表"""
        try:
            role = Role.objects.get(id=role_id)
            return set(
                role.permissions.filter(is_active=True, stage=role.stage).values_list(
                    "id", flat=True
                )
            )
        except Role.DoesNotExist:
            return set()

    @staticmethod
    def get_all_active_permission_ids():
        """獲取所有啟用權限的ID列表"""
        return list(
            Permission.objects.filter(is_active=True).values_list("id", flat=True)
        )


class RolePermissionRepository:
    """角色權限關聯資料存取層"""

    @staticmethod
    def get_by_role(role):
        """獲取角色的所有權限關聯"""
        return RolePermission.objects.filter(role=role)

    @staticmethod
    def get_by_permission(permission):
        """獲取權限的所有角色關聯"""
        return RolePermission.objects.filter(permission=permission)

    @staticmethod
    def get_active_by_role(role):
        """獲取角色的所有啟用權限關聯"""
        return RolePermission.objects.filter(role=role, is_active=True)

    @staticmethod
    def create(role, permission, is_active=True):
        """建立角色權限關聯"""
        # 檢查是否已存在相同的角色-權限關聯
        role_permission, created = RolePermission.objects.get_or_create(
            role=role, permission=permission, defaults={"is_active": is_active}
        )

        # 如果已存在但狀態不同，則更新狀態
        if not created and role_permission.is_active != is_active:
            role_permission.is_active = is_active
            role_permission.save()

        return role_permission

    @staticmethod
    def update(role_permission, **kwargs):
        """更新角色權限關聯"""
        for key, value in kwargs.items():
            setattr(role_permission, key, value)
        role_permission.save()
        return role_permission

    @staticmethod
    def delete(role_permission):
        """刪除角色權限關聯"""
        role_permission.delete()

    @staticmethod
    @transaction.atomic
    def bulk_create(role, permissions):
        """批次建立角色權限關聯"""
        # 刪除現有的關聯
        RolePermission.objects.filter(role=role).delete()

        # 建立新的關聯
        role_permissions = [
            RolePermission(role=role, permission=permission)
            for permission in permissions
        ]
        return RolePermission.objects.bulk_create(role_permissions)


class RoleHierarchyRepository:
    """角色階層關係資料存取層"""

    @staticmethod
    def get_by_parent(parent_role):
        """獲取父角色的所有子角色關聯"""
        return RoleHierarchy.objects.filter(parent_role=parent_role)

    @staticmethod
    def get_by_child(child_role):
        """獲取子角色的所有父角色關聯"""
        return RoleHierarchy.objects.filter(child_role=child_role)

    @staticmethod
    def create(parent_role, child_role):
        """建立角色階層關係"""
        return RoleHierarchy.objects.create(
            parent_role=parent_role, child_role=child_role
        )

    @staticmethod
    def delete(role_hierarchy):
        """刪除角色階層關係"""
        role_hierarchy.delete()

    @staticmethod
    def get_all_children(role):
        """獲取角色的所有子孫角色"""
        children = Role.objects.filter(parents__parent_role=role)
        all_children = set(children)
        for child in children:
            all_children.update(RoleHierarchyRepository.get_all_children(child))
        return all_children

    @staticmethod
    def get_all_edges():
        """取得所有 parent_role_id, child_role_id tuple"""
        return RoleHierarchy.objects.all().values_list(
            "parent_role_id", "child_role_id"
        )


class UserPermissionRepository:
    """用戶權限資料存取層"""

    @classmethod
    def model(cls):
        """獲取用戶模型"""
        return get_user_model()

    @classmethod
    def get_user_permissions(cls, user):
        """獲取用戶的所有權限"""
        model_name = cls.model().__name__
        cache_key = f"{model_name}_permissions:{user.id}"
        cached_permissions = cache.get(cache_key)

        if cached_permissions is not None:
            return Permission.objects.filter(id__in=cached_permissions)

        # 獲取用戶的所有角色（包含繼承關係）
        roles = set()
        user_roles = RoleRepository.get_user_roles(user)

        for role in user_roles:
            roles.add(role.id)
            # 遞迴獲取所有父角色
            parent_roles = RoleHierarchyRepository.get_by_child(role)

            for parent in parent_roles:
                if parent.parent_role.is_active:
                    roles.add(parent.parent_role.id)
                    # 遞迴獲取父角色的父角色
                    grandparent_roles = RoleHierarchyRepository.get_by_child(
                        parent.parent_role
                    )
                    for grandparent in grandparent_roles:
                        if grandparent.parent_role.is_active:
                            roles.add(grandparent.parent_role.id)

        # 獲取這些角色的所有權限
        permissions = set()
        for role_id in roles:
            role = Role.objects.get(id=role_id)
            role_permissions = RolePermissionRepository.get_active_by_role(role)
            for rp in role_permissions:
                permissions.add(rp.permission.id)

        # 移除被禁用的權限
        if user.disabled_permissions:
            permissions -= set(user.disabled_permissions)

        # 添加直接賦予的權限
        if user.enabled_permissions:
            for item in user.enabled_permissions:
                if isinstance(item, dict):
                    if "permission" in item:
                        permissions.add(item["permission"])
                    elif "role" in item:
                        role = Role.objects.get(id=item["role"])
                        role_perms = RolePermissionRepository.get_active_by_role(role)
                        for rp in role_perms:
                            permissions.add(rp.permission.id)
                else:
                    permissions.add(item)

        # 快取權限列表
        cache.set(cache_key, list(permissions), timeout=3600)

        return Permission.objects.filter(id__in=permissions)

    @staticmethod
    def clear_user_permissions_cache(user_id):
        """清除用戶權限快取"""
        cache.delete(f"user_permissions:{user_id}")

    @classmethod
    def get_direct_permissions(cls, user_id):
        """獲取用戶的直接權限"""
        user = cls.model().objects.get(id=user_id)
        return user.permissions.filter(is_active=True)

    @classmethod
    def get_role_permissions(cls, user_id):
        """獲取用戶透過角色獲得的權限"""
        user = cls.model().objects.get(id=user_id)
        permissions = set()
        for role in user.roles.filter(is_active=True):
            permissions.update(RoleRepository.get_all_permissions(role.id))
        return list(permissions)

    @classmethod
    def get_all_permissions(cls, user_id):
        """獲取用戶的所有權限（包括角色權限）"""
        direct_permissions = set(cls.get_direct_permissions(user_id))
        role_permissions = set(cls.get_role_permissions(user_id))
        return list(direct_permissions | role_permissions)

    @classmethod
    def get_roles(cls, user_id):
        """獲取用戶的角色"""
        user = cls.model().objects.get(id=user_id)
        return user.roles.filter(is_active=True)

    @classmethod
    def has_any_permission(cls, user_id, permission_ids):
        """檢查用戶是否擁有任一指定權限"""
        user = cls.model().objects.get(id=user_id)
        if user.is_superuser:
            return True
        permissions = cls.get_user_permissions(user)
        return any(p.id in permission_ids for p in permissions)

    @classmethod
    def has_all_permissions(cls, user_id, permission_ids):
        """檢查用戶是否擁有所有指定權限"""
        user = cls.model().objects.get(id=user_id)
        if user.is_superuser:
            return True
        permissions = cls.get_user_permissions(user)
        permission_ids_set = set(permission_ids)
        user_permission_ids = {p.id for p in permissions}
        return permission_ids_set.issubset(user_permission_ids)

    @classmethod
    def add_direct_permission(cls, user_id, permission_id):
        """添加單個直接權限給使用者"""
        user = cls.model().objects.get(id=user_id)
        permission = Permission.objects.get(id=permission_id)
        user.permissions.add(permission)
        UserPermissionRepository.clear_user_permissions_cache(user_id)

    @classmethod
    def remove_direct_permission(cls, user_id, permission_id):
        """移除使用者的直接權限"""
        user = cls.model().objects.get(id=user_id)
        permission = Permission.objects.get(id=permission_id)
        user.permissions.remove(permission)
        UserPermissionRepository.clear_user_permissions_cache(user_id)

    @classmethod
    def remove_all_direct_permissions(cls, user_id):
        """移除使用者的所有直接權限"""
        user = cls.model().objects.get(id=user_id)
        user.permissions.clear()
        UserPermissionRepository.clear_user_permissions_cache(user_id)

    @classmethod
    def add_role(cls, user_id, role_id):
        """添加單個角色給使用者"""
        user = cls.model().objects.get(id=user_id)
        role = Role.objects.get(id=role_id)
        user.roles.add(role)
        UserPermissionRepository.clear_user_permissions_cache(user_id)

    @classmethod
    def remove_role(cls, user_id, role_id):
        """移除使用者的角色"""
        user = cls.model().objects.get(id=user_id)
        role = Role.objects.get(id=role_id)
        user.roles.remove(role)
        UserPermissionRepository.clear_user_permissions_cache(user_id)

    @classmethod
    def remove_all_roles(cls, user_id):
        """移除使用者的所有角色"""
        user = cls.model().objects.get(id=user_id)
        user.roles.clear()
        UserPermissionRepository.clear_user_permissions_cache(user_id)

    @classmethod
    def has_permission(cls, user, api_url, method):
        """檢查用戶是否有權限訪問指定的 API"""
        if user.is_superuser:
            return True

        permissions = cls.get_user_permissions(user)
        result = any(p.api_url == api_url and p.method == method for p in permissions)
        return result


class UserRepository:
    """使用者資料存取層"""

    @classmethod
    def model(cls):
        """獲取使用者模型"""
        return get_user_model()

    @classmethod
    def get_active_users(cls):
        """獲取所有啟用的使用者"""
        return cls.model().objects.filter(is_active=True)

    @classmethod
    def get_users_by_role(cls, role):
        """獲取指定角色的使用者"""
        return (
            cls.model().objects.filter(roles=role, is_active=True).order_by("nickname")
        )

    @classmethod
    def get_all_users_by_role(cls, role):
        """獲取指定角色的所有使用者"""
        return cls.model().objects.filter(roles=role).order_by("nickname")

    @classmethod
    def search_users(cls, search=None, department=None):
        """搜尋使用者"""
        queryset = cls.get_active_users()

        if search:
            queryset = queryset.filter(
                Q(nickname__icontains=search) | Q(email__icontains=search)
            )

        if department:
            queryset = queryset.filter(department=department)

        return queryset.order_by("nickname")

    @classmethod
    def get_users_by_ids(cls, user_ids):
        """根據使用者ID列表獲取使用者"""
        return cls.model().objects.filter(id__in=user_ids)

    @classmethod
    def get_by_id(cls, user_id):
        """根據ID獲取使用者"""
        try:
            return cls.model().objects.get(id=user_id)
        except cls.model().DoesNotExist:
            return None

    @classmethod
    def filter(cls, **kwargs):
        """過濾使用者"""
        return cls.model().objects.filter(**kwargs)

    @classmethod
    def all(cls):
        """獲取所有使用者"""
        return cls.model().objects.all()

    @classmethod
    def create(cls, **kwargs):
        """建立使用者"""
        return cls.model().objects.create(**kwargs)

    @classmethod
    def update(cls, user, **kwargs):
        """更新使用者"""
        for key, value in kwargs.items():
            setattr(user, key, value)
        user.save()
        return user

    @classmethod
    def delete(cls, user):
        """刪除使用者"""
        user.delete()
