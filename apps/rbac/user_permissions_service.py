from rest_framework.exceptions import ValidationError

from apps.rbac.repositories import UserPermissionRepository


class UserPermissionService:
    repository_class = UserPermissionRepository

    @classmethod
    def get_user_permissions(cls, user):
        try:
            return cls.repository_class.get_user_permissions(user)
        except Exception as e:
            raise ValidationError(f"獲取用戶權限失敗: {str(e)}")

    @classmethod
    def clear_user_permissions_cache(cls, user_id):
        try:
            cls.repository_class.clear_user_permissions_cache(user_id)
        except Exception as e:
            raise ValidationError(f"清除用戶權限快取失敗: {str(e)}")

    @classmethod
    def has_permission(cls, user, api_url, method):
        try:
            return cls.repository_class.has_permission(user, api_url, method)
        except Exception as e:
            raise ValidationError(f"檢查用戶權限失敗: {str(e)}")

    @classmethod
    def enable_permission(cls, user, permission_id):
        try:
            if permission_id not in user.enabled_permissions:
                user.enabled_permissions.append(permission_id)
                user.save()
                cls.repository_class.clear_user_permissions_cache(user.id)
        except Exception as e:
            raise ValidationError(f"啟用用戶權限失敗: {str(e)}")

    @classmethod
    def disable_permission(cls, user, permission_id):
        try:
            if permission_id not in user.disabled_permissions:
                user.disabled_permissions.append(permission_id)
                user.save()
                cls.repository_class.clear_user_permissions_cache(user.id)
        except Exception as e:
            raise ValidationError(f"停用用戶權限失敗: {str(e)}")
