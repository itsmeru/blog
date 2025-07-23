from rest_framework.exceptions import ValidationError

from apps.rbac.repositories import UserPermissionRepository


class UserPermissionService:
    """用戶權限服務層"""

    @staticmethod
    def get_user_permissions(user):
        """獲取用戶的所有權限"""
        try:
            return UserPermissionRepository.get_user_permissions(user)
        except Exception as e:
            raise ValidationError(f"獲取用戶權限失敗: {str(e)}")

    @staticmethod
    def clear_user_permissions_cache(user_id):
        """清除用戶權限快取"""
        try:
            UserPermissionRepository.clear_user_permissions_cache(user_id)
        except Exception as e:
            raise ValidationError(f"清除用戶權限快取失敗: {str(e)}")

    @staticmethod
    def has_permission(user, api_url, method):
        """檢查用戶是否有權限訪問指定 API"""
        try:
            return UserPermissionRepository.has_permission(user, api_url, method)
        except Exception as e:
            raise ValidationError(f"檢查用戶權限失敗: {str(e)}")

    @staticmethod
    def enable_permission(user, permission_id):
        """啟用用戶的權限"""
        try:
            if permission_id not in user.enabled_permissions:
                user.enabled_permissions.append(permission_id)
                user.save()
                UserPermissionRepository.clear_user_permissions_cache(user.id)
        except Exception as e:
            raise ValidationError(f"啟用用戶權限失敗: {str(e)}")

    @staticmethod
    def disable_permission(user, permission_id):
        """停用用戶的權限"""
        try:
            if permission_id not in user.disabled_permissions:
                user.disabled_permissions.append(permission_id)
                user.save()
                UserPermissionRepository.clear_user_permissions_cache(user.id)
        except Exception as e:
            raise ValidationError(f"停用用戶權限失敗: {str(e)}")
