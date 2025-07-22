from rest_framework.permissions import BasePermission

class HasPermission(BasePermission):
    required_permissions = []

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        user_perms = set(
            rp.permission.code
            for ur in user.userrole_set.all()
            for rp in ur.role.rolepermission_set.all()
        )
        required = getattr(view, 'required_permissions', self.required_permissions)
        return any(p in user_perms for p in required) 