from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from apps.rbac.services.user_permissions_service import UserPermissionService


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

        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return False

        return True
