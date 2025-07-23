from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Permission, Role, RoleHierarchy, RolePermission


def _clear_user_permissions_cache(user_ids):
    """清除用戶權限快取"""
    if isinstance(user_ids, (int, str)):
        user_ids = [user_ids]
    for user_id in user_ids:
        cache.delete(f"user_permissions:{user_id}")


def _get_role_users(role):
    """獲取角色關聯的所有用戶"""
    return (
        get_user_model()
        .objects.filter(enabled_permissions__contains=[{"role": role.id}])
        .values_list("id", flat=True)
    )


def _get_roles_users(roles):
    """獲取多個角色關聯的所有用戶"""
    if not roles.exists():
        return []
    role_ids = [role.id for role in roles]
    user_ids = set()
    for role_id in role_ids:
        user_ids.update(
            get_user_model()
            .objects.filter(enabled_permissions__contains=[{"role": role_id}])
            .values_list("id", flat=True)
        )
    return list(user_ids)


@receiver([post_save, post_delete], sender=Permission)
def handle_permission_change(sender, instance, **kwargs):
    """當權限變更時，清除相關用戶的權限快取"""
    # 獲取使用此權限的所有角色
    roles = Role.objects.filter(permissions=instance)
    # 獲取這些角色關聯的所有用戶
    users = _get_roles_users(roles)
    # 清除這些用戶的權限快取
    _clear_user_permissions_cache(users)


@receiver([post_save, post_delete], sender=Role)
def handle_role_change(sender, instance, **kwargs):
    """當角色變更時，清除相關用戶的權限快取"""
    users = _get_role_users(instance)
    _clear_user_permissions_cache(users)


@receiver([post_save, post_delete], sender=RolePermission)
def handle_role_permission_change(sender, instance, **kwargs):
    """當角色權限關聯變更時，清除相關用戶的權限快取"""
    users = _get_role_users(instance.role)
    _clear_user_permissions_cache(users)


@receiver([post_save, post_delete], sender=RoleHierarchy)
def handle_role_hierarchy_change(sender, instance, **kwargs):
    """當角色階層關係變更時，清除相關用戶的權限快取"""
    # 獲取子角色關聯的用戶
    child_users = _get_role_users(instance.child_role)
    # 清除這些用戶的權限快取
    _clear_user_permissions_cache(child_users)


@receiver(post_save, sender=get_user_model())
def handle_user_permission_change(sender, instance, **kwargs):
    """當用戶變更時，清除其權限快取"""
    _clear_user_permissions_cache(instance.id)
