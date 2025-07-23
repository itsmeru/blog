from django.conf import settings
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from apps.rbac.user_permission_service import UserPermissionService


class IsRBACAllowed(BasePermission):
    def has_permission(self, request, view):
        if not self._should_check_permission(request):
            return True
        if not UserPermissionService.has_permission(
            request.user, request.path, request.method
        ):
            raise PermissionDenied("權限不足")
        return True

    def _should_check_permission(self, request):
        """判斷是否需要檢查權限"""
        # 如果不是 API 請求，不檢查權限
        if not request.path.startswith("/api/"):
            return False

        # 如果是匿名用戶，不檢查權限
        if not request.user.is_authenticated:
            return False

        # 如果是超級管理員，不檢查權限
        if request.user.is_superuser:
            return False

        # 如果是白名單 API，不檢查權限
        white_list = getattr(settings, "RBAC_WHITE_LIST", [])
        if any(request.path.rstrip("/") == path.rstrip("/") for path in white_list):
            return False

        return True
