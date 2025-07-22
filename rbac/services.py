from .models import UserRole, RolePermission

def user_has_permission(user, perm_code):
    return user.userrole_set.filter(
        is_active=True,
        role__is_active=True,
        role__rolepermission__is_active=True,
        role__rolepermission__permission__is_active=True,
        role__rolepermission__permission__code=perm_code
    ).exists() 