from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rbac.models import Permission

class RBACMiddleware(MiddlewareMixin):
    """
    RBAC 權限驗證 middleware：
    - 於每次請求時檢查 user 是否有對應權限
    - 需在 view 上設置 required_permissions 屬性（list of str）
    - 若無權限則回傳 403
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        user = request.user
        # 只檢查已登入用戶
        if not user.is_authenticated:
            return None
        # 取得 view 上的 required_permissions
        required = getattr(view_func.view_class, 'required_permissions', None)
        if not required:
            return None
        # 取得 user 所有權限 code
        user_perms = set(
            rp.permission.code
            for ur in user.userrole_set.filter(is_active=True, role__is_active=True)
            for rp in ur.role.rolepermission_set.filter(is_active=True, permission__is_active=True)
        )
        # 若有任一 required_permissions 則通過
        if any(p in user_perms for p in required):
            return None
        return JsonResponse({'detail': 'Permission denied.'}, status=403) 