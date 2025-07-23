from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction

from .models import Permission, Role, RolePermission


class PermissionRepository:
    model_class = Permission

    @classmethod
    def get_by_id(cls, permission_id):
        return cls.model_class.objects.get(id=permission_id)

    @classmethod
    def get_active(cls):
        return cls.model_class.objects.filter(is_active=True)

    @classmethod
    def create(cls, **kwargs):
        return cls.model_class.objects.create(**kwargs)

    @classmethod
    def update(cls, permission, **kwargs):
        for key, value in kwargs.items():
            setattr(permission, key, value)
        permission.save()
        return permission

    @classmethod
    def delete(cls, permission):
        permission.delete()

    @classmethod
    def batch_update_permissions(cls, permission_ids, is_active):
        return cls.model_class.objects.filter(id__in=permission_ids).update(
            is_active=is_active
        )


class RoleRepository:
    model_class = Role

    @classmethod
    def get_by_id(cls, role_id):
        return cls.model_class.objects.get(id=role_id)

    @classmethod
    def get_active(cls):
        return cls.model_class.objects.filter(is_active=True)

    @classmethod
    def create(cls, **kwargs):
        return cls.model_class.objects.create(**kwargs)

    @staticmethod
    def update(role, **kwargs):
        for key, value in kwargs.items():
            setattr(role, key, value)
        role.save()
        return role

    @staticmethod
    def delete(role):
        role.delete()

    @classmethod
    def set_role_permissions(cls, role_id, permission_ids):
        role = cls.model_class.objects.get(id=role_id)
        role.permissions.clear()
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            role.permissions.set(permissions)
        return role


class RolePermissionRepository:
    model_class = RolePermission

    @classmethod
    def get_active_by_role(cls, role):
        return cls.model_class.objects.filter(role=role, is_active=True)

    @classmethod
    @transaction.atomic
    def bulk_create(cls, role, permissions):
        cls.model_class.objects.filter(role=role).delete()
        role_permissions = [
            RolePermission(role=role, permission=permission)
            for permission in permissions
        ]
        return cls.model_class.objects.bulk_create(role_permissions)


class UserPermissionRepository:
    model_class = get_user_model()

    @classmethod
    def get_user_permissions(cls, user):
        model_name = cls.model_class.__name__
        cache_key = f"{model_name}_permissions:{user.id}"
        cached_permissions = cache.get(cache_key)
        if cached_permissions:
            return Permission.objects.filter(id__in=cached_permissions)
        permissions = set()
        # ... 這裡省略部分權限聚合邏輯 ...
        cache.set(cache_key, list(permissions), timeout=3600)
        return Permission.objects.filter(id__in=permissions)

    @staticmethod
    def clear_user_permissions_cache(user_id):
        cache.delete(f"user_permissions:{user_id}")

    @classmethod
    def has_permission(cls, user, api_url, method):
        if user.is_superuser:
            return True
        permissions = cls.get_user_permissions(user)
        result = any(p.api_url == api_url and p.method == method for p in permissions)
        return result


class UserRepository:
    model_class = get_user_model()

    @classmethod
    def get_active_users(cls):
        return cls.model_class.objects.filter(is_active=True)

    @classmethod
    def get_users_by_role(cls, role):
        return cls.model_class.objects.filter(roles=role, is_active=True)
